/**
 * 検収管理のServer Actions
 */

'use server'

import { revalidatePath } from 'next/cache'
import { cookies } from 'next/headers'
import { Inspection, InspectionStatus } from '@/types/list'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

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
 * 検収情報取得
 * セキュリティ: IDOR対策として、projectIdとlistIdの両方を要求し、
 * バックエンドでプロジェクトへのアクセス権を検証
 */
export async function getInspection(
  projectId: number,
  listId: number
): Promise<{ success: boolean; data?: Inspection; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    // IDOR対策: プロジェクトIDを含むURLで、バックエンド側でアクセス権を検証
    const response = await fetch(
      `${API_BASE_URL}/api/v1/projects/${projectId}/lists/${listId}/inspection`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        cache: 'no-store', // 常に最新データを取得
      }
    )

    const data = await handleApiResponse<Inspection>(response)
    return { success: true, data }
  } catch (error) {
    // セキュリティ: 環境に応じたログ出力（本番環境では機密情報を除外）
    if (process.env.NODE_ENV === 'production') {
      // 本番環境: 最小限の情報のみログ出力
      console.error('検収情報取得エラー', {
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      })
    } else {
      // 開発環境: デバッグ用に詳細情報を含める
      console.error('検収情報取得エラー', {
        projectId,
        listId,
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined,
        timestamp: new Date().toISOString(),
      })
    }
    return {
      success: false,
      error: error instanceof Error ? error.message : '検収情報の取得に失敗しました',
    }
  }
}

/**
 * 検収完了
 * セキュリティ: IDOR対策として、projectIdとlistIdの両方を要求し、
 * バックエンドでプロジェクトへのアクセス権を検証
 */
export async function completeInspection(
  projectId: number,
  listId: number,
  comment?: string
): Promise<{ success: boolean; data?: Inspection; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    // IDOR対策: プロジェクトIDを含むURLで、バックエンド側でアクセス権を検証
    const response = await fetch(
      `${API_BASE_URL}/api/v1/projects/${projectId}/lists/${listId}/inspection/complete`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ comment }),
      }
    )

    const data = await handleApiResponse<Inspection>(response)

    // キャッシュ再検証
    revalidatePath(`/projects/${projectId}/lists/${listId}/inspection`)

    return { success: true, data }
  } catch (error) {
    // セキュリティ: 環境に応じたログ出力（本番環境では機密情報を除外）
    if (process.env.NODE_ENV === 'production') {
      // 本番環境: 最小限の情報のみログ出力
      console.error('検収完了エラー', {
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      })
    } else {
      // 開発環境: デバッグ用に詳細情報を含める
      console.error('検収完了エラー', {
        projectId,
        listId,
        comment: comment ? '(あり)' : '(なし)',
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined,
        timestamp: new Date().toISOString(),
      })
    }
    return {
      success: false,
      error: error instanceof Error ? error.message : '検収完了処理に失敗しました',
    }
  }
}

/**
 * 検収ステータス更新
 * セキュリティ: IDOR対策として、projectIdとlistIdの両方を要求し、
 * バックエンドでプロジェクトへのアクセス権を検証
 */
export async function updateInspectionStatus(
  projectId: number,
  listId: number,
  status: InspectionStatus
): Promise<{ success: boolean; data?: Inspection; error?: string }> {
  try {
    const token = await getAuthToken()
    if (!token) {
      return { success: false, error: '認証が必要です' }
    }

    // IDOR対策: プロジェクトIDを含むURLで、バックエンド側でアクセス権を検証
    const response = await fetch(
      `${API_BASE_URL}/api/v1/projects/${projectId}/lists/${listId}/inspection`,
      {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status }),
      }
    )

    const data = await handleApiResponse<Inspection>(response)

    // キャッシュ再検証
    revalidatePath(`/projects/${projectId}/lists/${listId}`)
    revalidatePath(`/projects/${projectId}/lists`)

    return { success: true, data }
  } catch (error) {
    // セキュリティ: 環境に応じたログ出力（本番環境では機密情報を除外）
    if (process.env.NODE_ENV === 'production') {
      // 本番環境: 最小限の情報のみログ出力
      console.error('検収ステータス更新エラー', {
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      })
    } else {
      // 開発環境: デバッグ用に詳細情報を含める
      console.error('検収ステータス更新エラー', {
        projectId,
        listId,
        status,
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined,
        timestamp: new Date().toISOString(),
      })
    }
    return {
      success: false,
      error:
        error instanceof Error ? error.message : '検収ステータスの更新に失敗しました',
    }
  }
}
