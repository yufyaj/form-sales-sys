import { type ClassValue, clsx } from "clsx"

/**
 * Tailwind CSSのクラス名を結合するユーティリティ関数
 */
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

/**
 * エラーメッセージをユーザーフレンドリーな形式に変換
 */
export function formatErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }
  if (typeof error === 'string') {
    return error
  }
  return '予期しないエラーが発生しました'
}

/**
 * メールアドレスの簡易バリデーション
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}
