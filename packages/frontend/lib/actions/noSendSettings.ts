/**
 * 送信禁止設定管理のServer Actions
 *
 * セキュリティ対策:
 * - Next.js Server ActionsによるCSRF保護（内部的にトークン検証）
 * - Cookie認証トークンによる認可
 * - エラー情報の適切な隠蔽（機密情報の漏洩防止）
 */

'use server'

import { revalidatePath } from 'next/cache'
import { cookies } from 'next/headers'
import {
  NoSendSetting,
  CreateDayOfWeekSettingRequest,
  CreateTimeRangeSettingRequest,
  CreateSpecificDateSettingRequest,
  CreateDateRangeSettingRequest,
  UpdateNoSendSettingRequest,
} from '@/types/noSendSetting'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://localhost:8000'

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
        // 詳細は含めない（機密情報保護）
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
 * リストに紐づく送信禁止設定一覧取得
 */
export async function getNoSendSettings(
  listId: number
): Promise<{ success: boolean; data?: NoSendSetting[]; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(
      `${API_BASE_URL}/api/v1/no-send-settings?list_id=${listId}`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        cache: 'no-store', // 常に最新データを取得
      }
    )

    const data = await handleApiResponse<NoSendSetting[]>(response)
    return { success: true, data }
  } catch (error) {
    // セキュリティ: 機密情報を含まないログ記録
    console.error('送信禁止設定一覧取得エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error:
        error instanceof Error
          ? error.message
          : '送信禁止設定一覧の取得に失敗しました',
    }
  }
}

/**
 * 送信禁止設定詳細取得
 */
export async function getNoSendSetting(
  settingId: number
): Promise<{ success: boolean; data?: NoSendSetting; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(
      `${API_BASE_URL}/api/v1/no-send-settings/${settingId}`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        cache: 'no-store',
      }
    )

    const data = await handleApiResponse<NoSendSetting>(response)
    return { success: true, data }
  } catch (error) {
    // セキュリティ: 機密情報を含まないログ記録
    console.error('送信禁止設定取得エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error:
        error instanceof Error
          ? error.message
          : '送信禁止設定情報の取得に失敗しました',
    }
  }
}

/**
 * 曜日設定作成
 */
export async function createDayOfWeekSetting(
  request: CreateDayOfWeekSettingRequest
): Promise<{ success: boolean; data?: NoSendSetting; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(
      `${API_BASE_URL}/api/v1/no-send-settings/day-of-week`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      }
    )

    const data = await handleApiResponse<NoSendSetting>(response)

    // キャッシュ再検証
    revalidatePath(`/projects/[id]/lists/[listId]/settings`)

    return { success: true, data }
  } catch (error) {
    // セキュリティ: 機密情報を含まないログ記録
    console.error('曜日設定作成エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error:
        error instanceof Error ? error.message : '曜日設定の作成に失敗しました',
    }
  }
}

/**
 * 時間帯設定作成
 */
export async function createTimeRangeSetting(
  request: CreateTimeRangeSettingRequest
): Promise<{ success: boolean; data?: NoSendSetting; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(
      `${API_BASE_URL}/api/v1/no-send-settings/time-range`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      }
    )

    const data = await handleApiResponse<NoSendSetting>(response)

    // キャッシュ再検証
    revalidatePath(`/projects/[id]/lists/[listId]/settings`)

    return { success: true, data }
  } catch (error) {
    // セキュリティ: 機密情報を含まないログ記録
    console.error('時間帯設定作成エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error:
        error instanceof Error ? error.message : '時間帯設定の作成に失敗しました',
    }
  }
}

/**
 * 特定日付設定作成（単一日付）
 */
export async function createSpecificDateSetting(
  request: CreateSpecificDateSettingRequest
): Promise<{ success: boolean; data?: NoSendSetting; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(
      `${API_BASE_URL}/api/v1/no-send-settings/specific-date`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      }
    )

    const data = await handleApiResponse<NoSendSetting>(response)

    // キャッシュ再検証
    revalidatePath(`/projects/[id]/lists/[listId]/settings`)

    return { success: true, data }
  } catch (error) {
    // セキュリティ: 機密情報を含まないログ記録
    console.error('特定日付設定作成エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error:
        error instanceof Error
          ? error.message
          : '特定日付設定の作成に失敗しました',
    }
  }
}

/**
 * 期間設定作成
 */
export async function createDateRangeSetting(
  request: CreateDateRangeSettingRequest
): Promise<{ success: boolean; data?: NoSendSetting; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(
      `${API_BASE_URL}/api/v1/no-send-settings/specific-date`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      }
    )

    const data = await handleApiResponse<NoSendSetting>(response)

    // キャッシュ再検証
    revalidatePath(`/projects/[id]/lists/[listId]/settings`)

    return { success: true, data }
  } catch (error) {
    // セキュリティ: 機密情報を含まないログ記録
    console.error('期間設定作成エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error:
        error instanceof Error ? error.message : '期間設定の作成に失敗しました',
    }
  }
}

/**
 * 送信禁止設定更新
 */
export async function updateNoSendSetting(
  settingId: number,
  request: UpdateNoSendSettingRequest
): Promise<{ success: boolean; data?: NoSendSetting; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(
      `${API_BASE_URL}/api/v1/no-send-settings/${settingId}`,
      {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      }
    )

    const data = await handleApiResponse<NoSendSetting>(response)

    // キャッシュ再検証
    revalidatePath(`/projects/[id]/lists/[listId]/settings`)

    return { success: true, data }
  } catch (error) {
    // セキュリティ: 機密情報を含まないログ記録
    console.error('送信禁止設定更新エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error:
        error instanceof Error
          ? error.message
          : '送信禁止設定の更新に失敗しました',
    }
  }
}

/**
 * 送信禁止設定削除
 */
export async function deleteNoSendSetting(
  settingId: number
): Promise<{ success: boolean; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    const response = await fetch(
      `${API_BASE_URL}/api/v1/no-send-settings/${settingId}`,
      {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    )

    await handleApiResponse<void>(response)

    // キャッシュ再検証
    revalidatePath(`/projects/[id]/lists/[listId]/settings`)

    return { success: true }
  } catch (error) {
    // セキュリティ: 機密情報を含まないログ記録
    console.error('送信禁止設定削除エラー', {
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    })
    return {
      success: false,
      error:
        error instanceof Error
          ? error.message
          : '送信禁止設定の削除に失敗しました',
    }
  }
}
