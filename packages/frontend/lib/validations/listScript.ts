import { z } from 'zod'

/**
 * タイトルのバリデーション
 */
const titleValidator = z
  .string({ message: 'タイトルを入力してください' })
  .trim()
  .min(1, 'タイトルを入力してください')
  .max(255, 'タイトルは255文字以内で入力してください')
  .transform((val) => {
    // NULL文字と制御文字を除去（改行・タブ・復帰は許可）
    const cleaned = val.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '')
    return cleaned.trim()
  })
  .refine(
    (val) => {
      // 最終チェック: 空でないことを確認
      return val && val.length > 0
    },
    {
      message: 'タイトルを入力してください',
    }
  )

/**
 * 本文のバリデーション
 */
const contentValidator = z
  .string({ message: '本文を入力してください' })
  .trim()
  .min(1, '本文を入力してください')
  .max(10000, '本文は10,000文字以内で入力してください')
  .transform((val) => {
    // NULL文字と制御文字を除去（改行・タブ・復帰は許可）
    const cleaned = val.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '')
    return cleaned.trim()
  })
  .refine(
    (val) => {
      // 最終チェック: 空でないことを確認
      return val && val.length > 0
    },
    {
      message: '本文を入力してください',
    }
  )

/**
 * リストスクリプト単体のスキーマ
 */
export const listScriptItemSchema = z.object({
  title: titleValidator,
  content: contentValidator,
})

/**
 * リストスクリプトフォームのバリデーションスキーマ
 */
export const listScriptFormSchema = z.object({
  scripts: z
    .array(listScriptItemSchema)
    .min(1, '少なくとも1つのスクリプトを入力してください')
    .refine(
      (scripts) => {
        // 重複チェック（タイトルで判定）
        const titleSet = new Set(scripts.map((s) => s.title))
        return titleSet.size === scripts.length
      },
      {
        message: '重複したタイトルが含まれています',
      }
    ),
})

/**
 * リストスクリプト作成リクエストのバリデーションスキーマ
 */
export const listScriptCreateSchema = z.object({
  listId: z.number().int().positive('リストIDが不正です'),
  title: titleValidator,
  content: contentValidator,
})

/**
 * リストスクリプト更新リクエストのバリデーションスキーマ
 */
export const listScriptUpdateSchema = z.object({
  title: titleValidator.optional(),
  content: contentValidator.optional(),
})

// 型推論
export type ListScriptItemData = z.infer<typeof listScriptItemSchema>
export type ListScriptFormData = z.infer<typeof listScriptFormSchema>
export type ListScriptCreateData = z.infer<typeof listScriptCreateSchema>
export type ListScriptUpdateData = z.infer<typeof listScriptUpdateSchema>
