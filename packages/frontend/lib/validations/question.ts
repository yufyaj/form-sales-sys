/**
 * ワーカー質問フォームのバリデーションスキーマ
 *
 * Zodを使用してフロントエンド側のバリデーションを実施
 *
 * セキュリティ対策:
 * - trim(): 前後の空白を除去し、空白のみの入力を防止
 * - min(1): 空文字列を拒否
 * - max(): DoS攻撃やストレージ圧迫を防止
 * - enum: SQLインジェクション等を防止するため、優先度を限定
 */

import { z } from 'zod'

/**
 * ワーカー質問作成フォームのバリデーションスキーマ
 *
 * フロントエンドとサーバーサイドの両方で使用される
 */
export const createWorkerQuestionSchema = z.object({
  title: z
    .string()
    .trim() // XSS対策: 前後の空白除去
    .min(1, '質問タイトルを入力してください')
    .max(500, '質問タイトルは500文字以内で入力してください'),
  content: z
    .string()
    .trim() // XSS対策: 前後の空白除去
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
