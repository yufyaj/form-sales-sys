'use client'

import React, { use } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { getAssignmentDetail } from '@/lib/api/assignments'
import { createWorkRecord } from '@/lib/api/workRecords'
import { CompanyInfoCard } from '@/components/features/worker/CompanyInfoCard'
import { ScriptDisplay } from '@/components/features/worker/ScriptDisplay'
import { WorkRecordForm } from '@/components/features/worker/WorkRecordForm'
import type { WorkRecordFormData } from '@/lib/validations/workRecord'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import Link from 'next/link'

/**
 * ページプロパティ
 */
interface WorkerAssignmentPageProps {
  params: Promise<{
    assignmentId: string
  }>
}

/**
 * ワーカー作業画面ページ
 *
 * 割り当てられた作業の詳細を表示し、作業記録を行います。
 * - 企業情報表示
 * - スクリプト表示・コピー
 * - 作業記録フォーム
 */
export default function WorkerAssignmentPage({
  params,
}: WorkerAssignmentPageProps) {
  const { assignmentId } = use(params)
  const router = useRouter()
  const queryClient = useQueryClient()

  // 割り当て詳細を取得
  const {
    data: assignment,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['assignment', assignmentId],
    queryFn: () => getAssignmentDetail(assignmentId),
  })

  // 作業記録作成のミューテーション
  const createWorkRecordMutation = useMutation({
    mutationFn: (data: WorkRecordFormData) => {
      if (!assignment) {
        throw new Error('割り当て情報が見つかりません')
      }

      // 送信済みまたは送信不可のリクエストを作成
      const baseData = {
        assignment_id: Number(assignmentId),
        started_at: new Date().toISOString(),
        completed_at: new Date().toISOString(),
        notes: data.notes,
      }

      if (data.status === 'sent') {
        return createWorkRecord(baseData)
      } else {
        return createWorkRecord({
          ...baseData,
          cannot_send_reason_id: data.cannot_send_reason_id!,
        })
      }
    },
    onSuccess: () => {
      // キャッシュを無効化
      queryClient.invalidateQueries({ queryKey: ['assignment', assignmentId] })
      queryClient.invalidateQueries({ queryKey: ['assignments'] })

      // ダッシュボードにリダイレクト
      router.push('/dashboard/worker')
    },
    onError: (error) => {
      console.error('作業記録の保存に失敗しました:', error)
      alert('作業記録の保存に失敗しました。もう一度お試しください。')
    },
  })

  // 作業記録フォーム送信ハンドラー
  const handleSubmitWorkRecord = (data: WorkRecordFormData) => {
    createWorkRecordMutation.mutate(data)
  }

  // ローディング表示
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  // エラー表示
  // セキュリティ: 403と404を区別しない統一メッセージで情報漏洩を防止
  if (error || !assignment) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <p className="text-destructive mb-4">
            割り当て情報が見つからないか、アクセス権限がありません。
          </p>
          <Button asChild variant="outline">
            <Link href="/dashboard/worker">
              <ArrowLeft className="h-4 w-4" />
              ダッシュボードに戻る
            </Link>
          </Button>
        </div>
      </div>
    )
  }

  // リスト項目が存在しない場合
  if (!assignment.listItems || assignment.listItems.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <p className="text-muted-foreground mb-4">
            作業対象の企業情報が見つかりませんでした。
          </p>
          <Button asChild variant="outline">
            <Link href="/dashboard/worker">
              <ArrowLeft className="h-4 w-4" />
              ダッシュボードに戻る
            </Link>
          </Button>
        </div>
      </div>
    )
  }

  // 最初のリスト項目を表示（Phase5では1件ずつの作業を想定）
  const currentItem = assignment.listItems[0]

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* ヘッダー */}
      <div className="mb-6">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/dashboard/worker">
            <ArrowLeft className="h-4 w-4" />
            ダッシュボードに戻る
          </Link>
        </Button>
        <h1 className="text-3xl font-bold mb-2">作業画面</h1>
        <p className="text-muted-foreground">
          {assignment.projectName} / {assignment.listName}
        </p>
      </div>

      {/* メインコンテンツ */}
      <div className="space-y-6">
        {/* 企業情報カード */}
        <CompanyInfoCard item={currentItem} />

        {/* スクリプト表示（スクリプトが存在する場合） */}
        {assignment.script && (
          <ScriptDisplay
            title={assignment.script.title}
            content={assignment.script.content}
          />
        )}

        {/* 作業記録フォーム */}
        <WorkRecordForm
          assignmentId={assignmentId}
          workerId={Number(assignment.workerId)}
          onSubmit={handleSubmitWorkRecord}
          isSubmitting={createWorkRecordMutation.isPending}
        />
      </div>
    </div>
  )
}
