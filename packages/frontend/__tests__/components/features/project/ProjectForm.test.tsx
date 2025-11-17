import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useRouter } from 'next/navigation'
import ProjectForm from '@/components/features/project/ProjectForm'

// Next.jsのuseRouterをモック
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

const mockRouter = {
  push: jest.fn(),
  back: jest.fn(),
  refresh: jest.fn(),
}

const mockClientOrganizations = [
  { value: 1, label: '株式会社A' },
  { value: 2, label: '株式会社B' },
  { value: 3, label: '株式会社C' },
]

describe('ProjectForm', () => {
  beforeEach(() => {
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
    jest.clearAllMocks()
  })

  describe('フォームのレンダリング', () => {
    it('全てのフィールドが表示される', () => {
      const mockOnSubmit = jest.fn()
      render(
        <ProjectForm
          clientOrganizations={mockClientOrganizations}
          onSubmit={mockOnSubmit}
        />
      )

      expect(screen.getByLabelText('プロジェクト名')).toBeInTheDocument()
      expect(screen.getByLabelText('顧客企業')).toBeInTheDocument()
      expect(screen.getByLabelText('ステータス')).toBeInTheDocument()
      expect(screen.getByLabelText('開始日')).toBeInTheDocument()
      expect(screen.getByLabelText('終了日')).toBeInTheDocument()
      expect(screen.getByLabelText('説明（任意）')).toBeInTheDocument()
    })

    it('新規作成モードで適切なボタンが表示される', () => {
      const mockOnSubmit = jest.fn()
      render(
        <ProjectForm
          clientOrganizations={mockClientOrganizations}
          onSubmit={mockOnSubmit}
          isEditMode={false}
        />
      )

      expect(
        screen.getByRole('button', { name: 'プロジェクトを作成' })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'キャンセル' })
      ).toBeInTheDocument()
    })

    it('編集モードで適切なボタンが表示される', () => {
      const mockOnSubmit = jest.fn()
      render(
        <ProjectForm
          clientOrganizations={mockClientOrganizations}
          onSubmit={mockOnSubmit}
          isEditMode={true}
        />
      )

      expect(
        screen.getByRole('button', { name: 'プロジェクトを更新' })
      ).toBeInTheDocument()
    })

    it('デフォルト値が設定される', () => {
      const mockOnSubmit = jest.fn()
      const defaultValues = {
        name: 'テストプロジェクト',
        client_organization_id: 1,
        status: 'active' as const,
        start_date: '2025-04-01',
        end_date: '2025-09-30',
        description: 'テスト説明',
      }

      render(
        <ProjectForm
          clientOrganizations={mockClientOrganizations}
          onSubmit={mockOnSubmit}
          defaultValues={defaultValues}
          isEditMode={true}
        />
      )

      expect(screen.getByLabelText('プロジェクト名')).toHaveValue('テストプロジェクト')
      expect(screen.getByLabelText('説明（任意）')).toHaveValue('テスト説明')
    })
  })

  describe('バリデーション', () => {
    it('プロジェクト名が空の場合エラーが表示される', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn()

      render(
        <ProjectForm
          clientOrganizations={mockClientOrganizations}
          onSubmit={mockOnSubmit}
        />
      )

      const submitButton = screen.getByRole('button', {
        name: 'プロジェクトを作成',
      })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('プロジェクト名を入力してください')
        ).toBeInTheDocument()
      })

      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    it('顧客企業が選択されていない場合エラーが表示される', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn()

      render(
        <ProjectForm
          clientOrganizations={mockClientOrganizations}
          onSubmit={mockOnSubmit}
        />
      )

      const nameInput = screen.getByLabelText('プロジェクト名')
      await user.type(nameInput, 'テストプロジェクト')

      const submitButton = screen.getByRole('button', {
        name: 'プロジェクトを作成',
      })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('顧客企業を選択してください')
        ).toBeInTheDocument()
      })

      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    it('終了日が開始日より前の場合エラーが表示される', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn()

      render(
        <ProjectForm
          clientOrganizations={mockClientOrganizations}
          onSubmit={mockOnSubmit}
        />
      )

      const nameInput = screen.getByLabelText('プロジェクト名')
      await user.type(nameInput, 'テストプロジェクト')

      const clientSelect = screen.getByLabelText('顧客企業')
      await user.selectOptions(clientSelect, '1')

      const startDateInput = screen.getByLabelText('開始日')
      await user.type(startDateInput, '2025-09-30')

      const endDateInput = screen.getByLabelText('終了日')
      await user.type(endDateInput, '2025-04-01')

      const submitButton = screen.getByRole('button', {
        name: 'プロジェクトを作成',
      })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('終了日は開始日以降の日付を指定してください')
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
        <ProjectForm
          clientOrganizations={mockClientOrganizations}
          onSubmit={mockOnSubmit}
        />
      )

      const nameInput = screen.getByLabelText('プロジェクト名')
      await user.type(nameInput, 'テストプロジェクト')

      const clientSelect = screen.getByLabelText('顧客企業')
      await user.selectOptions(clientSelect, '1')

      const statusSelect = screen.getByLabelText('ステータス')
      await user.selectOptions(statusSelect, 'planning')

      const submitButton = screen.getByRole('button', {
        name: 'プロジェクトを作成',
      })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            name: 'テストプロジェクト',
            client_organization_id: 1,
            status: 'planning',
          })
        )
      })

      // 成功時は一覧画面にリダイレクト
      expect(mockRouter.push).toHaveBeenCalledWith('/projects')
      expect(mockRouter.refresh).toHaveBeenCalled()
    })

    it('送信エラー時にエラーメッセージが表示される', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest
        .fn()
        .mockRejectedValue(new Error('サーバーエラー'))

      render(
        <ProjectForm
          clientOrganizations={mockClientOrganizations}
          onSubmit={mockOnSubmit}
        />
      )

      const nameInput = screen.getByLabelText('プロジェクト名')
      await user.type(nameInput, 'テストプロジェクト')

      const clientSelect = screen.getByLabelText('顧客企業')
      await user.selectOptions(clientSelect, '1')

      const submitButton = screen.getByRole('button', {
        name: 'プロジェクトを作成',
      })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent('サーバーエラー')
      })
    })
  })

  describe('キャンセルボタン', () => {
    it('キャンセルボタンクリックでonCancelが呼ばれる', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn()
      const mockOnCancel = jest.fn()

      render(
        <ProjectForm
          clientOrganizations={mockClientOrganizations}
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
        <ProjectForm
          clientOrganizations={mockClientOrganizations}
          onSubmit={mockOnSubmit}
        />
      )

      const cancelButton = screen.getByRole('button', { name: 'キャンセル' })
      await user.click(cancelButton)

      expect(mockRouter.back).toHaveBeenCalled()
    })
  })
})
