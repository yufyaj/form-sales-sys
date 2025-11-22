/**
 * CSVインポート関連のバリデーションスキーマ
 *
 * Zodを使用してCSVデータのバリデーションを実施
 */

import { z } from 'zod'

/**
 * CSVファイルのバリデーションスキーマ
 */
export const csvFileSchema = z.object({
  name: z.string().refine((name) => name.endsWith('.csv'), {
    message: 'CSVファイルのみアップロード可能です',
  }),
  size: z.number().max(10 * 1024 * 1024, {
    message: 'ファイルサイズは10MB以下である必要があります',
  }),
  type: z.string().refine((type) => type === 'text/csv' || type === 'application/vnd.ms-excel', {
    message: 'CSVファイル形式である必要があります',
  }),
})

/**
 * CSVインポート用顧客組織データのバリデーションスキーマ
 */
export const csvClientOrganizationSchema = z.object({
  organizationName: z
    .string()
    .trim()
    .min(1, '組織名は必須です')
    .max(255, '組織名は255文字以内で入力してください'),
  industry: z
    .string()
    .max(255, '業種は255文字以内で入力してください')
    .optional()
    .or(z.literal(''))
    .nullable(),
  employeeCount: z
    .union([z.string(), z.number()])
    .transform((val) => {
      if (val === '' || val === null || val === undefined) return null
      const num = typeof val === 'string' ? parseInt(val, 10) : val
      return isNaN(num) ? null : num
    })
    .pipe(
      z
        .number()
        .int('従業員数は整数である必要があります')
        .nonnegative('従業員数は0以上である必要があります')
        .nullable()
    )
    .optional(),
  annualRevenue: z
    .union([z.string(), z.number()])
    .transform((val) => {
      if (val === '' || val === null || val === undefined) return null
      const num = typeof val === 'string' ? parseInt(val, 10) : val
      return isNaN(num) ? null : num
    })
    .pipe(
      z
        .number()
        .int('年商は整数である必要があります')
        .nonnegative('年商は0以上である必要があります')
        .nullable()
    )
    .optional(),
  establishedYear: z
    .union([z.string(), z.number()])
    .transform((val) => {
      if (val === '' || val === null || val === undefined) return null
      const num = typeof val === 'string' ? parseInt(val, 10) : val
      return isNaN(num) ? null : num
    })
    .pipe(
      z
        .number()
        .int('設立年は整数である必要があります')
        .min(1800, '設立年は1800年以降である必要があります')
        .max(new Date().getFullYear(), '設立年は未来の年を指定できません')
        .nullable()
    )
    .optional(),
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
    .or(z.literal(''))
    .nullable(),
  notes: z
    .string()
    .max(5000, '備考は5000文字以内で入力してください')
    .optional()
    .or(z.literal(''))
    .nullable(),
})

/**
 * CSVインポート用顧客担当者データのバリデーションスキーマ
 */
export const csvClientContactSchema = z.object({
  organizationName: z
    .string()
    .trim()
    .min(1, '組織名は必須です')
    .max(255, '組織名は255文字以内で入力してください'),
  fullName: z
    .string()
    .trim()
    .min(1, '氏名は必須です')
    .max(255, '氏名は255文字以内で入力してください'),
  department: z
    .string()
    .max(255, '部署名は255文字以内で入力してください')
    .optional()
    .or(z.literal(''))
    .nullable(),
  position: z
    .string()
    .max(255, '役職名は255文字以内で入力してください')
    .optional()
    .or(z.literal(''))
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
  isPrimary: z
    .union([z.string(), z.boolean()])
    .transform((val) => {
      if (typeof val === 'boolean') return val
      if (typeof val === 'string') {
        const lower = val.toLowerCase()
        if (lower === 'true' || lower === '1' || lower === 'yes') return true
        if (lower === 'false' || lower === '0' || lower === 'no') return false
      }
      return false
    })
    .optional(),
  notes: z
    .string()
    .max(5000, '備考は5000文字以内で入力してください')
    .optional()
    .or(z.literal(''))
    .nullable(),
})

/**
 * フォームデータ型の推論
 */
export type CSVFileData = z.infer<typeof csvFileSchema>
export type CSVClientOrganizationData = z.infer<typeof csvClientOrganizationSchema>
export type CSVClientContactData = z.infer<typeof csvClientContactSchema>

/**
 * CSVエクスポート用: 危険な文字列をサニタイズする
 * CSVインジェクション対策（Excel/Google Sheets等でCSVを開く際の数式実行防止）
 *
 * 注意: この関数はCSVエクスポート時に使用してください。
 * インポート時には使用しないでください（データに不要なシングルクォートが含まれます）
 *
 * @param value - サニタイズする値
 * @returns サニタイズされた値
 */
export function sanitizeCSVCellForExport(value: string): string {
  if (typeof value !== 'string') return String(value)

  const dangerousChars = ['=', '+', '-', '@', '\t', '\r']
  const trimmed = value.trim()

  if (dangerousChars.some((char) => trimmed.startsWith(char))) {
    return `'${value}` // 先頭にシングルクォート追加
  }

  return value
}

/**
 * CSVファイル内容の検証
 * スクリプトタグなど危険なパターンをチェック
 */
export function validateCSVContent(content: string): {
  valid: boolean
  errors: string[]
} {
  const errors: string[] = []

  const dangerousPatterns = [
    { pattern: /<script/i, message: 'スクリプトタグが含まれています' },
    { pattern: /javascript:/i, message: 'JavaScriptプロトコルが含まれています' },
    { pattern: /on\w+\s*=/i, message: 'イベントハンドラが含まれています' },
    { pattern: /<iframe/i, message: 'iframeタグが含まれています' },
    { pattern: /<object/i, message: 'objectタグが含まれています' },
    { pattern: /<embed/i, message: 'embedタグが含まれています' },
  ]

  for (const { pattern, message } of dangerousPatterns) {
    if (pattern.test(content)) {
      errors.push(message)
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  }
}
