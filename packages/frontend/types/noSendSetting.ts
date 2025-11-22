/**
 * 送信禁止設定の型定義
 * バックエンドAPIスキーマに準拠
 */

/**
 * 曜日の列挙型（ISO 8601準拠）
 */
export enum DayOfWeek {
  MONDAY = 1,
  TUESDAY = 2,
  WEDNESDAY = 3,
  THURSDAY = 4,
  FRIDAY = 5,
  SATURDAY = 6,
  SUNDAY = 7,
}

/**
 * 曜日のラベルマップ
 */
export const DAY_OF_WEEK_LABELS: Record<DayOfWeek, string> = {
  [DayOfWeek.MONDAY]: '月',
  [DayOfWeek.TUESDAY]: '火',
  [DayOfWeek.WEDNESDAY]: '水',
  [DayOfWeek.THURSDAY]: '木',
  [DayOfWeek.FRIDAY]: '金',
  [DayOfWeek.SATURDAY]: '土',
  [DayOfWeek.SUNDAY]: '日',
}

/**
 * 設定種別の列挙型
 */
export enum NoSendSettingType {
  DAY_OF_WEEK = 'day_of_week',
  TIME_RANGE = 'time_range',
  SPECIFIC_DATE = 'specific_date',
}

/**
 * 送信禁止設定の基本型
 */
export interface NoSendSettingBase {
  id?: number
  list_id: number
  setting_type: NoSendSettingType
  name: string
  description?: string | null
  is_enabled: boolean
  created_at?: string
  updated_at?: string
  deleted_at?: string | null
}

/**
 * 曜日設定
 */
export interface NoSendSettingDayOfWeek extends NoSendSettingBase {
  setting_type: NoSendSettingType.DAY_OF_WEEK
  day_of_week_list: DayOfWeek[]
  time_start?: null
  time_end?: null
  specific_date?: null
  date_range_start?: null
  date_range_end?: null
}

/**
 * 時間帯設定
 */
export interface NoSendSettingTimeRange extends NoSendSettingBase {
  setting_type: NoSendSettingType.TIME_RANGE
  time_start: string // HH:MM:SS形式
  time_end: string // HH:MM:SS形式
  day_of_week_list?: null
  specific_date?: null
  date_range_start?: null
  date_range_end?: null
}

/**
 * 特定日付設定（単一日付）
 */
export interface NoSendSettingSpecificDate extends NoSendSettingBase {
  setting_type: NoSendSettingType.SPECIFIC_DATE
  specific_date: string // YYYY-MM-DD形式
  date_range_start?: null
  date_range_end?: null
  day_of_week_list?: null
  time_start?: null
  time_end?: null
}

/**
 * 特定日付設定（期間指定）
 */
export interface NoSendSettingDateRange extends NoSendSettingBase {
  setting_type: NoSendSettingType.SPECIFIC_DATE
  date_range_start: string // YYYY-MM-DD形式
  date_range_end: string // YYYY-MM-DD形式
  specific_date?: null
  day_of_week_list?: null
  time_start?: null
  time_end?: null
}

/**
 * 送信禁止設定の型（全タイプのユニオン）
 */
export type NoSendSetting =
  | NoSendSettingDayOfWeek
  | NoSendSettingTimeRange
  | NoSendSettingSpecificDate
  | NoSendSettingDateRange

/**
 * 曜日設定作成リクエスト
 */
export interface CreateDayOfWeekSettingRequest {
  list_id: number
  name: string
  description?: string
  is_enabled?: boolean
  day_of_week_list: DayOfWeek[]
}

/**
 * 時間帯設定作成リクエスト
 */
export interface CreateTimeRangeSettingRequest {
  list_id: number
  name: string
  description?: string
  is_enabled?: boolean
  time_start: string
  time_end: string
}

/**
 * 特定日付設定作成リクエスト（単一日付）
 */
export interface CreateSpecificDateSettingRequest {
  list_id: number
  name: string
  description?: string
  is_enabled?: boolean
  specific_date: string
}

/**
 * 特定日付設定作成リクエスト（期間指定）
 */
export interface CreateDateRangeSettingRequest {
  list_id: number
  name: string
  description?: string
  is_enabled?: boolean
  date_range_start: string
  date_range_end: string
}

/**
 * 設定更新リクエスト
 */
export interface UpdateNoSendSettingRequest {
  name?: string
  description?: string | null
  is_enabled?: boolean
}
