/**
 * AnswerFormコンポーネントのテスト
 *
 * TDDサイクルに従って実装
 * - React Testing Library を使用
 * - ユーザー操作に近いセレクターを優先
 */

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AnswerForm from '@/components/features/worker-questions/AnswerForm'
import * as workerQuestionApi from '@/lib/workerQuestionApi'

// APIモジュールをモック
jest.mock('@/lib/workerQuestionApi')

describe('AnswerForm', () => {
  const mockOnSuccess = jest.fn()
  const mockOnCancel = jest.fn()
  const questionId = 1

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('レンダリング', () => {
    it('回答入力フィールドが表示される', () => {
      render(
        <AnswerForm
          questionId={questionId}
          onSuccess={mockOnSuccess}
        />
      )

      expect(screen.getByLabelText(/回答内容/)).toBeInTheDocument()
      expect(screen.getByRole('textbox', { name: /回答内容/ })).toBeInTheDocument()
    })

    it('送信ボタンが表示される', () => {
      render(
        <AnswerForm
          questionId={questionId}
          onSuccess={mockOnSuccess}
        />
      )

      expect(screen.getByRole('button', { name: /回答を送信/ })).toBeInTheDocument()
    })

    it('既存の回答がある場合は初期値として設定される', () => {
      const existingAnswer = '既存の回答です'

      render(
        <AnswerForm
          questionId={questionId}
          existingAnswer={existingAnswer}
          onSuccess={mockOnSuccess}
        />
      )

      const textarea = screen.getByRole('textbox', { name: /回答内容/ })
      expect(textarea).toHaveValue(existingAnswer)
      expect(screen.getByRole('button', { name: /回答を更新/ })).toBeInTheDocument()
    })

    it('キャンセルボタンが提供された場合は表示される', () => {
      render(
        <AnswerForm
          questionId={questionId}
          onSuccess={mockOnSuccess}
          onCancel={mockOnCancel}
        />
      )

      expect(screen.getByRole('button', { name: /キャンセル/ })).toBeInTheDocument()
    })
  })

  describe('バリデーション', () => {
    it('空の回答で送信するとエラーメッセージが表示される', async () => {
      const user = userEvent.setup()

      render(
        <AnswerForm
          questionId={questionId}
          onSuccess={mockOnSuccess}
        />
      )

      const submitButton = screen.getByRole('button', { name: /回答を送信/ })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('回答を入力してください')).toBeInTheDocument()
      })

      expect(mockOnSuccess).not.toHaveBeenCalled()
    })

    it('5001文字以上の回答で送信するとエラーメッセージが表示される', async () => {
      const user = userEvent.setup()
      const longAnswer = 'あ'.repeat(5001)

      render(
        <AnswerForm
          questionId={questionId}
          onSuccess={mockOnSuccess}
        />
      )

      const textarea = screen.getByRole('textbox', { name: /回答内容/ })
      await user.type(textarea, longAnswer)

      const submitButton = screen.getByRole('button', { name: /回答を送信/ })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('回答は5000文字以内で入力してください')
        ).toBeInTheDocument()
      })

      expect(mockOnSuccess).not.toHaveBeenCalled()
    })
  })

  describe('フォーム送信', () => {
    it('有効な回答を送信すると成功コールバックが呼ばれる', async () => {
      const user = userEvent.setup()
      const answer = 'これは回答です'
      const mockUpdatedQuestion = {
        id: questionId,
        workerId: 1,
        organizationId: 1,
        clientOrganizationId: null,
        title: 'テスト質問',
        content: '質問内容',
        status: 'answered' as const,
        priority: 'medium' as const,
        answer: answer,
        answeredByUserId: 1,
        answeredAt: new Date().toISOString(),
        tags: null,
        internalNotes: null,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        deletedAt: null,
      }

      ;(workerQuestionApi.addAnswerToWorkerQuestion as jest.Mock).mockResolvedValue(
        mockUpdatedQuestion
      )

      render(
        <AnswerForm
          questionId={questionId}
          onSuccess={mockOnSuccess}
        />
      )

      const textarea = screen.getByRole('textbox', { name: /回答内容/ })
      await user.type(textarea, answer)

      const submitButton = screen.getByRole('button', { name: /回答を送信/ })
      await user.click(submitButton)

      await waitFor(() => {
        expect(workerQuestionApi.addAnswerToWorkerQuestion).toHaveBeenCalledWith(
          questionId,
          { answer }
        )
      })

      expect(mockOnSuccess).toHaveBeenCalledWith(mockUpdatedQuestion)
    })

    it('送信中はボタンが無効化され「送信中...」と表示される', async () => {
      const user = userEvent.setup()
      const answer = 'これは回答です'

      // API呼び出しを遅延させる
      ;(workerQuestionApi.addAnswerToWorkerQuestion as jest.Mock).mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      )

      render(
        <AnswerForm
          questionId={questionId}
          onSuccess={mockOnSuccess}
        />
      )

      const textarea = screen.getByRole('textbox', { name: /回答内容/ })
      await user.type(textarea, answer)

      const submitButton = screen.getByRole('button', { name: /回答を送信/ })
      await user.click(submitButton)

      // 送信中の状態を確認
      expect(screen.getByRole('button', { name: /送信中/ })).toBeDisabled()
      expect(screen.getByText(/送信中/)).toBeInTheDocument()
    })

    it('送信エラー時はエラーメッセージが表示される', async () => {
      const user = userEvent.setup()
      const answer = 'これは回答です'
      const errorMessage = 'ネットワークエラーが発生しました'

      ;(workerQuestionApi.addAnswerToWorkerQuestion as jest.Mock).mockRejectedValue(
        new Error(errorMessage)
      )

      render(
        <AnswerForm
          questionId={questionId}
          onSuccess={mockOnSuccess}
        />
      )

      const textarea = screen.getByRole('textbox', { name: /回答内容/ })
      await user.type(textarea, answer)

      const submitButton = screen.getByRole('button', { name: /回答を送信/ })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument()
      })

      expect(mockOnSuccess).not.toHaveBeenCalled()
    })
  })

  describe('キャンセル処理', () => {
    it('キャンセルボタンをクリックするとコールバックが呼ばれる', async () => {
      const user = userEvent.setup()

      render(
        <AnswerForm
          questionId={questionId}
          onSuccess={mockOnSuccess}
          onCancel={mockOnCancel}
        />
      )

      const cancelButton = screen.getByRole('button', { name: /キャンセル/ })
      await user.click(cancelButton)

      expect(mockOnCancel).toHaveBeenCalled()
    })

    it('送信中はキャンセルボタンが無効化される', async () => {
      const user = userEvent.setup()
      const answer = 'これは回答です'

      // API呼び出しを遅延させる
      ;(workerQuestionApi.addAnswerToWorkerQuestion as jest.Mock).mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      )

      render(
        <AnswerForm
          questionId={questionId}
          onSuccess={mockOnSuccess}
          onCancel={mockOnCancel}
        />
      )

      const textarea = screen.getByRole('textbox', { name: /回答内容/ })
      await user.type(textarea, answer)

      const submitButton = screen.getByRole('button', { name: /回答を送信/ })
      await user.click(submitButton)

      // 送信中のキャンセルボタンの状態を確認
      const cancelButton = screen.getByRole('button', { name: /キャンセル/ })
      expect(cancelButton).toBeDisabled()
    })
  })

  describe('アクセシビリティ', () => {
    it('エラーメッセージがaria-describedbyで関連付けられる', async () => {
      const user = userEvent.setup()

      render(
        <AnswerForm
          questionId={questionId}
          onSuccess={mockOnSuccess}
        />
      )

      const submitButton = screen.getByRole('button', { name: /回答を送信/ })
      await user.click(submitButton)

      await waitFor(() => {
        const textarea = screen.getByRole('textbox', { name: /回答内容/ })
        const errorId = textarea.getAttribute('aria-describedby')
        expect(errorId).toBeTruthy()

        if (errorId) {
          const errorElement = document.getElementById(errorId)
          expect(errorElement).toHaveTextContent('回答を入力してください')
        }
      })
    })

    it('必須フィールドがマークされている', () => {
      render(
        <AnswerForm
          questionId={questionId}
          onSuccess={mockOnSuccess}
        />
      )

      const label = screen.getByText(/回答内容/)
      expect(label).toHaveTextContent('*')
    })
  })
})
