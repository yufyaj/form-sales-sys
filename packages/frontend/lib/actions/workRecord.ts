/**
 * 作業記録管理のServer Actions
 *
 * セキュリティ対策:
 * - Next.js Server ActionsによるCSRF保護（内部的にトークン検証）
 * - Cookie認証トークンによる認可
 * - エラー情報の適切な隠蔽（機密情報の漏洩防止）
 * - 送信可否のサーバー側再検証（クライアント側チェックのみに依存しない）
 */

'use server'

import { revalidatePath } from 'next/cache'
import { cookies } from 'next/headers'
import { z } from 'zod'
import type {
  WorkRecord,
  CreateSentWorkRecordRequest,
  CreateCannotSendWorkRecordRequest,
  UpdateWorkRecordRequest,
  CannotSendReason,
} from '@/types/workRecord'

// 環境変数からAPIベースURLを取得（フォールバック値なし - セキュリティ対策）
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL

if (!API_BASE_URL) {
  throw new Error(
    'NEXT_PUBLIC_API_BASE_URL environment variable is not set. ' +
    'Please set it in your .env.local file for local development or in your deployment environment.'
  )
}

/**
 * 入力バリデーションスキーマ
 * セキュリティ: クライアントからの入力を検証してバックエンドへの不正リクエストを防止
 */
const createSentWorkRecordSchema = z.object({
  assignment_id: z.number().int().positive('割り当てIDは正の整数である必要があります'),
  started_at: z.string().datetime('開始時刻はISO 8601形式である必要があります'),
  completed_at: z.string().datetime('完了時刻はISO 8601形式である必要があります'),
  notes: z.string().max(1000, 'メモは1000文字以内で入力してください').optional(),
})

const createCannotSendWorkRecordSchema = z.object({
  assignment_id: z.number().int().positive('割り当てIDは正の整数である必要があります'),
  started_at: z.string().datetime('開始時刻はISO 8601形式である必要があります'),
  completed_at: z.string().datetime('完了時刻はISO 8601形式である必要があります'),
  cannot_send_reason_id: z.number().int().positive('理由IDは正の整数である必要があります'),
  notes: z.string().max(1000, 'メモは1000文字以内で入力してください').optional(),
})

const updateWorkRecordSchema = z.object({
  notes: z.string().max(1000, 'メモは1000文字以内で入力してください').optional(),
  status: z.enum(['sent', 'cannot_send'], {
    errorMap: () => ({ message: 'ステータスはsentまたはcannot_sendである必要があります' }),
  }).optional(),
})

/**
 * 認証トークンを取得
 */
async function getAuthToken(): Promise<string | undefined> {
  const cookieStore = await cookies()
  return cookieStore.get('authToken')?.value
}

/**
 * APIエラーハンドリング
 * セキュリティ: サーバーエラーの詳細を隠蔽し、安全なメッセージのみを返す
 */
async function handleApiResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))

    // サーバー側エラー（500番台）は詳細を隠蔽
    if (response.status >= 500) {
      // ログには詳細を記録（サーバー側ログで確認可能）
      console.error('Server error occurred', {
        status: response.status,
        timestamp: new Date().toISOString(),
      })
      throw new Error(
        'サーバーエラーが発生しました。しばらく経ってから再度お試しください。'
      )
    }

    // クライアントエラー（400番台）は安全なメッセージのみ
    const safeErrorMessages: Record<number, string> = {
      400: '入力内容に誤りがあります',
      401: '認証が必要です',
      403: 'アクセス権限がありません',
      404: 'リソースが見つかりません',
      409: '既に存在するデータです',
      422: '入力内容を確認してください',
    }

    const safeMessage =
      safeErrorMessages[response.status] || 'リクエストの処理に失敗しました'
    throw new Error(safeMessage)
  }

  // 204 No Contentの場合は空のオブジェクトを返す
  if (response.status === 204) {
    return {} as T
  }

  return response.json()
}

/**
 * 作業記録一覧取得（割り当てID指定）
 */
export async function getWorkRecordsByAssignment(
  assignmentId: number
): Promise<{ success: boolean; data?: WorkRecord[]; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(
      `${API_BASE_URL}/api/v1/work-records?assignment_id=${assignmentId}`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        cache: 'no-store', // 常に最新データを取得
      }
    )

    const data = await handleApiResponse<WorkRecord[]>(response)
    return { success: true, data }
  } catch (error) {
    console.error('作業記録一覧取得エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error:
        error instanceof Error ? error.message : '作業記録一覧の取得に失敗しました',
    }
  }
}

/**
 * 送信不可理由一覧取得
 */
export async function getCannotSendReasons(): Promise<{
  success: boolean
  data?: CannotSendReason[]
  error?: string
}> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(`${API_BASE_URL}/api/v1/cannot-send-reasons`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      cache: 'force-cache', // マスターデータはキャッシュ可
    })

    const data = await handleApiResponse<CannotSendReason[]>(response)
    return { success: true, data }
  } catch (error) {
    console.error('送信不可理由一覧取得エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error:
        error instanceof Error ? error.message : '送信不可理由一覧の取得に失敗しました',
    }
  }
}

/**
 * 送信済み作業記録作成
 */
export async function createSentWorkRecord(
  request: CreateSentWorkRecordRequest
): Promise<{ success: boolean; data?: WorkRecord; error?: string }> {
  try {
    // 入力バリデーション
    const validation = createSentWorkRecordSchema.safeParse(request)
    if (!validation.success) {
      const firstError = validation.error.errors[0]
      return {
        success: false,
        error: firstError.message || '入力内容に誤りがあります'
      }
    }

    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(`${API_BASE_URL}/api/v1/work-records/sent`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    const data = await handleApiResponse<WorkRecord>(response)

    // キャッシュ再検証
    revalidatePath('/dashboard/worker')

    return { success: true, data }
  } catch (error) {
    console.error('送信済み作業記録作成エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error:
        error instanceof Error ? error.message : '送信済み作業記録の作成に失敗しました',
    }
  }
}

/**
 * 送信不可作業記録作成
 */
export async function createCannotSendWorkRecord(
  request: CreateCannotSendWorkRecordRequest
): Promise<{ success: boolean; data?: WorkRecord; error?: string }> {
  try {
    // 入力バリデーション
    const validation = createCannotSendWorkRecordSchema.safeParse(request)
    if (!validation.success) {
      const firstError = validation.error.errors[0]
      return {
        success: false,
        error: firstError.message || '入力内容に誤りがあります'
      }
    }

    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(
      `${API_BASE_URL}/api/v1/work-records/cannot-send`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      }
    )

    const data = await handleApiResponse<WorkRecord>(response)

    // キャッシュ再検証
    revalidatePath('/dashboard/worker')

    return { success: true, data }
  } catch (error) {
    console.error('送信不可作業記録作成エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error:
        error instanceof Error
          ? error.message
          : '送信不可作業記録の作成に失敗しました',
    }
  }
}

/**
 * 作業記録更新
 */
export async function updateWorkRecord(
  recordId: number,
  request: UpdateWorkRecordRequest
): Promise<{ success: boolean; data?: WorkRecord; error?: string }> {
  try {
    // recordIdのバリデーション
    if (!Number.isInteger(recordId) || recordId <= 0) {
      return { success: false, error: '作業記録IDは正の整数である必要があります' }
    }

    // 入力バリデーション
    const validation = updateWorkRecordSchema.safeParse(request)
    if (!validation.success) {
      const firstError = validation.error.errors[0]
      return {
        success: false,
        error: firstError.message || '入力内容に誤りがあります'
      }
    }

    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(`${API_BASE_URL}/api/v1/work-records/${recordId}`, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    const data = await handleApiResponse<WorkRecord>(response)

    // キャッシュ再検証
    revalidatePath('/dashboard/worker')

    return { success: true, data }
  } catch (error) {
    console.error('作業記録更新エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error: error instanceof Error ? error.message : '作業記録の更新に失敗しました',
    }
  }
}

/**
 * 作業記録削除
 */
export async function deleteWorkRecord(
  recordId: number
): Promise<{ success: boolean; error?: string }> {
  try {
    // recordIdのバリデーション
    if (!Number.isInteger(recordId) || recordId <= 0) {
      return { success: false, error: '作業記録IDは正の整数である必要があります' }
    }

    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(`${API_BASE_URL}/api/v1/work-records/${recordId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    await handleApiResponse<void>(response)

    // キャッシュ再検証
    revalidatePath('/dashboard/worker')

    return { success: true }
  } catch (error) {
    console.error('作業記録削除エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error: error instanceof Error ? error.message : '作業記録の削除に失敗しました',
    }
  }
}
