/**
 * ワーカー割り当てAPI
 */

import { get, post, del } from '@/lib/api-client'
import type {
  Assignment,
  AssignmentListResponse,
  AssignmentPriority,
} from '@/types/assignment'

/**
 * 割り当て作成リクエスト
 */
export interface AssignmentCreateRequest {
  worker_id: number
  start_row: number
  end_row: number
  priority?: AssignmentPriority
  due_date?: string | null
}

/**
 * 割り当て一覧取得のパラメータ
 */
export interface AssignmentListParams {
  page?: number
  page_size?: number
  status?: string
  worker_id?: number
  hide_assigned?: boolean
}

/**
 * プロジェクトとリストに紐づく割り当て一覧を取得
 */
export async function listAssignments(
  projectId: number,
  listId: number,
  params?: AssignmentListParams
): Promise<AssignmentListResponse> {
  const searchParams = new URLSearchParams()

  if (params?.page !== undefined) {
    searchParams.append('page', params.page.toString())
  }
  if (params?.page_size !== undefined) {
    searchParams.append('page_size', params.page_size.toString())
  }
  if (params?.status) {
    searchParams.append('status', params.status)
  }
  if (params?.worker_id !== undefined) {
    searchParams.append('worker_id', params.worker_id.toString())
  }
  if (params?.hide_assigned !== undefined) {
    searchParams.append('hide_assigned', params.hide_assigned.toString())
  }

  const url = `/api/v1/projects/${projectId}/lists/${listId}/assignments${
    searchParams.toString() ? `?${searchParams.toString()}` : ''
  }`
  return get<AssignmentListResponse>(url)
}

/**
 * 割り当て詳細を取得
 */
export async function getAssignment(
  projectId: number,
  listId: number,
  assignmentId: string
): Promise<Assignment> {
  return get<Assignment>(
    `/api/v1/projects/${projectId}/lists/${listId}/assignments/${assignmentId}`
  )
}

/**
 * ワーカーに割り当てを作成
 */
export async function createAssignment(
  projectId: number,
  listId: number,
  data: AssignmentCreateRequest
): Promise<Assignment> {
  return post<Assignment>(
    `/api/v1/projects/${projectId}/lists/${listId}/assignments`,
    data
  )
}

/**
 * 割り当てを解除（削除）
 */
export async function deleteAssignment(
  projectId: number,
  listId: number,
  assignmentId: string
): Promise<void> {
  return del<void>(
    `/api/v1/projects/${projectId}/lists/${listId}/assignments/${assignmentId}`
  )
}

/**
 * 複数の割り当てを一括解除
 */
export async function bulkDeleteAssignments(
  projectId: number,
  listId: number,
  assignmentIds: string[]
): Promise<void> {
  return post<void>(
    `/api/v1/projects/${projectId}/lists/${listId}/assignments/bulk-delete`,
    { assignment_ids: assignmentIds }
  )
}
