/**
 * 顧客管理フォームのバリデーションスキーマ
 *
 * Zodを使用してフロントエンド側のバリデーションを実施
 */

import { z } from 'zod'

/**
 * 顧客組織作成フォームのバリデーションスキーマ
 */
export const createClientOrganizationSchema = z.object({
  organizationId: z
    .number({ message: '組織IDは数値である必要があります' })
    .int('組織IDは整数である必要があります')
    .positive('組織IDは正の数である必要があります'),
  industry: z
    .string()
    .max(255, '業種は255文字以内で入力してください')
    .optional()
    .nullable(),
  employeeCount: z
    .number()
    .int('従業員数は整数である必要があります')
    .nonnegative('従業員数は0以上である必要があります')
    .optional()
    .nullable(),
  annualRevenue: z
    .number()
    .int('年商は整数である必要があります')
    .nonnegative('年商は0以上である必要があります')
    .optional()
    .nullable(),
  establishedYear: z
    .number()
    .int('設立年は整数である必要があります')
    .min(1800, '設立年は1800年以降である必要があります')
    .max(new Date().getFullYear(), '設立年は未来の年を指定できません')
    .optional()
    .nullable(),
  website: z
    .string()
    .max(500, 'WebサイトURLは500文字以内で入力してください')
    .url('有効なURLを入力してください')
    .optional()
    .or(z.literal(''))
    .nullable(),
  salesPerson: z
    .string()
    .max(255, '担当営業名は255文字以内で入力してください')
    .optional()
    .nullable(),
  notes: z
    .string()
    .max(5000, '備考は5000文字以内で入力してください')
    .optional()
    .nullable(),
})

/**
 * 顧客組織更新フォームのバリデーションスキーマ
 */
export const updateClientOrganizationSchema = z.object({
  industry: z
    .string()
    .max(255, '業種は255文字以内で入力してください')
    .optional()
    .nullable(),
  employeeCount: z
    .number()
    .int('従業員数は整数である必要があります')
    .nonnegative('従業員数は0以上である必要があります')
    .optional()
    .nullable(),
  annualRevenue: z
    .number()
    .int('年商は整数である必要があります')
    .nonnegative('年商は0以上である必要があります')
    .optional()
    .nullable(),
  establishedYear: z
    .number()
    .int('設立年は整数である必要があります')
    .min(1800, '設立年は1800年以降である必要があります')
    .max(new Date().getFullYear(), '設立年は未来の年を指定できません')
    .optional()
    .nullable(),
  website: z
    .string()
    .max(500, 'WebサイトURLは500文字以内で入力してください')
    .url('有効なURLを入力してください')
    .optional()
    .or(z.literal(''))
    .nullable(),
  salesPerson: z
    .string()
    .max(255, '担当営業名は255文字以内で入力してください')
    .optional()
    .nullable(),
  notes: z
    .string()
    .max(5000, '備考は5000文字以内で入力してください')
    .optional()
    .nullable(),
})

/**
 * 顧客担当者作成フォームのバリデーションスキーマ
 */
export const createClientContactSchema = z.object({
  clientOrganizationId: z
    .number()
    .int('顧客組織IDは整数である必要があります')
    .positive('顧客組織IDは正の数である必要があります'),
  fullName: z
    .string()
    .trim()
    .min(1, '氏名を入力してください')
    .max(255, '氏名は255文字以内で入力してください'),
  department: z
    .string()
    .max(255, '部署名は255文字以内で入力してください')
    .optional()
    .nullable(),
  position: z
    .string()
    .max(255, '役職名は255文字以内で入力してください')
    .optional()
    .nullable(),
  email: z
    .string()
    .email('有効なメールアドレスを入力してください')
    .max(255, 'メールアドレスは255文字以内で入力してください')
    .optional()
    .or(z.literal(''))
    .nullable(),
  phone: z
    .string()
    .max(50, '電話番号は50文字以内で入力してください')
    .regex(
      /^$|^[\d\-+() ]+$/,
      '電話番号は数字、ハイフン、括弧、プラス記号のみ使用できます'
    )
    .refine(
      (val) => !val || val.replace(/[\s\-+()]/g, '').length > 0,
      '有効な電話番号を入力してください'
    )
    .optional()
    .or(z.literal(''))
    .nullable(),
  mobile: z
    .string()
    .max(50, '携帯電話番号は50文字以内で入力してください')
    .regex(
      /^$|^[\d\-+() ]+$/,
      '携帯電話番号は数字、ハイフン、括弧、プラス記号のみ使用できます'
    )
    .refine(
      (val) => !val || val.replace(/[\s\-+()]/g, '').length > 0,
      '有効な携帯電話番号を入力してください'
    )
    .optional()
    .or(z.literal(''))
    .nullable(),
  isPrimary: z.boolean().optional(),
  notes: z
    .string()
    .max(5000, '備考は5000文字以内で入力してください')
    .optional()
    .nullable(),
})

/**
 * 顧客担当者更新フォームのバリデーションスキーマ
 */
export const updateClientContactSchema = z.object({
  fullName: z
    .string()
    .trim()
    .min(1, '氏名を入力してください')
    .max(255, '氏名は255文字以内で入力してください')
    .optional(),
  department: z
    .string()
    .max(255, '部署名は255文字以内で入力してください')
    .optional()
    .nullable(),
  position: z
    .string()
    .max(255, '役職名は255文字以内で入力してください')
    .optional()
    .nullable(),
  email: z
    .string()
    .email('有効なメールアドレスを入力してください')
    .max(255, 'メールアドレスは255文字以内で入力してください')
    .optional()
    .or(z.literal(''))
    .nullable(),
  phone: z
    .string()
    .max(50, '電話番号は50文字以内で入力してください')
    .regex(
      /^$|^[\d\-+() ]+$/,
      '電話番号は数字、ハイフン、括弧、プラス記号のみ使用できます'
    )
    .refine(
      (val) => !val || val.replace(/[\s\-+()]/g, '').length > 0,
      '有効な電話番号を入力してください'
    )
    .optional()
    .or(z.literal(''))
    .nullable(),
  mobile: z
    .string()
    .max(50, '携帯電話番号は50文字以内で入力してください')
    .regex(
      /^$|^[\d\-+() ]+$/,
      '携帯電話番号は数字、ハイフン、括弧、プラス記号のみ使用できます'
    )
    .refine(
      (val) => !val || val.replace(/[\s\-+()]/g, '').length > 0,
      '有効な携帯電話番号を入力してください'
    )
    .optional()
    .or(z.literal(''))
    .nullable(),
  isPrimary: z.boolean().optional(),
  notes: z
    .string()
    .max(5000, '備考は5000文字以内で入力してください')
    .optional()
    .nullable(),
})

/**
 * フォームデータ型の推論
 */
export type CreateClientOrganizationFormData = z.infer<
  typeof createClientOrganizationSchema
>
export type UpdateClientOrganizationFormData = z.infer<
  typeof updateClientOrganizationSchema
>
export type CreateClientContactFormData = z.infer<
  typeof createClientContactSchema
>
export type UpdateClientContactFormData = z.infer<
  typeof updateClientContactSchema
>
