import { z } from 'zod'

/**
 * プロジェクトステータスの列挙型
 */
export const ProjectStatus = {
  PLANNING: 'planning',
  ACTIVE: 'active',
  COMPLETED: 'completed',
  CANCELLED: 'cancelled',
} as const

export type ProjectStatusType = (typeof ProjectStatus)[keyof typeof ProjectStatus]

/**
 * プロジェクトフォームのバリデーションスキーマ
 */
export const projectSchema = z
  .object({
    name: z
      .string()
      .trim()
      .min(1, 'プロジェクト名を入力してください')
      .max(255, 'プロジェクト名は255文字以内で入力してください'),
    client_organization_id: z
      .number({
        required_error: '顧客企業を選択してください',
        invalid_type_error: '顧客企業を選択してください',
      })
      .int('無効な顧客企業IDです')
      .positive('顧客企業を選択してください'),
    status: z.enum(['planning', 'active', 'completed', 'cancelled'], {
      required_error: 'ステータスを選択してください',
    }),
    start_date: z.string().optional().nullable(),
    end_date: z.string().optional().nullable(),
    description: z
      .string()
      .trim()
      .max(5000, '説明は5000文字以内で入力してください')
      .optional()
      .nullable(),
  })
  .refine(
    (data) => {
      // 開始日と終了日が両方入力されている場合、終了日は開始日以降である必要がある
      if (data.start_date && data.end_date) {
        const startDate = new Date(data.start_date)
        const endDate = new Date(data.end_date)
        return endDate >= startDate
      }
      return true
    },
    {
      message: '終了日は開始日以降の日付を指定してください',
      path: ['end_date'],
    }
  )

/**
 * プロジェクト更新フォームのバリデーションスキーマ
 * 全てのフィールドをオプショナルにする
 */
export const projectUpdateSchema = z
  .object({
    name: z
      .string()
      .trim()
      .min(1, 'プロジェクト名を入力してください')
      .max(255, 'プロジェクト名は255文字以内で入力してください')
      .optional(),
    client_organization_id: z
      .number({
        invalid_type_error: '顧客企業を選択してください',
      })
      .int('無効な顧客企業IDです')
      .positive('顧客企業を選択してください')
      .optional(),
    status: z
      .enum(['planning', 'active', 'completed', 'cancelled'])
      .optional(),
    start_date: z.string().optional().nullable(),
    end_date: z.string().optional().nullable(),
    description: z
      .string()
      .trim()
      .max(5000, '説明は5000文字以内で入力してください')
      .optional()
      .nullable(),
  })
  .refine(
    (data) => {
      // 開始日と終了日が両方入力されている場合、終了日は開始日以降である必要がある
      if (data.start_date && data.end_date) {
        const startDate = new Date(data.start_date)
        const endDate = new Date(data.end_date)
        return endDate >= startDate
      }
      return true
    },
    {
      message: '終了日は開始日以降の日付を指定してください',
      path: ['end_date'],
    }
  )

// 型推論
export type ProjectFormData = z.infer<typeof projectSchema>
export type ProjectUpdateFormData = z.infer<typeof projectUpdateSchema>
