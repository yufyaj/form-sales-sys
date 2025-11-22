import { render, screen } from '@testing-library/react'
import InspectionStatusBadge from '@/components/features/list/InspectionStatusBadge'
import { InspectionStatus } from '@/types/list'

describe('InspectionStatusBadge', () => {
  describe('ステータス表示', () => {
    it('未検収ステータスを表示する', () => {
      render(<InspectionStatusBadge status="not_started" />)

      const badge = screen.getByText('未検収')
      expect(badge).toBeInTheDocument()
      // デフォルトvariantが適用されることを確認
      expect(badge).toHaveClass('bg-gray-100', 'text-gray-800')
    })

    it('検収中ステータスを表示する', () => {
      render(<InspectionStatusBadge status="in_progress" />)

      const badge = screen.getByText('検収中')
      expect(badge).toBeInTheDocument()
      // info variantが適用されることを確認
      expect(badge).toHaveClass('bg-blue-100', 'text-blue-800')
    })

    it('検収完了ステータスを表示する', () => {
      render(<InspectionStatusBadge status="completed" />)

      const badge = screen.getByText('検収完了')
      expect(badge).toBeInTheDocument()
      // success variantが適用されることを確認
      expect(badge).toHaveClass('bg-green-100', 'text-green-800')
    })

    it('却下ステータスを表示する', () => {
      render(<InspectionStatusBadge status="rejected" />)

      const badge = screen.getByText('却下')
      expect(badge).toBeInTheDocument()
      // danger variantが適用されることを確認
      expect(badge).toHaveClass('bg-red-100', 'text-red-800')
    })
  })

  describe('サイズ指定', () => {
    it('smサイズを表示する', () => {
      render(<InspectionStatusBadge status="completed" size="sm" />)

      const badge = screen.getByText('検収完了')
      expect(badge).toHaveClass('px-2', 'py-0.5', 'text-xs')
    })

    it('mdサイズ（デフォルト）を表示する', () => {
      render(<InspectionStatusBadge status="completed" />)

      const badge = screen.getByText('検収完了')
      expect(badge).toHaveClass('px-2.5', 'py-1', 'text-sm')
    })

    it('lgサイズを表示する', () => {
      render(<InspectionStatusBadge status="completed" size="lg" />)

      const badge = screen.getByText('検収完了')
      expect(badge).toHaveClass('px-3', 'py-1.5', 'text-base')
    })
  })

  describe('アクセシビリティ', () => {
    it('適切なrole属性を持つ', () => {
      render(<InspectionStatusBadge status="completed" />)

      const badge = screen.getByRole('status')
      expect(badge).toBeInTheDocument()
    })

    it('aria-labelが設定されている', () => {
      render(<InspectionStatusBadge status="completed" />)

      const badge = screen.getByRole('status')
      expect(badge).toHaveAttribute('aria-label', '検収ステータス: 検収完了')
    })
  })
})
