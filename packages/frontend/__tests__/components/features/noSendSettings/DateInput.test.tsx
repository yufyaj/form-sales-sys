import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import DateInput from '@/components/features/noSendSettings/DateInput'

describe('DateInput', () => {
  describe('単一日付モード', () => {
    it('日付入力フィールドがレンダリングされる', () => {
      render(<DateInput value="" onChange={jest.fn()} />)

      expect(screen.getByLabelText('日付')).toBeInTheDocument()
    })

    it('ラベルが表示される', () => {
      render(<DateInput label="送信禁止日" value="" onChange={jest.fn()} />)

      expect(screen.getByText('送信禁止日')).toBeInTheDocument()
    })

    it('日付を入力できる', async () => {
      const user = userEvent.setup()
      const handleChange = jest.fn()

      render(<DateInput value="" onChange={handleChange} />)

      const dateInput = screen.getByLabelText('日付')

      await user.type(dateInput, '2025-12-25')

      expect(handleChange).toHaveBeenCalled()
    })

    it('valueが正しく表示される', () => {
      render(<DateInput value="2025-12-25" onChange={jest.fn()} />)

      const dateInput = screen.getByLabelText('日付') as HTMLInputElement

      expect(dateInput.value).toBe('2025-12-25')
    })

    it('エラーメッセージが表示される', () => {
      render(
        <DateInput
          value=""
          onChange={jest.fn()}
          error="日付を入力してください"
        />
      )

      expect(screen.getByRole('alert')).toHaveTextContent(
        '日付を入力してください'
      )
    })

    it('無効化状態のとき入力できない', async () => {
      const user = userEvent.setup()
      const handleChange = jest.fn()

      render(<DateInput value="" onChange={handleChange} disabled />)

      const dateInput = screen.getByLabelText('日付')

      expect(dateInput).toBeDisabled()

      await user.type(dateInput, '2025-12-25')

      // disabledなのでonChangeは呼ばれない
      expect(handleChange).not.toHaveBeenCalled()
    })
  })

  describe('期間選択モード', () => {
    it('開始日と終了日の入力フィールドがレンダリングされる', () => {
      render(
        <DateInput
          mode="range"
          startDate=""
          endDate=""
          onStartDateChange={jest.fn()}
          onEndDateChange={jest.fn()}
        />
      )

      expect(screen.getByLabelText('開始日')).toBeInTheDocument()
      expect(screen.getByLabelText('終了日')).toBeInTheDocument()
    })

    it('開始日と終了日を入力できる', async () => {
      const user = userEvent.setup()
      const handleStartDateChange = jest.fn()
      const handleEndDateChange = jest.fn()

      render(
        <DateInput
          mode="range"
          startDate=""
          endDate=""
          onStartDateChange={handleStartDateChange}
          onEndDateChange={handleEndDateChange}
        />
      )

      const startInput = screen.getByLabelText('開始日')
      const endInput = screen.getByLabelText('終了日')

      await user.type(startInput, '2025-12-25')
      await user.type(endInput, '2025-12-31')

      expect(handleStartDateChange).toHaveBeenCalled()
      expect(handleEndDateChange).toHaveBeenCalled()
    })

    it('valueが正しく表示される', () => {
      render(
        <DateInput
          mode="range"
          startDate="2025-12-25"
          endDate="2025-12-31"
          onStartDateChange={jest.fn()}
          onEndDateChange={jest.fn()}
        />
      )

      const startInput = screen.getByLabelText('開始日') as HTMLInputElement
      const endInput = screen.getByLabelText('終了日') as HTMLInputElement

      expect(startInput.value).toBe('2025-12-25')
      expect(endInput.value).toBe('2025-12-31')
    })

    it('エラーメッセージが表示される', () => {
      render(
        <DateInput
          mode="range"
          startDate=""
          endDate=""
          onStartDateChange={jest.fn()}
          onEndDateChange={jest.fn()}
          error="期間を入力してください"
        />
      )

      expect(screen.getByRole('alert')).toHaveTextContent(
        '期間を入力してください'
      )
    })
  })

  it('説明文が表示される', () => {
    render(
      <DateInput
        value=""
        onChange={jest.fn()}
        description="年末年始の送信を禁止します"
      />
    )

    expect(
      screen.getByText('年末年始の送信を禁止します')
    ).toBeInTheDocument()
  })

  it('aria属性が正しく設定される', () => {
    render(<DateInput value="" onChange={jest.fn()} error="エラー" />)

    const dateInput = screen.getByLabelText('日付')

    expect(dateInput).toHaveAttribute('aria-invalid', 'true')
  })
})
