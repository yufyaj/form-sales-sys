import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Select from '@/components/ui/Select'

describe('Select', () => {
  const mockOptions = [
    { value: 1, label: '株式会社A' },
    { value: 2, label: '株式会社B' },
    { value: 3, label: '株式会社C' },
  ]

  it('ラベル付きでレンダリングされる', () => {
    render(<Select label="顧客企業" options={mockOptions} />)

    expect(screen.getByLabelText('顧客企業')).toBeInTheDocument()
  })

  it('プレースホルダーが表示される', () => {
    render(
      <Select
        label="顧客企業"
        options={mockOptions}
        placeholder="顧客企業を選択してください"
      />
    )

    expect(screen.getByText('顧客企業を選択してください')).toBeInTheDocument()
  })

  it('オプションが全て表示される', () => {
    render(<Select label="顧客企業" options={mockOptions} />)

    expect(screen.getByText('株式会社A')).toBeInTheDocument()
    expect(screen.getByText('株式会社B')).toBeInTheDocument()
    expect(screen.getByText('株式会社C')).toBeInTheDocument()
  })

  it('ユーザーが選択肢を変更できる', async () => {
    const user = userEvent.setup()
    const handleChange = jest.fn()

    render(
      <Select
        label="顧客企業"
        options={mockOptions}
        onChange={handleChange}
      />
    )

    const select = screen.getByLabelText('顧客企業')

    await user.selectOptions(select, '2')

    expect(handleChange).toHaveBeenCalled()
  })

  it('エラーメッセージが表示される', () => {
    render(
      <Select
        label="顧客企業"
        options={mockOptions}
        error="顧客企業を選択してください"
      />
    )

    expect(screen.getByRole('alert')).toHaveTextContent(
      '顧客企業を選択してください'
    )
  })

  it('disabledプロパティが機能する', () => {
    render(<Select label="顧客企業" options={mockOptions} disabled />)

    expect(screen.getByLabelText('顧客企業')).toBeDisabled()
  })

  it('valueプロパティが機能する', () => {
    render(<Select label="顧客企業" options={mockOptions} value={2} />)

    const select = screen.getByLabelText('顧客企業') as HTMLSelectElement
    expect(select.value).toBe('2')
  })

  it('aria属性が正しく設定される', () => {
    render(
      <Select
        label="顧客企業"
        options={mockOptions}
        error="エラーメッセージ"
      />
    )

    const select = screen.getByLabelText('顧客企業')
    expect(select).toHaveAttribute('aria-invalid', 'true')
    expect(select).toHaveAttribute('aria-describedby')
  })
})
