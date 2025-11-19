import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useRouter } from 'next/navigation'
import ListForm from '@/components/features/list/ListForm'

// Next.jsのuseRouterをモック
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

const mockRouter = {
  push: jest.fn(),
  back: jest.fn(),
  refresh: jest.fn(),
}

describe('ListForm', () => {
  const projectId = 1

  beforeEach(() => {
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
    jest.clearAllMocks()
  })

  describe('フォームのレンダリング', () => {
    it('全てのフィールドが表示される', () => {
      const mockOnSubmit = jest.fn()
      render(
        <ListForm
          projectId={projectId}
          onSubmit={mockOnSubmit}
        />
      )

      expect(screen.getByLabelText('リスト名')).toBeInTheDocument()
      expect(screen.getByLabelText('説明（任意）')).toBeInTheDocument()
    })

    it('新規作成モードで適切なボタンが表示される', () => {
      const mockOnSubmit = jest.fn()
      render(
        <ListForm
          projectId={projectId}
          onSubmit={mockOnSubmit}
          isEditMode={false}
        />
      )

      expect(
        screen.getByRole('button', { name: 'リストを作成' })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'キャンセル' })
      ).toBeInTheDocument()
    })

    it('編集モードで適切なボタンが表示される', () => {
      const mockOnSubmit = jest.fn()
      render(
        <ListForm
          projectId={projectId}
          onSubmit={mockOnSubmit}
          isEditMode={true}
        />
      )

      expect(
        screen.getByRole('button', { name: 'リストを更新' })
      ).toBeInTheDocument()
    })

    it('デフォルト値が設定される', () => {
      const mockOnSubmit = jest.fn()
      const defaultValues = {
        name: 'テストリスト',
        description: 'テスト説明',
      }

      render(
        <ListForm
          projectId={projectId}
          onSubmit={mockOnSubmit}
          defaultValues={defaultValues}
          isEditMode={true}
        />
      )

      expect(screen.getByLabelText('リスト名')).toHaveValue('テストリスト')
      expect(screen.getByLabelText('説明（任意）')).toHaveValue('テスト説明')
    })
  })

  describe('バリデーション', () => {
    it('リスト名が空の場合エラーが表示される', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn()

      render(
        <ListForm
          projectId={projectId}
          onSubmit={mockOnSubmit}
        />
      )

      const submitButton = screen.getByRole('button', {
        name: 'リストを作成',
      })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('リスト名を入力してください')
        ).toBeInTheDocument()
      })

      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    it('リスト名が255文字を超える場合エラーが表示される', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn()

      render(
        <ListForm
          projectId={projectId}
          onSubmit={mockOnSubmit}
        />
      )

      const nameInput = screen.getByLabelText('リスト名')
      const longName = 'あ'.repeat(256)
      await user.type(nameInput, longName)

      const submitButton = screen.getByRole('button', {
        name: 'リストを作成',
      })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('リスト名は255文字以内で入力してください')
        ).toBeInTheDocument()
      })

      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    it('説明が5000文字を超える場合エラーが表示される', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn()

      render(
        <ListForm
          projectId={projectId}
          onSubmit={mockOnSubmit}
        />
      )

      const nameInput = screen.getByLabelText('リスト名')
      await user.type(nameInput, 'テストリスト')

      const descriptionInput = screen.getByLabelText('説明（任意）')
      const longDescription = 'あ'.repeat(5001)
      await user.type(descriptionInput, longDescription)

      const submitButton = screen.getByRole('button', {
        name: 'リストを作成',
      })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('説明は5000文字以内で入力してください')
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
        <ListForm
          projectId={projectId}
          onSubmit={mockOnSubmit}
        />
      )

      const nameInput = screen.getByLabelText('リスト名')
      await user.type(nameInput, 'テストリスト')

      const descriptionInput = screen.getByLabelText('説明（任意）')
      await user.type(descriptionInput, 'テスト説明')

      const submitButton = screen.getByRole('button', {
        name: 'リストを作成',
      })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            name: 'テストリスト',
            description: 'テスト説明',
          })
        )
      })

      // 成功時は一覧画面にリダイレクト
      expect(mockRouter.push).toHaveBeenCalledWith('/projects/1/lists')
      expect(mockRouter.refresh).toHaveBeenCalled()
    })

    it('説明が空でもフォームが送信される', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn().mockResolvedValue(undefined)

      render(
        <ListForm
          projectId={projectId}
          onSubmit={mockOnSubmit}
        />
      )

      const nameInput = screen.getByLabelText('リスト名')
      await user.type(nameInput, 'テストリスト')

      const submitButton = screen.getByRole('button', {
        name: 'リストを作成',
      })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            name: 'テストリスト',
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
        <ListForm
          projectId={projectId}
          onSubmit={mockOnSubmit}
        />
      )

      const nameInput = screen.getByLabelText('リスト名')
      await user.type(nameInput, 'テストリスト')

      const submitButton = screen.getByRole('button', {
        name: 'リストを作成',
      })
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
        <ListForm
          projectId={projectId}
          onSubmit={mockOnSubmit}
        />
      )

      const nameInput = screen.getByLabelText('リスト名')
      await user.type(nameInput, 'テストリスト')

      const submitButton = screen.getByRole('button', {
        name: 'リストを作成',
      })
      await user.click(submitButton)

      // 送信中はボタンが無効化される
      expect(submitButton).toBeDisabled()
      expect(screen.getByText('作成中...')).toBeInTheDocument()

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
        <ListForm
          projectId={projectId}
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
        <ListForm
          projectId={projectId}
          onSubmit={mockOnSubmit}
        />
      )

      const cancelButton = screen.getByRole('button', { name: 'キャンセル' })
      await user.click(cancelButton)

      expect(mockRouter.back).toHaveBeenCalled()
    })
  })
})
