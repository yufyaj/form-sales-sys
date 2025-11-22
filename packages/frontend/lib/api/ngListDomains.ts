/**
 * NGリストドメインAPI クライアント関数
 */

import { z } from 'zod'
import { get, post, del } from '../api-client'
import type {
  NgListDomain,
  NgListDomainListResponse,
  NgListDomainCreateRequest,
  NgListDomainCheckRequest,
  NgListDomainCheckResponse,
} from '@/types/ngListDomain'

/**
 * APIレスポンススキーマ（バックエンドのsnake_case形式）
 */
const ngListDomainResponseSchema = z.object({
  id: z.number(),
  list_id: z.number(),
  domain: z.string(),
  domain_pattern: z.string(),
  is_wildcard: z.boolean(),
  memo: z.string().nullable().optional(),
  created_at: z.string(),
  updated_at: z.string(),
  deleted_at: z.string().nullable().optional(),
})

/**
 * APIレスポンスをフロントエンドの型に変換
 * バックエンドのsnake_caseをcamelCaseに変換
 *
 * @param data - 未検証のAPIレスポンスデータ
 * @returns 検証済みのNgListDomainオブジェクト
 * @throws ZodError - レスポンスが期待する型と一致しない場合
 */
function transformNgListDomain(data: unknown): NgListDomain {
  // ランタイム型検証
  const validated = ngListDomainResponseSchema.parse(data)

  return {
    id: validated.id,
    listId: validated.list_id,
    domain: validated.domain,
    domainPattern: validated.domain_pattern,
    isWildcard: validated.is_wildcard,
    memo: validated.memo ?? null,
    createdAt: validated.created_at,
    updatedAt: validated.updated_at,
    deletedAt: validated.deleted_at ?? null,
  }
}

/**
 * リストレスポンススキーマ
 */
const ngListDomainListResponseSchema = z.object({
  ng_domains: z.array(ngListDomainResponseSchema),
  total: z.number(),
})

/**
 * リストに属するNGドメイン一覧を取得
 *
 * @param listId - リストID
 * @returns NGドメイン一覧
 */
export async function fetchNgListDomains(
  listId: number
): Promise<NgListDomainListResponse> {
  const response = await get<unknown>(
    `/ng-list-domains?list_id=${listId}`
  )

  // ランタイム型検証
  const validated = ngListDomainListResponseSchema.parse(response)

  return {
    ngDomains: validated.ng_domains.map(transformNgListDomain),
    total: validated.total,
  }
}

/**
 * NGドメインを取得
 *
 * @param ngDomainId - NGドメインID
 * @returns NGドメイン
 */
export async function fetchNgListDomain(ngDomainId: number): Promise<NgListDomain> {
  const response = await get<unknown>(`/ng-list-domains/${ngDomainId}`)
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

  const response = await post<unknown>('/ng-list-domains', requestData)
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
 * チェックレスポンススキーマ
 */
const ngListDomainCheckResponseSchema = z.object({
  is_ng: z.boolean(),
  matched_pattern: z.string().nullable().optional(),
  extracted_domain: z.string().nullable().optional(),
})

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

  const response = await post<unknown>('/ng-list-domains/check', requestData)

  // ランタイム型検証
  const validated = ngListDomainCheckResponseSchema.parse(response)

  return {
    isNg: validated.is_ng,
    matchedPattern: validated.matched_pattern ?? null,
    extractedDomain: validated.extracted_domain ?? null,
  }
}
