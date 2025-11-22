'use client'

/**
 * CSVインポート統合フローコンポーネント
 *
 * アップロード、マッピング、プレビュー、インポートの一連の流れを管理
 */

import { useState, useMemo, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import CSVDropzone from './CSVDropzone'
import ColumnMappingEditor from './ColumnMappingEditor'
import CSVPreviewTable from './CSVPreviewTable'
import Button from '@/components/ui/Button'
import type {
  CSVImportStep,
  CSVColumn,
  SystemField,
  CSVValidationError,
} from '@/types/csvImport'

interface CSVImportFlowProps {
  systemFields: SystemField[]
  onImport: (data: any[]) => Promise<void>
  onCancel: () => void
  validationSchema?: any // Zodスキーマ
}

/**
 * CSVImportFlowコンポーネント
 *
 * CSVインポートの全体フローを統合管理
 */
export default function CSVImportFlow({
  systemFields,
  onImport,
  onCancel,
  validationSchema,
}: CSVImportFlowProps) {
  const [currentStep, setCurrentStep] = useState<CSVImportStep>('upload')
  const [file, setFile] = useState<File | null>(null)
  const [rawData, setRawData] = useState<any[]>([])
  const [columns, setColumns] = useState<CSVColumn[]>([])
  const [columnMappings, setColumnMappings] = useState<Record<string, string | null>>({})
  const [validationErrors, setValidationErrors] = useState<CSVValidationError[]>([])
  const [error, setError] = useState<string>('')
  const [isImporting, setIsImporting] = useState(false)

  /**
   * ステップ定義
   */
  const steps: { id: CSVImportStep; label: string; description: string }[] = [
    { id: 'upload', label: 'アップロード', description: 'CSVファイルを選択' },
    { id: 'mapping', label: 'マッピング', description: 'カラムを対応付け' },
    { id: 'preview', label: 'プレビュー', description: 'データを確認' },
    { id: 'confirm', label: '実行', description: 'インポート実行' },
  ]

  const currentStepIndex = steps.findIndex((s) => s.id === currentStep)

  /**
   * ファイルパース成功時の処理
   */
  const handleFileParsed = useCallback(
    (result: { data: any[]; columns: CSVColumn[] }) => {
      setRawData(result.data)
      setColumns(result.columns)
      setError('')
      setCurrentStep('mapping')
    },
    []
  )

  /**
   * ファイルパースエラー時の処理
   */
  const handleFileError = useCallback((errorMessage: string) => {
    setError(errorMessage)
  }, [])

  /**
   * マッピング後のデータ変換
   */
  const mappedData = useMemo(() => {
    if (Object.values(columnMappings).every((v) => v === null)) {
      return []
    }

    return rawData.map((row) => {
      const mappedRow: any = {}
      Object.entries(columnMappings).forEach(([csvColumn, systemField]) => {
        if (systemField) {
          mappedRow[systemField] = row[csvColumn]
        }
      })
      return mappedRow
    })
  }, [rawData, columnMappings])

  /**
   * データバリデーション
   */
  const validateData = useCallback(() => {
    if (!validationSchema) {
      setValidationErrors([])
      return true
    }

    const errors: CSVValidationError[] = []

    mappedData.forEach((row, index) => {
      const result = validationSchema.safeParse(row)
      if (!result.success) {
        result.error.errors.forEach((err: any) => {
          errors.push({
            row: index + 1,
            column: err.path[0]?.toString(),
            message: err.message,
            value: row[err.path[0]],
          })
        })
      }
    })

    setValidationErrors(errors)
    return errors.length === 0
  }, [mappedData, validationSchema])

  /**
   * 必須フィールドのチェック
   */
  const hasAllRequiredFields = useMemo(() => {
    const mappedSystemFields = new Set(Object.values(columnMappings).filter((v) => v !== null))
    return systemFields
      .filter((field) => field.required)
      .every((field) => mappedSystemFields.has(field.id))
  }, [columnMappings, systemFields])

  /**
   * 次のステップへ
   */
  const handleNext = () => {
    if (currentStep === 'mapping') {
      if (!hasAllRequiredFields) {
        setError('必須フィールドがすべてマッピングされていません')
        return
      }
      const isValid = validateData()
      if (!isValid) {
        setError('データにバリデーションエラーがあります')
      }
      setCurrentStep('preview')
    } else if (currentStep === 'preview') {
      setCurrentStep('confirm')
    }
  }

  /**
   * 前のステップへ
   */
  const handleBack = () => {
    if (currentStep === 'mapping') {
      setCurrentStep('upload')
      setRawData([])
      setColumns([])
      setColumnMappings({})
      setValidationErrors([])
      setError('')
    } else if (currentStep === 'preview') {
      setCurrentStep('mapping')
    } else if (currentStep === 'confirm') {
      setCurrentStep('preview')
    }
  }

  /**
   * インポート実行
   */
  const handleImport = async () => {
    try {
      setIsImporting(true)
      setError('')
      await onImport(mappedData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'インポートに失敗しました')
    } finally {
      setIsImporting(false)
    }
  }

  return (
    <div className="space-y-8">
      {/* ステップインジケーター */}
      <nav aria-label="Progress">
        <ol className="flex items-center">
          {steps.map((step, stepIdx) => (
            <li
              key={step.id}
              className={`relative ${stepIdx !== steps.length - 1 ? 'flex-1 pr-8' : ''}`}
            >
              {/* ステップの線 */}
              {stepIdx !== steps.length - 1 && (
                <div
                  className="absolute right-0 top-4 -mr-4 hidden h-0.5 w-full sm:block"
                  aria-hidden="true"
                >
                  <div
                    className={`h-full ${
                      stepIdx < currentStepIndex ? 'bg-blue-600' : 'bg-gray-200'
                    }`}
                  />
                </div>
              )}

              {/* ステップアイコン */}
              <div className="group relative flex items-start">
                <span className="flex h-9 items-center">
                  <span
                    className={`relative z-10 flex h-8 w-8 items-center justify-center rounded-full ${
                      stepIdx < currentStepIndex
                        ? 'bg-blue-600'
                        : stepIdx === currentStepIndex
                          ? 'border-2 border-blue-600 bg-white'
                          : 'border-2 border-gray-300 bg-white'
                    }`}
                  >
                    {stepIdx < currentStepIndex ? (
                      <svg
                        className="h-5 w-5 text-white"
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    ) : (
                      <span
                        className={`h-2.5 w-2.5 rounded-full ${
                          stepIdx === currentStepIndex ? 'bg-blue-600' : 'bg-gray-300'
                        }`}
                      />
                    )}
                  </span>
                </span>
                <span className="ml-4 flex min-w-0 flex-col">
                  <span
                    className={`text-sm font-medium ${
                      stepIdx <= currentStepIndex ? 'text-blue-600' : 'text-gray-500'
                    }`}
                  >
                    {step.label}
                  </span>
                  <span className="text-sm text-gray-500">{step.description}</span>
                </span>
              </div>
            </li>
          ))}
        </ol>
      </nav>

      {/* エラーメッセージ */}
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-red-400"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* ステップコンテンツ */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
        >
          {currentStep === 'upload' && (
            <CSVDropzone
              onFileParsed={handleFileParsed}
              onError={handleFileError}
              showProgress
            />
          )}

          {currentStep === 'mapping' && (
            <ColumnMappingEditor
              columns={columns}
              systemFields={systemFields}
              mappings={columnMappings}
              onMappingChange={setColumnMappings}
            />
          )}

          {currentStep === 'preview' && (
            <CSVPreviewTable
              data={mappedData}
              errors={validationErrors}
              showRowNumbers
              showStats
            />
          )}

          {currentStep === 'confirm' && (
            <div className="rounded-lg border border-gray-200 p-8">
              <div className="text-center">
                <svg
                  className="mx-auto h-12 w-12 text-green-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <h3 className="mt-4 text-lg font-medium text-gray-900">
                  インポートの準備が完了しました
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  {mappedData.length}件のデータをインポートします
                  <br />
                  {validationErrors.length === 0 ? (
                    <span className="text-green-600">バリデーションエラーはありません</span>
                  ) : (
                    <span className="text-red-600">
                      {validationErrors.length}件のエラーがあります
                    </span>
                  )}
                </p>
              </div>
            </div>
          )}
        </motion.div>
      </AnimatePresence>

      {/* アクションボタン */}
      <div className="flex items-center justify-between border-t border-gray-200 pt-6">
        <div>
          {currentStep !== 'upload' && (
            <Button type="button" variant="outline" onClick={handleBack} disabled={isImporting}>
              戻る
            </Button>
          )}
        </div>
        <div className="flex gap-3">
          <Button type="button" variant="outline" onClick={onCancel} disabled={isImporting}>
            キャンセル
          </Button>
          {currentStep === 'mapping' && (
            <Button
              type="button"
              onClick={handleNext}
              disabled={!hasAllRequiredFields || isImporting}
            >
              次へ
            </Button>
          )}
          {currentStep === 'preview' && (
            <Button type="button" onClick={handleNext} disabled={isImporting}>
              確認
            </Button>
          )}
          {currentStep === 'confirm' && (
            <Button
              type="button"
              onClick={handleImport}
              isLoading={isImporting}
              disabled={isImporting || validationErrors.length > 0}
            >
              {isImporting ? 'インポート中...' : 'インポート実行'}
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
