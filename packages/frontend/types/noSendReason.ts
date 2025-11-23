/**
 * 送信不可理由の型定義
 */

/**
 * 送信不可理由
 */
export interface NoSendReason {
  id: string
  label: string
  isDefault: boolean
}

/**
 * デフォルトの送信不可理由リスト
 */
export const DEFAULT_NO_SEND_REASONS: NoSendReason[] = [
  { id: 'invalid-email', label: 'メールアドレスが無効', isDefault: true },
  { id: 'bounced', label: 'バウンス履歴あり', isDefault: true },
  { id: 'unsubscribed', label: '配信停止済み', isDefault: true },
  { id: 'duplicate', label: '重複データ', isDefault: true },
  { id: 'spam-complaint', label: 'スパム報告履歴', isDefault: true },
]
