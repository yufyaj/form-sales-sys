import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import TimeRangeInput from '@/components/features/noSendSettings/TimeRangeInput'

describe('TimeRangeInput', () => {
  it('開始時刻と終了時刻の入力フィールドがレンダリングされる', () => {
    render(
      <TimeRangeInput
        timeStart=""
        timeEnd=""
        onTimeStartChange={jest.fn()}
        onTimeEndChange={jest.fn()}
      />
    )

    expect(screen.getByLabelText('開始時刻')).toBeInTheDocument()
    expect(screen.getByLabelText('終了時刻')).toBeInTheDocument()
  })

  it('ラベルが表示される', () => {
    render(
      <TimeRangeInput
        label="送信禁止時間帯"
        timeStart=""
        timeEnd=""
        onTimeStartChange={jest.fn()}
        onTimeEndChange={jest.fn()}
      />
    )

    expect(screen.getByText('送信禁止時間帯')).toBeInTheDocument()
  })

  it('時刻を入力できる', async () => {
    const user = userEvent.setup()
    const handleTimeStartChange = jest.fn()
    const handleTimeEndChange = jest.fn()

    render(
      <TimeRangeInput
        timeStart=""
        timeEnd=""
        onTimeStartChange={handleTimeStartChange}
        onTimeEndChange={handleTimeEndChange}
      />
    )

    const startInput = screen.getByLabelText('開始時刻')
    const endInput = screen.getByLabelText('終了時刻')

    await user.type(startInput, '09:00')
    await user.type(endInput, '18:00')

    expect(handleTimeStartChange).toHaveBeenCalled()
    expect(handleTimeEndChange).toHaveBeenCalled()
  })

  it('プレースホルダーが表示される', () => {
    render(
      <TimeRangeInput
        timeStart=""
        timeEnd=""
        onTimeStartChange={jest.fn()}
        onTimeEndChange={jest.fn()}
        placeholderStart="開始時刻を入力"
        placeholderEnd="終了時刻を入力"
      />
    )

    expect(screen.getByPlaceholderText('開始時刻を入力')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('終了時刻を入力')).toBeInTheDocument()
  })

  it('valueが正しく表示される', () => {
    render(
      <TimeRangeInput
        timeStart="09:00"
        timeEnd="18:00"
        onTimeStartChange={jest.fn()}
        onTimeEndChange={jest.fn()}
      />
    )

    const startInput = screen.getByLabelText('開始時刻') as HTMLInputElement
    const endInput = screen.getByLabelText('終了時刻') as HTMLInputElement

    expect(startInput.value).toBe('09:00')
    expect(endInput.value).toBe('18:00')
  })

  it('エラーメッセージが表示される', () => {
    render(
      <TimeRangeInput
        timeStart=""
        timeEnd=""
        onTimeStartChange={jest.fn()}
        onTimeEndChange={jest.fn()}
        error="時間帯を入力してください"
      />
    )

    expect(screen.getByRole('alert')).toHaveTextContent(
      '時間帯を入力してください'
    )
  })

  it('無効化状態のとき入力できない', async () => {
    const user = userEvent.setup()
    const handleTimeStartChange = jest.fn()

    render(
      <TimeRangeInput
        timeStart=""
        timeEnd=""
        onTimeStartChange={handleTimeStartChange}
        onTimeEndChange={jest.fn()}
        disabled
      />
    )

    const startInput = screen.getByLabelText('開始時刻')

    expect(startInput).toBeDisabled()

    await user.type(startInput, '09:00')

    // disabledなのでonChangeは呼ばれない
    expect(handleTimeStartChange).not.toHaveBeenCalled()
  })

  it('説明文が表示される', () => {
    render(
      <TimeRangeInput
        timeStart=""
        timeEnd=""
        onTimeStartChange={jest.fn()}
        onTimeEndChange={jest.fn()}
        description="22:00から翌朝8:00まで送信を禁止します"
      />
    )

    expect(
      screen.getByText('22:00から翌朝8:00まで送信を禁止します')
    ).toBeInTheDocument()
  })

  it('aria属性が正しく設定される', () => {
    render(
      <TimeRangeInput
        timeStart=""
        timeEnd=""
        onTimeStartChange={jest.fn()}
        onTimeEndChange={jest.fn()}
        error="エラーメッセージ"
      />
    )

    const startInput = screen.getByLabelText('開始時刻')
    const endInput = screen.getByLabelText('終了時刻')

    expect(startInput).toHaveAttribute('aria-invalid', 'true')
    expect(endInput).toHaveAttribute('aria-invalid', 'true')
  })

  it('秒付きの時刻フォーマット(HH:MM:SS)をサポートする', () => {
    render(
      <TimeRangeInput
        timeStart="09:00:00"
        timeEnd="18:00:00"
        onTimeStartChange={jest.fn()}
        onTimeEndChange={jest.fn()}
        showSeconds
      />
    )

    const startInput = screen.getByLabelText('開始時刻') as HTMLInputElement
    const endInput = screen.getByLabelText('終了時刻') as HTMLInputElement

    expect(startInput.value).toBe('09:00:00')
    expect(endInput.value).toBe('18:00:00')
  })
})
