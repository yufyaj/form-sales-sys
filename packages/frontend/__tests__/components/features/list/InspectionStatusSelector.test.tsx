import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import InspectionStatusSelector from '@/components/features/list/InspectionStatusSelector'
import type { InspectionStatus } from '@/types/list'

describe('InspectionStatusSelector', () => {
  const defaultProps = {
    currentStatus: 'not_started' as InspectionStatus,
    onChange: jest.fn(),
    disabled: false,
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('レンダリング', () => {
    it('セレクトボックスが正しくレンダリングされる', () => {
      render(<InspectionStatusSelector {...defaultProps} />)

      expect(screen.getByLabelText('検収ステータス')).toBeInTheDocument()
      expect(screen.getByRole('combobox')).toBeInTheDocument()
    })

    it('現在のステータスが選択されている', () => {
      render(<InspectionStatusSelector {...defaultProps} currentStatus="in_progress" />)

      const select = screen.getByRole('combobox') as HTMLSelectElement
      expect(select.value).toBe('in_progress')
    })

    it('全てのステータスオプションが表示される', () => {
      render(<InspectionStatusSelector {...defaultProps} />)

      const select = screen.getByRole('combobox')
      const options = Array.from(select.querySelectorAll('option'))

      expect(options).toHaveLength(4)
      expect(options.map((o) => o.value)).toEqual([
        'not_started',
        'in_progress',
        'completed',
        'rejected',
      ])
      expect(options.map((o) => o.textContent)).toEqual([
        '未検収',
        '検収中',
        '検収完了',
        '却下',
      ])
    })
  })

  describe('状態変更', () => {
    it('ステータスを変更できる', async () => {
      const user = userEvent.setup()
      const mockOnChange = jest.fn()

      render(<InspectionStatusSelector {...defaultProps} onChange={mockOnChange} />)

      const select = screen.getByRole('combobox')
      await user.selectOptions(select, 'completed')

      expect(mockOnChange).toHaveBeenCalledWith('completed')
    })

    it('複数回ステータスを変更できる', async () => {
      const user = userEvent.setup()
      const mockOnChange = jest.fn()

      render(<InspectionStatusSelector {...defaultProps} onChange={mockOnChange} />)

      const select = screen.getByRole('combobox')

      await user.selectOptions(select, 'in_progress')
      expect(mockOnChange).toHaveBeenNthCalledWith(1, 'in_progress')

      await user.selectOptions(select, 'completed')
      expect(mockOnChange).toHaveBeenNthCalledWith(2, 'completed')

      await user.selectOptions(select, 'rejected')
      expect(mockOnChange).toHaveBeenNthCalledWith(3, 'rejected')

      expect(mockOnChange).toHaveBeenCalledTimes(3)
    })
  })

  describe('無効化状態', () => {
    it('disabled時はセレクトボックスが無効化される', () => {
      render(<InspectionStatusSelector {...defaultProps} disabled={true} />)

      const select = screen.getByRole('combobox')
      expect(select).toBeDisabled()
    })

    it('disabled時は変更できない', async () => {
      const user = userEvent.setup()
      const mockOnChange = jest.fn()

      render(
        <InspectionStatusSelector
          {...defaultProps}
          disabled={true}
          onChange={mockOnChange}
        />
      )

      const select = screen.getByRole('combobox')

      // disabled状態でも操作を試みる
      await user.selectOptions(select, 'completed').catch(() => {
        // エラーは無視
      })

      // onChangeは呼ばれない
      expect(mockOnChange).not.toHaveBeenCalled()
    })
  })

  describe('アクセシビリティ', () => {
    it('ラベルとセレクトボックスが関連付けられている', () => {
      render(<InspectionStatusSelector {...defaultProps} />)

      const label = screen.getByText('検収ステータス')
      const select = screen.getByRole('combobox')

      expect(label).toHaveAttribute('for', select.id)
    })

    it('aria-labelが設定されている', () => {
      render(<InspectionStatusSelector {...defaultProps} />)

      const select = screen.getByRole('combobox')
      expect(select).toHaveAttribute('aria-label', '検収ステータスを変更')
    })
  })
})
