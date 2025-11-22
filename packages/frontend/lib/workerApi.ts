/**
 * ワーカーAPI関数
 *
 * ワーカー管理に関するAPI通信を担当
 */

import { apiClient } from "./api";
import type {
  Worker,
  WorkerCreateRequest,
  WorkerUpdateRequest,
  WorkerListResponse,
} from "@/types/worker";
import type { WorkerStatus } from "@/types/worker";

/**
 * ワーカー一覧取得のクエリパラメータ
 */
export interface WorkerListParams {
  status?: WorkerStatus;
  skip?: number;
  limit?: number;
}

/**
 * ワーカー一覧を取得
 *
 * @param params - クエリパラメータ
 * @returns ワーカー一覧レスポンス
 */
export async function fetchWorkers(
  params?: WorkerListParams
): Promise<WorkerListResponse> {
  const queryParams = new URLSearchParams();

  if (params?.status) {
    queryParams.append("status", params.status);
  }
  if (params?.skip !== undefined) {
    queryParams.append("skip", params.skip.toString());
  }
  if (params?.limit !== undefined) {
    queryParams.append("limit", params.limit.toString());
  }

  const queryString = queryParams.toString();
  const endpoint = `/workers${queryString ? `?${queryString}` : ""}`;

  return apiClient.get<WorkerListResponse>(endpoint);
}

/**
 * ワーカー詳細を取得
 *
 * @param workerId - ワーカーID
 * @returns ワーカー情報
 */
export async function fetchWorker(workerId: number): Promise<Worker> {
  return apiClient.get<Worker>(`/workers/${workerId}`);
}

/**
 * ワーカーを作成
 *
 * @param data - ワーカー作成データ
 * @returns 作成されたワーカー情報
 */
export async function createWorker(data: WorkerCreateRequest): Promise<Worker> {
  return apiClient.post<Worker>("/workers", data);
}

/**
 * ワーカー情報を更新
 *
 * @param workerId - ワーカーID
 * @param data - 更新データ
 * @returns 更新されたワーカー情報
 */
export async function updateWorker(
  workerId: number,
  data: WorkerUpdateRequest
): Promise<Worker> {
  return apiClient.patch<Worker>(`/workers/${workerId}`, data);
}

/**
 * ワーカーを削除（論理削除）
 *
 * @param workerId - ワーカーID
 */
export async function deleteWorker(workerId: number): Promise<void> {
  return apiClient.delete<void>(`/workers/${workerId}`);
}
