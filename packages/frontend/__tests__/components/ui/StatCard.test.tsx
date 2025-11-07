import { render, screen } from '@testing-library/react'
import StatCard from '@/components/ui/StatCard'

describe('StatCard', () => {
  // Arrange-Act-Assert パターンに従う

  it('基本的な統計情報を表示する', () => {
    // Arrange
    const props = {
      title: 'テストタイトル',
      value: 100,
      description: 'テスト説明',
    }

    // Act
    render(<StatCard {...props} />)

    // Assert
    expect(screen.getByText('テストタイトル')).toBeInTheDocument()
    expect(screen.getByText('100')).toBeInTheDocument()
    expect(screen.getByText('テスト説明')).toBeInTheDocument()
  })

  it('文字列の値を表示できる', () => {
    // Arrange
    const props = {
      title: 'プロジェクト数',
      value: '1,234',
    }

    // Act
    render(<StatCard {...props} />)

    // Assert
    expect(screen.getByText('プロジェクト数')).toBeInTheDocument()
    expect(screen.getByText('1,234')).toBeInTheDocument()
  })

  it('アイコンを表示できる', () => {
    // Arrange
    const icon = <span data-testid="test-icon">📊</span>
    const props = {
      title: 'タイトル',
      value: 50,
      icon,
    }

    // Act
    render(<StatCard {...props} />)

    // Assert
    expect(screen.getByTestId('test-icon')).toBeInTheDocument()
  })

  it('ポジティブなトレンドを表示できる', () => {
    // Arrange
    const props = {
      title: '売上',
      value: 1000,
      trend: {
        value: 15,
        isPositive: true,
      },
    }

    // Act
    render(<StatCard {...props} />)

    // Assert
    expect(screen.getByText('↑ 15%')).toBeInTheDocument()
    expect(screen.getByText('前月比')).toBeInTheDocument()
  })

  it('ネガティブなトレンドを表示できる', () => {
    // Arrange
    const props = {
      title: '売上',
      value: 900,
      trend: {
        value: -10,
        isPositive: false,
      },
    }

    // Act
    render(<StatCard {...props} />)

    // Assert
    expect(screen.getByText('↓ 10%')).toBeInTheDocument()
  })

  it('カスタムカラークラスを適用できる', () => {
    // Arrange
    const props = {
      title: 'テスト',
      value: 100,
      colorClass: 'text-red-600',
    }

    // Act
    const { container } = render(<StatCard {...props} />)

    // Assert
    const valueElement = screen.getByText('100')
    expect(valueElement).toHaveClass('text-red-600')
  })

  it('説明なしでもレンダリングできる', () => {
    // Arrange
    const props = {
      title: 'タイトルのみ',
      value: 42,
    }

    // Act
    render(<StatCard {...props} />)

    // Assert
    expect(screen.getByText('タイトルのみ')).toBeInTheDocument()
    expect(screen.getByText('42')).toBeInTheDocument()
  })
})
