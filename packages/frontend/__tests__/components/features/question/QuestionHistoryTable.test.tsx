import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import QuestionHistoryTable from '@/components/features/question/QuestionHistoryTable'
import { getQuestionsByClientOrganizationAction } from '@/lib/actions/questions'
import type { WorkerQuestion } from '@/types/question'

// Server Actionsのモック
jest.mock('@/lib/actions/questions', () => ({
  getQuestionsByClientOrganizationAction: jest.fn(),
}))

const mockGetQuestions = getQuestionsByClientOrganizationAction as jest.MockedFunction<
  typeof getQuestionsByClientOrganizationAction
>

describe('QuestionHistoryTable', () => {
  const mockQuestions: WorkerQuestion[] = [
    {
      id: 1,
      workerId: 1,
      organizationId: 1,
      clientOrganizationId: 1,
      title: 'フォーム入力の手順について',
      content: 'フォーム入力の手順がわかりません',
      status: 'pending',
      priority: 'medium',
      answer: null,
      answeredByUserId: null,
      answeredAt: null,
      tags: null,
      internalNotes: null,
      createdAt: '2025-01-01T10:00:00Z',
      updatedAt: '2025-01-01T10:00:00Z',
      deletedAt: null,
    },
    {
      id: 2,
      workerId: 1,
      organizationId: 1,
      clientOrganizationId: 1,
      title: '営業電話のスクリプトについて',
      content: '営業電話のスクリプトを教えてください',
      status: 'answered',
      priority: 'high',
      answer: '以下のスクリプトをご利用ください',
      answeredByUserId: 2,
      answeredAt: '2025-01-02T14:30:00Z',
      tags: '["営業", "スクリプト"]',
      internalNotes: null,
      createdAt: '2025-01-02T09:00:00Z',
      updatedAt: '2025-01-02T14:30:00Z',
      deletedAt: null,
    },
  ]

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('初期表示', () => {
    it('ローディング中は読み込みメッセージが表示される', () => {
      mockGetQuestions.mockReturnValue(new Promise(() => {}))

      render(<QuestionHistoryTable clientOrganizationId={1} />)

      expect(screen.getByText('読み込み中...')).toBeInTheDocument()
    })

    it('質問一覧が正常に表示される', async () => {
      mockGetQuestions.mockResolvedValue({
        success: true,
        data: {
          questions: mockQuestions,
          total: 2,
          skip: 0,
          limit: 100,
        },
      })

      render(<QuestionHistoryTable clientOrganizationId={1} />)

      await waitFor(() => {
        expect(screen.getByText('フォーム入力の手順について')).toBeInTheDocument()
        expect(screen.getByText('営業電話のスクリプトについて')).toBeInTheDocument()
      })
    })

    it('質問がない場合、空のメッセージが表示される', async () => {
      mockGetQuestions.mockResolvedValue({
        success: true,
        data: {
          questions: [],
          total: 0,
          skip: 0,
          limit: 100,
        },
      })

      render(<QuestionHistoryTable clientOrganizationId={1} />)

      await waitFor(() => {
        expect(screen.getByText('質問履歴がありません')).toBeInTheDocument()
      })
    })

    it('エラーが発生した場合、エラーメッセージが表示される', async () => {
      mockGetQuestions.mockResolvedValue({
        success: false,
        error: '質問一覧の取得に失敗しました',
      })

      render(<QuestionHistoryTable clientOrganizationId={1} />)

      await waitFor(() => {
        expect(
          screen.getByText('質問一覧の取得に失敗しました')
        ).toBeInTheDocument()
      })
    })
  })

  describe('テーブル表示', () => {
    beforeEach(() => {
      mockGetQuestions.mockResolvedValue({
        success: true,
        data: {
          questions: mockQuestions,
          total: 2,
          skip: 0,
          limit: 100,
        },
      })
    })

    it('投稿日時が正しくフォーマットされて表示される', async () => {
      render(<QuestionHistoryTable clientOrganizationId={1} />)

      await waitFor(() => {
        // 日本時間でフォーマットされた日時が表示される
        expect(screen.getAllByText(/2025\/01\/01/).length).toBeGreaterThan(0)
        expect(screen.getAllByText(/2025\/01\/02/).length).toBeGreaterThan(0)
      })
    })

    it('ステータスバッジが正しく表示される', async () => {
      render(<QuestionHistoryTable clientOrganizationId={1} />)

      await waitFor(() => {
        expect(screen.getByText('未対応')).toBeInTheDocument()
        expect(screen.getByText('回答済み')).toBeInTheDocument()
      })
    })

    it('優先度バッジが正しく表示される', async () => {
      render(<QuestionHistoryTable clientOrganizationId={1} />)

      await waitFor(() => {
        expect(screen.getByText('中')).toBeInTheDocument()
        expect(screen.getByText('高')).toBeInTheDocument()
      })
    })

    it('回答日時がnullの場合、ハイフンが表示される', async () => {
      render(<QuestionHistoryTable clientOrganizationId={1} />)

      await waitFor(() => {
        const rows = screen.getAllByRole('row')
        // ヘッダー行を除く最初のデータ行（回答なし）
        expect(rows[1]).toHaveTextContent('-')
      })
    })

    it('回答日時がある場合、正しくフォーマットされて表示される', async () => {
      render(<QuestionHistoryTable clientOrganizationId={1} />)

      await waitFor(() => {
        const rows = screen.getAllByRole('row')
        // 2行目（ヘッダーの次、2番目の質問）に回答日時が含まれている
        expect(rows[2].textContent).toMatch(/23:30/)
      })
    })
  })

  describe('行クリック', () => {
    it('onQuestionClickが提供された場合、行をクリックするとコールバックが呼ばれる', async () => {
      const mockOnQuestionClick = jest.fn()
      mockGetQuestions.mockResolvedValue({
        success: true,
        data: {
          questions: mockQuestions,
          total: 2,
          skip: 0,
          limit: 100,
        },
      })

      render(
        <QuestionHistoryTable
          clientOrganizationId={1}
          onQuestionClick={mockOnQuestionClick}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('フォーム入力の手順について')).toBeInTheDocument()
      })

      const user = userEvent.setup()
      const firstRow = screen.getByText('フォーム入力の手順について').closest('tr')
      if (firstRow) {
        await user.click(firstRow)
      }

      expect(mockOnQuestionClick).toHaveBeenCalledTimes(1)
      expect(mockOnQuestionClick).toHaveBeenCalledWith(mockQuestions[0])
    })
  })

  describe('リフレッシュ', () => {
    it('refreshTriggerが変更されると、質問一覧が再取得される', async () => {
      mockGetQuestions.mockResolvedValue({
        success: true,
        data: {
          questions: mockQuestions,
          total: 2,
          skip: 0,
          limit: 100,
        },
      })

      const { rerender } = render(
        <QuestionHistoryTable clientOrganizationId={1} refreshTrigger={0} />
      )

      await waitFor(() => {
        expect(mockGetQuestions).toHaveBeenCalledTimes(1)
      })

      // refreshTriggerを変更
      rerender(
        <QuestionHistoryTable clientOrganizationId={1} refreshTrigger={1} />
      )

      await waitFor(() => {
        expect(mockGetQuestions).toHaveBeenCalledTimes(2)
      })
    })
  })

  describe('APIコール', () => {
    it('正しいパラメータでAPIが呼ばれる', async () => {
      mockGetQuestions.mockResolvedValue({
        success: true,
        data: {
          questions: [],
          total: 0,
          skip: 0,
          limit: 100,
        },
      })

      render(<QuestionHistoryTable clientOrganizationId={123} />)

      await waitFor(() => {
        expect(mockGetQuestions).toHaveBeenCalledWith(123, {
          limit: 100,
        })
      })
    })
  })
})
