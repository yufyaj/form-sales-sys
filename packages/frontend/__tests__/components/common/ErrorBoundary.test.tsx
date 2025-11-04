import { render, screen } from '@testing-library/react'
import { ErrorBoundary } from '@/components/common/ErrorBoundary'

// エラーをスローするテストコンポーネント
function ThrowError({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error('Test error')
  }
  return <div>No error</div>
}

describe('ErrorBoundary', () => {
  // エラーログを抑制
  const originalConsoleError = console.error

  beforeAll(() => {
    console.error = jest.fn()
  })

  afterAll(() => {
    console.error = originalConsoleError
  })

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('正常時の動作', () => {
    it('エラーがない場合は子コンポーネントをレンダリングする', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      )

      expect(screen.getByText('No error')).toBeInTheDocument()
      expect(
        screen.queryByText('エラーが発生しました')
      ).not.toBeInTheDocument()
    })

    it('複数の子コンポーネントをレンダリングできる', () => {
      render(
        <ErrorBoundary>
          <div>Child 1</div>
          <div>Child 2</div>
          <div>Child 3</div>
        </ErrorBoundary>
      )

      expect(screen.getByText('Child 1')).toBeInTheDocument()
      expect(screen.getByText('Child 2')).toBeInTheDocument()
      expect(screen.getByText('Child 3')).toBeInTheDocument()
    })
  })

  describe('エラー発生時の動作', () => {
    it('エラーが発生した場合はエラー画面を表示する', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      )

      expect(screen.getByText('⚠️')).toBeInTheDocument()
      expect(screen.getByText('エラーが発生しました')).toBeInTheDocument()
      expect(
        screen.getByText(/ページの読み込み中に問題が発生しました/)
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'ページを再読み込み' })
      ).toBeInTheDocument()
    })

    it('エラーがコンソールに記録される', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      )

      expect(console.error).toHaveBeenCalledWith(
        'エラーが発生しました:',
        expect.any(Error),
        expect.any(Object)
      )
    })

    it('再読み込みボタンが表示される', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      )

      const reloadButton = screen.getByRole('button', {
        name: 'ページを再読み込み',
      })
      expect(reloadButton).toBeInTheDocument()
    })
  })

  describe('開発環境での動作', () => {
    const originalNodeEnv = process.env.NODE_ENV

    beforeEach(() => {
      process.env.NODE_ENV = 'development'
    })

    afterEach(() => {
      process.env.NODE_ENV = originalNodeEnv
    })

    it('開発環境ではエラー詳細を表示する', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      )

      expect(
        screen.getByText('エラー詳細（開発環境のみ表示）')
      ).toBeInTheDocument()
      expect(screen.getByText(/Error: Test error/)).toBeInTheDocument()
    })
  })

  describe('本番環境での動作', () => {
    const originalNodeEnv = process.env.NODE_ENV

    beforeEach(() => {
      process.env.NODE_ENV = 'production'
    })

    afterEach(() => {
      process.env.NODE_ENV = originalNodeEnv
    })

    it('本番環境ではエラー詳細を表示しない', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      )

      expect(
        screen.queryByText('エラー詳細（開発環境のみ表示）')
      ).not.toBeInTheDocument()
      expect(screen.queryByText(/Error: Test error/)).not.toBeInTheDocument()
    })
  })

  describe('UIアクセシビリティ', () => {
    it('エラー画面の再読み込みボタンにフォーカスできる', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      )

      const reloadButton = screen.getByRole('button', {
        name: 'ページを再読み込み',
      })

      reloadButton.focus()
      expect(reloadButton).toHaveFocus()
    })

    it('エラー画面に適切な見出しが表示される', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      )

      const heading = screen.getByRole('heading', {
        name: 'エラーが発生しました',
      })
      expect(heading).toBeInTheDocument()
    })
  })
})
