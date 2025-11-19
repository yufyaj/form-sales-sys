import { get, post, patch, del } from '@/lib/api-client'

/**
 * リストAPI型定義
 */

export interface List {
  id: number
  organization_id: number
  name: string
  description: string | null
  created_at: string
  updated_at: string
  deleted_at: string | null
}

export interface ListCreateRequest {
  name: string
  description?: string | null
}

export interface ListUpdateRequest {
  name?: string
  description?: string | null
}

export interface ListListParams {
  skip?: number
  limit?: number
}

export interface ListListResponse {
  lists: List[]
  total: number
  skip: number
  limit: number
}

/**
 * プロジェクトに紐づくリスト一覧を取得
 */
export async function listListsByProject(
  projectId: number,
  params?: ListListParams
): Promise<ListListResponse> {
  const searchParams = new URLSearchParams()

  if (params?.skip !== undefined) {
    searchParams.append('skip', params.skip.toString())
  }
  if (params?.limit !== undefined) {
    searchParams.append('limit', params.limit.toString())
  }

  const url = `/api/v1/projects/${projectId}/lists${searchParams.toString() ? `?${searchParams.toString()}` : ''}`
  return get<ListListResponse>(url)
}

/**
 * リスト詳細を取得
 */
export async function getList(
  projectId: number,
  listId: number
): Promise<List> {
  return get<List>(`/api/v1/projects/${projectId}/lists/${listId}`)
}

/**
 * リストを作成
 */
export async function createList(
  projectId: number,
  data: ListCreateRequest
): Promise<List> {
  return post<List>(`/api/v1/projects/${projectId}/lists`, data)
}

/**
 * リストを更新
 */
export async function updateList(
  projectId: number,
  listId: number,
  data: ListUpdateRequest
): Promise<List> {
  return patch<List>(`/api/v1/projects/${projectId}/lists/${listId}`, data)
}

/**
 * リストを削除
 */
export async function deleteList(
  projectId: number,
  listId: number
): Promise<void> {
  return del<void>(`/api/v1/projects/${projectId}/lists/${listId}`)
}
