/**
 * ワーカー質問フォームのバリデーションスキーマ
 *
 * Zodを使用してフロントエンド側のバリデーションを実施
 */

import { z } from 'zod'

/**
 * ワーカー質問作成フォームのバリデーションスキーマ
 */
export const createWorkerQuestionSchema = z.object({
  title: z
    .string()
    .trim()
    .min(1, '質問タイトルを入力してください')
    .max(500, '質問タイトルは500文字以内で入力してください'),
  content: z
    .string()
    .trim()
    .min(1, '質問内容を入力してください')
    .max(5000, '質問内容は5000文字以内で入力してください'),
  priority: z
    .enum(['low', 'medium', 'high'], {
      errorMap: () => ({ message: '優先度を選択してください' }),
    })
    .optional()
    .default('medium'),
})

/**
 * フォームデータ型の推論
 */
export type CreateWorkerQuestionFormData = z.infer<
  typeof createWorkerQuestionSchema
>
