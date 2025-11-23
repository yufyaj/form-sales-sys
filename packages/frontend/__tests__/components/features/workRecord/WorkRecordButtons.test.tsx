/**
 * 作業記録ボタンコンポーネントのテスト
 *
 * TDDサイクル: Red -> Green -> Refactor
 */

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import WorkRecordButtons from '@/components/features/workRecord/WorkRecordButtons'
import * as workRecordActions from '@/lib/actions/workRecord'
import type { ProhibitedTimeCheckResult } from '@/types/workRecord'

// Server Actionsをモック化
jest.mock('@/lib/actions/workRecord')

const mockProhibitedCheckNormal: ProhibitedTimeCheckResult = {
  isProhibited: false,
  reasons: [],
}

const mockProhibitedCheckRestricted: ProhibitedTimeCheckResult = {
  isProhibited: true,
  reasons: ['土日は送信禁止（曜日制限）'],
  nextAllowedTime: new Date('2025-11-24T00:00:00Z'),
}

describe('WorkRecordButtons', () => {
  const mockGetCannotSendReasons = jest.fn()
  const mockCreateSentWorkRecord = jest.fn()
  const mockCreateCannotSendWorkRecord = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    ;(workRecordActions.getCannotSendReasons as jest.Mock) = mockGetCannotSendReasons
    ;(workRecordActions.createSentWorkRecord as jest.Mock) = mockCreateSentWorkRecord
    ;(workRecordActions.createCannotSendWorkRecord as jest.Mock) = mockCreateCannotSendWorkRecord

    // デフォルトのモック実装
    mockGetCannotSendReasons.mockResolvedValue({
      success: true,
      data: [
        { id: 1, reason_code: 'FORM_NOT_FOUND', reason_name: 'フォームが見つからない', is_active: true },
        { id: 2, reason_code: 'CAPTCHA_REQUIRED', reason_name: 'CAPTCHA認証が必要', is_active: true },
      ],
    })
  })

  describe('通常時（送信可能）', () => {
    it('送信済みボタンと送信不可ボタンが表示される', () => {
      // Act
      render(
        <WorkRecordButtons
          assignmentId={1}
          prohibitedCheck={mockProhibitedCheckNormal}
          startedAt="2025-11-23T10:00:00Z"
        />
      )

      // Assert
      expect(screen.getByRole('button', { name: '送信済みとして記録' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: '送信不可として記録' })).toBeInTheDocument()
    })

    it('送信済みボタンが有効化されている', () => {
      // Act
      render(
        <WorkRecordButtons
          assignmentId={1}
          prohibitedCheck={mockProhibitedCheckNormal}
          startedAt="2025-11-23T10:00:00Z"
        />
      )

      // Assert
      const sentButton = screen.getByRole('button', { name: '送信済みとして記録' })
      expect(sentButton).not.toBeDisabled()
    })

    it('送信済みボタンをクリックすると作業記録が作成される', async () => {
      // Arrange
      const user = userEvent.setup()
      const onRecordCreated = jest.fn()
      mockCreateSentWorkRecord.mockResolvedValue({ success: true, data: {} })

      // Act
      render(
        <WorkRecordButtons
          assignmentId={1}
          prohibitedCheck={mockProhibitedCheckNormal}
          startedAt="2025-11-23T10:00:00Z"
          onRecordCreated={onRecordCreated}
        />
      )

      const sentButton = screen.getByRole('button', { name: '送信済みとして記録' })
      await user.click(sentButton)

      // Assert
      await waitFor(() => {
        expect(mockCreateSentWorkRecord).toHaveBeenCalledTimes(1)
        expect(mockCreateSentWorkRecord).toHaveBeenCalledWith(
          expect.objectContaining({
            assignment_id: 1,
            started_at: '2025-11-23T10:00:00Z',
          })
        )
        expect(onRecordCreated).toHaveBeenCalledTimes(1)
      })
    })

    it('メモを入力して送信済みボタンをクリックできる', async () => {
      // Arrange
      const user = userEvent.setup()
      mockCreateSentWorkRecord.mockResolvedValue({ success: true, data: {} })

      // Act
      render(
        <WorkRecordButtons
          assignmentId={1}
          prohibitedCheck={mockProhibitedCheckNormal}
          startedAt="2025-11-23T10:00:00Z"
        />
      )

      const notesTextarea = screen.getByLabelText('メモ（任意）')
      await user.type(notesTextarea, 'テストメモ')

      const sentButton = screen.getByRole('button', { name: '送信済みとして記録' })
      await user.click(sentButton)

      // Assert
      await waitFor(() => {
        expect(mockCreateSentWorkRecord).toHaveBeenCalledWith(
          expect.objectContaining({
            notes: 'テストメモ',
          })
        )
      })
    })
  })

  describe('送信不可ボタン', () => {
    it('送信不可ボタンをクリックすると理由選択ダイアログが表示される', async () => {
      // Arrange
      const user = userEvent.setup()

      // Act
      render(
        <WorkRecordButtons
          assignmentId={1}
          prohibitedCheck={mockProhibitedCheckNormal}
          startedAt="2025-11-23T10:00:00Z"
        />
      )

      // 非同期処理の完了を待つ
      await waitFor(() => {
        expect(mockGetCannotSendReasons).toHaveBeenCalled()
      })

      const cannotSendButton = screen.getByRole('button', { name: '送信不可として記録' })
      await user.click(cannotSendButton)

      // Assert - ダイアログが表示されるのを待つ
      const dialog = await screen.findByRole('dialog')
      expect(dialog).toBeInTheDocument()
      expect(screen.getByText('送信不可理由の選択')).toBeInTheDocument()
    })

    it('理由を選択して記録ボタンをクリックすると作業記録が作成される', async () => {
      // Arrange
      const user = userEvent.setup()
      const onRecordCreated = jest.fn()
      mockCreateCannotSendWorkRecord.mockResolvedValue({ success: true, data: {} })

      // Act
      render(
        <WorkRecordButtons
          assignmentId={1}
          prohibitedCheck={mockProhibitedCheckNormal}
          startedAt="2025-11-23T10:00:00Z"
          onRecordCreated={onRecordCreated}
        />
      )

      // 非同期処理の完了を待つ
      await waitFor(() => {
        expect(mockGetCannotSendReasons).toHaveBeenCalled()
      })

      // 送信不可ボタンをクリック
      const cannotSendButton = screen.getByRole('button', { name: '送信不可として記録' })
      await user.click(cannotSendButton)

      // ダイアログが表示されるのを待つ
      await screen.findByRole('dialog')

      const reasonSelect = screen.getByLabelText('理由を選択してください')
      await user.selectOptions(reasonSelect, '1')

      // 記録ボタンをクリック
      const submitButton = screen.getByRole('button', { name: '記録する' })
      await user.click(submitButton)

      // Assert
      await waitFor(() => {
        expect(mockCreateCannotSendWorkRecord).toHaveBeenCalledTimes(1)
        expect(mockCreateCannotSendWorkRecord).toHaveBeenCalledWith(
          expect.objectContaining({
            assignment_id: 1,
            started_at: '2025-11-23T10:00:00Z',
            cannot_send_reason_id: 1,
          })
        )
        expect(onRecordCreated).toHaveBeenCalledTimes(1)
      })
    })

    it('理由を選択せずに記録ボタンをクリックするとエラーが表示される', async () => {
      // Arrange
      const user = userEvent.setup()

      // Act
      render(
        <WorkRecordButtons
          assignmentId={1}
          prohibitedCheck={mockProhibitedCheckNormal}
          startedAt="2025-11-23T10:00:00Z"
        />
      )

      // 非同期処理の完了を待つ
      await waitFor(() => {
        expect(mockGetCannotSendReasons).toHaveBeenCalled()
      })

      // 送信不可ボタンをクリック
      const cannotSendButton = screen.getByRole('button', { name: '送信不可として記録' })

      // ボタンクリックとダイアログ表示を一連の非同期処理として扱う
      await user.click(cannotSendButton)

      // ダイアログが表示されるのを待つ
      const dialog = await screen.findByRole('dialog')
      expect(dialog).toBeInTheDocument()

      // 理由を選択せずに記録ボタンをクリック
      const submitButton = screen.getByRole('button', { name: '記録する' })
      await user.click(submitButton)

      // Assert
      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument()
        expect(screen.getByText('送信不可理由を選択してください')).toBeInTheDocument()
        expect(mockCreateCannotSendWorkRecord).not.toHaveBeenCalled()
      })
    })
  })

  describe('禁止時間帯', () => {
    it('禁止時間帯の警告が表示される', () => {
      // Act
      render(
        <WorkRecordButtons
          assignmentId={1}
          prohibitedCheck={mockProhibitedCheckRestricted}
          startedAt="2025-11-23T10:00:00Z"
        />
      )

      // Assert
      expect(screen.getByText('送信禁止時間帯')).toBeInTheDocument()
      expect(screen.getByText(/土日は送信禁止/)).toBeInTheDocument()
    })

    it('禁止時間帯は送信済みボタンが無効化される', () => {
      // Act
      render(
        <WorkRecordButtons
          assignmentId={1}
          prohibitedCheck={mockProhibitedCheckRestricted}
          startedAt="2025-11-23T10:00:00Z"
        />
      )

      // Assert
      const sentButton = screen.getByRole('button', { name: '送信済みとして記録' })
      expect(sentButton).toBeDisabled()
      expect(sentButton).toHaveAttribute('aria-disabled', 'true')
    })

    it('禁止時間帯でも送信不可ボタンは有効', () => {
      // Act
      render(
        <WorkRecordButtons
          assignmentId={1}
          prohibitedCheck={mockProhibitedCheckRestricted}
          startedAt="2025-11-23T10:00:00Z"
        />
      )

      // Assert
      const cannotSendButton = screen.getByRole('button', { name: '送信不可として記録' })
      expect(cannotSendButton).not.toBeDisabled()
    })
  })

  describe('エラーハンドリング', () => {
    it('作業記録作成に失敗した場合、エラーメッセージが表示される', async () => {
      // Arrange
      const user = userEvent.setup()
      mockCreateSentWorkRecord.mockResolvedValue({
        success: false,
        error: '作業記録の作成に失敗しました',
      })

      // Act
      render(
        <WorkRecordButtons
          assignmentId={1}
          prohibitedCheck={mockProhibitedCheckNormal}
          startedAt="2025-11-23T10:00:00Z"
        />
      )

      // 非同期処理の完了を待つ
      await waitFor(() => {
        expect(mockGetCannotSendReasons).toHaveBeenCalled()
      })

      const sentButton = screen.getByRole('button', { name: '送信済みとして記録' })
      await user.click(sentButton)

      // Assert
      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument()
        expect(screen.getByText('作業記録の作成に失敗しました')).toBeInTheDocument()
      })
    })
  })
})
