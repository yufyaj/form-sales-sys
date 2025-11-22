/**
 * ColumnMappingEditorコンポーネントのテスト
 *
 * TDDサイクル: Red（失敗するテスト）
 */

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ColumnMappingEditor from '@/components/features/csv-import/ColumnMappingEditor'
import type { CSVColumn, SystemField } from '@/types/csvImport'

describe('ColumnMappingEditor', () => {
  const mockColumns: CSVColumn[] = [
    {
      name: 'organizationName',
      index: 0,
      sampleValues: ['テスト株式会社', '株式会社サンプル', 'Example Inc.'],
    },
    {
      name: 'industry',
      index: 1,
      sampleValues: ['IT', '製造業', 'サービス業'],
    },
    {
      name: 'employeeCount',
      index: 2,
      sampleValues: ['100', '500', '1000'],
    },
  ]

  const mockSystemFields: SystemField[] = [
    {
      id: 'organizationName',
      label: '組織名',
      required: true,
      type: 'string',
      description: '顧客の組織名',
    },
    {
      id: 'industry',
      label: '業種',
      required: false,
      type: 'string',
    },
    {
      id: 'employeeCount',
      label: '従業員数',
      required: false,
      type: 'number',
    },
  ]

  const mockOnMappingChange = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('初期表示', () => {
    it('CSVカラムが表示される', () => {
      render(
        <ColumnMappingEditor
          columns={mockColumns}
          systemFields={mockSystemFields}
          mappings={{}}
          onMappingChange={mockOnMappingChange}
        />
      )

      expect(screen.getByText('organizationName')).toBeInTheDocument()
      expect(screen.getByText('industry')).toBeInTheDocument()
      expect(screen.getByText('employeeCount')).toBeInTheDocument()
    })

    it('サンプルデータが表示される', () => {
      render(
        <ColumnMappingEditor
          columns={mockColumns}
          systemFields={mockSystemFields}
          mappings={{}}
          onMappingChange={mockOnMappingChange}
        />
      )

      expect(screen.getByText('テスト株式会社')).toBeInTheDocument()
      expect(screen.getByText('IT')).toBeInTheDocument()
      expect(screen.getByText('100')).toBeInTheDocument()
    })

    it('システムフィールドの選択肢が表示される', () => {
      render(
        <ColumnMappingEditor
          columns={mockColumns}
          systemFields={mockSystemFields}
          mappings={{}}
          onMappingChange={mockOnMappingChange}
        />
      )

      const selects = screen.getAllByRole('combobox')
      expect(selects).toHaveLength(mockColumns.length)
    })
  })

  describe('マッピング操作', () => {
    it('ドロップダウンからフィールドを選択できる', async () => {
      render(
        <ColumnMappingEditor
          columns={mockColumns}
          systemFields={mockSystemFields}
          mappings={{}}
          onMappingChange={mockOnMappingChange}
        />
      )

      const selects = screen.getAllByRole('combobox')
      const firstSelect = selects[0]

      await userEvent.selectOptions(firstSelect, 'organizationName')

      expect(mockOnMappingChange).toHaveBeenCalledWith({
        organizationName: 'organizationName',
      })
    })

    it('マッピング済みのフィールドは初期値として表示される', () => {
      render(
        <ColumnMappingEditor
          columns={mockColumns}
          systemFields={mockSystemFields}
          mappings={{
            organizationName: 'organizationName',
            industry: 'industry',
          }}
          onMappingChange={mockOnMappingChange}
        />
      )

      const selects = screen.getAllByRole('combobox') as HTMLSelectElement[]
      expect(selects[0].value).toBe('organizationName')
      expect(selects[1].value).toBe('industry')
    })

    it('マッピングを解除できる', async () => {
      render(
        <ColumnMappingEditor
          columns={mockColumns}
          systemFields={mockSystemFields}
          mappings={{
            organizationName: 'organizationName',
          }}
          onMappingChange={mockOnMappingChange}
        />
      )

      const selects = screen.getAllByRole('combobox')
      const firstSelect = selects[0]

      await userEvent.selectOptions(firstSelect, '')

      expect(mockOnMappingChange).toHaveBeenCalledWith({
        organizationName: null,
      })
    })
  })

  describe('バリデーション', () => {
    it('必須フィールドがマッピングされていない場合、警告が表示される', () => {
      render(
        <ColumnMappingEditor
          columns={mockColumns}
          systemFields={mockSystemFields}
          mappings={{}}
          onMappingChange={mockOnMappingChange}
        />
      )

      expect(screen.getByText(/組織名は必須です/i)).toBeInTheDocument()
    })

    it('必須フィールドがマッピングされている場合、警告が表示されない', () => {
      render(
        <ColumnMappingEditor
          columns={mockColumns}
          systemFields={mockSystemFields}
          mappings={{
            organizationName: 'organizationName',
          }}
          onMappingChange={mockOnMappingChange}
        />
      )

      expect(screen.queryByText(/組織名は必須です/i)).not.toBeInTheDocument()
    })

    it('同じシステムフィールドに複数のCSVカラムがマッピングされている場合、警告が表示される', () => {
      render(
        <ColumnMappingEditor
          columns={mockColumns}
          systemFields={mockSystemFields}
          mappings={{
            organizationName: 'organizationName',
            industry: 'organizationName', // 重複
          }}
          onMappingChange={mockOnMappingChange}
        />
      )

      expect(screen.getByText(/同じフィールドに複数のカラムがマッピングされています/i)).toBeInTheDocument()
    })
  })

  describe('自動マッピング', () => {
    it('自動マッピングボタンが表示される', () => {
      render(
        <ColumnMappingEditor
          columns={mockColumns}
          systemFields={mockSystemFields}
          mappings={{}}
          onMappingChange={mockOnMappingChange}
        />
      )

      expect(screen.getByText(/自動マッピング/i)).toBeInTheDocument()
    })

    it('自動マッピングボタンをクリックすると、名前が一致するフィールドが自動的にマッピングされる', async () => {
      render(
        <ColumnMappingEditor
          columns={mockColumns}
          systemFields={mockSystemFields}
          mappings={{}}
          onMappingChange={mockOnMappingChange}
        />
      )

      const autoMapButton = screen.getByText(/自動マッピング/i)
      await userEvent.click(autoMapButton)

      expect(mockOnMappingChange).toHaveBeenCalledWith({
        organizationName: 'organizationName',
        industry: 'industry',
        employeeCount: 'employeeCount',
      })
    })
  })

  describe('UI/UX', () => {
    it('必須フィールドには * マークが表示される', () => {
      render(
        <ColumnMappingEditor
          columns={mockColumns}
          systemFields={mockSystemFields}
          mappings={{}}
          onMappingChange={mockOnMappingChange}
        />
      )

      // selectのoptionに*マークがあるか確認
      const options = screen.getAllByText(/組織名/)
      const requiredOption = options.find(el => el.textContent?.includes('*'))
      expect(requiredOption).toBeDefined()
    })

    it('フィールドの説明がツールチップとして表示される', () => {
      render(
        <ColumnMappingEditor
          columns={mockColumns}
          systemFields={mockSystemFields}
          mappings={{}}
          onMappingChange={mockOnMappingChange}
        />
      )

      expect(screen.getByText(/顧客の組織名/i)).toBeInTheDocument()
    })
  })
})
