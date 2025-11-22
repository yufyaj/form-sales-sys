/**
 * CSVPreviewTableコンポーネントのテスト
 *
 * TDDサイクル: Red（失敗するテスト）
 */

import { render, screen } from '@testing-library/react'
import CSVPreviewTable from '@/components/features/csv-import/CSVPreviewTable'
import type { CSVValidationError } from '@/types/csvImport'

describe('CSVPreviewTable', () => {
  const mockData = [
    {
      organizationName: 'テスト株式会社',
      industry: 'IT',
      employeeCount: 100,
    },
    {
      organizationName: '株式会社サンプル',
      industry: '製造業',
      employeeCount: 500,
    },
    {
      organizationName: 'Example Inc.',
      industry: 'サービス業',
      employeeCount: 1000,
    },
  ]

  const mockErrors: CSVValidationError[] = [
    {
      row: 2,
      column: 'employeeCount',
      message: '従業員数は整数である必要があります',
      value: 'invalid',
    },
  ]

  describe('初期表示', () => {
    it('データテーブルが表示される', () => {
      render(<CSVPreviewTable data={mockData} errors={[]} />)

      expect(screen.getByRole('table')).toBeInTheDocument()
    })

    it('ヘッダーが表示される', () => {
      render(<CSVPreviewTable data={mockData} errors={[]} />)

      expect(screen.getByText('organizationName')).toBeInTheDocument()
      expect(screen.getByText('industry')).toBeInTheDocument()
      expect(screen.getByText('employeeCount')).toBeInTheDocument()
    })

    it('データ行が表示される', () => {
      render(<CSVPreviewTable data={mockData} errors={[]} />)

      expect(screen.getByText('テスト株式会社')).toBeInTheDocument()
      expect(screen.getByText('株式会社サンプル')).toBeInTheDocument()
      expect(screen.getByText('Example Inc.')).toBeInTheDocument()
    })

    it('行番号が表示される', () => {
      render(<CSVPreviewTable data={mockData} errors={[]} showRowNumbers />)

      expect(screen.getByText('1')).toBeInTheDocument()
      expect(screen.getByText('2')).toBeInTheDocument()
      expect(screen.getByText('3')).toBeInTheDocument()
    })
  })

  describe('バリデーションエラー表示', () => {
    it('エラーがある行がハイライトされる', () => {
      render(<CSVPreviewTable data={mockData} errors={mockErrors} />)

      // 2行目（row: 2）がエラー行としてハイライトされる
      const errorRow = screen.getByText('株式会社サンプル').closest('tr')
      expect(errorRow).toHaveClass(/bg-red/i)
    })

    it('エラーメッセージが表示される', () => {
      render(<CSVPreviewTable data={mockData} errors={mockErrors} />)

      const messages = screen.getAllByText(/従業員数は整数である必要があります/i)
      expect(messages.length).toBeGreaterThan(0)
    })

    it('エラーサマリーが表示される', () => {
      render(<CSVPreviewTable data={mockData} errors={mockErrors} />)

      expect(screen.getByText(/1件のエラー/i)).toBeInTheDocument()
    })

    it('複数のエラーがある場合、すべて表示される', () => {
      const multipleErrors: CSVValidationError[] = [
        {
          row: 1,
          column: 'organizationName',
          message: '組織名は必須です',
        },
        {
          row: 2,
          column: 'employeeCount',
          message: '従業員数は整数である必要があります',
        },
      ]

      render(<CSVPreviewTable data={mockData} errors={multipleErrors} />)

      expect(screen.getByText(/2件のエラー/i)).toBeInTheDocument()
      expect(screen.getAllByText(/組織名は必須です/i).length).toBeGreaterThan(0)
      expect(screen.getAllByText(/従業員数は整数である必要があります/i).length).toBeGreaterThan(0)
    })
  })

  describe('データ制限', () => {
    it('100行を超えるデータの場合、最初の100行のみ表示される', () => {
      const largeData = Array.from({ length: 150 }, (_, i) => ({
        name: `Row ${i + 1}`,
      }))

      render(<CSVPreviewTable data={largeData} errors={[]} />)

      expect(screen.getByText('Row 1')).toBeInTheDocument()
      expect(screen.getByText('Row 100')).toBeInTheDocument()
      expect(screen.queryByText('Row 101')).not.toBeInTheDocument()
    })

    it('データ制限の警告メッセージが表示される', () => {
      const largeData = Array.from({ length: 150 }, (_, i) => ({
        name: `Row ${i + 1}`,
      }))

      render(<CSVPreviewTable data={largeData} errors={[]} />)

      expect(screen.getByText(/最初の100行のみ表示/i)).toBeInTheDocument()
    })
  })

  describe('空データ', () => {
    it('データが空の場合、メッセージが表示される', () => {
      render(<CSVPreviewTable data={[]} errors={[]} />)

      expect(screen.getByText(/データがありません/i)).toBeInTheDocument()
    })
  })

  describe('統計情報', () => {
    it('総行数が表示される', () => {
      render(<CSVPreviewTable data={mockData} errors={[]} showStats />)

      expect(screen.getByText('総行数:')).toBeInTheDocument()
      // 3が複数表示されるため、getAllByTextを使用
      const threes = screen.getAllByText('3')
      expect(threes.length).toBeGreaterThan(0)
    })

    it('有効行数とエラー行数が表示される', () => {
      render(<CSVPreviewTable data={mockData} errors={mockErrors} showStats />)

      expect(screen.getByText('有効:')).toBeInTheDocument()
      expect(screen.getByText('エラー:')).toBeInTheDocument()
    })
  })

  describe('スクロール', () => {
    it('横スクロール可能なコンテナが使用される', () => {
      render(<CSVPreviewTable data={mockData} errors={[]} />)

      const container = screen.getByRole('table').closest('div')
      expect(container).toHaveClass(/overflow-x-auto/i)
    })
  })
})
