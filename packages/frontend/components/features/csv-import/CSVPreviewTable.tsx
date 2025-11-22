'use client'

/**
 * CSVデータプレビューテーブルコンポーネント
 *
 * マッピング後のCSVデータをプレビュー表示し、バリデーションエラーを表示
 */

import { useMemo } from 'react'
import { CSV_LIMITS, type CSVValidationError } from '@/types/csvImport'

interface CSVPreviewTableProps {
  data: any[]
  errors: CSVValidationError[]
  showRowNumbers?: boolean
  showStats?: boolean
}

/**
 * CSVPreviewTableコンポーネント
 *
 * CSVデータのプレビューとバリデーションエラーの表示
 */
export default function CSVPreviewTable({
  data,
  errors,
  showRowNumbers = false,
  showStats = false,
}: CSVPreviewTableProps) {
  /**
   * プレビュー用のデータ（最初の100行のみ）
   */
  const previewData = useMemo(() => {
    return data.slice(0, CSV_LIMITS.PREVIEW_ROWS)
  }, [data])

  /**
   * カラム名の取得
   */
  const columns = useMemo(() => {
    if (data.length === 0) return []
    return Object.keys(data[0])
  }, [data])

  /**
   * エラーが存在する行のセット
   */
  const errorRows = useMemo(() => {
    return new Set(errors.map((e) => e.row))
  }, [errors])

  /**
   * 行ごとのエラーメッセージマップ
   */
  const errorMessagesByRow = useMemo(() => {
    const map = new Map<number, CSVValidationError[]>()
    errors.forEach((error) => {
      if (!map.has(error.row)) {
        map.set(error.row, [])
      }
      map.get(error.row)?.push(error)
    })
    return map
  }, [errors])

  /**
   * 統計情報
   */
  const stats = useMemo(() => {
    return {
      total: data.length,
      valid: data.length - errorRows.size,
      invalid: errorRows.size,
    }
  }, [data.length, errorRows.size])

  // データが空の場合
  if (data.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-12 text-center">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        <p className="mt-4 text-sm text-gray-500">データがありません</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* エラーサマリー */}
      {errors.length > 0 && (
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
              <h3 className="text-sm font-medium text-red-800">
                {errors.length}件のエラーが見つかりました
              </h3>
              <div className="mt-2 text-sm text-red-700">
                <ul className="list-disc space-y-1 pl-5">
                  {errors.slice(0, 5).map((error, idx) => (
                    <li key={idx}>
                      行{error.row}
                      {error.column && ` - ${error.column}`}: {error.message}
                    </li>
                  ))}
                  {errors.length > 5 && (
                    <li className="text-red-600">他 {errors.length - 5} 件のエラー</li>
                  )}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 統計情報 */}
      {showStats && (
        <div className="flex items-center gap-6 rounded-lg bg-gray-50 p-4 text-sm">
          <div>
            <span className="font-medium text-gray-700">総行数:</span>
            <span className="ml-2 text-gray-900">{stats.total}</span>
          </div>
          <div>
            <span className="font-medium text-green-700">有効:</span>
            <span className="ml-2 text-green-900">{stats.valid}</span>
          </div>
          {stats.invalid > 0 && (
            <div>
              <span className="font-medium text-red-700">エラー:</span>
              <span className="ml-2 text-red-900">{stats.invalid}</span>
            </div>
          )}
        </div>
      )}

      {/* データ制限警告 */}
      {data.length > CSV_LIMITS.PREVIEW_ROWS && (
        <div className="rounded-md bg-blue-50 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-blue-400"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-700">
                最初の{CSV_LIMITS.PREVIEW_ROWS}行のみ表示しています（全{data.length}行）
              </p>
            </div>
          </div>
        </div>
      )}

      {/* データテーブル */}
      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {showRowNumbers && (
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  #
                </th>
              )}
              {columns.map((column) => (
                <th
                  key={column}
                  className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {previewData.map((row, rowIndex) => {
              const actualRowNumber = rowIndex + 1
              const hasError = errorRows.has(actualRowNumber)
              const rowErrors = errorMessagesByRow.get(actualRowNumber)

              return (
                <tr
                  key={rowIndex}
                  className={hasError ? 'bg-red-50' : rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                >
                  {showRowNumbers && (
                    <td className="whitespace-nowrap px-4 py-4 text-sm text-gray-500">
                      {actualRowNumber}
                    </td>
                  )}
                  {columns.map((column) => (
                    <td
                      key={column}
                      className="whitespace-nowrap px-6 py-4 text-sm text-gray-900"
                    >
                      <div>
                        {row[column] !== null && row[column] !== undefined
                          ? String(row[column])
                          : '(空)'}
                      </div>
                      {hasError && rowErrors?.some((e) => e.column === column) && (
                        <div className="mt-1 text-xs text-red-600">
                          {rowErrors
                            .filter((e) => e.column === column)
                            .map((e) => e.message)
                            .join(', ')}
                        </div>
                      )}
                    </td>
                  ))}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
