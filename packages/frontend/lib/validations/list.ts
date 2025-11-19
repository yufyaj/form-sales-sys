import { z } from 'zod'

/**
 * リストフォームのバリデーションスキーマ
 */
export const listSchema = z.object({
  name: z
    .string({ message: 'リスト名を入力してください' })
    .trim()
    .min(1, 'リスト名を入力してください')
    .max(255, 'リスト名は255文字以内で入力してください'),
  description: z
    .string()
    .trim()
    .max(5000, '説明は5000文字以内で入力してください')
    .optional()
    .nullable(),
})

/**
 * リスト更新フォームのバリデーションスキーマ
 * 全てのフィールドをオプショナルにする
 */
export const listUpdateSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, 'リスト名を入力してください')
    .max(255, 'リスト名は255文字以内で入力してください')
    .optional(),
  description: z
    .string()
    .trim()
    .max(5000, '説明は5000文字以内で入力してください')
    .optional()
    .nullable(),
})

// 型推論
export type ListFormData = z.infer<typeof listSchema>
export type ListUpdateFormData = z.infer<typeof listUpdateSchema>
