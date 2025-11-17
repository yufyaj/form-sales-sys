import { get } from '@/lib/api-client'

/**
 * 顧客企業API型定義
 */

export interface ClientOrganization {
  id: number
  name: string
  email: string | null
  phone: string | null
  address: string | null
  sales_support_organization_id: number
  created_at: string
  updated_at: string
}

export interface ClientOrganizationListParams {
  skip?: number
  limit?: number
}

export interface ClientOrganizationListResponse {
  items: ClientOrganization[]
  total: number
}

/**
 * 顧客企業一覧を取得
 */
export async function listClientOrganizations(
  params?: ClientOrganizationListParams
): Promise<ClientOrganizationListResponse> {
  const searchParams = new URLSearchParams()

  if (params?.skip !== undefined) {
    searchParams.append('skip', params.skip.toString())
  }
  if (params?.limit !== undefined) {
    searchParams.append('limit', params.limit.toString())
  }

  const url = `/api/v1/client-organizations${searchParams.toString() ? `?${searchParams.toString()}` : ''}`
  return get<ClientOrganizationListResponse>(url)
}

/**
 * 顧客企業詳細を取得
 */
export async function getClientOrganization(
  clientOrganizationId: number
): Promise<ClientOrganization> {
  return get<ClientOrganization>(`/api/v1/client-organizations/${clientOrganizationId}`)
}
