import { NextResponse } from 'next/server'
import { cookies } from 'next/headers'

/**
 * 現在のユーザー情報を取得するAPIエンドポイント
 * セッション検証とユーザー情報の返却を行う
 */
export async function GET(request: Request) {
  try {
    const cookieStore = await cookies()
    const authToken = cookieStore.get('authToken')

    // 認証トークンがない場合は未認証
    if (!authToken) {
      return NextResponse.json(
        { message: 'Unauthorized' },
        { status: 401 }
      )
    }

    // バックエンドの /auth/me を呼び出してユーザー情報を取得
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authToken.value}`,
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      // バックエンドから401が返ってきた場合は認証トークンを削除
      if (response.status === 401) {
        cookieStore.delete('authToken')
        cookieStore.delete('user')
      }

      return NextResponse.json(
        { message: 'Unauthorized' },
        { status: response.status }
      )
    }

    const userData = await response.json()

    // ユーザー情報を返す
    return NextResponse.json({
      id: userData.id.toString(),
      email: userData.email,
      name: userData.full_name,
      role: 'sales_company', // TODO: バックエンドからロール情報を取得
    })
  } catch (error) {
    console.error('認証エラー:', error)
    return NextResponse.json(
      { message: 'Internal Server Error' },
      { status: 500 }
    )
  }
}
