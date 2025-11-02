import { type ClassValue, clsx } from "clsx"

/**
 * Tailwind CSSのクラス名を結合するユーティリティ関数
 */
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
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
