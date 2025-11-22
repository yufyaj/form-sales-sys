'use client'

/**
 * CSVファイルアップロード用ドロップゾーンコンポーネント
 *
 * react-dropzoneとpapaparseを使用してCSVファイルのアップロードとパースを行う
 */

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import Papa from 'papaparse'
import { csvFileSchema, validateCSVContent } from '@/lib/validations/csvImport'
import { CSV_LIMITS, type CSVColumn } from '@/types/csvImport'

interface CSVDropzoneProps {
  onFileParsed: (result: { data: any[]; columns: CSVColumn[] }) => void
  onError: (error: string) => void
  showProgress?: boolean
}

/**
 * CSVDropzoneコンポーネント
 *
 * ファイルのドラッグ&ドロップ、選択によるアップロード機能を提供
 */
export default function CSVDropzone({
  onFileParsed,
  onError,
  showProgress = false,
}: CSVDropzoneProps) {
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState(0)

  /**
   * ファイルドロップ時の処理
   */
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const file = acceptedFiles[0]

      if (!file) return

      // ファイルバリデーション
      const fileValidation = csvFileSchema.safeParse({
        name: file.name,
        size: file.size,
        type: file.type,
      })

      if (!fileValidation.success) {
        const errorMessage = fileValidation.error.errors[0]?.message || 'ファイルが無効です'
        onError(errorMessage)
        return
      }

      setIsProcessing(true)
      setProgress(0)

      // ファイル内容のセキュリティチェック
      const reader = new FileReader()
      reader.onload = (e) => {
        const content = e.target?.result as string

        // セキュリティチェック（ファイル全体をチェック）
        const securityCheck = validateCSVContent(content)
        if (!securityCheck.valid) {
          onError(securityCheck.errors[0] || 'ファイル内容が無効です')
          setIsProcessing(false)
          return
        }

        // CSVパース
        Papa.parse(file, {
          header: true, // 1行目をヘッダーとして扱う
          skipEmptyLines: true, // 空行をスキップ
          dynamicTyping: false, // 文字列のまま保持（後でバリデーション時に型変換）
          worker: false, // テスト環境との互換性のためworkerは無効化
          step: showProgress
            ? (results, parser) => {
                // プログレス更新
                const currentProgress = Math.round((parser.cursor() / file.size) * 100)
                setProgress(currentProgress)
              }
            : undefined,
          complete: (results) => {
            setIsProcessing(false)
            setProgress(100)

            // パースエラーチェック
            if (results.errors && results.errors.length > 0) {
              const firstError = results.errors[0]
              onError(`CSVパースエラー: ${firstError.message}`)
              return
            }

            // データが空でないかチェック
            if (!results.data || results.data.length === 0) {
              onError('データが空です')
              return
            }

            // カラム情報を抽出
            const firstRow = results.data[0] as Record<string, any>
            const columns: CSVColumn[] = Object.keys(firstRow).map((name, index) => ({
              name,
              index,
              sampleValues: results.data
                .slice(0, CSV_LIMITS.SAMPLE_VALUES_COUNT)
                .map((row: any) => String(row[name] || '')),
            }))

            // 成功コールバック
            onFileParsed({
              data: results.data,
              columns,
            })
          },
          error: (error) => {
            setIsProcessing(false)
            onError(`CSVパースエラー: ${error.message}`)
          },
        })
      }

      reader.onerror = () => {
        setIsProcessing(false)
        onError('ファイルの読み込みに失敗しました')
      }

      reader.readAsText(file)
    },
    [onFileParsed, onError, showProgress]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
    maxFiles: 1,
    maxSize: CSV_LIMITS.MAX_FILE_SIZE,
    disabled: isProcessing,
  })

  return (
    <div className="w-full">
      {/* ドロップゾーン */}
      <div
        {...getRootProps()}
        className={`
          relative cursor-pointer rounded-lg border-2 border-dashed p-12 text-center transition-colors
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'}
          ${isProcessing ? 'pointer-events-none opacity-50' : 'hover:border-blue-400 hover:bg-blue-50'}
        `}
      >
        <input {...getInputProps()} aria-label="ファイルを選択" />

        {isProcessing ? (
          <div className="space-y-4">
            <div className="text-blue-600">
              <svg
                className="mx-auto h-12 w-12 animate-spin"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            </div>
            <p className="text-sm text-gray-600">処理中...</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-gray-400">
              <svg
                className="mx-auto h-12 w-12"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
                aria-hidden="true"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>
            <div className="text-sm text-gray-600">
              {isDragActive ? (
                <p className="font-semibold">ここにドロップ</p>
              ) : (
                <div>
                  <p className="font-semibold">CSVファイルをドラッグ&ドロップ</p>
                  <p className="mt-1 text-xs text-gray-500">または、クリックしてファイルを選択</p>
                </div>
              )}
            </div>
            <p className="text-xs text-gray-400">最大ファイルサイズ: 10MB</p>
          </div>
        )}
      </div>

      {/* プログレスバー */}
      {showProgress && isProcessing && progress > 0 && (
        <div className="mt-4">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span>アップロード中</span>
            <span>{progress}%</span>
          </div>
          <div
            className="mt-2 h-2 w-full overflow-hidden rounded-full bg-gray-200"
            role="progressbar"
            aria-valuenow={progress}
            aria-valuemin={0}
            aria-valuemax={100}
          >
            <div
              className="h-full bg-blue-500 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}
    </div>
  )
}
