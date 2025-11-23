import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import QuestionForm from '@/components/features/question/QuestionForm'
import { createQuestionAction } from '@/lib/actions/questions'

// Server Actionsのモック
jest.mock('@/lib/actions/questions', () => ({
  createQuestionAction: jest.fn(),
}))

const mockCreateQuestionAction = createQuestionAction as jest.MockedFunction<
  typeof createQuestionAction
>

describe('QuestionForm', () => {
  const defaultProps = {
    clientOrganizationId: 1,
    clientOrganizationName: '株式会社テスト',
  }

  const mockOnSuccess = jest.fn()
  const mockOnCancel = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('初期表示', () => {
    it('全ての入力フィールドが表示される', () => {
      render(<QuestionForm {...defaultProps} />)

      expect(screen.getByText('質問対象の顧客')).toBeInTheDocument()
      expect(screen.getByText('株式会社テスト')).toBeInTheDocument()
      expect(screen.getByLabelText('質問タイトル')).toBeInTheDocument()
      expect(screen.getByLabelText(/質問内容/i)).toBeInTheDocument()
      expect(screen.getByLabelText('優先度')).toBeInTheDocument()
    })

    it('質問を投稿ボタンが表示される', () => {
      render(<QuestionForm {...defaultProps} />)

      expect(
        screen.getByRole('button', { name: '質問を投稿' })
      ).toBeInTheDocument()
    })

    it('onCancelが提供された場合、キャンセルボタンが表示される', () => {
      render(<QuestionForm {...defaultProps} onCancel={mockOnCancel} />)

      expect(
        screen.getByRole('button', { name: 'キャンセル' })
      ).toBeInTheDocument()
    })

    it('優先度のデフォルト値が「中」である', () => {
      render(<QuestionForm {...defaultProps} />)

      const prioritySelect = screen.getByLabelText('優先度') as HTMLSelectElement
      expect(prioritySelect.value).toBe('medium')
    })
  })

  describe('バリデーション', () => {
    it('質問タイトルが空の場合、エラーが表示される', async () => {
      const user = userEvent.setup()
      render(<QuestionForm {...defaultProps} />)

      const titleInput = screen.getByLabelText('質問タイトル')
      await user.click(titleInput)
      await user.tab()

      await waitFor(() => {
        expect(
          screen.getByText('質問タイトルを入力してください')
        ).toBeInTheDocument()
      })
    })

    it('質問内容が空の場合、エラーが表示される', async () => {
      const user = userEvent.setup()
      render(<QuestionForm {...defaultProps} />)

      const contentTextarea = screen.getByLabelText(/質問内容/i)
      await user.click(contentTextarea)
      await user.tab()

      await waitFor(() => {
        expect(
          screen.getByText('質問内容を入力してください')
        ).toBeInTheDocument()
      })
    })

    it('質問タイトルが500文字を超える場合、エラーが表示される', async () => {
      const user = userEvent.setup()
      render(<QuestionForm {...defaultProps} />)

      const longTitle = 'a'.repeat(501)
      const titleInput = screen.getByLabelText('質問タイトル')

      await user.click(titleInput)
      await user.paste(longTitle)
      await user.tab()

      await waitFor(() => {
        expect(
          screen.getByText('質問タイトルは500文字以内で入力してください')
        ).toBeInTheDocument()
      })
    })

    it('質問内容が5000文字を超える場合、エラーが表示される', async () => {
      const user = userEvent.setup()
      render(<QuestionForm {...defaultProps} />)

      const longContent = 'a'.repeat(5001)
      const contentTextarea = screen.getByLabelText(/質問内容/i)

      await user.click(contentTextarea)
      await user.paste(longContent)
      await user.tab()

      await waitFor(() => {
        expect(
          screen.getByText('質問内容は5000文字以内で入力してください')
        ).toBeInTheDocument()
      })
    })
  })

  describe('フォーム送信', () => {
    it('正しい入力で送信すると、createQuestionActionが呼ばれる', async () => {
      const user = userEvent.setup()
      mockCreateQuestionAction.mockResolvedValue({
        success: true,
        data: {
          id: 1,
          workerId: 1,
          organizationId: 1,
          clientOrganizationId: 1,
          title: 'テスト質問',
          content: 'テスト質問の内容です',
          status: 'pending',
          priority: 'medium',
          answer: null,
          answeredByUserId: null,
          answeredAt: null,
          tags: null,
          internalNotes: null,
          createdAt: '2025-01-01T00:00:00Z',
          updatedAt: '2025-01-01T00:00:00Z',
          deletedAt: null,
        },
      })

      render(<QuestionForm {...defaultProps} onSuccess={mockOnSuccess} />)

      await user.type(
        screen.getByLabelText('質問タイトル'),
        'テスト質問'
      )
      await user.type(
        screen.getByLabelText(/質問内容/i),
        'テスト質問の内容です'
      )

      const submitButton = screen.getByRole('button', { name: '質問を投稿' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockCreateQuestionAction).toHaveBeenCalledTimes(1)
        expect(mockCreateQuestionAction).toHaveBeenCalledWith(1, {
          title: 'テスト質問',
          content: 'テスト質問の内容です',
          priority: 'medium',
        })
      })
    })

    it('送信成功後、成功メッセージが表示される', async () => {
      const user = userEvent.setup()
      mockCreateQuestionAction.mockResolvedValue({
        success: true,
        data: {
          id: 1,
          workerId: 1,
          organizationId: 1,
          clientOrganizationId: 1,
          title: 'テスト質問',
          content: 'テスト質問の内容です',
          status: 'pending',
          priority: 'medium',
          answer: null,
          answeredByUserId: null,
          answeredAt: null,
          tags: null,
          internalNotes: null,
          createdAt: '2025-01-01T00:00:00Z',
          updatedAt: '2025-01-01T00:00:00Z',
          deletedAt: null,
        },
      })

      render(<QuestionForm {...defaultProps} />)

      await user.type(
        screen.getByLabelText('質問タイトル'),
        'テスト質問'
      )
      await user.type(
        screen.getByLabelText(/質問内容/i),
        'テスト質問の内容です'
      )

      const submitButton = screen.getByRole('button', { name: '質問を投稿' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('質問を投稿しました')).toBeInTheDocument()
      })
    })

    it('送信成功後、フォームがリセットされる', async () => {
      const user = userEvent.setup()
      mockCreateQuestionAction.mockResolvedValue({
        success: true,
        data: {
          id: 1,
          workerId: 1,
          organizationId: 1,
          clientOrganizationId: 1,
          title: 'テスト質問',
          content: 'テスト質問の内容です',
          status: 'pending',
          priority: 'medium',
          answer: null,
          answeredByUserId: null,
          answeredAt: null,
          tags: null,
          internalNotes: null,
          createdAt: '2025-01-01T00:00:00Z',
          updatedAt: '2025-01-01T00:00:00Z',
          deletedAt: null,
        },
      })

      render(<QuestionForm {...defaultProps} />)

      const titleInput = screen.getByLabelText('質問タイトル') as HTMLInputElement
      const contentTextarea = screen.getByLabelText(/質問内容/i) as HTMLTextAreaElement

      await user.type(titleInput, 'テスト質問')
      await user.type(contentTextarea, 'テスト質問の内容です')

      const submitButton = screen.getByRole('button', { name: '質問を投稿' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(titleInput.value).toBe('')
        expect(contentTextarea.value).toBe('')
      })
    })

    it('送信失敗時、エラーメッセージが表示される', async () => {
      const user = userEvent.setup()
      mockCreateQuestionAction.mockResolvedValue({
        success: false,
        error: '質問の投稿に失敗しました',
      })

      render(<QuestionForm {...defaultProps} />)

      await user.type(
        screen.getByLabelText('質問タイトル'),
        'テスト質問'
      )
      await user.type(
        screen.getByLabelText(/質問内容/i),
        'テスト質問の内容です'
      )

      const submitButton = screen.getByRole('button', { name: '質問を投稿' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('質問の投稿に失敗しました')
        ).toBeInTheDocument()
      })
    })
  })

  describe('優先度選択', () => {
    it('優先度を変更できる', async () => {
      const user = userEvent.setup()
      mockCreateQuestionAction.mockResolvedValue({
        success: true,
        data: {
          id: 1,
          workerId: 1,
          organizationId: 1,
          clientOrganizationId: 1,
          title: 'テスト質問',
          content: 'テスト質問の内容です',
          status: 'pending',
          priority: 'high',
          answer: null,
          answeredByUserId: null,
          answeredAt: null,
          tags: null,
          internalNotes: null,
          createdAt: '2025-01-01T00:00:00Z',
          updatedAt: '2025-01-01T00:00:00Z',
          deletedAt: null,
        },
      })

      render(<QuestionForm {...defaultProps} />)

      await user.type(
        screen.getByLabelText('質問タイトル'),
        'テスト質問'
      )
      await user.type(
        screen.getByLabelText(/質問内容/i),
        'テスト質問の内容です'
      )

      const prioritySelect = screen.getByLabelText('優先度')
      await user.selectOptions(prioritySelect, 'high')

      const submitButton = screen.getByRole('button', { name: '質問を投稿' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockCreateQuestionAction).toHaveBeenCalledWith(1, {
          title: 'テスト質問',
          content: 'テスト質問の内容です',
          priority: 'high',
        })
      })
    })
  })

  describe('キャンセル', () => {
    it('キャンセルボタンをクリックすると、onCancelが呼ばれる', async () => {
      const user = userEvent.setup()
      render(<QuestionForm {...defaultProps} onCancel={mockOnCancel} />)

      const cancelButton = screen.getByRole('button', { name: 'キャンセル' })
      await user.click(cancelButton)

      expect(mockOnCancel).toHaveBeenCalledTimes(1)
    })
  })

  describe('ローディング状態', () => {
    it('送信中はボタンが無効化される', async () => {
      const user = userEvent.setup()
      mockCreateQuestionAction.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(
              () =>
                resolve({
                  success: true,
                  data: {
                    id: 1,
                    workerId: 1,
                    organizationId: 1,
                    clientOrganizationId: 1,
                    title: 'テスト質問',
                    content: 'テスト質問の内容です',
                    status: 'pending',
                    priority: 'medium',
                    answer: null,
                    answeredByUserId: null,
                    answeredAt: null,
                    tags: null,
                    internalNotes: null,
                    createdAt: '2025-01-01T00:00:00Z',
                    updatedAt: '2025-01-01T00:00:00Z',
                    deletedAt: null,
                  },
                }),
              100
            )
          )
      )

      render(<QuestionForm {...defaultProps} onCancel={mockOnCancel} />)

      await user.type(
        screen.getByLabelText('質問タイトル'),
        'テスト質問'
      )
      await user.type(
        screen.getByLabelText(/質問内容/i),
        'テスト質問の内容です'
      )

      const submitButton = screen.getByRole('button', { name: '質問を投稿' })
      await user.click(submitButton)

      // 送信中の状態を確認
      expect(screen.getByRole('button', { name: '投稿中...' })).toBeDisabled()
      expect(screen.getByRole('button', { name: 'キャンセル' })).toBeDisabled()

      // 送信完了まで待機
      await waitFor(() => {
        expect(screen.getByText('質問を投稿しました')).toBeInTheDocument()
      })
    })
  })
})
