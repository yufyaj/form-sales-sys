'use client'

/**
 * カラムマッピングエディタコンポーネント
 *
 * CSVのカラムとシステムのフィールドをマッピングするUI
 */

import { useMemo } from 'react'
import type { CSVColumn, SystemField } from '@/types/csvImport'
import Button from '@/components/ui/Button'
import Select from '@/components/ui/Select'

interface ColumnMappingEditorProps {
  columns: CSVColumn[]
  systemFields: SystemField[]
  mappings: Record<string, string | null>
  onMappingChange: (mappings: Record<string, string | null>) => void
}

/**
 * ColumnMappingEditorコンポーネント
 *
 * CSVカラムとシステムフィールドのマッピングを設定
 */
export default function ColumnMappingEditor({
  columns,
  systemFields,
  mappings,
  onMappingChange,
}: ColumnMappingEditorProps) {
  /**
   * バリデーション: 必須フィールドのチェック
   */
  const missingRequiredFields = useMemo(() => {
    const mappedSystemFields = new Set(Object.values(mappings).filter((v) => v !== null))
    return systemFields.filter((field) => field.required && !mappedSystemFields.has(field.id))
  }, [mappings, systemFields])

  /**
   * バリデーション: 重複マッピングのチェック
   */
  const duplicateMappings = useMemo(() => {
    const systemFieldCounts = new Map<string, number>()
    Object.values(mappings).forEach((systemField) => {
      if (systemField) {
        systemFieldCounts.set(systemField, (systemFieldCounts.get(systemField) || 0) + 1)
      }
    })
    return Array.from(systemFieldCounts.entries())
      .filter(([, count]) => count > 1)
      .map(([fieldId]) => fieldId)
  }, [mappings])

  /**
   * マッピング変更ハンドラ
   */
  const handleMappingChange = (csvColumn: string, systemField: string) => {
    onMappingChange({
      ...mappings,
      [csvColumn]: systemField === '' ? null : systemField,
    })
  }

  /**
   * 自動マッピング: カラム名が一致するフィールドを自動的にマッピング
   */
  const handleAutoMapping = () => {
    const newMappings: Record<string, string | null> = {}

    columns.forEach((column) => {
      const matchingField = systemFields.find(
        (field) => field.id.toLowerCase() === column.name.toLowerCase()
      )
      newMappings[column.name] = matchingField ? matchingField.id : null
    })

    onMappingChange(newMappings)
  }

  /**
   * システムフィールドの検索（IDから）
   */
  const getSystemField = (fieldId: string | null): SystemField | undefined => {
    if (!fieldId) return undefined
    return systemFields.find((f) => f.id === fieldId)
  }

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">カラムマッピング</h3>
          <p className="mt-1 text-sm text-gray-500">
            CSVのカラムとシステムのフィールドを対応付けてください
          </p>
        </div>
        <Button type="button" variant="outline" onClick={handleAutoMapping}>
          自動マッピング
        </Button>
      </div>

      {/* 警告メッセージ */}
      {missingRequiredFields.length > 0 && (
        <div className="rounded-md bg-yellow-50 p-4" role="alert">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-yellow-400"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">必須フィールドが未設定です</h3>
              <div className="mt-2 text-sm text-yellow-700">
                <ul className="list-disc space-y-1 pl-5">
                  {missingRequiredFields.map((field) => (
                    <li key={field.id}>{field.label}は必須です</li>
                  ))}
                </ul>              </div>
            </div>
          </div>
        </div>
      )}

      {duplicateMappings.length > 0 && (
        <div className="rounded-md bg-red-50 p-4" role="alert">
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
                同じフィールドに複数のカラムがマッピングされています
              </h3>
              <div className="mt-2 text-sm text-red-700">
                <ul className="list-disc space-y-1 pl-5">
                  {duplicateMappings.map((fieldId) => {
                    const field = getSystemField(fieldId)
                    return <li key={fieldId}>{field?.label || fieldId}</li>
                  })}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* マッピングテーブル */}
      <div className="overflow-hidden rounded-lg border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                CSVカラム
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                サンプルデータ
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                マッピング先
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {columns.map((column) => {
              const currentMapping = mappings[column.name]
              const mappedField = getSystemField(currentMapping)

              return (
                <tr key={column.name}>
                  {/* CSVカラム名 */}
                  <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-gray-900">
                    {column.name}
                  </td>

                  {/* サンプルデータ */}
                  <td className="px-6 py-4 text-sm text-gray-500">
                    <div className="space-y-1">
                      {column.sampleValues.slice(0, 3).map((value, idx) => (
                        <div key={idx} className="truncate">
                          {value || '(空)'}
                        </div>
                      ))}
                    </div>
                  </td>

                  {/* マッピング先選択 */}
                  <td className="px-6 py-4">
                    <div className="space-y-2">
                      <select
                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        value={currentMapping || ''}
                        onChange={(e) => handleMappingChange(column.name, e.target.value)}
                        aria-label={`${column.name}のマッピング先`}
                      >
                        <option value="">-- 選択してください --</option>
                        {systemFields.map((field) => (
                          <option key={field.id} value={field.id}>
                            {field.label}
                            {field.required && ' *'}
                          </option>
                        ))}
                      </select>
                      {mappedField?.description && (
                        <p className="text-xs text-gray-500">{mappedField.description}</p>
                      )}
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* フィールド凡例 */}
      <div className="rounded-md bg-gray-50 p-4">
        <h4 className="text-sm font-medium text-gray-900">システムフィールド一覧</h4>
        <div className="mt-2 grid grid-cols-2 gap-4">
          {systemFields.map((field) => (
            <div key={field.id} className="text-sm">
              <span className="font-medium text-gray-700">
                {field.label}
                {field.required && <span className="ml-1 text-red-500">*</span>}
              </span>
              <span className="ml-2 text-gray-500">({field.type})</span>
              {field.description && (
                <p className="mt-1 text-xs text-gray-500">{field.description}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
