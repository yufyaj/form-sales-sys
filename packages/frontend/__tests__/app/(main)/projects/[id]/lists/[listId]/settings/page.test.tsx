import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SettingsPage from '@/app/(main)/projects/[id]/lists/[listId]/settings/page'
import {
  getNoSendSettings,
  createDayOfWeekSetting,
  createTimeRangeSetting,
  createSpecificDateSetting,
  createDateRangeSetting,
  deleteNoSendSetting,
} from '@/lib/actions/noSendSettings'
import { NoSendSettingType, DayOfWeek } from '@/types/noSendSetting'

// next/navigationのモック
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({
    push: jest.fn(),
    refresh: jest.fn(),
  })),
  notFound: jest.fn(),
}))

// Server Actionsのモック
jest.mock('@/lib/actions/noSendSettings', () => ({
  getNoSendSettings: jest.fn(),
  createDayOfWeekSetting: jest.fn(),
  createTimeRangeSetting: jest.fn(),
  createSpecificDateSetting: jest.fn(),
  createDateRangeSetting: jest.fn(),
  deleteNoSendSetting: jest.fn(),
}))

// UIコンポーネントのモック
jest.mock('@/components/ui/Card', () => {
  return function Card({ children }: { children: React.ReactNode }) {
    return <div data-testid="card">{children}</div>
  }
})

jest.mock('@/components/ui/Button', () => {
  return function Button({
    children,
    onClick,
    variant,
    disabled,
  }: {
    children: React.ReactNode
    onClick?: () => void
    variant?: string
    disabled?: boolean
  }) {
    return (
      <button
        onClick={onClick}
        data-variant={variant}
        disabled={disabled}
        data-testid="button"
      >
        {children}
      </button>
    )
  }
})

describe('SettingsPage', () => {
  const mockParams = Promise.resolve({
    id: '1',
    listId: '10',
  })

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('初期表示', () => {
    it('設定一覧を取得して表示する', async () => {
      const mockSettings = [
        {
          id: 1,
          list_id: 10,
          setting_type: NoSendSettingType.DAY_OF_WEEK,
          name: '休日送信禁止',
          description: '土日の送信を禁止',
          is_enabled: true,
          day_of_week_list: [DayOfWeek.SATURDAY, DayOfWeek.SUNDAY],
          time_start: null,
          time_end: null,
          specific_date: null,
          date_range_start: null,
          date_range_end: null,
        },
      ]

      ;(getNoSendSettings as jest.Mock).mockResolvedValue({
        success: true,
        data: mockSettings,
      })

      render(<SettingsPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText('休日送信禁止')).toBeInTheDocument()
        expect(screen.getByText('土、日')).toBeInTheDocument()
      })
    })

    it('設定が0件の場合はメッセージを表示する', async () => {
      ;(getNoSendSettings as jest.Mock).mockResolvedValue({
        success: true,
        data: [],
      })

      render(<SettingsPage params={mockParams} />)

      await waitFor(() => {
        expect(
          screen.getByText('設定がまだ登録されていません')
        ).toBeInTheDocument()
      })
    })

    it('エラー時はエラーメッセージを表示する', async () => {
      ;(getNoSendSettings as jest.Mock).mockResolvedValue({
        success: false,
        error: '設定の取得に失敗しました',
      })

      render(<SettingsPage params={mockParams} />)

      await waitFor(() => {
        expect(
          screen.getByText('設定の取得に失敗しました')
        ).toBeInTheDocument()
      })
    })
  })

  describe('新規作成フォーム', () => {
    beforeEach(() => {
      ;(getNoSendSettings as jest.Mock).mockResolvedValue({
        success: true,
        data: [],
      })
    })

    it('新規作成ボタンをクリックするとフォームが表示される', async () => {
      const user = userEvent.setup()

      render(<SettingsPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText('新規作成')).toBeInTheDocument()
      })

      await user.click(screen.getByText('新規作成'))

      expect(screen.getByText('新しい設定を追加')).toBeInTheDocument()
      expect(screen.getByText('曜日指定')).toBeInTheDocument()
      expect(screen.getByText('時間帯指定')).toBeInTheDocument()
      expect(screen.getByText('日付指定')).toBeInTheDocument()
    })

    it('キャンセルボタンをクリックするとフォームが閉じる', async () => {
      const user = userEvent.setup()

      render(<SettingsPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText('新規作成')).toBeInTheDocument()
      })

      // フォームを開く
      await user.click(screen.getByText('新規作成'))
      expect(screen.getByText('新しい設定を追加')).toBeInTheDocument()

      // フォームを閉じる
      const cancelButtons = screen.getAllByText('キャンセル')
      await user.click(cancelButtons[0])

      await waitFor(() => {
        expect(
          screen.queryByText('新しい設定を追加')
        ).not.toBeInTheDocument()
      })
    })
  })

  describe('曜日設定の作成', () => {
    beforeEach(() => {
      ;(getNoSendSettings as jest.Mock).mockResolvedValue({
        success: true,
        data: [],
      })
    })

    it('曜日設定を作成できる', async () => {
      const user = userEvent.setup()

      const mockNewSetting = {
        id: 2,
        list_id: 10,
        setting_type: NoSendSettingType.DAY_OF_WEEK,
        name: '平日送信禁止',
        description: '',
        is_enabled: true,
        day_of_week_list: [DayOfWeek.MONDAY, DayOfWeek.FRIDAY],
        time_start: null,
        time_end: null,
        specific_date: null,
        date_range_start: null,
        date_range_end: null,
      }

      ;(createDayOfWeekSetting as jest.Mock).mockResolvedValue({
        success: true,
        data: mockNewSetting,
      })

      render(<SettingsPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText('新規作成')).toBeInTheDocument()
      })

      // フォームを開く
      await user.click(screen.getByText('新規作成'))

      // 設定名を入力
      const nameInput = screen.getByLabelText('設定名')
      await user.type(nameInput, '平日送信禁止')

      // 保存ボタンをクリック
      const saveButtons = screen.getAllByText('保存')
      await user.click(saveButtons[0])

      await waitFor(() => {
        expect(createDayOfWeekSetting).toHaveBeenCalledWith(
          expect.objectContaining({
            list_id: 10,
            name: '平日送信禁止',
          })
        )
      })
    })
  })

  describe('時間帯設定の作成', () => {
    beforeEach(() => {
      ;(getNoSendSettings as jest.Mock).mockResolvedValue({
        success: true,
        data: [],
      })
    })

    it('時間帯設定を作成できる', async () => {
      const user = userEvent.setup()

      const mockNewSetting = {
        id: 3,
        list_id: 10,
        setting_type: NoSendSettingType.TIME_RANGE,
        name: '夜間送信禁止',
        description: '',
        is_enabled: true,
        day_of_week_list: null,
        time_start: '22:00:00',
        time_end: '08:00:00',
        specific_date: null,
        date_range_start: null,
        date_range_end: null,
      }

      ;(createTimeRangeSetting as jest.Mock).mockResolvedValue({
        success: true,
        data: mockNewSetting,
      })

      render(<SettingsPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText('新規作成')).toBeInTheDocument()
      })

      // フォームを開く
      await user.click(screen.getByText('新規作成'))

      // 時間帯指定タブをクリック
      await user.click(screen.getByText('時間帯指定'))

      // 設定名を入力
      const nameInput = screen.getByLabelText('設定名')
      await user.type(nameInput, '夜間送信禁止')

      // 保存ボタンをクリック
      const saveButtons = screen.getAllByText('保存')
      await user.click(saveButtons[0])

      await waitFor(() => {
        expect(createTimeRangeSetting).toHaveBeenCalled()
      })
    })
  })

  describe('特定日付設定の作成', () => {
    beforeEach(() => {
      ;(getNoSendSettings as jest.Mock).mockResolvedValue({
        success: true,
        data: [],
      })
    })

    it('単一日付設定を作成できる', async () => {
      const user = userEvent.setup()

      const mockNewSetting = {
        id: 4,
        list_id: 10,
        setting_type: NoSendSettingType.SPECIFIC_DATE,
        name: '元日送信禁止',
        description: '',
        is_enabled: true,
        day_of_week_list: null,
        time_start: null,
        time_end: null,
        specific_date: '2025-01-01',
        date_range_start: null,
        date_range_end: null,
      }

      ;(createSpecificDateSetting as jest.Mock).mockResolvedValue({
        success: true,
        data: mockNewSetting,
      })

      render(<SettingsPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText('新規作成')).toBeInTheDocument()
      })

      // フォームを開く
      await user.click(screen.getByText('新規作成'))

      // 日付指定タブをクリック
      await user.click(screen.getByText('日付指定'))

      // 設定名を入力
      const nameInput = screen.getByLabelText('設定名')
      await user.type(nameInput, '元日送信禁止')

      // 保存ボタンをクリック
      const saveButtons = screen.getAllByText('保存')
      await user.click(saveButtons[0])

      await waitFor(() => {
        expect(createSpecificDateSetting).toHaveBeenCalled()
      })
    })
  })

  describe('設定の削除', () => {
    it('設定を削除できる', async () => {
      const user = userEvent.setup()

      const mockSettings = [
        {
          id: 1,
          list_id: 10,
          setting_type: NoSendSettingType.DAY_OF_WEEK,
          name: '休日送信禁止',
          description: '',
          is_enabled: true,
          day_of_week_list: [DayOfWeek.SATURDAY, DayOfWeek.SUNDAY],
          time_start: null,
          time_end: null,
          specific_date: null,
          date_range_start: null,
          date_range_end: null,
        },
      ]

      ;(getNoSendSettings as jest.Mock).mockResolvedValue({
        success: true,
        data: mockSettings,
      })

      ;(deleteNoSendSetting as jest.Mock).mockResolvedValue({
        success: true,
      })

      // window.confirmのモック
      global.confirm = jest.fn(() => true)

      render(<SettingsPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText('休日送信禁止')).toBeInTheDocument()
      })

      // 削除ボタンをクリック
      const deleteButton = screen.getByText('削除')
      await user.click(deleteButton)

      await waitFor(() => {
        expect(deleteNoSendSetting).toHaveBeenCalledWith(1)
      })
    })

    it('削除確認でキャンセルした場合は削除しない', async () => {
      const user = userEvent.setup()

      const mockSettings = [
        {
          id: 1,
          list_id: 10,
          setting_type: NoSendSettingType.DAY_OF_WEEK,
          name: '休日送信禁止',
          description: '',
          is_enabled: true,
          day_of_week_list: [DayOfWeek.SATURDAY, DayOfWeek.SUNDAY],
          time_start: null,
          time_end: null,
          specific_date: null,
          date_range_start: null,
          date_range_end: null,
        },
      ]

      ;(getNoSendSettings as jest.Mock).mockResolvedValue({
        success: true,
        data: mockSettings,
      })

      // window.confirmのモック（キャンセル）
      global.confirm = jest.fn(() => false)

      render(<SettingsPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText('休日送信禁止')).toBeInTheDocument()
      })

      // 削除ボタンをクリック
      const deleteButton = screen.getByText('削除')
      await user.click(deleteButton)

      // 削除されないことを確認
      expect(deleteNoSendSetting).not.toHaveBeenCalled()
    })
  })

  describe('設定タイプ別の表示', () => {
    it('時間帯設定を正しく表示する', async () => {
      const mockSettings = [
        {
          id: 2,
          list_id: 10,
          setting_type: NoSendSettingType.TIME_RANGE,
          name: '夜間送信禁止',
          description: '',
          is_enabled: true,
          day_of_week_list: null,
          time_start: '22:00:00',
          time_end: '08:00:00',
          specific_date: null,
          date_range_start: null,
          date_range_end: null,
        },
      ]

      ;(getNoSendSettings as jest.Mock).mockResolvedValue({
        success: true,
        data: mockSettings,
      })

      render(<SettingsPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText('夜間送信禁止')).toBeInTheDocument()
        expect(screen.getByText('22:00 〜 08:00')).toBeInTheDocument()
      })
    })

    it('特定日付設定を正しく表示する', async () => {
      const mockSettings = [
        {
          id: 3,
          list_id: 10,
          setting_type: NoSendSettingType.SPECIFIC_DATE,
          name: '元日送信禁止',
          description: '',
          is_enabled: true,
          day_of_week_list: null,
          time_start: null,
          time_end: null,
          specific_date: '2025-01-01',
          date_range_start: null,
          date_range_end: null,
        },
      ]

      ;(getNoSendSettings as jest.Mock).mockResolvedValue({
        success: true,
        data: mockSettings,
      })

      render(<SettingsPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText('元日送信禁止')).toBeInTheDocument()
        expect(screen.getByText('2025-01-01')).toBeInTheDocument()
      })
    })

    it('期間設定を正しく表示する', async () => {
      const mockSettings = [
        {
          id: 4,
          list_id: 10,
          setting_type: NoSendSettingType.SPECIFIC_DATE,
          name: '年末年始送信禁止',
          description: '',
          is_enabled: true,
          day_of_week_list: null,
          time_start: null,
          time_end: null,
          specific_date: null,
          date_range_start: '2025-12-29',
          date_range_end: '2026-01-03',
        },
      ]

      ;(getNoSendSettings as jest.Mock).mockResolvedValue({
        success: true,
        data: mockSettings,
      })

      render(<SettingsPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText('年末年始送信禁止')).toBeInTheDocument()
        expect(
          screen.getByText('2025-12-29 〜 2026-01-03')
        ).toBeInTheDocument()
      })
    })
  })
})
