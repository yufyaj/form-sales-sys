/**
 * ワーカー質問関連のServer Actions
 *
 * フォーム送信やデータ操作をサーバー側で処理
 */

'use server'

import { revalidatePath } from 'next/cache'
import { cookies } from 'next/headers'
import { createWorkerQuestionSchema } from '@/lib/validations/question'
import type {
  CreateWorkerQuestionFormData,
} from '@/lib/validations/question'
import type {
  WorkerQuestion,
  WorkerQuestionListResponse,
  CreateWorkerQuestionRequest,
} from '@/types/question'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * 認証トークンを取得
 */
async function getAuthToken(): Promise<string | null> {
  const cookieStore = await cookies()
  const authToken = cookieStore.get('authToken')
  return authToken?.value || null
}

/**
 * APIリクエストのエラーハンドリング
 */
async function handleApiResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      message: 'リクエストの処理中にエラーが発生しました',
    }))
    throw new Error(error.message || 'エラーが発生しました')
  }
  return response.json()
}

/**
 * ワーカー質問を作成
 *
 * @param clientOrganizationId 顧客組織ID
 * @param formData フォームデータ
 * @returns 成功時は作成された質問、失敗時はエラーメッセージ
 */
export async function createQuestionAction(
  clientOrganizationId: number,
  formData: CreateWorkerQuestionFormData
): Promise<{ success: true; data: WorkerQuestion } | { success: false; error: string }> {
  try {
    // サーバーサイドでの再バリデーション
    const validationResult = createWorkerQuestionSchema.safeParse(formData)
    if (!validationResult.success) {
      return {
        success: false,
        error: '入力内容に誤りがあります。もう一度確認してください。'
      }
    }

    const authToken = await getAuthToken()

    if (!authToken) {
      return { success: false, error: 'リクエストの処理中にエラーが発生しました' }
    }

    const requestData: CreateWorkerQuestionRequest = {
      title: validationResult.data.title,
      content: validationResult.data.content,
      clientOrganizationId,
      priority: validationResult.data.priority,
    }

    const response = await fetch(`${API_BASE_URL}/worker-questions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`,
      },
      body: JSON.stringify(requestData),
      credentials: 'include',
    })

    const data = await handleApiResponse<WorkerQuestion>(response)

    // 質問一覧のキャッシュを無効化
    revalidatePath(`/customers/${clientOrganizationId}`)

    return { success: true, data }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : '質問の投稿に失敗しました',
    }
  }
}

/**
 * 顧客組織に関連する質問一覧を取得
 *
 * @param clientOrganizationId 顧客組織ID
 * @param options フィルタオプション
 * @returns 質問一覧
 */
export async function getQuestionsByClientOrganizationAction(
  clientOrganizationId: number,
  options?: {
    status?: string
    skip?: number
    limit?: number
  }
): Promise<{ success: true; data: WorkerQuestionListResponse } | { success: false; error: string }> {
  try {
    const authToken = await getAuthToken()

    if (!authToken) {
      return { success: false, error: 'リクエストの処理中にエラーが発生しました' }
    }

    const params = new URLSearchParams({
      client_organization_id: clientOrganizationId.toString(),
      ...(options?.status && { status: options.status }),
      ...(options?.skip !== undefined && { skip: options.skip.toString() }),
      ...(options?.limit !== undefined && { limit: options.limit.toString() }),
    })

    const response = await fetch(
      `${API_BASE_URL}/worker-questions?${params.toString()}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
        credentials: 'include',
        // Server Actionsではキャッシュを無効化
        cache: 'no-store',
      }
    )

    const data = await handleApiResponse<WorkerQuestionListResponse>(response)

    return { success: true, data }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : '質問一覧の取得に失敗しました',
    }
  }
}

/**
 * 質問詳細を取得
 *
 * @param questionId 質問ID
 * @returns 質問詳細
 */
export async function getQuestionAction(
  questionId: number
): Promise<{ success: true; data: WorkerQuestion } | { success: false; error: string }> {
  try {
    const authToken = await getAuthToken()

    if (!authToken) {
      return { success: false, error: 'リクエストの処理中にエラーが発生しました' }
    }

    const response = await fetch(
      `${API_BASE_URL}/worker-questions/${questionId}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
        credentials: 'include',
        cache: 'no-store',
      }
    )

    const data = await handleApiResponse<WorkerQuestion>(response)

    return { success: true, data }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : '質問の取得に失敗しました',
    }
  }
}
