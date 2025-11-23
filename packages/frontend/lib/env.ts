/**
 * 環境変数のバリデーション
 *
 * セキュリティ: 環境変数の型安全性と妥当性を保証
 */

import { z } from 'zod'

/**
 * 環境変数スキーマ
 */
const envSchema = z.object({
  /**
   * バックエンドAPIのベースURL
   * 本番環境ではHTTPSを強制
   */
  NEXT_PUBLIC_API_URL: z
    .string()
    .url('有効なURLを指定してください')
    .refine(
      (url) => {
        // 開発環境ではlocalhost HTTPを許可
        if (process.env.NODE_ENV === 'development') {
          return true
        }
        // 本番環境ではHTTPSを強制
        return url.startsWith('https://')
      },
      {
        message: '本番環境ではHTTPSのURLを指定してください',
      }
    )
    .optional(),
})

/**
 * 環境変数の型
 */
export type Env = z.infer<typeof envSchema>

/**
 * 環境変数のパース
 */
function parseEnv(): Env {
  try {
    return envSchema.parse({
      NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    })
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors = error.errors
        .map((e) => `${e.path.join('.')}: ${e.message}`)
        .join('\n')

      console.error('環境変数のバリデーションエラー:\n', errors)

      // 開発環境では警告のみ、本番環境ではエラーをスロー
      if (process.env.NODE_ENV === 'production') {
        throw new Error(`環境変数の設定に問題があります:\n${errors}`)
      }
    }

    // バリデーションエラーでもデフォルト値で続行
    return {
      NEXT_PUBLIC_API_URL: undefined,
    }
  }
}

/**
 * 検証済みの環境変数
 */
export const env = parseEnv()
