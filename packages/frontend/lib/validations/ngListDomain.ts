import { z } from 'zod'

/**
 * ドメイン名のバリデーションと正規化
 */
const domainValidator = z
  .string({ message: 'ドメインを入力してください' })
  .trim()
  .min(1, 'ドメインを入力してください')
  .max(255, 'ドメインは255文字以内で入力してください')
  .transform((val) => {
    // 制御文字と空白を除去
    const cleaned = val.replace(/[^\x20-\x7E]/g, '').replace(/\s/g, '')
    return cleaned.toLowerCase()
  })
  .refine(
    (val) => {
      if (!val) return false

      // ワイルドカードのチェック
      let domainToValidate = val
      if (val.includes('*')) {
        // ワイルドカードは先頭の *.domain.com 形式のみ許可
        if (!val.startsWith('*.')) return false
        // *.以降にワイルドカードがないかチェック
        if (val.slice(2).includes('*')) return false
        // *.のみは不可
        if (val.length <= 2) return false

        // ワイルドカード部分を除いたドメインを検証対象にする
        domainToValidate = val.slice(2)
      }

      // RFC 1035準拠のドメイン名検証
      // 各ラベル（ドット区切りの部分）が以下を満たすこと:
      // - 英数字で開始
      // - 英数字で終了
      // - 途中にハイフンを含んでもよい
      // - 63文字以内
      const domainPattern = /^([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)*[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$/
      if (!domainPattern.test(domainToValidate)) return false

      // 連続するドットの禁止
      if (domainToValidate.includes('..')) return false

      // 先頭または末尾のドット/ハイフンの禁止（パターンでチェック済みだが念のため）
      if (domainToValidate.startsWith('.') || domainToValidate.endsWith('.')) return false
      if (domainToValidate.startsWith('-') || domainToValidate.endsWith('-')) return false

      return true
    },
    {
      message: 'ドメイン形式が正しくありません。例: example.com, *.example.com',
    }
  )
  .transform((val) => {
    // www.プレフィックスを除去（正規化）
    // ただし、*.www.example.comのようなパターンは保持
    if (val.startsWith('www.') && !val.startsWith('*.')) {
      return val.slice(4)
    }
    return val
  })
  .refine(
    (val) => {
      // 最終チェック: 空でないことを確認
      return val && val !== '*.'
    },
    {
      message: '有効なドメインを入力してください',
    }
  )

/**
 * メモのバリデーション
 */
const memoValidator = z
  .string()
  .max(500, 'メモは500文字以内で入力してください')
  .transform((val) => {
    if (!val) return ''
    // 制御文字除去（改行・タブは許可）
    const cleaned = val.replace(/[^\x20-\x7E\n\t]/g, '')
    return cleaned.trim()
  })
  .optional()

/**
 * NGリストドメイン単体のスキーマ
 */
export const ngListDomainItemSchema = z.object({
  domain: domainValidator,
  memo: memoValidator,
})

/**
 * NGリストドメインフォームのバリデーションスキーマ
 */
export const ngListDomainFormSchema = z.object({
  domains: z
    .array(ngListDomainItemSchema)
    .min(1, '少なくとも1つのドメインを入力してください')
    .refine(
      (domains) => {
        // 重複チェック
        const domainSet = new Set(domains.map((d) => d.domain))
        return domainSet.size === domains.length
      },
      {
        message: '重複したドメインが含まれています',
      }
    ),
})

/**
 * NGリストドメイン作成リクエストのバリデーションスキーマ
 */
export const ngListDomainCreateSchema = z.object({
  listId: z.number().int().positive('リストIDが不正です'),
  domain: domainValidator,
  memo: memoValidator,
})

/**
 * NGリストドメインチェックリクエストのバリデーションスキーマ
 */
export const ngListDomainCheckSchema = z.object({
  listId: z.number().int().positive('リストIDが不正です'),
  url: z
    .string({ message: 'URLを入力してください' })
    .trim()
    .min(1, 'URLを入力してください')
    .max(2000, 'URLは2000文字以内で入力してください')
    .refine(
      (val) => {
        try {
          // スキームがない場合は追加
          const urlString = val.startsWith('http://') || val.startsWith('https://')
            ? val
            : `https://${val}`

          const url = new URL(urlString)

          // HTTP/HTTPSのみ許可
          if (!['http:', 'https:'].includes(url.protocol)) {
            return false
          }

          // 基本的な形式チェック
          if (!url.hostname || !url.hostname.includes('.')) {
            return false
          }

          // SSRF対策: ローカルホストへのアクセスを禁止
          const hostname = url.hostname.toLowerCase()
          if (['localhost', '127.0.0.1', '0.0.0.0', '::1'].includes(hostname)) {
            return false
          }

          // SSRF対策: プライベートIPアドレスへのアクセスを禁止
          if (
            hostname.startsWith('10.') ||
            hostname.startsWith('172.') ||
            hostname.startsWith('192.168.') ||
            hostname.startsWith('169.254.')
          ) {
            return false
          }

          return true
        } catch {
          return false
        }
      },
      {
        message: '有効なURLを入力してください（例: https://example.com）',
      }
    ),
})

// 型推論
export type NgListDomainItemData = z.infer<typeof ngListDomainItemSchema>
export type NgListDomainFormData = z.infer<typeof ngListDomainFormSchema>
export type NgListDomainCreateData = z.infer<typeof ngListDomainCreateSchema>
export type NgListDomainCheckData = z.infer<typeof ngListDomainCheckSchema>
