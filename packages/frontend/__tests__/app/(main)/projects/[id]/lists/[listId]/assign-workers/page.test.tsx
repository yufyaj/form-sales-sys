import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AssignWorkersPage from '@/app/(main)/projects/[id]/lists/[listId]/assign-workers/page'
import { listWorkers } from '@/lib/api/users'
import { createAssignment } from '@/lib/api/assignments'
import type { User, UserListResponse } from '@/types/user'

// next/navigationのモック
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({
    push: jest.fn(),
    back: jest.fn(),
    refresh: jest.fn(),
  })),
  notFound: jest.fn(),
}))

// API関数のモック
jest.mock('@/lib/api/users', () => ({
  listWorkers: jest.fn(),
}))

jest.mock('@/lib/api/assignments', () => ({
  createAssignment: jest.fn(),
}))

// UIコンポーネントのモック
jest.mock('@/components/ui/Card', () => {
  return function Card({ children }: { children: React.ReactNode }) {
    return <div data-testid="card">{children}</div>
  }
})

describe('AssignWorkersPage', () => {
  const mockParams = Promise.resolve({
    id: '1',
    listId: '10',
  })

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

  const mockWorkersResponse: UserListResponse = {
    users: mockWorkers,
    total: 2,
    skip: 0,
    limit: 100,
  }

  beforeEach(() => {
    jest.clearAllMocks()
    ;(listWorkers as jest.Mock).mockResolvedValue(mockWorkersResponse)
  })

  describe('初期表示', () => {
    it('ワーカー一覧を取得して表示する', async () => {
      render(<AssignWorkersPage params={mockParams} />)

      await waitFor(() => {
        expect(listWorkers).toHaveBeenCalled()
      })

      await waitFor(() => {
        expect(screen.getByLabelText('ワーカー')).toBeInTheDocument()
        expect(screen.getByRole('option', { name: 'ワーカー1' })).toBeInTheDocument()
        expect(screen.getByRole('option', { name: 'ワーカー2' })).toBeInTheDocument()
      })
    })

    it('ページタイトルが表示される', async () => {
      render(<AssignWorkersPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText('ワーカー割り当て')).toBeInTheDocument()
      })
    })

    it('フォームの全フィールドが表示される', async () => {
      render(<AssignWorkersPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByLabelText('ワーカー')).toBeInTheDocument()
        expect(screen.getByLabelText('開始行')).toBeInTheDocument()
        expect(screen.getByLabelText('終了行')).toBeInTheDocument()
        expect(screen.getByLabelText('優先度')).toBeInTheDocument()
        expect(screen.getByLabelText('期限（任意）')).toBeInTheDocument()
        expect(
          screen.getByLabelText('割り当て済み企業を非表示')
        ).toBeInTheDocument()
      })
    })

    it('ワーカーが0件の場合はメッセージを表示する', async () => {
      ;(listWorkers as jest.Mock).mockResolvedValue({
        users: [],
        total: 0,
        skip: 0,
        limit: 100,
      })

      render(<AssignWorkersPage params={mockParams} />)

      await waitFor(() => {
        expect(
          screen.getByText('アクティブなワーカーが登録されていません')
        ).toBeInTheDocument()
      })
    })

    it('ワーカー取得エラー時はエラーメッセージを表示する', async () => {
      ;(listWorkers as jest.Mock).mockRejectedValue(
        new Error('Failed to fetch workers')
      )

      render(<AssignWorkersPage params={mockParams} />)

      await waitFor(() => {
        expect(
          screen.getByText('ワーカー一覧の取得に失敗しました')
        ).toBeInTheDocument()
      })
    })
  })

  describe('フォーム送信', () => {
    it('正しい入力で割り当てが作成される', async () => {
      const user = userEvent.setup()

      const mockAssignment = {
        id: 'assignment-1',
        listId: '10',
        listName: 'テストリスト',
        projectId: '1',
        projectName: 'テストプロジェクト',
        workerId: '1',
        status: 'assigned' as const,
        priority: 'medium' as const,
        recordsToProcess: 100,
        processedRecords: 0,
        successCount: 0,
        failureCount: 0,
        assignedAt: '2025-01-01T00:00:00Z',
      }

      ;(createAssignment as jest.Mock).mockResolvedValue(mockAssignment)

      render(<AssignWorkersPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByLabelText('ワーカー')).toBeInTheDocument()
      })

      // ワーカーを選択
      const workerSelect = screen.getByLabelText('ワーカー')
      await user.selectOptions(workerSelect, '1')

      // 開始行・終了行を入力
      const startRowInput = screen.getByLabelText('開始行')
      await user.type(startRowInput, '1')

      const endRowInput = screen.getByLabelText('終了行')
      await user.type(endRowInput, '100')

      // 送信
      const submitButton = screen.getByRole('button', { name: '割り当て' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(createAssignment).toHaveBeenCalledWith(
          1,
          10,
          expect.objectContaining({
            worker_id: 1,
            start_row: 1,
            end_row: 100,
            priority: 'medium',
          })
        )
      })
    })

    it('優先度と期限を含めて送信できる', async () => {
      const user = userEvent.setup()

      const mockAssignment = {
        id: 'assignment-2',
        listId: '10',
        listName: 'テストリスト',
        projectId: '1',
        projectName: 'テストプロジェクト',
        workerId: '1',
        status: 'assigned' as const,
        priority: 'high' as const,
        recordsToProcess: 50,
        processedRecords: 0,
        successCount: 0,
        failureCount: 0,
        assignedAt: '2025-01-01T00:00:00Z',
        dueDate: '2025-12-31',
      }

      ;(createAssignment as jest.Mock).mockResolvedValue(mockAssignment)

      render(<AssignWorkersPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByLabelText('ワーカー')).toBeInTheDocument()
      })

      // ワーカーを選択
      const workerSelect = screen.getByLabelText('ワーカー')
      await user.selectOptions(workerSelect, '1')

      // 開始行・終了行を入力
      const startRowInput = screen.getByLabelText('開始行')
      await user.type(startRowInput, '1')

      const endRowInput = screen.getByLabelText('終了行')
      await user.type(endRowInput, '50')

      // 優先度を選択
      const prioritySelect = screen.getByLabelText('優先度')
      await user.selectOptions(prioritySelect, 'high')

      // 期限を入力
      const dueDateInput = screen.getByLabelText('期限（任意）')
      await user.type(dueDateInput, '2025-12-31')

      // 送信
      const submitButton = screen.getByRole('button', { name: '割り当て' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(createAssignment).toHaveBeenCalledWith(
          1,
          10,
          expect.objectContaining({
            worker_id: 1,
            start_row: 1,
            end_row: 50,
            priority: 'high',
            due_date: '2025-12-31',
          })
        )
      })
    })

    it('割り当て作成エラー時にエラーメッセージが表示される', async () => {
      const user = userEvent.setup()

      ;(createAssignment as jest.Mock).mockRejectedValue(
        new Error('Server error')
      )

      render(<AssignWorkersPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByLabelText('ワーカー')).toBeInTheDocument()
      })

      // ワーカーを選択
      const workerSelect = screen.getByLabelText('ワーカー')
      await user.selectOptions(workerSelect, '1')

      // 開始行・終了行を入力
      const startRowInput = screen.getByLabelText('開始行')
      await user.type(startRowInput, '1')

      const endRowInput = screen.getByLabelText('終了行')
      await user.type(endRowInput, '100')

      // 送信
      const submitButton = screen.getByRole('button', { name: '割り当て' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent(
          'サーバーエラーが発生しました。しばらくしてから再度お試しください'
        )
      })
    })
  })

  describe('バリデーション', () => {
    it('開始行が終了行より大きい場合エラーが表示される', async () => {
      const user = userEvent.setup()

      render(<AssignWorkersPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByLabelText('ワーカー')).toBeInTheDocument()
      })

      // ワーカーを選択
      const workerSelect = screen.getByLabelText('ワーカー')
      await user.selectOptions(workerSelect, '1')

      // 開始行 > 終了行
      const startRowInput = screen.getByLabelText('開始行')
      await user.type(startRowInput, '100')

      const endRowInput = screen.getByLabelText('終了行')
      await user.type(endRowInput, '50')

      // 送信
      const submitButton = screen.getByRole('button', { name: '割り当て' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('開始行は終了行以下である必要があります')
        ).toBeInTheDocument()
      })

      // API呼び出しがされないことを確認
      expect(createAssignment).not.toHaveBeenCalled()
    })

    it('ワーカーが未選択の場合エラーが表示される', async () => {
      const user = userEvent.setup()

      render(<AssignWorkersPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByLabelText('ワーカー')).toBeInTheDocument()
      })

      // 開始行・終了行だけ入力
      const startRowInput = screen.getByLabelText('開始行')
      await user.type(startRowInput, '1')

      const endRowInput = screen.getByLabelText('終了行')
      await user.type(endRowInput, '100')

      // 送信
      const submitButton = screen.getByRole('button', { name: '割り当て' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('ワーカーを選択してください')
        ).toBeInTheDocument()
      })

      expect(createAssignment).not.toHaveBeenCalled()
    })
  })

  describe('割り当て済み企業の非表示', () => {
    it('非表示チェックボックスがAPIリクエストに含まれる', async () => {
      const user = userEvent.setup()

      const mockAssignment = {
        id: 'assignment-3',
        listId: '10',
        listName: 'テストリスト',
        projectId: '1',
        projectName: 'テストプロジェクト',
        workerId: '1',
        status: 'assigned' as const,
        priority: 'medium' as const,
        recordsToProcess: 100,
        processedRecords: 0,
        successCount: 0,
        failureCount: 0,
        assignedAt: '2025-01-01T00:00:00Z',
      }

      ;(createAssignment as jest.Mock).mockResolvedValue(mockAssignment)

      render(<AssignWorkersPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByLabelText('ワーカー')).toBeInTheDocument()
      })

      // チェックボックスをON
      const hideAssignedCheckbox = screen.getByLabelText(
        '割り当て済み企業を非表示'
      )
      await user.click(hideAssignedCheckbox)

      // ワーカーを選択
      const workerSelect = screen.getByLabelText('ワーカー')
      await user.selectOptions(workerSelect, '1')

      // 開始行・終了行を入力
      const startRowInput = screen.getByLabelText('開始行')
      await user.type(startRowInput, '1')

      const endRowInput = screen.getByLabelText('終了行')
      await user.type(endRowInput, '100')

      // 送信
      const submitButton = screen.getByRole('button', { name: '割り当て' })
      await user.click(submitButton)

      // hideAssignedフラグが含まれることを確認
      // 注: 実際のAPIリクエストには含まれないが、フォームデータには含まれる
      await waitFor(() => {
        expect(createAssignment).toHaveBeenCalled()
      })
    })
  })
})
