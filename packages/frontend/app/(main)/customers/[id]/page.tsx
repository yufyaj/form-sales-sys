'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import type {
  ClientOrganizationDetail,
  UpdateClientOrganizationFormData,
  CreateClientContactFormData,
  UpdateClientContactFormData,
} from '@/types/customer'
import CustomerForm from '@/components/features/customer/CustomerForm'
import CustomerContactList from '@/components/features/customer/CustomerContactList'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import { get, put, post, del } from '@/lib/api'
import { isSafeUrl } from '@/lib/utils'

/**
 * 顧客詳細ページ
 *
 * 顧客情報の表示・編集と担当者管理を提供
 */
export default function CustomerDetailPage() {
  const router = useRouter()
  const params = useParams()
  const customerIdStr = params.id as string

  const [customer, setCustomer] = useState<ClientOrganizationDetail | null>(
    null
  )
  const [isLoading, setIsLoading] = useState(true)
  const [isEditing, setIsEditing] = useState(false)
  const [error, setError] = useState<string>('')

  // 顧客IDの検証
  const customerId = parseInt(customerIdStr, 10)
  const isValidId = !isNaN(customerId) && customerId > 0

  useEffect(() => {
    if (!isValidId) {
      setError('無効な顧客IDです')
      setIsLoading(false)
      return
    }
    fetchCustomer()
  }, [customerIdStr, isValidId])

  const fetchCustomer = async () => {
    setIsLoading(true)
    setError('')

    try {
      // TODO: 実際のAPIエンドポイントに置き換える
      // const data = await get<ClientOrganizationDetail>(`/api/customers/${customerId}`)

      // 仮のモックデータ（開発中）
      const mockData: ClientOrganizationDetail = {
        id: customerId,
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
        contacts: [
          {
            id: 1,
            clientOrganizationId: customerId,
            fullName: '田中 一郎',
            department: '営業部',
            position: '部長',
            email: 'tanaka@example.com',
            phone: '03-1234-5678',
            mobile: '090-1234-5678',
            isPrimary: true,
            notes: null,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            deletedAt: null,
          },
          {
            id: 2,
            clientOrganizationId: customerId,
            fullName: '鈴木 花子',
            department: '総務部',
            position: '課長',
            email: 'suzuki@example.com',
            phone: '03-1234-5679',
            mobile: null,
            isPrimary: false,
            notes: null,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            deletedAt: null,
          },
        ],
      }

      setCustomer(mockData)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : '顧客情報の取得に失敗しました'
      )
    } finally {
      setIsLoading(false)
    }
  }

  const handleUpdateCustomer = async (data: UpdateClientOrganizationFormData) => {
    if (!customer) return

    try {
      // TODO: 実際のAPIエンドポイントに置き換える
      // await put(`/api/customers/${customerId}`, data)

      // モックの更新処理
      setCustomer({
        ...customer,
        ...data,
        updatedAt: new Date().toISOString(),
      })

      setIsEditing(false)
    } catch (err) {
      throw new Error(
        err instanceof Error ? err.message : '顧客情報の更新に失敗しました'
      )
    }
  }

  const handleAddContact = async (data: CreateClientContactFormData) => {
    if (!customer) return

    try {
      // TODO: 実際のAPIエンドポイントに置き換える
      // const newContact = await post<ClientContact>('/api/contacts', data)

      // モックの追加処理
      const newContact = {
        id: customer.contacts.length + 1,
        clientOrganizationId: data.clientOrganizationId,
        fullName: data.fullName,
        department: data.department ?? null,
        position: data.position ?? null,
        email: data.email ?? null,
        phone: data.phone ?? null,
        mobile: data.mobile ?? null,
        isPrimary: data.isPrimary ?? false,
        notes: data.notes ?? null,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        deletedAt: null,
      }

      setCustomer({
        ...customer,
        contacts: [...customer.contacts, newContact],
      })
    } catch (err) {
      throw new Error(
        err instanceof Error ? err.message : '担当者の追加に失敗しました'
      )
    }
  }

  const handleUpdateContact = async (
    contactId: number,
    data: UpdateClientContactFormData
  ) => {
    if (!customer) return

    try {
      // TODO: 実際のAPIエンドポイントに置き換える
      // await put(`/api/contacts/${contactId}`, data)

      // モックの更新処理
      setCustomer({
        ...customer,
        contacts: customer.contacts.map((contact) =>
          contact.id === contactId
            ? { ...contact, ...data, updatedAt: new Date().toISOString() }
            : contact
        ),
      })
    } catch (err) {
      throw new Error(
        err instanceof Error ? err.message : '担当者の更新に失敗しました'
      )
    }
  }

  const handleDeleteContact = async (contactId: number) => {
    if (!customer) return

    try {
      // TODO: 実際のAPIエンドポイントに置き換える
      // await del(`/api/contacts/${contactId}`)

      // モックの削除処理
      setCustomer({
        ...customer,
        contacts: customer.contacts.filter((contact) => contact.id !== contactId),
      })
    } catch (err) {
      throw new Error(
        err instanceof Error ? err.message : '担当者の削除に失敗しました'
      )
    }
  }

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

  if (error || !customer) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">{error || '顧客情報が見つかりません'}</p>
          <button
            onClick={() => router.push('/customers')}
            className="mt-4 text-blue-600 hover:underline"
          >
            一覧に戻る
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <button
            onClick={() => router.push('/customers')}
            className="mb-2 text-sm text-blue-600 hover:underline"
          >
            ← 一覧に戻る
          </button>
          <h1 className="text-3xl font-bold text-gray-900">
            {customer.organizationName}
          </h1>
        </div>
        {!isEditing && (
          <Button onClick={() => setIsEditing(true)}>顧客情報を編集</Button>
        )}
      </div>

      <div className="space-y-6">
        {/* 顧客情報 */}
        <Card>
          <h2 className="mb-4 text-xl font-semibold text-gray-900">顧客情報</h2>
          {isEditing ? (
            <CustomerForm
              customer={customer}
              onSubmit={handleUpdateCustomer}
              onCancel={() => setIsEditing(false)}
            />
          ) : (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm text-gray-500">業種</p>
                <p className="font-medium text-gray-900">
                  {customer.industry || '-'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">従業員数</p>
                <p className="font-medium text-gray-900">
                  {customer.employeeCount
                    ? `${customer.employeeCount.toLocaleString('ja-JP')}名`
                    : '-'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">年商</p>
                <p className="font-medium text-gray-900">
                  {customer.annualRevenue
                    ? `¥${customer.annualRevenue.toLocaleString('ja-JP')}`
                    : '-'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">設立年</p>
                <p className="font-medium text-gray-900">
                  {customer.establishedYear
                    ? `${customer.establishedYear}年`
                    : '-'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Webサイト</p>
                {customer.website && isSafeUrl(customer.website) ? (
                  <a
                    href={customer.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-medium text-blue-600 hover:underline"
                  >
                    {customer.website}
                  </a>
                ) : customer.website ? (
                  <p className="font-medium text-red-600" title="無効なURL形式です">
                    無効なURL
                  </p>
                ) : (
                  <p className="font-medium text-gray-900">-</p>
                )}
              </div>
              <div>
                <p className="text-sm text-gray-500">担当営業</p>
                <p className="font-medium text-gray-900">
                  {customer.salesPerson || '-'}
                </p>
              </div>
              {customer.notes && (
                <div className="col-span-2">
                  <p className="text-sm text-gray-500">備考</p>
                  <p className="font-medium text-gray-900">{customer.notes}</p>
                </div>
              )}
            </div>
          )}
        </Card>

        {/* 担当者一覧 */}
        <Card>
          <CustomerContactList
            clientOrganizationId={customer.id}
            contacts={customer.contacts}
            onAddContact={handleAddContact}
            onUpdateContact={handleUpdateContact}
            onDeleteContact={handleDeleteContact}
          />
        </Card>
      </div>
    </div>
  )
}
