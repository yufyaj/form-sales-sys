'use client'

import { use, useEffect, useState } from 'react'
import { useRouter, notFound } from 'next/navigation'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import DayOfWeekSelector from '@/components/features/noSendSettings/DayOfWeekSelector'
import TimeRangeInput from '@/components/features/noSendSettings/TimeRangeInput'
import DateInput from '@/components/features/noSendSettings/DateInput'
import {
  getNoSendSettings,
  createDayOfWeekSetting,
  createTimeRangeSetting,
  createSpecificDateSetting,
  createDateRangeSetting,
  deleteNoSendSetting,
} from '@/lib/actions/noSendSettings'
import {
  NoSendSetting,
  NoSendSettingType,
  DayOfWeek,
  DAY_OF_WEEK_LABELS,
} from '@/types/noSendSetting'
import { validateTimeFormat, validateDateRange } from '@/lib/utils'

interface SettingsPageProps {
  params: Promise<{
    id: string
    listId: string
  }>
}

/**
 * リスト送信禁止設定ページ
 */
export default function SettingsPage({ params }: SettingsPageProps) {
  const router = useRouter()
  const { id, listId } = use(params)
  const projectId = parseInt(id, 10)
  const listIdNum = parseInt(listId, 10)

  const [settings, setSettings] = useState<NoSendSetting[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [formType, setFormType] = useState<NoSendSettingType>(
    NoSendSettingType.DAY_OF_WEEK
  )

  // フォームの状態
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    dayOfWeekList: [] as DayOfWeek[],
    timeStart: '',
    timeEnd: '',
    specificDate: '',
    dateRangeStart: '',
    dateRangeEnd: '',
    isDateRange: false,
  })

  if (isNaN(projectId) || isNaN(listIdNum)) {
    notFound()
  }

  // 設定一覧を取得
  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const result = await getNoSendSettings(listIdNum)

        if (result.success && result.data) {
          setSettings(result.data)
        } else {
          setError(result.error || '設定の取得に失敗しました')
        }
      } catch (err) {
        console.error('Failed to fetch settings:', err)
        setError('データの取得に失敗しました')
      } finally {
        setIsLoading(false)
      }
    }

    fetchSettings()
  }, [listIdNum])

  /**
   * 設定を作成
   */
  const handleCreateSetting = async () => {
    try {
      setIsLoading(true)
      setError(null)

      // 設定名のバリデーション
      if (!formData.name || formData.name.trim().length === 0) {
        setError('設定名を入力してください')
        setIsLoading(false)
        return
      }

      let result

      switch (formType) {
        case NoSendSettingType.DAY_OF_WEEK:
          // 曜日選択の必須検証
          if (formData.dayOfWeekList.length === 0) {
            setError('少なくとも1つの曜日を選択してください')
            setIsLoading(false)
            return
          }

          result = await createDayOfWeekSetting({
            list_id: listIdNum,
            name: formData.name,
            description: formData.description || undefined,
            day_of_week_list: formData.dayOfWeekList,
          })
          break

        case NoSendSettingType.TIME_RANGE:
          // 時刻フォーマットの検証
          if (!validateTimeFormat(formData.timeStart)) {
            setError('開始時刻は00:00から23:59の形式で入力してください')
            setIsLoading(false)
            return
          }
          if (!validateTimeFormat(formData.timeEnd)) {
            setError('終了時刻は00:00から23:59の形式で入力してください')
            setIsLoading(false)
            return
          }

          result = await createTimeRangeSetting({
            list_id: listIdNum,
            name: formData.name,
            description: formData.description || undefined,
            time_start: formData.timeStart + ':00', // HH:MM:SS形式に変換
            time_end: formData.timeEnd + ':00',
          })
          break

        case NoSendSettingType.SPECIFIC_DATE:
          if (formData.isDateRange) {
            // 期間の妥当性検証
            if (!formData.dateRangeStart || !formData.dateRangeEnd) {
              setError('期間の開始日と終了日を両方入力してください')
              setIsLoading(false)
              return
            }
            if (!validateDateRange(formData.dateRangeStart, formData.dateRangeEnd)) {
              setError('開始日は終了日より前の日付を指定してください')
              setIsLoading(false)
              return
            }

            result = await createDateRangeSetting({
              list_id: listIdNum,
              name: formData.name,
              description: formData.description || undefined,
              date_range_start: formData.dateRangeStart,
              date_range_end: formData.dateRangeEnd,
            })
          } else {
            // 単一日付の必須検証
            if (!formData.specificDate) {
              setError('日付を入力してください')
              setIsLoading(false)
              return
            }

            result = await createSpecificDateSetting({
              list_id: listIdNum,
              name: formData.name,
              description: formData.description || undefined,
              specific_date: formData.specificDate,
            })
          }
          break
      }

      if (result && result.success && result.data) {
        // 成功: 設定一覧に追加
        setSettings([...settings, result.data])
        setShowForm(false)
        // フォームをリセット
        setFormData({
          name: '',
          description: '',
          dayOfWeekList: [],
          timeStart: '',
          timeEnd: '',
          specificDate: '',
          dateRangeStart: '',
          dateRangeEnd: '',
          isDateRange: false,
        })
      } else {
        setError(result?.error || '設定の作成に失敗しました')
      }
    } catch (err) {
      console.error('Failed to create setting:', err)
      setError('設定の作成に失敗しました')
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * 設定を削除
   */
  const handleDeleteSetting = async (settingId: number) => {
    if (!confirm('この設定を削除してもよろしいですか?')) {
      return
    }

    try {
      setIsLoading(true)
      setError(null)

      const result = await deleteNoSendSetting(settingId)

      if (result.success) {
        // 成功: 設定一覧から削除
        setSettings(settings.filter((s) => s.id !== settingId))
      } else {
        setError(result.error || '設定の削除に失敗しました')
      }
    } catch (err) {
      console.error('Failed to delete setting:', err)
      setError('設定の削除に失敗しました')
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * 設定タイプに応じた表示テキストを生成
   */
  const formatSettingDisplay = (setting: NoSendSetting): string => {
    switch (setting.setting_type) {
      case NoSendSettingType.DAY_OF_WEEK:
        return setting.day_of_week_list
          .map((day) => DAY_OF_WEEK_LABELS[day])
          .join('、')

      case NoSendSettingType.TIME_RANGE:
        return `${setting.time_start.slice(0, 5)} 〜 ${setting.time_end.slice(0, 5)}`

      case NoSendSettingType.SPECIFIC_DATE:
        if (setting.specific_date) {
          return setting.specific_date
        } else if (setting.date_range_start && setting.date_range_end) {
          return `${setting.date_range_start} 〜 ${setting.date_range_end}`
        }
        return ''

      default:
        return ''
    }
  }

  if (isLoading && settings.length === 0) {
    return (
      <div className="container mx-auto max-w-4xl py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight">送信禁止設定</h1>
          <p className="text-muted-foreground">
            送信を禁止する曜日・時間帯・日付を設定します
          </p>
        </div>
        <Card>
          <div className="flex h-64 items-center justify-center">
            <div className="text-muted-foreground">読み込み中...</div>
          </div>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto max-w-4xl py-8 space-y-6">
      {/* ヘッダー */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">送信禁止設定</h1>
          <p className="text-muted-foreground">
            送信を禁止する曜日・時間帯・日付を設定します
          </p>
        </div>
        <Button
          onClick={() => setShowForm(!showForm)}
          variant={showForm ? 'secondary' : 'default'}
        >
          {showForm ? 'キャンセル' : '新規作成'}
        </Button>
      </div>

      {/* エラーメッセージ */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* 新規作成フォーム */}
      {showForm && (
        <Card>
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">新しい設定を追加</h2>

            {/* 設定タイプ選択 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                設定タイプ
              </label>
              <div className="flex gap-2">
                <Button
                  variant={
                    formType === NoSendSettingType.DAY_OF_WEEK
                      ? 'default'
                      : 'secondary'
                  }
                  onClick={() => setFormType(NoSendSettingType.DAY_OF_WEEK)}
                >
                  曜日指定
                </Button>
                <Button
                  variant={
                    formType === NoSendSettingType.TIME_RANGE
                      ? 'default'
                      : 'secondary'
                  }
                  onClick={() => setFormType(NoSendSettingType.TIME_RANGE)}
                >
                  時間帯指定
                </Button>
                <Button
                  variant={
                    formType === NoSendSettingType.SPECIFIC_DATE
                      ? 'default'
                      : 'secondary'
                  }
                  onClick={() => setFormType(NoSendSettingType.SPECIFIC_DATE)}
                >
                  日付指定
                </Button>
              </div>
            </div>

            {/* 設定名 */}
            <div>
              <label
                htmlFor="setting-name"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                設定名
              </label>
              <input
                type="text"
                id="setting-name"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                maxLength={100}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="例: 休日送信禁止"
              />
            </div>

            {/* 説明 */}
            <div>
              <label
                htmlFor="setting-description"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                説明（任意）
              </label>
              <textarea
                id="setting-description"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="この設定の詳細説明"
              />
            </div>

            {/* 設定タイプ別のフォーム */}
            {formType === NoSendSettingType.DAY_OF_WEEK && (
              <DayOfWeekSelector
                label="送信禁止曜日"
                value={formData.dayOfWeekList}
                onChange={(value) =>
                  setFormData({ ...formData, dayOfWeekList: value })
                }
                showSelectAll
              />
            )}

            {formType === NoSendSettingType.TIME_RANGE && (
              <TimeRangeInput
                label="送信禁止時間帯"
                timeStart={formData.timeStart}
                timeEnd={formData.timeEnd}
                onTimeStartChange={(value) =>
                  setFormData({ ...formData, timeStart: value })
                }
                onTimeEndChange={(value) =>
                  setFormData({ ...formData, timeEnd: value })
                }
              />
            )}

            {formType === NoSendSettingType.SPECIFIC_DATE && (
              <div className="space-y-4">
                {/* 単一日付 or 期間選択 */}
                <div className="flex gap-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      checked={!formData.isDateRange}
                      onChange={() =>
                        setFormData({ ...formData, isDateRange: false })
                      }
                      className="mr-2"
                    />
                    単一日付
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      checked={formData.isDateRange}
                      onChange={() =>
                        setFormData({ ...formData, isDateRange: true })
                      }
                      className="mr-2"
                    />
                    期間指定
                  </label>
                </div>

                {formData.isDateRange ? (
                  <DateInput
                    mode="range"
                    label="送信禁止期間"
                    startDate={formData.dateRangeStart}
                    endDate={formData.dateRangeEnd}
                    onStartDateChange={(value) =>
                      setFormData({ ...formData, dateRangeStart: value })
                    }
                    onEndDateChange={(value) =>
                      setFormData({ ...formData, dateRangeEnd: value })
                    }
                  />
                ) : (
                  <DateInput
                    label="送信禁止日"
                    value={formData.specificDate}
                    onChange={(value) =>
                      setFormData({ ...formData, specificDate: value })
                    }
                  />
                )}
              </div>
            )}

            {/* 保存ボタン */}
            <div className="flex justify-end gap-2">
              <Button variant="secondary" onClick={() => setShowForm(false)}>
                キャンセル
              </Button>
              <Button
                variant="default"
                onClick={handleCreateSetting}
                disabled={isLoading || !formData.name}
              >
                保存
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* 設定一覧 */}
      <Card>
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">設定一覧</h2>

          {settings.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              設定がまだ登録されていません
            </p>
          ) : (
            <div className="space-y-2">
              {settings.map((setting) => (
                <div
                  key={setting.id}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium">{setting.name}</h3>
                      <span
                        className={`px-2 py-1 text-xs rounded ${
                          setting.is_enabled
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {setting.is_enabled ? '有効' : '無効'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                      {formatSettingDisplay(setting)}
                    </p>
                    {setting.description && (
                      <p className="text-xs text-gray-400 mt-1">
                        {setting.description}
                      </p>
                    )}
                  </div>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => setting.id && handleDeleteSetting(setting.id)}
                  >
                    削除
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}
