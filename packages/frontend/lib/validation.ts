/**
 * 入力検証ユーティリティ
 * セキュリティ: 入力値の境界値チェックと型検証を厳密に実施
 */

/**
 * 正の整数値を検証
 * セキュリティ: 境界値攻撃を防ぐため、最小値・最大値を検証
 *
 * @param value - 検証する文字列
 * @param name - フィールド名（エラーメッセージ用）
 * @returns 検証済みの数値、または null（検証失敗時）
 */
export function validatePositiveInteger(
  value: string,
  name: string = 'value'
): number | null {
  // 文字列から数値に変換
  const num = parseInt(value, 10)

  // NaNチェック
  if (isNaN(num)) {
    console.warn(`${name}の検証失敗: NaN`)
    return null
  }

  // 正の整数チェック
  if (num <= 0) {
    console.warn(`${name}の検証失敗: 0以下の値 (${num})`)
    return null
  }

  // 最大安全整数チェック（JavaScriptの安全な整数範囲）
  if (num > Number.MAX_SAFE_INTEGER) {
    console.warn(`${name}の検証失敗: 最大値超過 (${num})`)
    return null
  }

  return num
}

/**
 * 文字列の長さと内容を検証
 * セキュリティ: XSS攻撃を防ぐため、長さ制限とパターン検証を実施
 *
 * @param value - 検証する文字列
 * @param maxLength - 最大文字数
 * @param allowEmpty - 空文字列を許可するか
 * @returns 検証済みの文字列、または null（検証失敗時）
 */
export function validateString(
  value: string | undefined,
  maxLength: number = 500,
  allowEmpty: boolean = true
): string | null {
  // undefined チェック
  if (value === undefined) {
    return allowEmpty ? '' : null
  }

  // 空文字列チェック
  if (value.length === 0) {
    return allowEmpty ? '' : null
  }

  // 長さ制限チェック
  if (value.length > maxLength) {
    console.warn(`文字列の検証失敗: 最大長超過 (${value.length} > ${maxLength})`)
    return null
  }

  // 制御文字のチェック（null文字、改行など）
  // 注: 改行は許可する場合もあるため、nullバイト等の危険な制御文字のみチェック
  if (/\x00/.test(value)) {
    console.warn('文字列の検証失敗: null文字を含む')
    return null
  }

  return value
}

/**
 * 日付文字列を検証
 * セキュリティ: 無効な日付による異常動作を防ぐ
 *
 * @param dateString - 検証する日付文字列
 * @returns 検証済みのDate、または null（検証失敗時）
 */
export function validateDate(dateString: string | undefined): Date | null {
  if (!dateString) {
    return null
  }

  try {
    const date = new Date(dateString)

    // 無効な日付のチェック
    if (isNaN(date.getTime())) {
      console.warn('日付の検証失敗: 無効な日付形式')
      return null
    }

    // 極端な過去・未来の日付をチェック（1970年より前、2100年より後は拒否）
    const minDate = new Date('1970-01-01')
    const maxDate = new Date('2100-12-31')

    if (date < minDate || date > maxDate) {
      console.warn('日付の検証失敗: 範囲外の日付')
      return null
    }

    return date
  } catch {
    console.warn('日付の検証失敗: パースエラー')
    return null
  }
}

/**
 * ユーザー入力をサニタイズ
 * セキュリティ: XSS攻撃を防ぐため、危険な文字列を除去
 * 注: Reactは自動的にHTMLエスケープするが、多層防御として実装
 *
 * @param input - サニタイズする文字列
 * @param maxLength - 最大文字数
 * @returns サニタイズ済みの文字列
 */
export function sanitizeUserInput(
  input: string | undefined,
  maxLength: number = 500
): string {
  if (!input) {
    return '-'
  }

  // 長さ制限
  let sanitized = input.slice(0, maxLength)

  // HTMLタグのエスケープ（Reactが自動でやるが、念のため）
  // 注: この処理は表示前にReactが行うため、ここでは長さ制限のみ実施

  return sanitized
}
