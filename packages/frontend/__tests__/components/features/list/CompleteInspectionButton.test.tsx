import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import CompleteInspectionButton from '@/components/features/list/CompleteInspectionButton'

describe('CompleteInspectionButton', () => {
  describe('基本表示', () => {
    it('検収完了ボタンを表示する', () => {
      const mockOnComplete = jest.fn()

      render(<CompleteInspectionButton onComplete={mockOnComplete} />)

      const button = screen.getByRole('button', { name: '検収完了' })
      expect(button).toBeInTheDocument()
    })

    it('無効状態で表示できる', () => {
      const mockOnComplete = jest.fn()

      render(<CompleteInspectionButton onComplete={mockOnComplete} disabled />)

      const button = screen.getByRole('button', { name: '検収完了' })
      expect(button).toBeDisabled()
    })

    it('ローディング状態で表示できる', () => {
      const mockOnComplete = jest.fn()

      render(<CompleteInspectionButton onComplete={mockOnComplete} isLoading />)

      const button = screen.getByRole('button')
      expect(button).toBeDisabled()
      // ローディングスピナーが表示されていることを確認
      expect(button.querySelector('svg')).toBeInTheDocument()
    })
  })

  describe('ボタンクリック', () => {
    it('ボタンクリック時にonCompleteが呼ばれる', async () => {
      const user = userEvent.setup()
      const mockOnComplete = jest.fn()

      render(<CompleteInspectionButton onComplete={mockOnComplete} />)

      const button = screen.getByRole('button', { name: '検収完了' })
      await user.click(button)

      expect(mockOnComplete).toHaveBeenCalledTimes(1)
    })

    it('無効状態ではonCompleteが呼ばれない', async () => {
      const user = userEvent.setup()
      const mockOnComplete = jest.fn()

      render(<CompleteInspectionButton onComplete={mockOnComplete} disabled />)

      const button = screen.getByRole('button', { name: '検収完了' })
      await user.click(button)

      expect(mockOnComplete).not.toHaveBeenCalled()
    })

    it('ローディング中はonCompleteが呼ばれない', async () => {
      const user = userEvent.setup()
      const mockOnComplete = jest.fn()

      render(<CompleteInspectionButton onComplete={mockOnComplete} isLoading />)

      const button = screen.getByRole('button')
      await user.click(button)

      expect(mockOnComplete).not.toHaveBeenCalled()
    })
  })

  describe('確認ダイアログ', () => {
    it('確認ダイアログが有効な場合、確認後にonCompleteが呼ばれる', async () => {
      const user = userEvent.setup()
      const mockOnComplete = jest.fn()

      // window.confirmのモック
      global.confirm = jest.fn(() => true)

      render(
        <CompleteInspectionButton
          onComplete={mockOnComplete}
          showConfirm
          confirmMessage="検収を完了してもよろしいですか？"
        />
      )

      const button = screen.getByRole('button', { name: '検収完了' })
      await user.click(button)

      expect(global.confirm).toHaveBeenCalledWith(
        '検収を完了してもよろしいですか？'
      )
      expect(mockOnComplete).toHaveBeenCalledTimes(1)
    })

    it('確認ダイアログでキャンセルした場合、onCompleteが呼ばれない', async () => {
      const user = userEvent.setup()
      const mockOnComplete = jest.fn()

      // window.confirmのモック（キャンセル）
      global.confirm = jest.fn(() => false)

      render(
        <CompleteInspectionButton
          onComplete={mockOnComplete}
          showConfirm
          confirmMessage="検収を完了してもよろしいですか？"
        />
      )

      const button = screen.getByRole('button', { name: '検収完了' })
      await user.click(button)

      expect(global.confirm).toHaveBeenCalledWith(
        '検収を完了してもよろしいですか？'
      )
      expect(mockOnComplete).not.toHaveBeenCalled()
    })
  })

  describe('アクセシビリティ', () => {
    it('適切なaria属性を持つ', () => {
      const mockOnComplete = jest.fn()

      render(<CompleteInspectionButton onComplete={mockOnComplete} />)

      const button = screen.getByRole('button', { name: '検収完了' })
      expect(button).toHaveAttribute('type', 'button')
    })
  })
})
