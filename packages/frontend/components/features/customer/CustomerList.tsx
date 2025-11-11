'use client'

import { useState } from 'react'
import type { ClientOrganization } from '@/types/customer'
import Table from '@/components/ui/Table'
import Badge from '@/components/ui/Badge'
import Button from '@/components/ui/Button'

interface CustomerListProps {
  customers: ClientOrganization[]
  onCustomerClick?: (customer: ClientOrganization) => void
  onAddCustomer?: () => void
  isLoading?: boolean
}

/**
 * 顧客一覧表示コンポーネント
 *
 * 顧客組織のリストをテーブル形式で表示し、検索・フィルタ・ソート機能を提供
 */
export default function CustomerList({
  customers,
  onCustomerClick,
  onAddCustomer,
  isLoading = false,
}: CustomerListProps) {
  const [searchTerm, setSearchTerm] = useState('')

  // 年商を日本円形式でフォーマット
  const formatRevenue = (revenue: number | null): string => {
    if (!revenue) return '-'
    return `¥${revenue.toLocaleString('ja-JP')}`
  }

  // 従業員数をフォーマット
  const formatEmployeeCount = (count: number | null): string => {
    if (!count) return '-'
    return `${count.toLocaleString('ja-JP')}名`
  }

  // 検索フィルタリング
  const filteredCustomers = customers.filter((customer) => {
    if (!searchTerm) return true
    const searchLower = searchTerm.toLowerCase()
    return (
      customer.organizationName.toLowerCase().includes(searchLower) ||
      customer.industry?.toLowerCase().includes(searchLower) ||
      customer.salesPerson?.toLowerCase().includes(searchLower)
    )
  })

  // テーブルカラム定義
  const columns = [
    {
      key: 'organizationName',
      header: '顧客名',
      render: (customer: ClientOrganization) => (
        <div className="flex flex-col">
          <span className="font-medium text-gray-900">
            {customer.organizationName}
          </span>
          {customer.industry && (
            <span className="text-sm text-gray-500">{customer.industry}</span>
          )}
        </div>
      ),
    },
    {
      key: 'employeeCount',
      header: '従業員数',
      render: (customer: ClientOrganization) => (
        <span className="text-sm text-gray-900">
          {formatEmployeeCount(customer.employeeCount)}
        </span>
      ),
      align: 'right' as const,
    },
    {
      key: 'annualRevenue',
      header: '年商',
      render: (customer: ClientOrganization) => (
        <span className="text-sm text-gray-900">
          {formatRevenue(customer.annualRevenue)}
        </span>
      ),
      align: 'right' as const,
    },
    {
      key: 'salesPerson',
      header: '担当営業',
      render: (customer: ClientOrganization) => (
        <span className="text-sm text-gray-900">
          {customer.salesPerson || '-'}
        </span>
      ),
    },
    {
      key: 'website',
      header: 'Webサイト',
      render: (customer: ClientOrganization) =>
        customer.website ? (
          <a
            href={customer.website}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-blue-600 hover:text-blue-800 hover:underline"
            onClick={(e) => e.stopPropagation()}
          >
            リンク
          </a>
        ) : (
          <span className="text-sm text-gray-400">-</span>
        ),
    },
  ]

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="text-center">
          <div className="mb-4 inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-gray-900">顧客一覧</h2>
          <p className="mt-1 text-sm text-gray-500">
            {filteredCustomers.length}件の顧客を表示中
          </p>
        </div>
        {onAddCustomer && (
          <Button onClick={onAddCustomer} variant="default">
            顧客を追加
          </Button>
        )}
      </div>

      {/* 検索バー */}
      <div className="flex items-center gap-4">
        <div className="flex-1">
          <input
            type="text"
            placeholder="顧客名、業種、担当営業で検索..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* テーブル */}
      <Table<ClientOrganization>
        columns={columns}
        data={filteredCustomers}
        keyExtractor={(customer) => customer.id.toString()}
        onRowClick={onCustomerClick}
        emptyMessage={
          searchTerm
            ? '検索条件に一致する顧客が見つかりませんでした'
            : '顧客が登録されていません'
        }
      />
    </div>
  )
}
