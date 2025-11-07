import { render, screen } from '@testing-library/react'
import StatCard from '@/components/ui/StatCard'
import Badge from '@/components/ui/Badge'
import Table from '@/components/ui/Table'

/**
 * XSS（Cross-Site Scripting）脆弱性のテスト
 *
 * テスト内容:
 * - 悪意のあるスクリプトタグが実行されないこと
 * - HTMLタグが適切にエスケープされること
 * - 特殊文字が安全に表示されること
 */
describe('XSS Prevention', () => {
  describe('StatCard', () => {
    it('悪意のあるスクリプトタグがtitleに含まれても実行されない', () => {
      const maliciousTitle = '<script>alert("XSS")</script>'
      render(<StatCard title={maliciousTitle} value={100} />)

      // スクリプトタグがDOMに挿入されていないことを確認
      expect(document.querySelector('script')).not.toBeInTheDocument()

      // テキストとしてエスケープされて表示されることを確認
      expect(screen.getByText(maliciousTitle)).toBeInTheDocument()
    })

    it('HTMLタグがエスケープされて表示される', () => {
      const htmlContent = '<img src=x onerror="alert(1)">'
      render(<StatCard title={htmlContent} value={100} />)

      // imgタグが実際には挿入されていないことを確認
      expect(document.querySelector('img[src="x"]')).not.toBeInTheDocument()

      // テキストとして表示されることを確認
      expect(screen.getByText(htmlContent)).toBeInTheDocument()
    })

    it('JavaScriptイベントハンドラが実行されない', () => {
      const maliciousValue = 'onclick="alert(1)"'
      render(<StatCard title={maliciousValue} value={100} />)

      // onclickイベントが設定されていないことを確認
      const element = screen.getByText(maliciousValue)
      expect(element.onclick).toBeNull()
    })
  })

  describe('Badge', () => {
    it('悪意のあるスクリプトがchildrenに含まれても実行されない', () => {
      const maliciousContent = '<script>alert("XSS")</script>'
      render(<Badge variant="default">{maliciousContent}</Badge>)

      // スクリプトタグが挿入されていないことを確認
      expect(document.querySelector('script')).not.toBeInTheDocument()

      // テキストとしてエスケープされて表示されることを確認
      expect(screen.getByText(maliciousContent)).toBeInTheDocument()
    })

    it('特殊文字が正しくエスケープされる', () => {
      const specialChars = '< > & " \' / \\'
      render(<Badge variant="default">{specialChars}</Badge>)

      // 特殊文字がテキストとして表示されることを確認
      expect(screen.getByText(specialChars)).toBeInTheDocument()
    })
  })

  describe('Table', () => {
    it('テーブルのセル内容が安全にレンダリングされる', () => {
      const maliciousData = [
        {
          id: '1',
          name: '<script>alert("XSS")</script>',
          description: '<img src=x onerror="alert(1)">',
        },
      ]

      const columns = [
        { key: 'id', header: 'ID' },
        { key: 'name', header: '名前' },
        { key: 'description', header: '説明' },
      ]

      render(
        <Table
          columns={columns}
          data={maliciousData}
          keyExtractor={(item) => item.id}
        />
      )

      // スクリプトタグとimgタグが実行・挿入されていないことを確認
      expect(document.querySelector('script')).not.toBeInTheDocument()
      expect(document.querySelector('img[src="x"]')).not.toBeInTheDocument()

      // テキストとして表示されることを確認
      expect(screen.getByText('<script>alert("XSS")</script>')).toBeInTheDocument()
      expect(screen.getByText('<img src=x onerror="alert(1)">')).toBeInTheDocument()
    })

    it('カスタムレンダー関数で悪意のあるコンテンツが安全に処理される', () => {
      const data = [{ id: '1', content: '<b>Bold</b>' }]

      const columns = [
        {
          key: 'content',
          header: 'Content',
          render: (item: { content: string }) => <span>{item.content}</span>,
        },
      ]

      render(<Table columns={columns} data={data} keyExtractor={(item) => item.id} />)

      // bタグが実際には挿入されず、テキストとして表示されることを確認
      expect(screen.getByText('<b>Bold</b>')).toBeInTheDocument()
    })

    it('align属性に不正な値が渡されても安全に処理される', () => {
      const data = [{ id: '1', value: 'test' }]

      // 意図的に不正な型をanyでキャストして渡す
      const columns = [
        {
          key: 'value',
          header: 'Value',
          align: 'javascript:alert(1)' as 'left', // 不正な値
        },
      ]

      render(<Table columns={columns} data={data} keyExtractor={(item) => item.id} />)

      // エラーなくレンダリングされることを確認
      expect(screen.getByText('test')).toBeInTheDocument()

      // 不正なクラス名が適用されていないことを確認
      const cell = screen.getByText('test')
      expect(cell.className).not.toContain('javascript')
    })
  })

  describe('制御文字の除去', () => {
    it('制御文字が含まれる文字列が安全に処理される', () => {
      // 制御文字を含む文字列
      const controlChars = 'Test\x00\x01\x1F\x7F\x9FData'
      render(<StatCard title={controlChars} value={100} />)

      // レンダリングされていることを確認（制御文字は除去される可能性がある）
      const element = screen.getByText(/Test.*Data/)
      expect(element).toBeInTheDocument()
    })
  })

  describe('長い文字列の処理', () => {
    it('非常に長い文字列が渡されてもパフォーマンスが低下しない', () => {
      const longString = 'A'.repeat(10000)
      const startTime = performance.now()

      render(<StatCard title={longString} value={100} />)

      const endTime = performance.now()
      const renderTime = endTime - startTime

      // レンダリング時間が1秒以内であることを確認（パフォーマンステスト）
      expect(renderTime).toBeLessThan(1000)
    })
  })
})
