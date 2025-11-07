import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

/**
 * Next.js Middleware
 *
 * セキュリティヘッダーの設定:
 * - CSP (Content Security Policy): nonce-basedで実装
 * - その他のセキュリティヘッダーはnext.config.mjsで設定
 */
export function middleware(request: NextRequest) {
  // nonceを生成（32文字のランダム文字列）
  const nonce = Buffer.from(crypto.randomUUID()).toString('base64')

  // API URLを環境変数から取得
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  // CSPヘッダーを構築
  const cspHeader = [
    "default-src 'self'",
    // strict-dynamicを使用してnonce付きスクリプトから読み込まれたスクリプトを許可
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'`,
    // Tailwind CSSのため、一時的にunsafe-inlineを許可（将来的には削除予定）
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: https:",
    "font-src 'self' data:",
    `connect-src 'self' ${apiUrl}`,
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "object-src 'none'",
  ].join('; ')

  // レスポンスを作成
  const response = NextResponse.next()

  // CSPヘッダーを設定
  response.headers.set('Content-Security-Policy', cspHeader)

  // nonceをカスタムヘッダーとして追加（Next.jsのスクリプトタグで使用）
  response.headers.set('x-nonce', nonce)

  return response
}

/**
 * Middlewareを適用するパスの設定
 * - API routes, 静的ファイル, Next.js internal filesを除外
 */
export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}
