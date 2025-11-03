import { sanitizeUserName } from '@/types/auth'

describe('sanitizeUserName', () => {
  describe('正常なケース', () => {
    it('通常の文字列はそのまま返す', () => {
      expect(sanitizeUserName('John Doe')).toBe('John Doe')
      expect(sanitizeUserName('山田太郎')).toBe('山田太郎')
      expect(sanitizeUserName('Alice123')).toBe('Alice123')
    })

    it('空白を含む文字列を正しく処理する', () => {
      expect(sanitizeUserName('First Last')).toBe('First Last')
      expect(sanitizeUserName('  Spaces  ')).toBe('  Spaces  ')
    })

    it('特殊文字を含む文字列を正しく処理する', () => {
      expect(sanitizeUserName('Alice_Bob')).toBe('Alice_Bob')
      expect(sanitizeUserName('user@domain')).toBe('user@domain')
      expect(sanitizeUserName('O\'Connor')).toBe('O\'Connor')
    })
  })

  describe('エッジケース', () => {
    it('undefinedの場合はundefinedを返す', () => {
      expect(sanitizeUserName(undefined)).toBeUndefined()
    })

    it('空文字列の場合はundefinedを返す', () => {
      expect(sanitizeUserName('')).toBeUndefined()
    })

    it('制御文字のみの文字列の場合はundefinedを返す', () => {
      expect(sanitizeUserName('\x00\x01\x02')).toBeUndefined()
    })
  })

  describe('制御文字の除去', () => {
    it('NULL文字を除去する', () => {
      expect(sanitizeUserName('Hello\x00World')).toBe('HelloWorld')
    })

    it('制御文字(0x00-0x1F)を除去する', () => {
      expect(sanitizeUserName('Test\x01\x02\x03String')).toBe('TestString')
      expect(sanitizeUserName('Line\x0ABreak')).toBe('LineBreak')
      expect(sanitizeUserName('Tab\x09Test')).toBe('TabTest')
    })

    it('DEL文字(0x7F)を除去する', () => {
      expect(sanitizeUserName('Hello\x7FWorld')).toBe('HelloWorld')
    })

    it('C1制御文字(0x80-0x9F)を除去する', () => {
      expect(sanitizeUserName('Test\x80\x90\x9FString')).toBe('TestString')
    })

    it('複数の制御文字を除去する', () => {
      expect(sanitizeUserName('A\x00B\x01C\x02D')).toBe('ABCD')
    })
  })

  describe('長さの制限', () => {
    it('50文字以下の文字列はそのまま返す', () => {
      const input = 'a'.repeat(50)
      expect(sanitizeUserName(input)).toBe(input)
    })

    it('51文字以上の文字列は50文字に切り詰める', () => {
      const input = 'a'.repeat(100)
      const expected = 'a'.repeat(50)
      expect(sanitizeUserName(input)).toBe(expected)
    })

    it('切り詰め後に制御文字を除去する', () => {
      const input = 'a'.repeat(49) + '\x00' + 'b'.repeat(50)
      const expected = 'a'.repeat(49)
      expect(sanitizeUserName(input)).toBe(expected)
    })
  })

  describe('XSS対策', () => {
    it('スクリプトタグを含む文字列を安全に処理する', () => {
      // NOTE: この関数は制御文字のみを除去するため、
      // HTMLタグはそのまま残ります。実際の使用時は
      // Reactが自動的にエスケープします。
      const input = '<script>alert("xss")</script>'
      expect(sanitizeUserName(input)).toBe(input)
    })

    it('改行文字を除去する', () => {
      const input = 'Line1\nLine2\rLine3'
      expect(sanitizeUserName(input)).toBe('Line1Line2Line3')
    })

    it('タブ文字を除去する', () => {
      const input = 'Column1\tColumn2\tColumn3'
      expect(sanitizeUserName(input)).toBe('Column1Column2Column3')
    })
  })

  describe('実際の使用例', () => {
    it('正常なユーザー名は変更されない', () => {
      expect(sanitizeUserName('田中太郎')).toBe('田中太郎')
      expect(sanitizeUserName('John Smith')).toBe('John Smith')
      expect(sanitizeUserName('user_123')).toBe('user_123')
    })

    it('不正な制御文字を含むユーザー名は浄化される', () => {
      expect(sanitizeUserName('Evil\x00User')).toBe('EvilUser')
      expect(sanitizeUserName('Bad\x01Name')).toBe('BadName')
    })

    it('長すぎるユーザー名は切り詰められる', () => {
      const longName =
        'これは非常に長いユーザー名です。実際にはこのような長い名前は想定されていませんが、セキュリティのため制限をかけています。'
      const result = sanitizeUserName(longName)
      expect(result?.length).toBeLessThanOrEqual(50)
    })
  })
})
