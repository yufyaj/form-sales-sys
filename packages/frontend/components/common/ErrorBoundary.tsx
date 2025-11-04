'use client'

import { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

/**
 * エラーバウンダリコンポーネント
 * 予期しないエラーをキャッチし、ユーザーフレンドリーなエラー画面を表示
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // エラーをコンソールに記録
    console.error('エラーが発生しました:', error, errorInfo)

    // 本番環境ではエラーログサービスに送信（例: Sentry）
    if (process.env.NODE_ENV === 'production') {
      // TODO: エラーログサービスへの送信を実装
      // Example: Sentry.captureException(error, { contexts: { react: errorInfo } })
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
          <div className="w-full max-w-md text-center">
            <div className="mb-4 text-6xl">⚠️</div>
            <h1 className="mb-2 text-2xl font-bold text-gray-900">
              エラーが発生しました
            </h1>
            <p className="mb-6 text-gray-600">
              ページの読み込み中に問題が発生しました。
              <br />
              お手数ですが、ページを再読み込みしてください。
            </p>
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mb-6 rounded-lg bg-red-50 p-4 text-left">
                <summary className="cursor-pointer font-semibold text-red-900">
                  エラー詳細（開発環境のみ表示）
                </summary>
                <pre className="mt-2 overflow-auto text-xs text-red-800">
                  {this.state.error.toString()}
                </pre>
              </details>
            )}
            <button
              onClick={() => window.location.reload()}
              className="rounded-lg bg-blue-600 px-6 py-3 text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              ページを再読み込み
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
