import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ScriptDisplay } from '@/components/features/worker/ScriptDisplay'

// クリップボードAPIのモック
Object.assign(navigator, {
  clipboard: {
    writeText: jest.fn(),
  },
})

describe('ScriptDisplay', () => {
  const mockScript = {
    title: 'お問い合わせの件',
    content: `お世話になっております。
株式会社テストの山田と申します。

弊社のサービスについてご紹介させていただきたく、
ご連絡いたしました。

よろしくお願いいたします。`,
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('基本表示', () => {
    it('スクリプトカードのタイトルが表示される', () => {
      render(<ScriptDisplay {...mockScript} />)

      expect(screen.getByText('スクリプト')).toBeInTheDocument()
      expect(screen.getByText('営業文章・スクリプト本文')).toBeInTheDocument()
    })

    it('件名が表示される', () => {
      render(<ScriptDisplay {...mockScript} />)

      expect(screen.getByText('件名')).toBeInTheDocument()
      expect(screen.getByText('お問い合わせの件')).toBeInTheDocument()
    })

    it('本文が表示される', () => {
      render(<ScriptDisplay {...mockScript} />)

      expect(screen.getByText('本文')).toBeInTheDocument()
      expect(screen.getByText(/お世話になっております/)).toBeInTheDocument()
      expect(screen.getByText(/株式会社テストの山田と申します/)).toBeInTheDocument()
    })

    it('コピーボタンが表示される', () => {
      render(<ScriptDisplay {...mockScript} />)

      const copyButton = screen.getByRole('button', { name: /コピー/ })
      expect(copyButton).toBeInTheDocument()
    })
  })

  describe('クリップボードコピー機能', () => {
    it('コピーボタンをクリックするとクリップボードにコピーされる', async () => {
      const user = userEvent.setup()
      const mockWriteText = jest.fn().mockResolvedValue(undefined)
      Object.assign(navigator.clipboard, { writeText: mockWriteText })

      render(<ScriptDisplay {...mockScript} />)

      const copyButton = screen.getByRole('button', { name: /コピー/ })
      await user.click(copyButton)

      expect(mockWriteText).toHaveBeenCalledWith(mockScript.content)
    })

    it('コピー後にボタンのテキストが「コピー済み」に変わる', async () => {
      const user = userEvent.setup()
      const mockWriteText = jest.fn().mockResolvedValue(undefined)
      Object.assign(navigator.clipboard, { writeText: mockWriteText })

      render(<ScriptDisplay {...mockScript} />)

      const copyButton = screen.getByRole('button', { name: /コピー/ })
      await user.click(copyButton)

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /コピー済み/ })).toBeInTheDocument()
      })
    })

    it('コピー後2秒でボタンのテキストが「コピー」に戻る', async () => {
      jest.useFakeTimers()
      const user = userEvent.setup({ delay: null })
      const mockWriteText = jest.fn().mockResolvedValue(undefined)
      Object.assign(navigator.clipboard, { writeText: mockWriteText })

      render(<ScriptDisplay {...mockScript} />)

      const copyButton = screen.getByRole('button', { name: /コピー/ })
      await user.click(copyButton)

      // コピー直後は「コピー済み」
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /コピー済み/ })).toBeInTheDocument()
      })

      // 2秒経過
      jest.advanceTimersByTime(2000)

      // 「コピー」に戻る
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /^コピー$/ })).toBeInTheDocument()
      })

      jest.useRealTimers()
    })

    it('クリップボードAPIが失敗してもエラーがスローされない', async () => {
      const user = userEvent.setup()
      const consoleError = jest.spyOn(console, 'error').mockImplementation()
      const mockWriteText = jest
        .fn()
        .mockRejectedValue(new Error('Clipboard API error'))
      Object.assign(navigator.clipboard, { writeText: mockWriteText })

      render(<ScriptDisplay {...mockScript} />)

      const copyButton = screen.getByRole('button', { name: /コピー/ })

      // エラーがスローされないことを確認
      await expect(user.click(copyButton)).resolves.not.toThrow()

      // エラーがコンソールに出力されることを確認
      await waitFor(() => {
        expect(consoleError).toHaveBeenCalledWith(
          'クリップボードへのコピーに失敗しました:',
          expect.any(Error)
        )
      })

      consoleError.mockRestore()
    })
  })

  describe('テキストのフォーマット', () => {
    it('本文の改行が保持される', () => {
      render(<ScriptDisplay {...mockScript} />)

      const contentElement = screen.getByText(/お世話になっております/)

      // pre要素に whitespace-pre-wrap が適用されている
      expect(contentElement.tagName).toBe('PRE')
      expect(contentElement).toHaveClass('whitespace-pre-wrap')
    })
  })

  describe('様々なスクリプト内容', () => {
    it('長いスクリプトも正しく表示される', () => {
      const longScript = {
        title: '長い件名'.repeat(20),
        content: '長い本文\n'.repeat(50),
      }

      render(<ScriptDisplay {...longScript} />)

      expect(screen.getByText(longScript.title)).toBeInTheDocument()
      expect(screen.getByText(/長い本文/)).toBeInTheDocument()
    })

    it('特殊文字を含むスクリプトも正しく表示される', () => {
      const specialScript = {
        title: '【重要】お問い合わせ <テスト>',
        content: 'Hello & goodbye\n"Quote" \'Single\' \n<tag>',
      }

      render(<ScriptDisplay {...specialScript} />)

      expect(
        screen.getByText('【重要】お問い合わせ <テスト>')
      ).toBeInTheDocument()
      expect(screen.getByText(/Hello & goodbye/)).toBeInTheDocument()
    })
  })
})
