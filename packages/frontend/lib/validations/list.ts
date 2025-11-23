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

/**
 * URL編集フォームのバリデーションスキーマ
 * セキュリティ: HTTPSのURLのみ許可
 */
export const urlEditSchema = z.object({
  url: z
    .string()
    .trim()
    .refine(
      (val) => {
        // 空文字列はOK（オプショナル）
        if (val === '') return true
        // URLフォーマットチェック
        try {
          new URL(val)
          return true
        } catch {
          return false
        }
      },
      { message: '有効なURLを入力してください' }
    )
    .refine(
      (val) => {
        // 空文字列はOK（オプショナル）
        if (val === '') return true
        // HTTPSのみ許可（セキュリティ強化）
        return val.startsWith('https://')
      },
      { message: 'HTTPSのURLを入力してください' }
    )
    .optional()
    .nullable(),
})

/**
 * リストメタデータ編集フォームのバリデーションスキーマ
 */
export const listMetadataSchema = z.object({
  url: z
    .string()
    .trim()
    .refine(
      (val) => {
        // 空文字列はOK（オプショナル）
        if (val === '') return true
        // URLフォーマットチェック
        try {
          new URL(val)
          return true
        } catch {
          return false
        }
      },
      { message: '有効なURLを入力してください' }
    )
    .refine(
      (val) => {
        // 空文字列はOK（オプショナル）
        if (val === '') return true
        // HTTPSのみ許可（セキュリティ強化）
        return val.startsWith('https://')
      },
      { message: 'HTTPSのURLを入力してください' }
    )
    .optional()
    .nullable(),
  description: z
    .string()
    .trim()
    .max(5000, '説明は5000文字以内で入力してください')
    .transform((val) => {
      // XSS対策: 制御文字を除去
      return val.replace(/[\x00-\x1F\x7F]/g, '')
    })
    .optional()
    .nullable(),
})

// 型推論
export type ListFormData = z.infer<typeof listSchema>
export type ListUpdateFormData = z.infer<typeof listUpdateSchema>
export type UrlEditFormData = z.infer<typeof urlEditSchema>
export type ListMetadataFormData = z.infer<typeof listMetadataSchema>
