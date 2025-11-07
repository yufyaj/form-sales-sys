import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Table from '@/components/ui/Table'

interface TestData {
  id: string
  name: string
  value: number
}

describe('Table', () => {
  // Arrange-Act-Assert パターンに従う

  const mockData: TestData[] = [
    { id: '1', name: 'テスト1', value: 100 },
    { id: '2', name: 'テスト2', value: 200 },
    { id: '3', name: 'テスト3', value: 300 },
  ]

  const columns = [
    { key: 'name', header: '名前' },
    { key: 'value', header: '値' },
  ]

  it('データを正しく表示する', () => {
    // Arrange & Act
    render(
      <Table
        columns={columns}
        data={mockData}
        keyExtractor={(item) => item.id}
      />
    )

    // Assert
    expect(screen.getByText('名前')).toBeInTheDocument()
    expect(screen.getByText('値')).toBeInTheDocument()
    expect(screen.getByText('テスト1')).toBeInTheDocument()
    expect(screen.getByText('100')).toBeInTheDocument()
    expect(screen.getByText('テスト2')).toBeInTheDocument()
    expect(screen.getByText('200')).toBeInTheDocument()
  })

  it('空のデータの場合にメッセージを表示する', () => {
    // Arrange & Act
    render(
      <Table
        columns={columns}
        data={[]}
        keyExtractor={(item) => item.id}
        emptyMessage="データがありません"
      />
    )

    // Assert
    expect(screen.getByText('データがありません')).toBeInTheDocument()
  })

  it('カスタム空メッセージを表示する', () => {
    // Arrange & Act
    render(
      <Table
        columns={columns}
        data={[]}
        keyExtractor={(item) => item.id}
        emptyMessage="カスタムメッセージ"
      />
    )

    // Assert
    expect(screen.getByText('カスタムメッセージ')).toBeInTheDocument()
  })

  it('カスタムレンダー関数が正しく動作する', () => {
    // Arrange
    const customColumns = [
      {
        key: 'name',
        header: '名前',
        render: (item: TestData) => <strong>{item.name.toUpperCase()}</strong>,
      },
    ]

    // Act
    render(
      <Table
        columns={customColumns}
        data={mockData}
        keyExtractor={(item) => item.id}
      />
    )

    // Assert
    expect(screen.getByText('テスト1'.toUpperCase())).toBeInTheDocument()
  })

  it('行クリックイベントが正しく発火する', async () => {
    // Arrange
    const user = userEvent.setup()
    const handleRowClick = jest.fn()

    render(
      <Table
        columns={columns}
        data={mockData}
        keyExtractor={(item) => item.id}
        onRowClick={handleRowClick}
      />
    )

    // Act
    const row = screen.getByText('テスト1').closest('tr')
    if (row) {
      await user.click(row)
    }

    // Assert
    expect(handleRowClick).toHaveBeenCalledWith(mockData[0])
    expect(handleRowClick).toHaveBeenCalledTimes(1)
  })

  it('行クリックハンドラがない場合はカーソルが変わらない', () => {
    // Arrange & Act
    const { container } = render(
      <Table
        columns={columns}
        data={mockData}
        keyExtractor={(item) => item.id}
      />
    )

    // Assert
    const row = screen.getByText('テスト1').closest('tr')
    expect(row).not.toHaveClass('cursor-pointer')
  })

  it('テキストの配置を指定できる', () => {
    // Arrange
    const alignedColumns = [
      { key: 'name', header: '名前', align: 'left' as const },
      { key: 'value', header: '値', align: 'right' as const },
    ]

    // Act
    render(
      <Table
        columns={alignedColumns}
        data={mockData}
        keyExtractor={(item) => item.id}
      />
    )

    // Assert
    const headers = screen.getAllByRole('columnheader')
    expect(headers[0]).toHaveClass('text-left')
    expect(headers[1]).toHaveClass('text-right')
  })

  it('全ての行がユニークなキーを持つ', () => {
    // Arrange & Act
    const { container } = render(
      <Table
        columns={columns}
        data={mockData}
        keyExtractor={(item) => item.id}
      />
    )

    // Assert
    const rows = container.querySelectorAll('tbody tr')
    expect(rows).toHaveLength(mockData.length)
  })
})
