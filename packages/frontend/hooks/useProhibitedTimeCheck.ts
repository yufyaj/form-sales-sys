/**
 * 禁止時間帯チェックカスタムフック
 * リアルタイムで送信禁止時間帯を判定する
 *
 * セキュリティ対策:
 * - クライアント側のチェックはUI表示用
 * - 実際の送信可否はサーバー側で再度検証すること
 */

'use client'

import { useState, useEffect, useCallback } from 'react'
import type { NoSendSetting, NoSendSettingType } from '@/types/noSendSetting'
import type { ProhibitedTimeCheckResult } from '@/types/workRecord'

/**
 * 現在時刻が禁止時間帯かどうかをチェック
 *
 * @param settings 送信禁止設定の配列
 * @param checkInterval チェック間隔（ミリ秒）デフォルト: 60秒
 * @returns 禁止時間帯チェック結果
 */
export function useProhibitedTimeCheck(
  settings: NoSendSetting[],
  checkInterval: number = 60000
): ProhibitedTimeCheckResult {
  const [result, setResult] = useState<ProhibitedTimeCheckResult>({
    isProhibited: false,
    reasons: [],
  })

  // 禁止時間帯チェックロジック
  const checkProhibitedTime = useCallback((): ProhibitedTimeCheckResult => {
    const now = new Date()
    const reasons: string[] = []
    let nextAllowedTime: Date | undefined

    // 有効な設定のみをフィルター
    const activeSettings = settings.filter((s) => s.is_enabled && !s.deleted_at)

    for (const setting of activeSettings) {
      switch (setting.setting_type) {
        case 'day_of_week' as NoSendSettingType: {
          // 曜日チェック（ISO 8601: 月=1, 日=7）
          const currentDayOfWeek = now.getDay() === 0 ? 7 : now.getDay()
          if (
            'day_of_week_list' in setting &&
            setting.day_of_week_list?.includes(currentDayOfWeek)
          ) {
            reasons.push(`${setting.name}（曜日制限）`)
            // 次回許可時刻は翌日0時
            const nextDay = new Date(now)
            nextDay.setDate(nextDay.getDate() + 1)
            nextDay.setHours(0, 0, 0, 0)
            if (!nextAllowedTime || nextDay < nextAllowedTime) {
              nextAllowedTime = nextDay
            }
          }
          break
        }

        case 'time_range' as NoSendSettingType: {
          // 時間帯チェック
          if ('time_start' in setting && 'time_end' in setting) {
            const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`
            const timeStart = setting.time_start
            const timeEnd = setting.time_end

            if (timeStart && timeEnd) {
              // 時間範囲が日をまたぐ場合の処理
              if (timeStart <= timeEnd) {
                // 通常の範囲（例: 09:00 ~ 18:00）
                if (currentTime >= timeStart && currentTime <= timeEnd) {
                  reasons.push(`${setting.name}（時間帯制限: ${timeStart}～${timeEnd}）`)
                  // 次回許可時刻は終了時刻
                  const [endHour, endMinute, endSecond] = timeEnd.split(':').map(Number)
                  const endTime = new Date(now)
                  endTime.setHours(endHour, endMinute, endSecond, 0)
                  if (endTime <= now) {
                    endTime.setDate(endTime.getDate() + 1)
                  }
                  if (!nextAllowedTime || endTime < nextAllowedTime) {
                    nextAllowedTime = endTime
                  }
                }
              } else {
                // 日をまたぐ範囲（例: 22:00 ~ 06:00）
                if (currentTime >= timeStart || currentTime <= timeEnd) {
                  reasons.push(`${setting.name}（時間帯制限: ${timeStart}～${timeEnd}）`)
                  // 次回許可時刻は終了時刻
                  const [endHour, endMinute, endSecond] = timeEnd.split(':').map(Number)
                  const endTime = new Date(now)
                  endTime.setHours(endHour, endMinute, endSecond, 0)
                  if (endTime <= now) {
                    endTime.setDate(endTime.getDate() + 1)
                  }
                  if (!nextAllowedTime || endTime < nextAllowedTime) {
                    nextAllowedTime = endTime
                  }
                }
              }
            }
          }
          break
        }

        case 'specific_date' as NoSendSettingType: {
          // 特定日付チェック
          const today = now.toISOString().split('T')[0] // YYYY-MM-DD

          // 単一日付チェック
          if ('specific_date' in setting && setting.specific_date) {
            if (today === setting.specific_date) {
              reasons.push(`${setting.name}（特定日: ${setting.specific_date}）`)
              // 次回許可時刻は翌日0時
              const tomorrow = new Date(now)
              tomorrow.setDate(tomorrow.getDate() + 1)
              tomorrow.setHours(0, 0, 0, 0)
              if (!nextAllowedTime || tomorrow < nextAllowedTime) {
                nextAllowedTime = tomorrow
              }
            }
          }

          // 期間チェック
          if (
            'date_range_start' in setting &&
            'date_range_end' in setting &&
            setting.date_range_start &&
            setting.date_range_end
          ) {
            if (today >= setting.date_range_start && today <= setting.date_range_end) {
              reasons.push(
                `${setting.name}（期間: ${setting.date_range_start}～${setting.date_range_end}）`
              )
              // 次回許可時刻は期間終了日の翌日0時
              const endDate = new Date(setting.date_range_end)
              endDate.setDate(endDate.getDate() + 1)
              endDate.setHours(0, 0, 0, 0)
              if (!nextAllowedTime || endDate < nextAllowedTime) {
                nextAllowedTime = endDate
              }
            }
          }
          break
        }
      }
    }

    return {
      isProhibited: reasons.length > 0,
      reasons,
      nextAllowedTime,
    }
  }, [settings])

  // 初回チェックと定期チェック
  useEffect(() => {
    // 初回実行
    setResult(checkProhibitedTime())

    // 定期実行
    const intervalId = setInterval(() => {
      setResult(checkProhibitedTime())
    }, checkInterval)

    // クリーンアップ
    return () => {
      clearInterval(intervalId)
    }
  }, [checkProhibitedTime, checkInterval])

  return result
}
