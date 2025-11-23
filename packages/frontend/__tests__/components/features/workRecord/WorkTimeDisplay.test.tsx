/**
 * 作業時間表示コンポーネントのテスト
 *
 * TDDサイクル: Red -> Green -> Refactor
 */

import { render, screen, waitFor } from '@testing-library/react'
import WorkTimeDisplay from '@/components/features/workRecord/WorkTimeDisplay'

// タイマーをモック化
jest.useFakeTimers()

describe('WorkTimeDisplay', () => {
  beforeEach(() => {
    jest.clearAllTimers()
  })

  afterEach(() => {
    jest.clearAllTimers()
  })

  it('作業開始時刻が表示される', () => {
    // Arrange
    const startedAt = '2025-11-23T10:00:00Z'

    // Act
    render(<WorkTimeDisplay startedAt={startedAt} />)

    // Assert
    expect(screen.getByText('作業開始時刻')).toBeInTheDocument()
    // 日本時間に変換された時刻が表示される
    const timeElement = screen.getByRole('time')
    expect(timeElement).toHaveAttribute('datetime', startedAt)
  })

  it('経過時間が表示される', () => {
    // Arrange
    const startedAt = new Date(Date.now() - 3661000).toISOString() // 1時間1分1秒前

    // Act
    render(<WorkTimeDisplay startedAt={startedAt} />)

    // Assert
    expect(screen.getByText('経過時間')).toBeInTheDocument()
    expect(screen.getByRole('timer')).toBeInTheDocument()
  })

  it('経過時間が1秒ごとに更新される', async () => {
    // Arrange
    const now = Date.now()
    const startedAt = new Date(now - 5000).toISOString() // 5秒前
    jest.spyOn(Date, 'now').mockReturnValue(now)

    // Act
    render(<WorkTimeDisplay startedAt={startedAt} updateInterval={1000} />)

    // 初期表示
    expect(screen.getByText(/5秒/)).toBeInTheDocument()

    // 1秒進める
    jest.spyOn(Date, 'now').mockReturnValue(now + 1000)
    jest.advanceTimersByTime(1000)

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/6秒/)).toBeInTheDocument()
    })
  })

  it('経過時間が1時間を超えた場合、時間表示が含まれる', () => {
    // Arrange
    const startedAt = new Date(Date.now() - 3661000).toISOString() // 1時間1分1秒前

    // Act
    render(<WorkTimeDisplay startedAt={startedAt} />)

    // Assert
    const timerElement = screen.getByRole('timer')
    expect(timerElement.textContent).toMatch(/1時間/)
    expect(timerElement.textContent).toMatch(/1分/)
    expect(timerElement.textContent).toMatch(/秒/)
  })

  it('経過時間が1分未満の場合、秒のみ表示される', () => {
    // Arrange
    const startedAt = new Date(Date.now() - 30000).toISOString() // 30秒前

    // Act
    render(<WorkTimeDisplay startedAt={startedAt} />)

    // Assert
    const timerElement = screen.getByRole('timer')
    expect(timerElement.textContent).toMatch(/30秒/)
    expect(timerElement.textContent).not.toMatch(/時間/)
    expect(timerElement.textContent).not.toMatch(/分/)
  })

  it('コンポーネントがアンマウントされたら、タイマーがクリアされる', () => {
    // Arrange
    const startedAt = new Date().toISOString()
    const clearIntervalSpy = jest.spyOn(global, 'clearInterval')

    // Act
    const { unmount } = render(<WorkTimeDisplay startedAt={startedAt} />)
    unmount()

    // Assert
    expect(clearIntervalSpy).toHaveBeenCalled()
  })
})
