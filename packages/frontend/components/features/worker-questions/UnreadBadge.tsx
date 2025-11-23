/**
 * 未読質問数バッジコンポーネント
 *
 * TanStack Queryを使用してポーリングで未読数を取得
 */

"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchUnreadQuestionCount } from "@/lib/workerQuestionApi";

/**
 * 未読質問数バッジ
 *
 * 30秒ごとに未読数を自動更新
 */
export default function UnreadBadge() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["workerQuestions", "unreadCount"],
    queryFn: fetchUnreadQuestionCount,
    refetchInterval: 30000, // 30秒ごとにポーリング
    staleTime: 25000, // 25秒間はキャッシュを使用
  });

  // ローディング中やエラー時は非表示
  if (isLoading || error || !data) {
    return null;
  }

  // 未読がない場合は非表示
  if (data.unreadCount === 0) {
    return null;
  }

  return (
    <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-600 rounded-full">
      {data.unreadCount > 99 ? "99+" : data.unreadCount}
    </span>
  );
}
