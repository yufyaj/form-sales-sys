'use client'

import { use, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { ArrowLeft, Plus, Shield } from 'lucide-react'

import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { NgListDomainForm } from '@/components/features/ngList/NgListDomainForm'
import { NgListDomainTable } from '@/components/features/ngList/NgListDomainTable'
import { fetchNgListDomains } from '@/lib/api/ngListDomains'
import type { NgListDomain } from '@/types/ngListDomain'
import { transitions } from '@/lib/motion'

interface NgDomainsPageProps {
  params: Promise<{
    id: string
    listId: string
  }>
}

/**
 * NGリスト管理ページ
 * リストごとのNG（送信禁止）ドメインの登録・管理を行います
 */
export default function NgDomainsPage({ params }: NgDomainsPageProps) {
  const router = useRouter()
  const { id, listId } = use(params)
  const projectId = parseInt(id, 10)
  const listIdNum = parseInt(listId, 10)

  const [ngDomains, setNgDomains] = useState<NgListDomain[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [showForm, setShowForm] = useState(false)

  /**
   * NGドメイン一覧を取得
   */
  const fetchNgDomains = async () => {
    setIsLoading(true)
    setError('')

    try {
      const response = await fetchNgListDomains(listIdNum)
      setNgDomains(response.ngDomains)
    } catch (err) {
      console.error('NGドメイン取得エラー:', err)
      setError('NGドメインの取得に失敗しました')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchNgDomains()
  }, [listIdNum])

  /**
   * リスト詳細に戻る
   */
  const handleBackClick = () => {
    router.push(`/projects/${projectId}/lists`)
  }

  /**
   * フォーム表示切り替え
   */
  const handleToggleForm = () => {
    setShowForm(!showForm)
  }

  /**
   * 登録成功時の処理
   */
  const handleSuccess = () => {
    setShowForm(false)
    fetchNgDomains()
  }

  return (
    <div className="container mx-auto py-8">
      {/* ヘッダー */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={transitions.fast}
        className="mb-6"
      >
        <Button variant="outline" onClick={handleBackClick} className="mb-4">
          <ArrowLeft className="h-4 w-4" />
          リスト一覧に戻る
        </Button>

        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3">
              <Shield className="h-8 w-8 text-primary" />
              <h1 className="text-3xl font-bold tracking-tight">NGリスト管理</h1>
            </div>
            <p className="mt-2 text-muted-foreground">
              送信禁止ドメインの登録・管理を行います
            </p>
          </div>

          {!showForm && (
            <Button onClick={handleToggleForm}>
              <Plus className="h-4 w-4" />
              NGドメイン追加
            </Button>
          )}
        </div>
      </motion.div>

      {/* エラー表示 */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 rounded-md bg-destructive/10 p-4 text-sm text-destructive"
          role="alert"
        >
          {error}
        </motion.div>
      )}

      {/* NGドメイン登録フォーム */}
      {showForm && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={transitions.fast}
          className="mb-8"
        >
          <Card className="p-6">
            <h2 className="mb-4 text-xl font-semibold">NGドメイン登録</h2>
            <NgListDomainForm
              listId={listIdNum}
              onSuccess={handleSuccess}
              onCancel={handleToggleForm}
            />
          </Card>
        </motion.div>
      )}

      {/* NGドメイン一覧 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ ...transitions.fast, delay: 0.1 }}
      >
        <Card className="p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold">登録済みNGドメイン</h2>
            <div className="text-sm text-muted-foreground">
              合計: {ngDomains.length}件
            </div>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
            </div>
          ) : (
            <NgListDomainTable ngDomains={ngDomains} onDelete={fetchNgDomains} />
          )}
        </Card>
      </motion.div>

      {/* 説明カード */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ ...transitions.fast, delay: 0.2 }}
        className="mt-6"
      >
        <Card className="bg-muted/50 p-6">
          <h3 className="mb-2 font-semibold">NGリストについて</h3>
          <ul className="space-y-1 text-sm text-muted-foreground">
            <li>• NGドメインに登録されたドメインへのメール送信は自動的にブロックされます</li>
            <li>• ワイルドカード（*.example.com）を使用すると、サブドメインもまとめて指定できます</li>
            <li>• 重複したドメインは登録できません</li>
          </ul>
        </Card>
      </motion.div>
    </div>
  )
}
