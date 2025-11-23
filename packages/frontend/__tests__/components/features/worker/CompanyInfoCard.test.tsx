import { render, screen } from '@testing-library/react'
import { CompanyInfoCard } from '@/components/features/worker/CompanyInfoCard'
import type { ListItem } from '@/types/assignment'

describe('CompanyInfoCard', () => {
  // テスト用のモックデータ
  const mockListItem: ListItem = {
    id: 1,
    listId: 100,
    companyName: '株式会社テスト',
    companyUrl: 'https://example.com',
    contactEmail: 'contact@example.com',
    contactName: '山田太郎',
    notes: 'テスト用の備考です',
    status: 'pending',
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-01-01T00:00:00Z',
  }

  describe('基本表示', () => {
    it('企業情報カードのタイトルが表示される', () => {
      render(<CompanyInfoCard item={mockListItem} />)

      expect(screen.getByText('企業情報')).toBeInTheDocument()
      expect(screen.getByText('作業対象の企業情報')).toBeInTheDocument()
    })

    it('会社名が表示される', () => {
      render(<CompanyInfoCard item={mockListItem} />)

      expect(screen.getByText('会社名')).toBeInTheDocument()
      expect(screen.getByText('株式会社テスト')).toBeInTheDocument()
    })

    it('企業URLが表示され、クリック可能なリンクである', () => {
      render(<CompanyInfoCard item={mockListItem} />)

      expect(screen.getByText('企業URL')).toBeInTheDocument()

      const urlLink = screen.getByRole('link', {
        name: 'https://example.com',
      })
      expect(urlLink).toBeInTheDocument()
      expect(urlLink).toHaveAttribute('href', 'https://example.com')
      expect(urlLink).toHaveAttribute('target', '_blank')
      expect(urlLink).toHaveAttribute('rel', 'noopener noreferrer')
    })

    it('担当者名が表示される', () => {
      render(<CompanyInfoCard item={mockListItem} />)

      expect(screen.getByText('担当者名')).toBeInTheDocument()
      expect(screen.getByText('山田太郎')).toBeInTheDocument()
    })

    it('メールアドレスが表示され、クリック可能なリンクである', () => {
      render(<CompanyInfoCard item={mockListItem} />)

      expect(screen.getByText('メールアドレス')).toBeInTheDocument()

      const emailLink = screen.getByRole('link', {
        name: 'contact@example.com',
      })
      expect(emailLink).toBeInTheDocument()
      expect(emailLink).toHaveAttribute('href', 'mailto:contact@example.com')
    })

    it('備考が表示される', () => {
      render(<CompanyInfoCard item={mockListItem} />)

      expect(screen.getByText('備考')).toBeInTheDocument()
      expect(screen.getByText('テスト用の備考です')).toBeInTheDocument()
    })
  })

  describe('オプション項目の表示', () => {
    it('企業URLがない場合は表示されない', () => {
      const itemWithoutUrl: ListItem = {
        ...mockListItem,
        companyUrl: undefined,
      }

      render(<CompanyInfoCard item={itemWithoutUrl} />)

      expect(screen.queryByText('企業URL')).not.toBeInTheDocument()
    })

    it('担当者名がない場合は表示されない', () => {
      const itemWithoutContact: ListItem = {
        ...mockListItem,
        contactName: undefined,
      }

      render(<CompanyInfoCard item={itemWithoutContact} />)

      expect(screen.queryByText('担当者名')).not.toBeInTheDocument()
    })

    it('メールアドレスがない場合は表示されない', () => {
      const itemWithoutEmail: ListItem = {
        ...mockListItem,
        contactEmail: undefined,
      }

      render(<CompanyInfoCard item={itemWithoutEmail} />)

      expect(screen.queryByText('メールアドレス')).not.toBeInTheDocument()
    })

    it('備考がない場合は表示されない', () => {
      const itemWithoutNotes: ListItem = {
        ...mockListItem,
        notes: undefined,
      }

      render(<CompanyInfoCard item={itemWithoutNotes} />)

      expect(screen.queryByText('備考')).not.toBeInTheDocument()
    })
  })

  describe('最小限のデータでの表示', () => {
    it('会社名のみの場合でも正しく表示される', () => {
      const minimalItem: ListItem = {
        id: 1,
        listId: 100,
        companyName: '最小限株式会社',
        status: 'pending',
        createdAt: '2025-01-01T00:00:00Z',
        updatedAt: '2025-01-01T00:00:00Z',
      }

      render(<CompanyInfoCard item={minimalItem} />)

      // 必須項目のみ表示される
      expect(screen.getByText('企業情報')).toBeInTheDocument()
      expect(screen.getByText('会社名')).toBeInTheDocument()
      expect(screen.getByText('最小限株式会社')).toBeInTheDocument()

      // オプション項目は表示されない
      expect(screen.queryByText('企業URL')).not.toBeInTheDocument()
      expect(screen.queryByText('担当者名')).not.toBeInTheDocument()
      expect(screen.queryByText('メールアドレス')).not.toBeInTheDocument()
      expect(screen.queryByText('備考')).not.toBeInTheDocument()
    })
  })

  describe('アクセシビリティ', () => {
    it('外部リンクに適切な属性が設定されている', () => {
      render(<CompanyInfoCard item={mockListItem} />)

      const urlLink = screen.getByRole('link', {
        name: 'https://example.com',
      })

      // セキュリティのための属性
      expect(urlLink).toHaveAttribute('rel', 'noopener noreferrer')
      expect(urlLink).toHaveAttribute('target', '_blank')
    })
  })
})
