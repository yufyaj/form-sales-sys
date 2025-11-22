import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import DayOfWeekSelector from '@/components/features/noSendSettings/DayOfWeekSelector'
import { DayOfWeek } from '@/types/noSendSetting'

describe('DayOfWeekSelector', () => {
  it('全ての曜日ボタンがレンダリングされる', () => {
    render(<DayOfWeekSelector value={[]} onChange={jest.fn()} />)

    expect(screen.getByRole('button', { name: '月' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '火' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '水' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '木' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '金' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '土' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '日' })).toBeInTheDocument()
  })

  it('選択された曜日が強調表示される', () => {
    render(
      <DayOfWeekSelector
        value={[DayOfWeek.SATURDAY, DayOfWeek.SUNDAY]}
        onChange={jest.fn()}
      />
    )

    const saturdayButton = screen.getByRole('button', { name: '土' })
    const sundayButton = screen.getByRole('button', { name: '日' })
    const mondayButton = screen.getByRole('button', { name: '月' })

    // 選択された曜日はaria-pressed="true"
    expect(saturdayButton).toHaveAttribute('aria-pressed', 'true')
    expect(sundayButton).toHaveAttribute('aria-pressed', 'true')

    // 選択されていない曜日はaria-pressed="false"
    expect(mondayButton).toHaveAttribute('aria-pressed', 'false')
  })

  it('曜日ボタンをクリックすると選択状態がトグルされる', async () => {
    const user = userEvent.setup()
    const handleChange = jest.fn()

    render(<DayOfWeekSelector value={[]} onChange={handleChange} />)

    const mondayButton = screen.getByRole('button', { name: '月' })

    // 曜日を選択
    await user.click(mondayButton)

    expect(handleChange).toHaveBeenCalledWith([DayOfWeek.MONDAY])
  })

  it('選択済みの曜日ボタンをクリックすると選択解除される', async () => {
    const user = userEvent.setup()
    const handleChange = jest.fn()

    render(
      <DayOfWeekSelector
        value={[DayOfWeek.MONDAY, DayOfWeek.FRIDAY]}
        onChange={handleChange}
      />
    )

    const mondayButton = screen.getByRole('button', { name: '月' })

    // 選択済みの曜日をクリックして選択解除
    await user.click(mondayButton)

    expect(handleChange).toHaveBeenCalledWith([DayOfWeek.FRIDAY])
  })

  it('複数の曜日を選択できる', async () => {
    const user = userEvent.setup()
    const handleChange = jest.fn()

    render(
      <DayOfWeekSelector
        value={[DayOfWeek.MONDAY]}
        onChange={handleChange}
      />
    )

    const tuesdayButton = screen.getByRole('button', { name: '火' })

    // 2つ目の曜日を選択
    await user.click(tuesdayButton)

    expect(handleChange).toHaveBeenCalledWith([
      DayOfWeek.MONDAY,
      DayOfWeek.TUESDAY,
    ])
  })

  it('ラベルが表示される', () => {
    render(
      <DayOfWeekSelector
        label="送信禁止曜日"
        value={[]}
        onChange={jest.fn()}
      />
    )

    expect(screen.getByText('送信禁止曜日')).toBeInTheDocument()
  })

  it('エラーメッセージが表示される', () => {
    render(
      <DayOfWeekSelector
        value={[]}
        onChange={jest.fn()}
        error="少なくとも1つの曜日を選択してください"
      />
    )

    expect(screen.getByRole('alert')).toHaveTextContent(
      '少なくとも1つの曜日を選択してください'
    )
  })

  it('無効化状態のときボタンがクリックできない', async () => {
    const user = userEvent.setup()
    const handleChange = jest.fn()

    render(<DayOfWeekSelector value={[]} onChange={handleChange} disabled />)

    const mondayButton = screen.getByRole('button', { name: '月' })

    expect(mondayButton).toBeDisabled()

    await user.click(mondayButton)

    // disabledなのでonChangeは呼ばれない
    expect(handleChange).not.toHaveBeenCalled()
  })

  it('全曜日選択が機能する', async () => {
    const user = userEvent.setup()
    const handleChange = jest.fn()

    render(
      <DayOfWeekSelector value={[]} onChange={handleChange} showSelectAll />
    )

    const selectAllButton = screen.getByRole('button', { name: '全て選択' })

    await user.click(selectAllButton)

    expect(handleChange).toHaveBeenCalledWith([
      DayOfWeek.MONDAY,
      DayOfWeek.TUESDAY,
      DayOfWeek.WEDNESDAY,
      DayOfWeek.THURSDAY,
      DayOfWeek.FRIDAY,
      DayOfWeek.SATURDAY,
      DayOfWeek.SUNDAY,
    ])
  })

  it('全解除が機能する', async () => {
    const user = userEvent.setup()
    const handleChange = jest.fn()

    render(
      <DayOfWeekSelector
        value={[DayOfWeek.MONDAY, DayOfWeek.TUESDAY]}
        onChange={handleChange}
        showSelectAll
      />
    )

    const clearAllButton = screen.getByRole('button', { name: '全て解除' })

    await user.click(clearAllButton)

    expect(handleChange).toHaveBeenCalledWith([])
  })
})
