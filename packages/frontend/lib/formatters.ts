/**
 * データフォーマット用ユーティリティ関数
 *
 * セキュリティとプライバシーを考慮した表示形式の提供
 */

/**
 * ワーカーIDをマスキング表示
 *
 * セキュリティ: 内部識別子を直接露出せず、最後の3桁のみ表示
 * 例: 12345 → "W***345"
 *
 * @param workerId - ワーカーID
 * @returns マスキングされた表示文字列
 */
export function maskWorkerId(workerId: number): string {
  const idStr = String(workerId);
  const lastThreeDigits = idStr.slice(-3).padStart(3, '0');
  return `W***${lastThreeDigits}`;
}

/**
 * ワーカーの表示名を取得
 *
 * ワーカー名が存在する場合は名前を表示し、なければマスキングされたIDを表示
 *
 * @param workerId - ワーカーID
 * @param workerName - ワーカー名（オプション）
 * @returns 表示用の文字列
 */
export function getWorkerDisplayName(
  workerId: number,
  workerName?: string | null
): string {
  if (workerName) {
    return workerName;
  }
  return maskWorkerId(workerId);
}

/**
 * 日時を日本語フォーマットで表示
 *
 * @param dateString - ISO形式の日時文字列
 * @returns フォーマットされた日時文字列
 */
export function formatDateTime(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * 日付のみを日本語フォーマットで表示
 *
 * @param dateString - ISO形式の日時文字列
 * @returns フォーマットされた日付文字列
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
}
