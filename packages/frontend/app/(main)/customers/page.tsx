'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import type { ClientOrganization } from '@/types/customer'
import CustomerList from '@/components/features/customer/CustomerList'
import { get } from '@/lib/api'

/**
 * 顧客一覧ページ
 *
 * 顧客組織の一覧を表示し、詳細ページへの遷移を提供
 */
export default function CustomersPage() {
  const router = useRouter()
  const [customers, setCustomers] = useState<ClientOrganization[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    fetchCustomers()
  }, [])

  const fetchCustomers = async () => {
    setIsLoading(true)
    setError('')

    try {
      // TODO: 実際のAPIエンドポイントに置き換える
      // const data = await get<ClientOrganization[]>('/api/customers')

      // 仮のモックデータ（開発中）
      const mockData: ClientOrganization[] = [
        {
          id: 1,
          organizationId: 101,
          organizationName: '株式会社サンプル',
          industry: '製造業',
          employeeCount: 500,
          annualRevenue: 5000000000,
          establishedYear: 1990,
          website: 'https://example.com',
          salesPerson: '山田 太郎',
          notes: 'メインクライアント',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          deletedAt: null,
        },
        {
          id: 2,
          organizationId: 102,
          organizationName: 'テクノロジー株式会社',
          industry: 'IT・通信',
          employeeCount: 200,
          annualRevenue: 2000000000,
          establishedYear: 2010,
          website: 'https://tech-example.com',
          salesPerson: '佐藤 花子',
          notes: null,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          deletedAt: null,
        },
      ]

      setCustomers(mockData)
    } catch (err) {
      setError(err instanceof Error ? err.message : '顧客情報の取得に失敗しました')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCustomerClick = (customer: ClientOrganization) => {
    router.push(`/customers/${customer.id}`)
  }

  const handleAddCustomer = () => {
    router.push('/customers/new')
  }

  if (error) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">{error}</p>
          <button
            onClick={fetchCustomers}
            className="mt-4 text-blue-600 hover:underline"
          >
            再試行
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <CustomerList
        customers={customers}
        onCustomerClick={handleCustomerClick}
        onAddCustomer={handleAddCustomer}
        isLoading={isLoading}
      />
    </div>
  )
}
