/**
 * ロギングユーティリティ
 *
 * セキュリティ:
 * - 開発環境と本番環境で異なるログレベルを使用
 * - 本番環境では機密情報を含むスタックトレースを出力しない
 * - エラー監視サービスとの統合をサポート
 */

/**
 * ログレベル
 */
export type LogLevel = 'debug' | 'info' | 'warn' | 'error'

/**
 * 環境判定
 */
const isDevelopment = process.env.NODE_ENV === 'development'
const isProduction = process.env.NODE_ENV === 'production'

/**
 * エラーをログに記録する
 *
 * 開発環境: 詳細なエラー情報をconsole.errorに出力
 * 本番環境: エラーメッセージのみをログに記録し、詳細はエラー監視サービスに送信
 *
 * @param message - エラーメッセージ
 * @param error - エラーオブジェクト
 * @param context - 追加のコンテキスト情報
 */
export function logError(message: string, error?: unknown, context?: Record<string, unknown>) {
  if (isDevelopment) {
    // 開発環境: 詳細な情報を出力
    console.error(`[ERROR] ${message}`, error, context)
  } else {
    // 本番環境: メッセージのみを出力
    console.error(`[ERROR] ${message}`)

    // TODO: エラー監視サービスに送信（Sentry、Datadog等）
    // if (typeof window !== 'undefined' && window.Sentry) {
    //   window.Sentry.captureException(error, {
    //     tags: { message },
    //     extra: context,
    //   })
    // }
  }
}

/**
 * 警告をログに記録する
 *
 * @param message - 警告メッセージ
 * @param context - 追加のコンテキスト情報
 */
export function logWarn(message: string, context?: Record<string, unknown>) {
  if (isDevelopment) {
    console.warn(`[WARN] ${message}`, context)
  } else {
    console.warn(`[WARN] ${message}`)
  }
}

/**
 * 情報をログに記録する
 *
 * @param message - 情報メッセージ
 * @param context - 追加のコンテキスト情報
 */
export function logInfo(message: string, context?: Record<string, unknown>) {
  if (isDevelopment) {
    console.info(`[INFO] ${message}`, context)
  } else {
    console.info(`[INFO] ${message}`)
  }
}

/**
 * デバッグ情報をログに記録する
 * 本番環境では出力されない
 *
 * @param message - デバッグメッセージ
 * @param data - デバッグデータ
 */
export function logDebug(message: string, data?: unknown) {
  if (isDevelopment) {
    console.debug(`[DEBUG] ${message}`, data)
  }
}

/**
 * API エラーをログに記録する
 *
 * @param endpoint - APIエンドポイント
 * @param status - HTTPステータスコード
 * @param error - エラーオブジェクト
 */
export function logApiError(endpoint: string, status: number, error: unknown) {
  const message = `API Error: ${endpoint} (${status})`

  if (isDevelopment) {
    console.error(`[API ERROR] ${message}`, error)
  } else {
    console.error(`[API ERROR] ${message}`)

    // TODO: エラー監視サービスに送信
  }
}

/**
 * 認証エラーをログに記録する
 *
 * セキュリティ上の理由から、詳細な情報は記録しない
 *
 * @param message - エラーメッセージ
 */
export function logAuthError(message: string) {
  // 本番環境・開発環境ともに、認証エラーの詳細は記録しない
  console.error(`[AUTH ERROR] ${message}`)

  // TODO: セキュリティ監査ログに記録
  if (isProduction) {
    // 本番環境では、セキュリティイベントとして記録
    // 例: 異常なログイン試行、権限昇格の試み等
  }
}

/**
 * パフォーマンスメトリクスをログに記録する
 *
 * @param label - メトリクス名
 * @param duration - 処理時間（ミリ秒）
 */
export function logPerformance(label: string, duration: number) {
  if (isDevelopment) {
    console.log(`[PERF] ${label}: ${duration.toFixed(2)}ms`)
  }

  // TODO: パフォーマンス監視サービスに送信（New Relic、Datadog等）
}
