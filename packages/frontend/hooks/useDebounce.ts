import { useEffect, useState } from 'react'

/**
 * デバウンスフック
 *
 * 入力値の変更を遅延させることでパフォーマンスを最適化
 * 検索ボックスやフィルタなど、頻繁に変更される値に使用
 *
 * @param value - デバウンスさせる値
 * @param delay - 遅延時間（ミリ秒）
 * @returns デバウンスされた値
 */
export function useDebounce<T>(value: T, delay: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    // 値が変更されたらタイマーをセット
    const timer = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    // クリーンアップ関数で前のタイマーをキャンセル
    return () => {
      clearTimeout(timer)
    }
  }, [value, delay])

  return debouncedValue
}
