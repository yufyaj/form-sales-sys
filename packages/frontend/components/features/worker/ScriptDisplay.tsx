'use client'

import React, { useState } from 'react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { FileText, Copy, Check } from 'lucide-react'

/**
 * スクリプト表示のプロパティ
 */
export interface ScriptDisplayProps {
  /**
   * スクリプトタイトル（件名）
   */
  title: string
  /**
   * スクリプト本文
   */
  content: string
}

/**
 * スクリプト表示・コピーコンポーネント
 *
 * ワーカー作業画面でスクリプト（営業文章等）を表示し、
 * クリップボードにコピーする機能を提供します。
 */
export function ScriptDisplay({ title, content }: ScriptDisplayProps) {
  const [isCopied, setIsCopied] = useState(false)

  /**
   * クリップボードにスクリプトをコピー
   */
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content)
      setIsCopied(true)

      // 2秒後にコピー状態をリセット
      setTimeout(() => {
        setIsCopied(false)
      }, 2000)
    } catch (error) {
      console.error('クリップボードへのコピーに失敗しました:', error)
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            <CardTitle>スクリプト</CardTitle>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleCopy}
            className="min-w-[100px]"
          >
            {isCopied ? (
              <>
                <Check className="h-4 w-4" />
                コピー済み
              </>
            ) : (
              <>
                <Copy className="h-4 w-4" />
                コピー
              </>
            )}
          </Button>
        </div>
        <CardDescription>営業文章・スクリプト本文</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* タイトル（件名） */}
        <div>
          <p className="text-sm font-medium text-muted-foreground mb-2">
            件名
          </p>
          <div className="p-3 bg-muted rounded-md">
            <p className="text-base font-semibold">{title}</p>
          </div>
        </div>

        {/* 本文 */}
        <div>
          <p className="text-sm font-medium text-muted-foreground mb-2">
            本文
          </p>
          <div className="p-4 bg-muted rounded-md border border-border">
            <pre className="text-sm whitespace-pre-wrap font-sans leading-relaxed">
              {content}
            </pre>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
