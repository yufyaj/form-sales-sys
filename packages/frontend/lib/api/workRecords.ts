/**
 * 作業記録API
 */

import { get, post, patch } from '@/lib/api-client'
import type {
  WorkRecord,
  WorkRecordListResponse,
  WorkRecordCreateRequest,
  WorkRecordUpdateRequest,
} from '@/types/workRecord'

/**
 * 作業記録一覧取得のパラメータ
 */
export interface WorkRecordListParams {
  workerId?: number
  assignmentId?: number
  page?: number
  pageSize?: number
}

/**
 * 作業記録一覧を取得
 */
export async function listWorkRecords(
  params?: WorkRecordListParams
): Promise<WorkRecordListResponse> {
  const searchParams = new URLSearchParams()

  if (params?.workerId !== undefined) {
    searchParams.append('worker_id', params.workerId.toString())
  }
  if (params?.assignmentId !== undefined) {
    searchParams.append('assignment_id', params.assignmentId.toString())
  }
  if (params?.page !== undefined) {
    searchParams.append('page', params.page.toString())
  }
  if (params?.pageSize !== undefined) {
    searchParams.append('page_size', params.pageSize.toString())
  }

  const url = `/api/v1/work-records${
    searchParams.toString() ? `?${searchParams.toString()}` : ''
  }`
  return get<WorkRecordListResponse>(url)
}

/**
 * 作業記録詳細を取得
 */
export async function getWorkRecord(workRecordId: number): Promise<WorkRecord> {
  return get<WorkRecord>(
    `/api/v1/work-records/${encodeURIComponent(workRecordId)}`
  )
}

/**
 * 作業記録を作成
 */
export async function createWorkRecord(
  data: WorkRecordCreateRequest
): Promise<WorkRecord> {
  return post<WorkRecord>('/api/v1/work-records', data)
}

/**
 * 作業記録を更新
 */
export async function updateWorkRecord(
  workRecordId: number,
  data: WorkRecordUpdateRequest
): Promise<WorkRecord> {
  return patch<WorkRecord>(
    `/api/v1/work-records/${encodeURIComponent(workRecordId)}`,
    data
  )
}
