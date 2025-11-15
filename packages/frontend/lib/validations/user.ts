/**
 * ユーザー関連のバリデーションスキーマ
 */

import { z } from 'zod'

/**
 * パスワードバリデーションルール
 * - 12文字以上
 * - 大文字、小文字、数字を含む
 */
const passwordSchema = z
  .string()
  .min(12, 'パスワードは12文字以上で入力してください')
  .regex(/[A-Z]/, 'パスワードには大文字を含めてください')
  .regex(/[a-z]/, 'パスワードには小文字を含めてください')
  .regex(/[0-9]/, 'パスワードには数字を含めてください')

/**
 * メールアドレスバリデーション
 */
const emailSchema = z
  .string()
  .trim()
  .toLowerCase()
  .email('有効なメールアドレスを入力してください')

/**
 * ユーザー作成フォームスキーマ
 */
export const userCreateSchema = z.object({
  email: emailSchema,
  full_name: z
    .string()
    .trim()
    .min(1, '氏名を入力してください')
    .max(100, '氏名は100文字以内で入力してください'),
  password: passwordSchema,
  password_confirmation: z.string(),
  phone: z
    .string()
    .trim()
    .transform((val) => (val === '' ? null : val))
    .nullable(),
  description: z
    .string()
    .trim()
    .transform((val) => (val === '' ? null : val))
    .nullable(),
}).refine((data) => data.password === data.password_confirmation, {
  message: 'パスワードが一致しません',
  path: ['password_confirmation'],
})

/**
 * ユーザー更新フォームスキーマ
 */
export const userUpdateSchema = z.object({
  email: emailSchema.optional(),
  full_name: z
    .string()
    .trim()
    .min(1, '氏名を入力してください')
    .max(100, '氏名は100文字以内で入力してください')
    .optional(),
  phone: z
    .string()
    .trim()
    .transform((val) => (val === '' ? null : val))
    .nullable()
    .optional(),
  description: z
    .string()
    .trim()
    .transform((val) => (val === '' ? null : val))
    .nullable()
    .optional(),
  is_active: z.boolean().optional(),
})

/**
 * パスワード変更フォームスキーマ
 */
export const passwordChangeSchema = z
  .object({
    old_password: z.string().min(1, '現在のパスワードを入力してください'),
    new_password: passwordSchema,
    new_password_confirmation: z.string(),
  })
  .refine((data) => data.new_password === data.new_password_confirmation, {
    message: 'パスワードが一致しません',
    path: ['new_password_confirmation'],
  })

/**
 * 型推論用
 */
export type UserCreateFormData = z.infer<typeof userCreateSchema>
export type UserUpdateFormData = z.infer<typeof userUpdateSchema>
export type PasswordChangeFormData = z.infer<typeof passwordChangeSchema>
