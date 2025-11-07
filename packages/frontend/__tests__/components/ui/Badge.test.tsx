import { render, screen } from '@testing-library/react'
import Badge from '@/components/ui/Badge'

describe('Badge', () => {
  // Arrange-Act-Assert パターンに従う

  it('デフォルトバリアントでレンダリングされる', () => {
    // Arrange & Act
    render(<Badge>テストバッジ</Badge>)

    // Assert
    const badge = screen.getByText('テストバッジ')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('bg-gray-100', 'text-gray-800')
  })

  it('成功バリアントが正しく表示される', () => {
    // Arrange & Act
    render(<Badge variant="success">成功</Badge>)

    // Assert
    const badge = screen.getByText('成功')
    expect(badge).toHaveClass('bg-green-100', 'text-green-800')
  })

  it('警告バリアントが正しく表示される', () => {
    // Arrange & Act
    render(<Badge variant="warning">警告</Badge>)

    // Assert
    const badge = screen.getByText('警告')
    expect(badge).toHaveClass('bg-yellow-100', 'text-yellow-800')
  })

  it('危険バリアントが正しく表示される', () => {
    // Arrange & Act
    render(<Badge variant="danger">エラー</Badge>)

    // Assert
    const badge = screen.getByText('エラー')
    expect(badge).toHaveClass('bg-red-100', 'text-red-800')
  })

  it('情報バリアントが正しく表示される', () => {
    // Arrange & Act
    render(<Badge variant="info">情報</Badge>)

    // Assert
    const badge = screen.getByText('情報')
    expect(badge).toHaveClass('bg-blue-100', 'text-blue-800')
  })

  it('小サイズが正しく表示される', () => {
    // Arrange & Act
    render(<Badge size="sm">小</Badge>)

    // Assert
    const badge = screen.getByText('小')
    expect(badge).toHaveClass('px-2', 'py-0.5', 'text-xs')
  })

  it('中サイズが正しく表示される', () => {
    // Arrange & Act
    render(<Badge size="md">中</Badge>)

    // Assert
    const badge = screen.getByText('中')
    expect(badge).toHaveClass('px-2.5', 'py-1', 'text-sm')
  })

  it('大サイズが正しく表示される', () => {
    // Arrange & Act
    render(<Badge size="lg">大</Badge>)

    // Assert
    const badge = screen.getByText('大')
    expect(badge).toHaveClass('px-3', 'py-1.5', 'text-base')
  })

  it('子要素を正しくレンダリングする', () => {
    // Arrange & Act
    render(
      <Badge>
        <span>複雑な</span>
        <strong>コンテンツ</strong>
      </Badge>
    )

    // Assert
    expect(screen.getByText('複雑な')).toBeInTheDocument()
    expect(screen.getByText('コンテンツ')).toBeInTheDocument()
  })
})
