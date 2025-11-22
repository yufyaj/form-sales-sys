/**
 * ワーカー割り当てバリデーションスキーマ
 */

import { z } from 'zod'

/**
 * ワーカー割り当てフォームのバリデーションスキーマ
 */
export const assignmentSchema = z
  .object({
    workerId: z
      .number({ message: 'ワーカーを選択してください' })
      .int('ワーカーIDは整数である必要があります')
      .positive('ワーカーIDは正の数である必要があります'),

    startRow: z
      .number({ message: '開始行を入力してください' })
      .int('開始行は整数である必要があります')
      .min(1, '開始行は1以上である必要があります'),

    endRow: z
      .number({ message: '終了行を入力してください' })
      .int('終了行は整数である必要があります')
      .min(1, '終了行は1以上である必要があります'),

    priority: z
      .enum(['low', 'medium', 'high', 'urgent'], {
        message: '優先度を選択してください',
      })
      .optional()
      .default('medium'),

    dueDate: z
      .string()
      .trim()
      .refine(
        (val) => {
          // 空文字列またはnullの場合はOK
          if (!val) return true
          // YYYY-MM-DD形式のチェック
          if (!/^\d{4}-\d{2}-\d{2}$/.test(val)) {
            return false
          }
          // ISO 8601形式で日付を解釈（YYYY-MM-DDT00:00:00Z）
          const inputDate = new Date(val + 'T00:00:00Z')
          const today = new Date()
          today.setHours(0, 0, 0, 0)
          return !isNaN(inputDate.getTime()) && inputDate >= today
        },
        { message: '日付はYYYY-MM-DD形式で、今日以降の日付を指定してください' }
      )
      .optional()
      .nullable(),

    hideAssigned: z.boolean().optional().default(false),
  })
  .refine((data) => data.startRow <= data.endRow, {
    message: '開始行は終了行以下である必要があります',
    path: ['endRow'],
  })

/**
 * 割り当て解除のバリデーションスキーマ
 */
export const unassignmentSchema = z.object({
  assignmentIds: z
    .array(z.string().uuid('無効な割り当てIDです'))
    .min(1, '解除する割り当てを選択してください'),
})

/**
 * 型推論用
 */
export type AssignmentFormData = z.infer<typeof assignmentSchema>
export type UnassignmentFormData = z.infer<typeof unassignmentSchema>
