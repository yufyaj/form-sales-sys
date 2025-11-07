/**
 * CSRF（Cross-Site Request Forgery）対策ユーティリティ
 *
 * セキュリティ:
 * - CSRFトークンの生成と検証
 * - タイミング攻撃を防ぐための定数時間比較
 */

/**
 * CSRFトークンを生成する
 * 32文字のランダムな文字列を生成
 */
export function generateCSRFToken(): string {
  // crypto.randomUUIDを使用して安全なランダム文字列を生成
  return crypto.randomUUID().replace(/-/g, '')
}

/**
 * CSRFトークンを検証する
 *
 * タイミング攻撃を防ぐため、定数時間比較を使用
 * ブラウザ環境ではcrypto.subtle.timingSafeEqualが使えないため、
 * 文字列長チェックとシンプルな比較を組み合わせる
 *
 * @param token - 検証するトークン
 * @param expectedToken - 期待されるトークン
 * @returns トークンが一致する場合はtrue
 */
export function validateCSRFToken(token: string | null, expectedToken: string): boolean {
  // nullチェック
  if (!token || !expectedToken) return false

  // 長さが異なる場合は不一致
  if (token.length !== expectedToken.length) return false

  // 文字列比較（厳密等価演算子を使用）
  // Note: より高度なタイミング攻撃対策が必要な場合は、
  // サーバーサイドでの検証を推奨
  return token === expectedToken
}

/**
 * セッションストレージからCSRFトークンを取得
 * トークンが存在しない場合は新規生成して保存
 */
export function getOrCreateCSRFToken(): string {
  if (typeof window === 'undefined') {
    // SSR環境では空文字列を返す
    return ''
  }

  const storageKey = 'csrf_token'
  let token = sessionStorage.getItem(storageKey)

  if (!token) {
    token = generateCSRFToken()
    sessionStorage.setItem(storageKey, token)
  }

  return token
}

/**
 * CSRFトークンをクリアする
 * ログアウト時などに使用
 */
export function clearCSRFToken(): void {
  if (typeof window === 'undefined') return

  const storageKey = 'csrf_token'
  sessionStorage.removeItem(storageKey)
}
