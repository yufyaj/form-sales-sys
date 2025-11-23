import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import NoSendReasonSelector from '@/components/features/noSendSettings/NoSendReasonSelector'
import { NoSendReason } from '@/types/noSendReason'

// テスト用の送信不可理由データ
const mockReasons: NoSendReason[] = [
  { id: 'invalid-email', label: 'メールアドレスが無効', isDefault: true },
  { id: 'bounced', label: 'バウンス履歴あり', isDefault: true },
  { id: 'unsubscribed', label: '配信停止済み', isDefault: true },
  { id: 'custom-1', label: 'カスタム理由1', isDefault: false },
]

describe('NoSendReasonSelector', () => {
  it('全ての理由がチェックボックスとしてレンダリングされる', () => {
    render(
      <NoSendReasonSelector
        reasons={mockReasons}
        value={[]}
        onChange={jest.fn()}
      />
    )

    expect(
      screen.getByRole('checkbox', { name: 'メールアドレスが無効' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('checkbox', { name: 'バウンス履歴あり' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('checkbox', { name: '配信停止済み' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('checkbox', { name: 'カスタム理由1' })
    ).toBeInTheDocument()
  })

  it('選択された理由がチェックされる', () => {
    render(
      <NoSendReasonSelector
        reasons={mockReasons}
        value={['invalid-email', 'bounced']}
        onChange={jest.fn()}
      />
    )

    const invalidEmailCheckbox = screen.getByRole('checkbox', {
      name: 'メールアドレスが無効',
    })
    const bouncedCheckbox = screen.getByRole('checkbox', {
      name: 'バウンス履歴あり',
    })
    const unsubscribedCheckbox = screen.getByRole('checkbox', {
      name: '配信停止済み',
    })

    expect(invalidEmailCheckbox).toBeChecked()
    expect(bouncedCheckbox).toBeChecked()
    expect(unsubscribedCheckbox).not.toBeChecked()
  })

  it('チェックボックスをクリックすると選択状態が変更される', async () => {
    const user = userEvent.setup()
    const handleChange = jest.fn()

    render(
      <NoSendReasonSelector
        reasons={mockReasons}
        value={[]}
        onChange={handleChange}
      />
    )

    const invalidEmailCheckbox = screen.getByRole('checkbox', {
      name: 'メールアドレスが無効',
    })

    // チェックボックスを選択
    await user.click(invalidEmailCheckbox)

    expect(handleChange).toHaveBeenCalledWith(['invalid-email'])
  })

  it('選択済みのチェックボックスをクリックすると選択解除される', async () => {
    const user = userEvent.setup()
    const handleChange = jest.fn()

    render(
      <NoSendReasonSelector
        reasons={mockReasons}
        value={['invalid-email', 'bounced']}
        onChange={handleChange}
      />
    )

    const invalidEmailCheckbox = screen.getByRole('checkbox', {
      name: 'メールアドレスが無効',
    })

    // 選択済みのチェックボックスをクリックして選択解除
    await user.click(invalidEmailCheckbox)

    expect(handleChange).toHaveBeenCalledWith(['bounced'])
  })

  it('複数の理由を選択できる', async () => {
    const user = userEvent.setup()
    const handleChange = jest.fn()

    render(
      <NoSendReasonSelector
        reasons={mockReasons}
        value={['invalid-email']}
        onChange={handleChange}
      />
    )

    const bouncedCheckbox = screen.getByRole('checkbox', {
      name: 'バウンス履歴あり',
    })

    // 2つ目の理由を選択
    await user.click(bouncedCheckbox)

    expect(handleChange).toHaveBeenCalledWith(['invalid-email', 'bounced'])
  })

  it('ラベルが表示される', () => {
    render(
      <NoSendReasonSelector
        reasons={mockReasons}
        value={[]}
        onChange={jest.fn()}
        label="送信不可理由を選択"
      />
    )

    expect(screen.getByText('送信不可理由を選択')).toBeInTheDocument()
  })

  it('エラーメッセージが表示される', () => {
    render(
      <NoSendReasonSelector
        reasons={mockReasons}
        value={[]}
        onChange={jest.fn()}
        error="少なくとも1つの理由を選択してください"
      />
    )

    expect(screen.getByRole('alert')).toHaveTextContent(
      '少なくとも1つの理由を選択してください'
    )
  })

  it('無効化状態のときチェックボックスがクリックできない', async () => {
    const user = userEvent.setup()
    const handleChange = jest.fn()

    render(
      <NoSendReasonSelector
        reasons={mockReasons}
        value={[]}
        onChange={handleChange}
        disabled
      />
    )

    const invalidEmailCheckbox = screen.getByRole('checkbox', {
      name: 'メールアドレスが無効',
    })

    expect(invalidEmailCheckbox).toBeDisabled()

    await user.click(invalidEmailCheckbox)

    // disabledなのでonChangeは呼ばれない
    expect(handleChange).not.toHaveBeenCalled()
  })

  it('全選択が機能する', async () => {
    const user = userEvent.setup()
    const handleChange = jest.fn()

    render(
      <NoSendReasonSelector
        reasons={mockReasons}
        value={[]}
        onChange={handleChange}
        showSelectAll
      />
    )

    const selectAllButton = screen.getByRole('button', { name: '全て選択' })

    await user.click(selectAllButton)

    expect(handleChange).toHaveBeenCalledWith([
      'invalid-email',
      'bounced',
      'unsubscribed',
      'custom-1',
    ])
  })

  it('全解除が機能する', async () => {
    const user = userEvent.setup()
    const handleChange = jest.fn()

    render(
      <NoSendReasonSelector
        reasons={mockReasons}
        value={['invalid-email', 'bounced']}
        onChange={handleChange}
        showSelectAll
      />
    )

    const clearAllButton = screen.getByRole('button', { name: '全て解除' })

    await user.click(clearAllButton)

    expect(handleChange).toHaveBeenCalledWith([])
  })

  it('デフォルト理由とカスタム理由が区別して表示される', () => {
    render(
      <NoSendReasonSelector
        reasons={mockReasons}
        value={[]}
        onChange={jest.fn()}
      />
    )

    // デフォルト理由のセクションが存在する
    expect(screen.getByText('デフォルト理由')).toBeInTheDocument()

    // カスタム理由のセクションが存在する
    expect(screen.getByText('カスタム理由')).toBeInTheDocument()
  })

  it('カスタム理由が存在しない場合はセクションを表示しない', () => {
    const defaultReasonsOnly = mockReasons.filter((r) => r.isDefault)

    render(
      <NoSendReasonSelector
        reasons={defaultReasonsOnly}
        value={[]}
        onChange={jest.fn()}
      />
    )

    // デフォルト理由のセクションは存在する
    expect(screen.getByText('デフォルト理由')).toBeInTheDocument()

    // カスタム理由のセクションは存在しない
    expect(screen.queryByText('カスタム理由')).not.toBeInTheDocument()
  })
})
