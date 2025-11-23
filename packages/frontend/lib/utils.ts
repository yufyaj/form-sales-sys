import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Tailwind CSSのクラス名を結合するユーティリティ関数
 * clsxとtailwind-mergeを組み合わせて使用し、重複するTailwindクラスを適切にマージ
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * エラーメッセージのホワイトリスト
 * セキュリティ上の理由から、表示可能なエラーメッセージを制限
 */
const SAFE_ERROR_MESSAGES: Record<string, string> = {
  // 認証エラー
  'Invalid credentials': 'メールアドレスまたはパスワードが正しくありません',
  'User not found': 'メールアドレスまたはパスワードが正しくありません', // ユーザー列挙攻撃対策
  'Incorrect password': 'メールアドレスまたはパスワードが正しくありません', // ユーザー列挙攻撃対策
  'Email not verified': 'メールアドレスが確認されていません',
  'Account locked': 'アカウントがロックされています。しばらくしてから再度お試しください',

  // ネットワークエラー
  'Network error': 'ネットワークエラーが発生しました',
  'ネットワークエラーが発生しました': 'ネットワークエラーが発生しました',

  // サーバーエラー
  'Server error': 'サーバーエラーが発生しました。しばらくしてから再度お試しください',
  'Internal server error':
    'サーバーエラーが発生しました。しばらくしてから再度お試しください',

  // パスワードリセット
  'Email sent': 'パスワードリセットリンクをメールで送信しました',
  'Reset link expired': 'リセットリンクの有効期限が切れています',

  // レート制限
  'Too many requests': '試行回数が多すぎます。しばらく待ってから再度お試しください',

  // その他
  'Session expired': 'セッションの有効期限が切れています。再度ログインしてください',
}

/**
 * エラーメッセージをユーザーフレンドリーかつ安全な形式に変換
 * ホワイトリストにないメッセージは汎用メッセージに置き換える
 */
export function formatErrorMessage(error: unknown): string {
  let message = '予期しないエラーが発生しました'

  if (error instanceof Error) {
    message = error.message
  } else if (typeof error === 'string') {
    message = error
  }

  // ホワイトリストに含まれるメッセージのみ返す
  // これにより、システム内部情報の漏洩を防ぐ
  return SAFE_ERROR_MESSAGES[message] || '予期しないエラーが発生しました'
}

/**
 * メールアドレスの簡易バリデーション
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * URLの安全性を検証
 * javascript:, data:, vbscript: などの危険なプロトコルを除外してXSS攻撃を防止
 *
 * @param url - 検証するURL文字列
 * @returns 安全なURLの場合true、危険な場合やnull/undefinedの場合false
 */
export function isSafeUrl(url: string | null | undefined): boolean {
  if (!url) return false

  const urlLower = url.toLowerCase().trim()
  const dangerousProtocols = ['javascript:', 'data:', 'vbscript:', 'file:']

  return !dangerousProtocols.some(protocol => urlLower.startsWith(protocol))
}

/**
 * メールアドレスをサニタイズ
 * mailto:リンクに使用する際に、危険な文字を除去してXSS攻撃を防止
 *
 * @param email - サニタイズするメールアドレス
 * @returns サニタイズされたメールアドレス
 */
export function sanitizeEmail(email: string): string {
  // メールアドレスの形式を再検証し、危険な文字を除去
  return email.replace(/[<>'"]/g, '')
}

/**
 * 時刻フォーマットのバリデーション
 * HH:MM形式（00:00〜23:59）の妥当性を検証
 *
 * @param time - 検証する時刻文字列
 * @returns 正しいフォーマットの場合true
 */
export function validateTimeFormat(time: string): boolean {
  if (!time) return false
  const timeRegex = /^([01]\d|2[0-3]):([0-5]\d)$/
  return timeRegex.test(time)
}

/**
 * 日付範囲の妥当性検証
 * 開始日が終了日より前であることを確認
 *
 * @param startDate - 開始日（YYYY-MM-DD形式）
 * @param endDate - 終了日（YYYY-MM-DD形式）
 * @returns 妥当な範囲の場合true
 */
export function validateDateRange(startDate: string, endDate: string): boolean {
  if (!startDate || !endDate) return false

  // ISO 8601形式（YYYY-MM-DD）の基本的な検証
  const dateRegex = /^\d{4}-\d{2}-\d{2}$/
  if (!dateRegex.test(startDate) || !dateRegex.test(endDate)) {
    return false
  }

  // 開始日 <= 終了日の確認
  return startDate <= endDate
}

/**
 * プロトタイプ汚染対策: 危険なキーのブロックリスト
 */
const BLOCKED_KEYS = ['__proto__', 'constructor', 'prototype']

/**
 * プロトタイプ汚染攻撃から保護するため、危険なキーをチェック
 *
 * @param key - チェックするオブジェクトキー
 * @returns 安全なキーの場合true
 */
export function isSafeKey(key: string): boolean {
  return !BLOCKED_KEYS.includes(key)
}

/**
 * プロトタイプ汚染対策: 安全なオブジェクト作成
 * Object.create(null)を使用してプロトタイプチェーンを持たないオブジェクトを作成
 *
 * @returns プロトタイプを持たない空オブジェクト
 */
export function createSafeObject<T extends Record<string, unknown>>(): T {
  return Object.create(null) as T
}

/**
 * オブジェクトのキーをフィルタリングして安全なオブジェクトを作成
 * プロトタイプ汚染攻撃を防止
 *
 * @param obj - フィルタリングするオブジェクト
 * @returns 危険なキーを除外したオブジェクト
 */
export function sanitizeObject<T extends Record<string, unknown>>(
  obj: T
): Partial<T> {
  const safeObj = createSafeObject<Partial<T>>()

  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key) && isSafeKey(key)) {
      safeObj[key] = obj[key]
    }
  }

  return safeObj
}
