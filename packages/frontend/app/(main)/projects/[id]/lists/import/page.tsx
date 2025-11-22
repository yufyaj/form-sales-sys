'use client'

/**
 * CSVインポートページ
 *
 * 顧客担当者情報をCSVファイルからインポート
 */

import { use, useState } from 'react'
import { useRouter } from 'next/navigation'
import CSVImportFlow from '@/components/features/csv-import/CSVImportFlow'
import { csvClientContactSchema } from '@/lib/validations/csvImport'
import type { SystemField } from '@/types/csvImport'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'

interface CSVImportPageProps {
  params: Promise<{
    id: string
  }>
}

/**
 * 顧客担当者のシステムフィールド定義
 */
const CONTACT_SYSTEM_FIELDS: SystemField[] = [
  {
    id: 'organizationName',
    label: '組織名',
    required: true,
    type: 'string',
    description: '顧客の組織名（既存組織または新規作成）',
  },
  {
    id: 'fullName',
    label: '氏名',
    required: true,
    type: 'string',
    description: '担当者の氏名',
  },
  {
    id: 'department',
    label: '部署',
    required: false,
    type: 'string',
    description: '担当者の所属部署',
  },
  {
    id: 'position',
    label: '役職',
    required: false,
    type: 'string',
    description: '担当者の役職',
  },
  {
    id: 'email',
    label: 'メールアドレス',
    required: false,
    type: 'email',
    description: '担当者のメールアドレス',
  },
  {
    id: 'phone',
    label: '電話番号',
    required: false,
    type: 'string',
    description: '担当者の固定電話番号',
  },
  {
    id: 'mobile',
    label: '携帯電話',
    required: false,
    type: 'string',
    description: '担当者の携帯電話番号',
  },
  {
    id: 'isPrimary',
    label: '主担当',
    required: false,
    type: 'string',
    description: '主担当フラグ（true/false、1/0、yes/no）',
  },
  {
    id: 'notes',
    label: '備考',
    required: false,
    type: 'string',
    description: 'その他メモ',
  },
]

/**
 * CSVインポートページコンポーネント
 */
export default function CSVImportPage({ params }: CSVImportPageProps) {
  const router = useRouter()
  const { id } = use(params)
  const projectId = parseInt(id, 10)

  const [importSuccess, setImportSuccess] = useState(false)
  const [importedCount, setImportedCount] = useState(0)

  /**
   * インポート実行
   */
  const handleImport = async (data: any[]) => {
    try {
      // TODO: バックエンドAPIにデータを送信
      // const response = await fetch(`/api/projects/${projectId}/contacts/import`, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ contacts: data }),
      // })
      //
      // if (!response.ok) {
      //   throw new Error('インポートに失敗しました')
      // }
      //
      // const result = await response.json()

      // 仮実装: 成功とする
      console.log('Importing data:', data)
      setImportedCount(data.length)
      setImportSuccess(true)

      // 3秒後にリスト一覧に戻る
      setTimeout(() => {
        router.push(`/projects/${projectId}/lists`)
      }, 3000)
    } catch (error) {
      throw new Error(
        error instanceof Error ? error.message : 'インポート中にエラーが発生しました'
      )
    }
  }

  /**
   * キャンセル処理
   */
  const handleCancel = () => {
    router.push(`/projects/${projectId}/lists`)
  }

  /**
   * インポート成功画面
   */
  if (importSuccess) {
    return (
      <div className="container mx-auto py-8">
        <Card className="mx-auto max-w-2xl">
          <div className="p-8 text-center">
            <svg
              className="mx-auto h-16 w-16 text-green-500"
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
            <h2 className="mt-4 text-2xl font-bold text-gray-900">インポート完了</h2>
            <p className="mt-2 text-gray-600">
              {importedCount}件の顧客担当者情報をインポートしました
            </p>
            <p className="mt-4 text-sm text-gray-500">
              3秒後にリスト一覧に戻ります...
            </p>
            <div className="mt-6">
              <Button onClick={handleCancel}>リスト一覧に戻る</Button>
            </div>
          </div>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8">
      {/* ヘッダー */}
      <div className="mb-6">
        <Button
          variant="outline"
          onClick={() => router.push(`/projects/${projectId}/lists`)}
          className="mb-4"
        >
          ← リスト一覧に戻る
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">CSVインポート</h1>
          <p className="mt-2 text-gray-600">
            CSVファイルから顧客担当者情報を一括インポートします
          </p>
        </div>
      </div>

      {/* 使い方ガイド */}
      <Card className="mb-6">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900">CSVファイルの形式</h3>
          <div className="mt-4 space-y-2 text-sm text-gray-600">
            <p>以下のカラムを含むCSVファイルをアップロードしてください：</p>
            <ul className="list-inside list-disc space-y-1 pl-4">
              <li>
                <span className="font-medium">organizationName</span> (必須): 組織名
              </li>
              <li>
                <span className="font-medium">fullName</span> (必須): 担当者氏名
              </li>
              <li>department (任意): 部署</li>
              <li>position (任意): 役職</li>
              <li>email (任意): メールアドレス</li>
              <li>phone (任意): 電話番号</li>
              <li>mobile (任意): 携帯電話</li>
              <li>isPrimary (任意): 主担当フラグ (true/false)</li>
              <li>notes (任意): 備考</li>
            </ul>
          </div>
          <div className="mt-4">
            <p className="text-sm text-gray-600">
              <span className="font-medium">サンプルCSV:</span>
            </p>
            <pre className="mt-2 overflow-x-auto rounded-md bg-gray-50 p-4 text-xs">
              {`organizationName,fullName,department,position,email,phone,mobile,isPrimary,notes
テスト株式会社,山田太郎,営業部,部長,yamada@example.com,03-1234-5678,090-1234-5678,true,重要顧客
株式会社サンプル,佐藤花子,総務部,課長,sato@sample.com,03-8765-4321,080-9876-5432,false,`}
            </pre>
          </div>
        </div>
      </Card>

      {/* インポートフロー */}
      <Card>
        <div className="p-6">
          <CSVImportFlow
            systemFields={CONTACT_SYSTEM_FIELDS}
            onImport={handleImport}
            onCancel={handleCancel}
            validationSchema={csvClientContactSchema}
          />
        </div>
      </Card>
    </div>
  )
}
