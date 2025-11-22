/**
 * NGリストドメインAPI クライアント関数
 */

import { get, post, del } from '../api-client'
import type {
  NgListDomain,
  NgListDomainListResponse,
  NgListDomainCreateRequest,
  NgListDomainCheckRequest,
  NgListDomainCheckResponse,
} from '@/types/ngListDomain'

/**
 * APIレスポンスをフロントエンドの型に変換
 * バックエンドのsnake_caseをcamelCaseに変換
 */
function transformNgListDomain(data: any): NgListDomain {
  return {
    id: data.id,
    listId: data.list_id,
    domain: data.domain,
    domainPattern: data.domain_pattern,
    isWildcard: data.is_wildcard,
    memo: data.memo,
    createdAt: data.created_at,
    updatedAt: data.updated_at,
    deletedAt: data.deleted_at,
  }
}

/**
 * リストに属するNGドメイン一覧を取得
 *
 * @param listId - リストID
 * @returns NGドメイン一覧
 */
export async function fetchNgListDomains(
  listId: number
): Promise<NgListDomainListResponse> {
  const response = await get<{ ng_domains: any[]; total: number }>(
    `/ng-list-domains?list_id=${listId}`
  )

  return {
    ngDomains: response.ng_domains.map(transformNgListDomain),
    total: response.total,
  }
}

/**
 * NGドメインを取得
 *
 * @param ngDomainId - NGドメインID
 * @returns NGドメイン
 */
export async function fetchNgListDomain(ngDomainId: number): Promise<NgListDomain> {
  const response = await get<any>(`/ng-list-domains/${ngDomainId}`)
  return transformNgListDomain(response)
}

/**
 * NGドメインを追加
 *
 * @param data - 作成データ
 * @returns 作成されたNGドメイン
 */
export async function createNgListDomain(
  data: NgListDomainCreateRequest
): Promise<NgListDomain> {
  // camelCaseをsnake_caseに変換
  const requestData = {
    list_id: data.listId,
    domain: data.domain,
    memo: data.memo,
  }

  const response = await post<any>('/ng-list-domains', requestData)
  return transformNgListDomain(response)
}

/**
 * NGドメインを削除
 *
 * @param ngDomainId - NGドメインID
 */
export async function deleteNgListDomain(ngDomainId: number): Promise<void> {
  await del(`/ng-list-domains/${ngDomainId}`)
}

/**
 * URLがNGリストに含まれるかチェック
 *
 * @param data - チェックリクエスト
 * @returns チェック結果
 */
export async function checkUrlIsNg(
  data: NgListDomainCheckRequest
): Promise<NgListDomainCheckResponse> {
  // camelCaseをsnake_caseに変換
  const requestData = {
    list_id: data.listId,
    url: data.url,
  }

  const response = await post<{
    is_ng: boolean
    matched_pattern?: string | null
    extracted_domain?: string | null
  }>('/ng-list-domains/check', requestData)

  return {
    isNg: response.is_ng,
    matchedPattern: response.matched_pattern,
    extractedDomain: response.extracted_domain,
  }
}
