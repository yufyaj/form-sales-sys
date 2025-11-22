/**
 * TanStack Query Provider
 *
 * アプリケーション全体でTanStack Queryを使用できるようにする
 */

"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

export function QueryProvider({ children }: { children: React.ReactNode }) {
  // クライアント側でQueryClientインスタンスを作成
  // useState内で作成することで、再レンダリング時に新しいインスタンスが作成されないようにする
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // デフォルトのクエリオプション
            staleTime: 60 * 1000, // 1分間はキャッシュを新鮮とみなす
            gcTime: 5 * 60 * 1000, // 5分間キャッシュを保持
            retry: (failureCount, error) => {
              // 認証エラー（401, 403）の場合はリトライしない
              if (
                error instanceof Error &&
                (error.message.includes('401') || error.message.includes('403'))
              ) {
                return false
              }
              return failureCount < 1
            },
            refetchOnWindowFocus: false, // ウィンドウフォーカス時の自動再取得を無効化
          },
          mutations: {
            // デフォルトのミューテーションオプション
            retry: 0, // ミューテーションは基本的にリトライしない
            onError: (error) => {
              // 認証エラーの場合はキャッシュをクリア
              if (
                error instanceof Error &&
                (error.message.includes('401') || error.message.includes('403'))
              ) {
                queryClient.clear()
              }
            },
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
