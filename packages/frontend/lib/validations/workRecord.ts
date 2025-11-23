/**
 * 作業記録フォームのバリデーションスキーマ
 */

import { z } from 'zod'

/**
 * 作業記録フォームスキーマ
 */
export const workRecordFormSchema = z.object({
  status: z.enum(['sent', 'cannot_send'], {
    required_error: '作業ステータスを選択してください',
  }),
  cannotSendReasonId: z.number().optional(),
  notes: z.string().max(1000, '備考は1000文字以内で入力してください').optional(),
})

/**
 * 作業記録フォームデータ型
 */
export type WorkRecordFormData = z.infer<typeof workRecordFormSchema>
