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
          if (!val) return true
          const date = new Date(val)
          return !isNaN(date.getTime()) && date > new Date()
        },
        { message: '期限は未来の日時を指定してください' }
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
