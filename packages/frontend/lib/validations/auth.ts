import { z } from 'zod'

/**
 * ログインフォームのバリデーションスキーマ
 * セキュリティ強化版：パスワード強度要件、入力のサニタイゼーション
 */
export const loginSchema = z.object({
  email: z
    .string()
    .trim() // 前後の空白を削除
    .toLowerCase() // 小文字に変換（メールアドレスの正規化）
    .min(1, 'メールアドレスを入力してください')
    .email('有効なメールアドレスを入力してください')
    .max(255, 'メールアドレスが長すぎます'),
  password: z
    .string()
    .min(1, 'パスワードを入力してください')
    .min(12, 'パスワードは12文字以上で入力してください')
    .max(128, 'パスワードが長すぎます')
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      'パスワードは大文字、小文字、数字を含む必要があります'
    ),
})

/**
 * パスワードリセットフォームのバリデーションスキーマ
 */
export const resetPasswordSchema = z.object({
  email: z
    .string()
    .trim() // 前後の空白を削除
    .toLowerCase() // 小文字に変換
    .min(1, 'メールアドレスを入力してください')
    .email('有効なメールアドレスを入力してください')
    .max(255, 'メールアドレスが長すぎます'),
})

// 型推論
export type LoginFormData = z.infer<typeof loginSchema>
export type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>
