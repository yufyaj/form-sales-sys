import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { WorkRecordForm } from '@/components/features/worker/WorkRecordForm'
import type { WorkRecordFormData } from '@/lib/validations/workRecord'

describe('WorkRecordForm', () => {
  const mockProps = {
    assignmentId: '123',
    workerId: 1,
    onSubmit: jest.fn(),
    isSubmitting: false,
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('基本表示', () => {
    it('フォームのタイトルが表示される', () => {
      render(<WorkRecordForm {...mockProps} />)

      expect(screen.getByText('作業記録')).toBeInTheDocument()
      expect(screen.getByText('作業結果を記録してください')).toBeInTheDocument()
    })

    it('作業ステータスの選択肢が表示される', () => {
      render(<WorkRecordForm {...mockProps} />)

      expect(screen.getByLabelText('作業ステータス')).toBeInTheDocument()
      const select = screen.getByLabelText('作業ステータス') as HTMLSelectElement

      const options = Array.from(select.options).map((opt) => opt.text)
      expect(options).toContain('送信完了')
      expect(options).toContain('送信不可')
    })

    it('備考の入力欄が表示される', () => {
      render(<WorkRecordForm {...mockProps} />)

      expect(screen.getByLabelText('備考')).toBeInTheDocument()
      expect(
        screen.getByPlaceholderText('補足情報があれば入力してください')
      ).toBeInTheDocument()
    })

    it('送信ボタンが表示される', () => {
      render(<WorkRecordForm {...mockProps} />)

      expect(
        screen.getByRole('button', { name: '記録を保存' })
      ).toBeInTheDocument()
    })
  })

  describe('条件付き表示', () => {
    it('初期状態では送信不可理由は表示されない', () => {
      render(<WorkRecordForm {...mockProps} />)

      expect(screen.queryByLabelText('送信不可理由')).not.toBeInTheDocument()
    })

    it('作業ステータスを「送信不可」にすると送信不可理由が表示される', async () => {
      const user = userEvent.setup()
      render(<WorkRecordForm {...mockProps} />)

      const statusSelect = screen.getByLabelText('作業ステータス')
      await user.selectOptions(statusSelect, 'cannot_send')

      await waitFor(() => {
        expect(screen.getByLabelText('送信不可理由')).toBeInTheDocument()
      })

      const reasonSelect = screen.getByLabelText('送信不可理由') as HTMLSelectElement
      const options = Array.from(reasonSelect.options).map((opt) => opt.text)

      expect(options).toContain('問い合わせフォームが見つからない')
      expect(options).toContain('フォームが機能していない')
      expect(options).toContain('営業お断りと明記されている')
      expect(options).toContain('その他')
    })

    it('作業ステータスを「送信完了」に戻すと送信不可理由が非表示になる', async () => {
      const user = userEvent.setup()
      render(<WorkRecordForm {...mockProps} />)

      const statusSelect = screen.getByLabelText('作業ステータス')

      // 送信不可に変更
      await user.selectOptions(statusSelect, 'cannot_send')
      await waitFor(() => {
        expect(screen.getByLabelText('送信不可理由')).toBeInTheDocument()
      })

      // 送信完了に戻す
      await user.selectOptions(statusSelect, 'sent')
      await waitFor(() => {
        expect(screen.queryByLabelText('送信不可理由')).not.toBeInTheDocument()
      })
    })
  })

  describe('フォーム送信', () => {
    it('送信完了でフォームを送信できる', async () => {
      const user = userEvent.setup()
      const onSubmit = jest.fn()

      render(<WorkRecordForm {...mockProps} onSubmit={onSubmit} />)

      // デフォルトで 'sent' が選択されているため、selectOptionsは不要
      const notesTextarea = screen.getByLabelText('備考')
      await user.type(notesTextarea, 'テスト備考')

      const submitButton = screen.getByRole('button', { name: '記録を保存' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalled()
      })

      // 最初の引数(フォームデータ)を確認
      const formData = onSubmit.mock.calls[0][0]
      expect(formData.status).toBe('sent')
      expect(formData.notes).toBe('テスト備考')
    })

    it('送信不可でフォームを送信できる', async () => {
      const user = userEvent.setup()
      const onSubmit = jest.fn()

      render(<WorkRecordForm {...mockProps} onSubmit={onSubmit} />)

      const statusSelect = screen.getByLabelText('作業ステータス')
      await user.selectOptions(statusSelect, 'cannot_send')

      await waitFor(() => {
        expect(screen.getByLabelText('送信不可理由')).toBeInTheDocument()
      })

      const reasonSelect = screen.getByLabelText('送信不可理由')
      await user.selectOptions(reasonSelect, '1')

      const notesTextarea = screen.getByLabelText('備考')
      await user.type(notesTextarea, 'フォームが見つかりませんでした')

      const submitButton = screen.getByRole('button', { name: '記録を保存' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalled()
      })

      // 最初の引数(フォームデータ)を確認
      const formData = onSubmit.mock.calls[0][0]
      expect(formData.status).toBe('cannot_send')
      expect(formData.cannot_send_reason_id).toBe(1)
      expect(formData.notes).toBe('フォームが見つかりませんでした')
    })

    it('備考なしでも送信できる', async () => {
      const user = userEvent.setup()
      const onSubmit = jest.fn()

      render(<WorkRecordForm {...mockProps} onSubmit={onSubmit} />)

      // デフォルトで 'sent' が選択されている
      const submitButton = screen.getByRole('button', { name: '記録を保存' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalled()
      })

      // 最初の引数(フォームデータ)を確認
      const formData = onSubmit.mock.calls[0][0]
      expect(formData.status).toBe('sent')
    })
  })

  describe('バリデーション', () => {
    it('備考が1000文字を超える場合はエラーが表示される', async () => {
      const user = userEvent.setup()
      const onSubmit = jest.fn()

      render(<WorkRecordForm {...mockProps} onSubmit={onSubmit} />)

      const notesTextarea = screen.getByLabelText('備考')
      const longText = 'あ'.repeat(1001)
      await user.type(notesTextarea, longText)

      const submitButton = screen.getByRole('button', { name: '記録を保存' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('備考は1000文字以内で入力してください')
        ).toBeInTheDocument()
      })

      expect(onSubmit).not.toHaveBeenCalled()
    })
  })

  describe('送信中の状態', () => {
    it('isSubmittingがtrueの場合、ボタンがローディング状態になる', () => {
      render(<WorkRecordForm {...mockProps} isSubmitting={true} />)

      const submitButton = screen.getByRole('button', { name: /記録を保存/ })
      expect(submitButton).toBeDisabled()
    })

    it('isSubmittingがtrueの場合、フォーム送信ができない', async () => {
      const user = userEvent.setup()
      const onSubmit = jest.fn()

      render(
        <WorkRecordForm {...mockProps} onSubmit={onSubmit} isSubmitting={true} />
      )

      const submitButton = screen.getByRole('button', { name: /記録を保存/ })
      await user.click(submitButton)

      // ボタンが無効化されているため、送信されない
      expect(onSubmit).not.toHaveBeenCalled()
    })
  })

  describe('デフォルト値', () => {
    it('初期状態で作業ステータスは「送信完了」が選択されている', () => {
      render(<WorkRecordForm {...mockProps} />)

      const statusSelect = screen.getByLabelText(
        '作業ステータス'
      ) as HTMLSelectElement
      expect(statusSelect.value).toBe('sent')
    })
  })
})
