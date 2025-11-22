/**
 * リストスクリプトAPI クライアント関数
 */

import { z } from 'zod'
import { get, post, patch, del } from '../api-client'
import type {
  ListScript,
  ListScriptListResponse,
  ListScriptCreateRequest,
  ListScriptUpdateRequest,
} from '@/types/listScript'

/**
 * APIレスポンススキーマ（バックエンドのsnake_case形式）
 */
const listScriptResponseSchema = z.object({
  id: z.number(),
  list_id: z.number(),
  title: z.string(),
  content: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
  deleted_at: z.string().nullable().optional(),
})

/**
 * APIレスポンスをフロントエンドの型に変換
 * バックエンドのsnake_caseをcamelCaseに変換
 *
 * @param data - 未検証のAPIレスポンスデータ
 * @returns 検証済みのListScriptオブジェクト
 * @throws ZodError - レスポンスが期待する型と一致しない場合
 */
function transformListScript(data: unknown): ListScript {
  // ランタイム型検証
  const validated = listScriptResponseSchema.parse(data)

  return {
    id: validated.id,
    listId: validated.list_id,
    title: validated.title,
    content: validated.content,
    createdAt: validated.created_at,
    updatedAt: validated.updated_at,
    deletedAt: validated.deleted_at ?? null,
  }
}

/**
 * リストレスポンススキーマ
 */
const listScriptListResponseSchema = z.object({
  scripts: z.array(listScriptResponseSchema),
  total: z.number(),
})

/**
 * リストに属するスクリプト一覧を取得
 *
 * @param listId - リストID
 * @returns スクリプト一覧
 */
export async function fetchListScripts(
  listId: number
): Promise<ListScriptListResponse> {
  const response = await get<unknown>(
    `/list-scripts?list_id=${listId}`
  )

  // ランタイム型検証
  const validated = listScriptListResponseSchema.parse(response)

  return {
    scripts: validated.scripts.map(transformListScript),
    total: validated.total,
  }
}

/**
 * スクリプトを取得
 *
 * @param scriptId - スクリプトID
 * @returns スクリプト
 */
export async function fetchListScript(scriptId: number): Promise<ListScript> {
  const response = await get<unknown>(`/list-scripts/${scriptId}`)
  return transformListScript(response)
}

/**
 * スクリプトを追加
 *
 * @param data - 作成データ
 * @returns 作成されたスクリプト
 */
export async function createListScript(
  data: ListScriptCreateRequest
): Promise<ListScript> {
  // camelCaseをsnake_caseに変換
  const requestData = {
    list_id: data.listId,
    title: data.title,
    content: data.content,
  }

  const response = await post<unknown>('/list-scripts', requestData)
  return transformListScript(response)
}

/**
 * スクリプトを更新
 *
 * @param scriptId - スクリプトID
 * @param data - 更新データ
 * @returns 更新されたスクリプト
 */
export async function updateListScript(
  scriptId: number,
  data: ListScriptUpdateRequest
): Promise<ListScript> {
  // camelCaseをsnake_caseに変換（undefinedフィールドは除外）
  const requestData: Record<string, string> = {}
  if (data.title !== undefined) requestData.title = data.title
  if (data.content !== undefined) requestData.content = data.content

  const response = await patch<unknown>(`/list-scripts/${scriptId}`, requestData)
  return transformListScript(response)
}

/**
 * スクリプトを削除
 *
 * @param scriptId - スクリプトID
 */
export async function deleteListScript(scriptId: number): Promise<void> {
  await del(`/list-scripts/${scriptId}`)
}
