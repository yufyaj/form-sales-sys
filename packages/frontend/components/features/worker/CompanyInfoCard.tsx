'use client'

import React from 'react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/Card'
import type { ListItem } from '@/types/assignment'
import { Building2, Globe, Mail, User } from 'lucide-react'

/**
 * 企業情報カードのプロパティ
 */
export interface CompanyInfoCardProps {
  /**
   * リスト項目（企業情報）
   */
  item: ListItem
}

/**
 * 企業情報表示カード
 *
 * ワーカー作業画面で企業の詳細情報（会社名、URL、担当者等）を表示します。
 */
export function CompanyInfoCard({ item }: CompanyInfoCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Building2 className="h-5 w-5" />
          企業情報
        </CardTitle>
        <CardDescription>作業対象の企業情報</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* 会社名 */}
        <div className="flex items-start gap-3">
          <Building2 className="h-5 w-5 mt-0.5 text-muted-foreground" />
          <div className="flex-1">
            <p className="text-sm font-medium text-muted-foreground">会社名</p>
            <p className="text-base font-semibold">{item.companyName}</p>
          </div>
        </div>

        {/* 企業URL */}
        {item.companyUrl && (
          <div className="flex items-start gap-3">
            <Globe className="h-5 w-5 mt-0.5 text-muted-foreground" />
            <div className="flex-1">
              <p className="text-sm font-medium text-muted-foreground">
                企業URL
              </p>
              <a
                href={item.companyUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-base text-primary hover:underline break-all"
              >
                {item.companyUrl}
              </a>
            </div>
          </div>
        )}

        {/* 担当者名 */}
        {item.contactName && (
          <div className="flex items-start gap-3">
            <User className="h-5 w-5 mt-0.5 text-muted-foreground" />
            <div className="flex-1">
              <p className="text-sm font-medium text-muted-foreground">
                担当者名
              </p>
              <p className="text-base">{item.contactName}</p>
            </div>
          </div>
        )}

        {/* 担当者メールアドレス */}
        {item.contactEmail && (
          <div className="flex items-start gap-3">
            <Mail className="h-5 w-5 mt-0.5 text-muted-foreground" />
            <div className="flex-1">
              <p className="text-sm font-medium text-muted-foreground">
                メールアドレス
              </p>
              <a
                href={`mailto:${item.contactEmail}`}
                className="text-base text-primary hover:underline break-all"
              >
                {item.contactEmail}
              </a>
            </div>
          </div>
        )}

        {/* 備考 */}
        {item.notes && (
          <div className="pt-4 border-t">
            <p className="text-sm font-medium text-muted-foreground mb-2">
              備考
            </p>
            <p className="text-sm text-muted-foreground whitespace-pre-wrap">
              {item.notes}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
