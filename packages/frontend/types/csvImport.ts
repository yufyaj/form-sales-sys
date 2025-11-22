/**
 * CSVインポート関連の型定義
 */

/**
 * CSVインポートのステップ
 */
export type CSVImportStep = 'upload' | 'mapping' | 'preview' | 'confirm'

/**
 * CSVカラム情報
 */
export interface CSVColumn {
  name: string // CSVのカラム名
  index: number // カラムのインデックス
  sampleValues: string[] // サンプルデータ（最初の3件程度）
}

/**
 * カラムマッピング
 * CSVのカラムとシステムのフィールドの対応関係
 */
export interface ColumnMapping {
  csvColumn: string // CSVのカラム名
  systemField: string | null // システムのフィールド名（未マッピングの場合はnull）
}

/**
 * CSVインポートのバリデーションエラー
 */
export interface CSVValidationError {
  row: number // 行番号（1から始まる）
  column?: string // エラーが発生したカラム
  message: string // エラーメッセージ
  value?: any // エラーが発生した値
}

/**
 * CSVインポート状態
 */
export interface CSVImportState {
  currentStep: CSVImportStep
  file: File | null
  rawData: any[] // パース後の生データ
  columns: CSVColumn[] // 検出されたカラム情報
  columnMappings: Record<string, string | null> // カラムマッピング（CSVカラム名 -> システムフィールド名）
  validationErrors: CSVValidationError[] // バリデーションエラー
  isProcessing: boolean // 処理中フラグ
  progress: number // 進捗率（0-100）
}

/**
 * システムフィールド定義
 */
export interface SystemField {
  id: string // フィールドID
  label: string // フィールドラベル
  required: boolean // 必須フラグ
  type: 'string' | 'number' | 'email' | 'url' | 'date' // データ型
  description?: string // フィールドの説明
}

/**
 * CSVインポート設定の制限値
 */
export const CSV_LIMITS = {
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  MAX_ROWS: 100000, // 10万行
  CHUNK_SIZE: 1000, // チャンクサイズ
  PREVIEW_ROWS: 100, // プレビュー表示行数
  SAMPLE_VALUES_COUNT: 3, // サンプル値の表示数
} as const

/**
 * CSVインポート結果
 */
export interface CSVImportResult {
  success: boolean
  totalRows: number // 総行数
  importedRows: number // インポート成功行数
  errorRows: number // エラー行数
  errors: CSVValidationError[] // エラー詳細
}
