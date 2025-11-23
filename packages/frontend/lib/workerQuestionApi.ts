/**
 * ワーカー質問API関数
 *
 * ワーカー質問管理に関するAPI通信を担当
 */

import { apiClient } from "./api";
import type {
  WorkerQuestion,
  WorkerQuestionCreateRequest,
  WorkerQuestionUpdateRequest,
  WorkerQuestionAnswerRequest,
  WorkerQuestionListResponse,
  WorkerQuestionListParams,
  UnreadCountResponse,
} from "@/types/workerQuestion";

/**
 * 質問一覧を取得
 *
 * @param params - クエリパラメータ
 * @returns 質問一覧レスポンス
 */
export async function fetchWorkerQuestions(
  params?: WorkerQuestionListParams
): Promise<WorkerQuestionListResponse> {
  const queryParams = new URLSearchParams();

  if (params?.status) {
    queryParams.append("status", params.status);
  }
  if (params?.priority) {
    queryParams.append("priority", params.priority);
  }
  if (params?.workerId !== undefined) {
    queryParams.append("worker_id", params.workerId.toString());
  }
  if (params?.skip !== undefined) {
    queryParams.append("skip", params.skip.toString());
  }
  if (params?.limit !== undefined) {
    queryParams.append("limit", params.limit.toString());
  }

  const queryString = queryParams.toString();
  const endpoint = `/worker-questions${queryString ? `?${queryString}` : ""}`;

  return apiClient.get<WorkerQuestionListResponse>(endpoint);
}

/**
 * 質問詳細を取得
 *
 * @param questionId - 質問ID
 * @returns 質問情報
 */
export async function fetchWorkerQuestion(
  questionId: number
): Promise<WorkerQuestion> {
  return apiClient.get<WorkerQuestion>(`/worker-questions/${questionId}`);
}

/**
 * 質問を作成
 *
 * @param data - 質問作成データ
 * @returns 作成された質問情報
 */
export async function createWorkerQuestion(
  data: WorkerQuestionCreateRequest
): Promise<WorkerQuestion> {
  return apiClient.post<WorkerQuestion>("/worker-questions", data);
}

/**
 * 質問情報を更新
 *
 * @param questionId - 質問ID
 * @param data - 更新データ
 * @returns 更新された質問情報
 */
export async function updateWorkerQuestion(
  questionId: number,
  data: WorkerQuestionUpdateRequest
): Promise<WorkerQuestion> {
  return apiClient.patch<WorkerQuestion>(
    `/worker-questions/${questionId}`,
    data
  );
}

/**
 * 質問に回答を追加
 *
 * @param questionId - 質問ID
 * @param data - 回答データ
 * @returns 更新された質問情報
 */
export async function addAnswerToWorkerQuestion(
  questionId: number,
  data: WorkerQuestionAnswerRequest
): Promise<WorkerQuestion> {
  return apiClient.post<WorkerQuestion>(
    `/worker-questions/${questionId}/answer`,
    data
  );
}

/**
 * 質問を削除（論理削除）
 *
 * @param questionId - 質問ID
 */
export async function deleteWorkerQuestion(questionId: number): Promise<void> {
  return apiClient.delete<void>(`/worker-questions/${questionId}`);
}

/**
 * 未読質問数を取得
 *
 * @returns 未読質問数
 */
export async function fetchUnreadQuestionCount(): Promise<UnreadCountResponse> {
  return apiClient.get<UnreadCountResponse>(
    "/worker-questions/stats/unread-count"
  );
}

/**
 * ワーカー別の質問一覧を取得
 *
 * @param workerId - ワーカーID
 * @param params - クエリパラメータ
 * @returns 質問一覧レスポンス
 */
export async function fetchWorkerQuestionsByWorker(
  workerId: number,
  params?: Omit<WorkerQuestionListParams, "workerId">
): Promise<WorkerQuestionListResponse> {
  const queryParams = new URLSearchParams();

  if (params?.status) {
    queryParams.append("status", params.status);
  }
  if (params?.priority) {
    queryParams.append("priority", params.priority);
  }
  if (params?.skip !== undefined) {
    queryParams.append("skip", params.skip.toString());
  }
  if (params?.limit !== undefined) {
    queryParams.append("limit", params.limit.toString());
  }

  const queryString = queryParams.toString();
  const endpoint = `/worker-questions/workers/${workerId}${
    queryString ? `?${queryString}` : ""
  }`;

  return apiClient.get<WorkerQuestionListResponse>(endpoint);
}
