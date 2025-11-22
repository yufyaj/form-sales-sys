import {
  validatePositiveInteger,
  validateString,
  validateDate,
  sanitizeUserInput,
} from '@/lib/validation'

describe('validation utilities', () => {
  describe('validatePositiveInteger', () => {
    it('有効な正の整数を返す', () => {
      expect(validatePositiveInteger('123')).toBe(123)
      expect(validatePositiveInteger('1')).toBe(1)
      expect(validatePositiveInteger('999999')).toBe(999999)
    })

    it('0以下の値はnullを返す', () => {
      expect(validatePositiveInteger('0')).toBeNull()
      expect(validatePositiveInteger('-1')).toBeNull()
      expect(validatePositiveInteger('-999')).toBeNull()
    })

    it('NaNはnullを返す', () => {
      expect(validatePositiveInteger('abc')).toBeNull()
      expect(validatePositiveInteger('12.34')).toBe(12) // parseIntは小数点以下を切り捨て
      expect(validatePositiveInteger('')).toBeNull()
    })

    it('最大安全整数を超える値はnullを返す', () => {
      const maxSafe = Number.MAX_SAFE_INTEGER.toString()
      const overMax = (Number.MAX_SAFE_INTEGER + 1).toString()

      expect(validatePositiveInteger(maxSafe)).toBe(Number.MAX_SAFE_INTEGER)
      expect(validatePositiveInteger(overMax)).toBeNull()
    })
  })

  describe('validateString', () => {
    it('有効な文字列を返す', () => {
      expect(validateString('hello')).toBe('hello')
      expect(validateString('テスト')).toBe('テスト')
      expect(validateString('123')).toBe('123')
    })

    it('undefinedの場合、allowEmptyに応じて処理する', () => {
      expect(validateString(undefined, 500, true)).toBe('')
      expect(validateString(undefined, 500, false)).toBeNull()
    })

    it('空文字列の場合、allowEmptyに応じて処理する', () => {
      expect(validateString('', 500, true)).toBe('')
      expect(validateString('', 500, false)).toBeNull()
    })

    it('最大長を超える文字列はnullを返す', () => {
      const longString = 'a'.repeat(501)
      expect(validateString(longString, 500)).toBeNull()
      expect(validateString('a'.repeat(500), 500)).toBe('a'.repeat(500))
    })

    it('null文字を含む文字列はnullを返す', () => {
      expect(validateString('hello\x00world')).toBeNull()
    })
  })

  describe('validateDate', () => {
    it('有効な日付を返す', () => {
      const date = validateDate('2025-01-15T10:30:00Z')
      expect(date).toBeInstanceOf(Date)
      expect(date?.getFullYear()).toBe(2025)
    })

    it('undefinedの場合はnullを返す', () => {
      expect(validateDate(undefined)).toBeNull()
    })

    it('無効な日付文字列はnullを返す', () => {
      expect(validateDate('invalid-date')).toBeNull()
      expect(validateDate('2025-13-40')).toBeNull()
    })

    it('範囲外の日付はnullを返す', () => {
      expect(validateDate('1969-12-31')).toBeNull()
      expect(validateDate('2101-01-01')).toBeNull()
    })

    it('範囲内の境界値は有効', () => {
      const minDate = validateDate('1970-01-01')
      const maxDate = validateDate('2100-12-31')

      expect(minDate).toBeInstanceOf(Date)
      expect(maxDate).toBeInstanceOf(Date)
    })
  })

  describe('sanitizeUserInput', () => {
    it('有効な文字列をそのまま返す', () => {
      expect(sanitizeUserInput('hello world')).toBe('hello world')
      expect(sanitizeUserInput('テストコメント')).toBe('テストコメント')
    })

    it('undefinedの場合は"-"を返す', () => {
      expect(sanitizeUserInput(undefined)).toBe('-')
    })

    it('空文字列の場合は"-"を返す', () => {
      expect(sanitizeUserInput('')).toBe('-')
    })

    it('最大長を超える文字列は切り詰める', () => {
      const longString = 'a'.repeat(600)
      const sanitized = sanitizeUserInput(longString, 500)

      expect(sanitized.length).toBe(500)
      expect(sanitized).toBe('a'.repeat(500))
    })

    it('カスタム最大長が適用される', () => {
      const input = 'hello world'
      const sanitized = sanitizeUserInput(input, 5)

      expect(sanitized).toBe('hello')
    })
  })
})
