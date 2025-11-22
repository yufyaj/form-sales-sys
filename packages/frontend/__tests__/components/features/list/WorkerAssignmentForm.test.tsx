import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useRouter } from 'next/navigation'
import WorkerAssignmentForm from '@/components/features/list/WorkerAssignmentForm'
import type { User } from '@/types/user'

// Next.jsのuseRouterをモック
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

const mockRouter = {
  push: jest.fn(),
  back: jest.fn(),
  refresh: jest.fn(),
}

describe('WorkerAssignmentForm', () => {
  const projectId = 1
  const listId = 1

  const mockWorkers: User[] = [
    {
      id: 1,
      organization_id: 1,
      email: 'worker1@example.com',
      full_name: 'ワーカー1',
      phone: null,
      avatar_url: null,
      description: null,
      is_active: true,
      is_email_verified: true,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
      deleted_at: null,
    },
    {
      id: 2,
      organization_id: 1,
      email: 'worker2@example.com',
      full_name: 'ワーカー2',
      phone: null,
      avatar_url: null,
      description: null,
      is_active: true,
      is_email_verified: true,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
      deleted_at: null,
    },
  ]

  beforeEach(() => {
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
    jest.clearAllMocks()
  })

  describe('フォームのレンダリング', () => {
    it('全てのフィールドが表示される', () => {
      const mockOnSubmit = jest.fn()
      render(
        <WorkerAssignmentForm
          projectId={projectId}
          listId={listId}
          workers={mockWorkers}
          onSubmit={mockOnSubmit}
        />
      )

      expect(screen.getByLabelText('ワーカー')).toBeInTheDocument()
      expect(screen.getByLabelText('開始行')).toBeInTheDocument()
      expect(screen.getByLabelText('終了行')).toBeInTheDocument()
      expect(screen.getByLabelText('優先度')).toBeInTheDocument()
      expect(screen.getByLabelText('期限（任意）')).toBeInTheDocument()
      expect(
        screen.getByLabelText('割り当て済み企業を非表示')
      ).toBeInTheDocument()
    })

    it('ワーカー選択肢が表示される', () => {
      const mockOnSubmit = jest.fn()
      render(
        <WorkerAssignmentForm
          projectId={projectId}
          listId={listId}
          workers={mockWorkers}
          onSubmit={mockOnSubmit}
        />
      )

      const workerSelect = screen.getByLabelText('ワーカー')
      expect(workerSelect).toBeInTheDocument()

      // ワーカーの選択肢が表示されているか
      expect(screen.getByRole('option', { name: 'ワーカー1' })).toBeInTheDocument()
      expect(screen.getByRole('option', { name: 'ワーカー2' })).toBeInTheDocument()
    })

    it('適切なボタンが表示される', () => {
      const mockOnSubmit = jest.fn()
      render(
        <WorkerAssignmentForm
          projectId={projectId}
          listId={listId}
          workers={mockWorkers}
          onSubmit={mockOnSubmit}
        />
      )

      expect(
        screen.getByRole('button', { name: '割り当て' })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'キャンセル' })
      ).toBeInTheDocument()
    })
  })

  describe('バリデーション', () => {
    it('ワーカーが未選択の場合エラーが表示される', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn()

      render(
        <WorkerAssignmentForm
          projectId={projectId}
          listId={listId}
          workers={mockWorkers}
          onSubmit={mockOnSubmit}
        />
      )

      const submitButton = screen.getByRole('button', { name: '割り当て' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('ワーカーを選択してください')
        ).toBeInTheDocument()
      })

      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    it('開始行が未入力の場合エラーが表示される', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn()

      render(
        <WorkerAssignmentForm
          projectId={projectId}
          listId={listId}
          workers={mockWorkers}
          onSubmit={mockOnSubmit}
        />
      )

      const submitButton = screen.getByRole('button', { name: '割り当て' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('開始行を入力してください')
        ).toBeInTheDocument()
      })

      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    it('終了行が未入力の場合エラーが表示される', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn()

      render(
        <WorkerAssignmentForm
          projectId={projectId}
          listId={listId}
          workers={mockWorkers}
          onSubmit={mockOnSubmit}
        />
      )

      const submitButton = screen.getByRole('button', { name: '割り当て' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('終了行を入力してください')
        ).toBeInTheDocument()
      })

      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    it('開始行が終了行より大きい場合エラーが表示される', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn()

      render(
        <WorkerAssignmentForm
          projectId={projectId}
          listId={listId}
          workers={mockWorkers}
          onSubmit={mockOnSubmit}
        />
      )

      // ワーカーを選択
      const workerSelect = screen.getByLabelText('ワーカー')
      await user.selectOptions(workerSelect, '1')

      // 開始行 > 終了行
      const startRowInput = screen.getByLabelText('開始行')
      await user.type(startRowInput, '100')

      const endRowInput = screen.getByLabelText('終了行')
      await user.type(endRowInput, '50')

      const submitButton = screen.getByRole('button', { name: '割り当て' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('開始行は終了行以下である必要があります')
        ).toBeInTheDocument()
      })

      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    it('開始行が1未満の場合エラーが表示される', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn()

      render(
        <WorkerAssignmentForm
          projectId={projectId}
          listId={listId}
          workers={mockWorkers}
          onSubmit={mockOnSubmit}
        />
      )

      const startRowInput = screen.getByLabelText('開始行')
      await user.type(startRowInput, '0')

      const submitButton = screen.getByRole('button', { name: '割り当て' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('開始行は1以上である必要があります')
        ).toBeInTheDocument()
      })

      expect(mockOnSubmit).not.toHaveBeenCalled()
    })
  })

  describe('フォーム送信', () => {
    it('正しい入力でフォームが送信される', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn().mockResolvedValue(undefined)

      render(
        <WorkerAssignmentForm
          projectId={projectId}
          listId={listId}
          workers={mockWorkers}
          onSubmit={mockOnSubmit}
        />
      )

      // ワーカーを選択
      const workerSelect = screen.getByLabelText('ワーカー')
      await user.selectOptions(workerSelect, '1')

      // 開始行・終了行を入力
      const startRowInput = screen.getByLabelText('開始行')
      await user.type(startRowInput, '1')

      const endRowInput = screen.getByLabelText('終了行')
      await user.type(endRowInput, '100')

      const submitButton = screen.getByRole('button', { name: '割り当て' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            workerId: 1,
            startRow: 1,
            endRow: 100,
            priority: 'medium',
            hideAssigned: false,
          })
        )
      })

      // 成功時は前の画面に戻る
      expect(mockRouter.back).toHaveBeenCalled()
      expect(mockRouter.refresh).toHaveBeenCalled()
    })

    it('優先度と期限を含めて送信できる', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn().mockResolvedValue(undefined)

      render(
        <WorkerAssignmentForm
          projectId={projectId}
          listId={listId}
          workers={mockWorkers}
          onSubmit={mockOnSubmit}
        />
      )

      // ワーカーを選択
      const workerSelect = screen.getByLabelText('ワーカー')
      await user.selectOptions(workerSelect, '1')

      // 開始行・終了行を入力
      const startRowInput = screen.getByLabelText('開始行')
      await user.type(startRowInput, '1')

      const endRowInput = screen.getByLabelText('終了行')
      await user.type(endRowInput, '100')

      // 優先度を選択
      const prioritySelect = screen.getByLabelText('優先度')
      await user.selectOptions(prioritySelect, 'high')

      // 期限を入力
      const dueDateInput = screen.getByLabelText('期限（任意）')
      await user.type(dueDateInput, '2025-12-31')

      const submitButton = screen.getByRole('button', { name: '割り当て' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            workerId: 1,
            startRow: 1,
            endRow: 100,
            priority: 'high',
            dueDate: '2025-12-31',
          })
        )
      })
    })

    it('送信エラー時にエラーメッセージが表示される', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest
        .fn()
        .mockRejectedValue(new Error('Server error'))

      render(
        <WorkerAssignmentForm
          projectId={projectId}
          listId={listId}
          workers={mockWorkers}
          onSubmit={mockOnSubmit}
        />
      )

      // ワーカーを選択
      const workerSelect = screen.getByLabelText('ワーカー')
      await user.selectOptions(workerSelect, '1')

      // 開始行・終了行を入力
      const startRowInput = screen.getByLabelText('開始行')
      await user.type(startRowInput, '1')

      const endRowInput = screen.getByLabelText('終了行')
      await user.type(endRowInput, '100')

      const submitButton = screen.getByRole('button', { name: '割り当て' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent(
          'サーバーエラーが発生しました。しばらくしてから再度お試しください'
        )
      })
    })

    it('送信中はボタンが無効化される', async () => {
      const user = userEvent.setup()
      // 送信を遅延させるPromiseを返す
      const mockOnSubmit = jest.fn().mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      )

      render(
        <WorkerAssignmentForm
          projectId={projectId}
          listId={listId}
          workers={mockWorkers}
          onSubmit={mockOnSubmit}
        />
      )

      // ワーカーを選択
      const workerSelect = screen.getByLabelText('ワーカー')
      await user.selectOptions(workerSelect, '1')

      // 開始行・終了行を入力
      const startRowInput = screen.getByLabelText('開始行')
      await user.type(startRowInput, '1')

      const endRowInput = screen.getByLabelText('終了行')
      await user.type(endRowInput, '100')

      const submitButton = screen.getByRole('button', { name: '割り当て' })
      await user.click(submitButton)

      // 送信中はローディングテキストが表示される
      await waitFor(() => {
        expect(screen.getByText('割り当て中...')).toBeInTheDocument()
      })

      // 送信完了まで待機
      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled()
      })
    })
  })

  describe('キャンセルボタン', () => {
    it('キャンセルボタンクリックでonCancelが呼ばれる', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn()
      const mockOnCancel = jest.fn()

      render(
        <WorkerAssignmentForm
          projectId={projectId}
          listId={listId}
          workers={mockWorkers}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      )

      const cancelButton = screen.getByRole('button', { name: 'キャンセル' })
      await user.click(cancelButton)

      expect(mockOnCancel).toHaveBeenCalled()
    })

    it('onCancelが未指定の場合、router.backが呼ばれる', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn()

      render(
        <WorkerAssignmentForm
          projectId={projectId}
          listId={listId}
          workers={mockWorkers}
          onSubmit={mockOnSubmit}
        />
      )

      const cancelButton = screen.getByRole('button', { name: 'キャンセル' })
      await user.click(cancelButton)

      expect(mockRouter.back).toHaveBeenCalled()
    })
  })

  describe('割り当て済み企業の非表示', () => {
    it('非表示チェックボックスが機能する', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn().mockResolvedValue(undefined)

      render(
        <WorkerAssignmentForm
          projectId={projectId}
          listId={listId}
          workers={mockWorkers}
          onSubmit={mockOnSubmit}
        />
      )

      // チェックボックスをON
      const hideAssignedCheckbox = screen.getByLabelText('割り当て済み企業を非表示')
      await user.click(hideAssignedCheckbox)

      // ワーカーを選択
      const workerSelect = screen.getByLabelText('ワーカー')
      await user.selectOptions(workerSelect, '1')

      // 開始行・終了行を入力
      const startRowInput = screen.getByLabelText('開始行')
      await user.type(startRowInput, '1')

      const endRowInput = screen.getByLabelText('終了行')
      await user.type(endRowInput, '100')

      const submitButton = screen.getByRole('button', { name: '割り当て' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            hideAssigned: true,
          })
        )
      })
    })
  })
})
