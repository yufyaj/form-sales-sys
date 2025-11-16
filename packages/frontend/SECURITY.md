# セキュリティガイド

## 概要

このドキュメントは、営業支援会社担当者管理機能のセキュリティ実装状況と、今後対応が必要な項目を記載しています。

## 実装済みセキュリティ対策

### ✅ 入力バリデーション

#### パスワードポリシー（NIST SP 800-63B準拠）
- 最小12文字、最大128文字
- 大文字、小文字、数字、特殊文字を含む
- 実装箇所: `lib/validations/user.ts`

#### メールアドレス検証
- フォーマット検証
- 使い捨てメールドメインのブロック
  - tempmail.com
  - guerrillamail.com
  - mailinator.com
  - 10minutemail.com
  - throwaway.email

#### 電話番号検証
- 日本の電話番号フォーマットに対応
- 正規表現: `^(\+81|0)\d{1,4}-?\d{1,4}-?\d{4}$`

### ✅ エラーハンドリング

#### 情報漏洩防止
- サーバーエラー（500番台）: 詳細を隠蔽し、汎用メッセージを返す
- クライアントエラー（400番台）: 安全な定義済みメッセージのみ返す
- 実装箇所: `lib/actions/users.ts:handleApiResponse()`

#### ログ出力の安全化
- 機密情報（トークン、パスワード、個人情報）をログに出力しない
- 構造化ログ形式を使用
- タイムスタンプとエラーメッセージのみ記録

### ✅ 認証・セッション管理

#### httpOnlyクッキー
- 認証トークンはhttpOnlyクッキーに保存
- JavaScriptからのアクセスを防止（XSS対策）

#### HTTPS強制（本番環境）
- 環境変数検証で本番環境のHTTPS使用を確保
- 実装箇所: `lib/actions/users.ts`

### ✅ クライアントサイドセキュリティ

#### XSS対策
- Reactの自動エスケープに依存
- ユーザー入力はすべて`{}`で表示（自動エスケープ）

#### CSP（Content Security Policy）
- Next.js middlewareで実装
- 実装箇所: `middleware.ts`

## ⚠️ 対応が必要なセキュリティ課題

### 🔴 Critical（重大）

#### 1. IDOR（Insecure Direct Object Reference）脆弱性

**問題**:
現在、フロントエンドから`organization_id`をクエリパラメータとして送信しているため、攻撃者が他の組織のデータにアクセスできる可能性があります。

**影響範囲**:
- `GET /users?organization_id={id}` - ユーザー一覧取得
- `GET /users/{user_id}?organization_id={id}` - ユーザー詳細取得
- `PATCH /users/{user_id}?organization_id={id}` - ユーザー更新
- `DELETE /users/{user_id}?organization_id={id}` - ユーザー削除

**推奨対策**:

##### バックエンド側（優先度: 最高）
```python
# packages/backend/src/app/api/users.py

@router.get("")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),  # ← 追加
) -> UserListResponse:
    """
    組織IDはトークンから取得（フロントエンドから受け取らない）
    """
    organization_id = current_user.organization_id  # ← JWTから取得
    users, total = await use_cases.list_users(organization_id, skip, limit)
    return UserListResponse(...)
```

##### フロントエンド側
```typescript
// lib/actions/users.ts

// 修正前
const response = await fetch(
  `${API_BASE_URL}/users?organization_id=${organizationId}&skip=${skip}&limit=${limit}`,
  // ...
)

// 修正後
const response = await fetch(
  `${API_BASE_URL}/users?skip=${skip}&limit=${limit}`,
  // ...
)
```

**ステータス**: 未対応（バックエンドAPI変更が必要）

---

#### 2. CSRF対策の追加検証

**問題**:
Next.js 16のデフォルトCSRF保護のみに依存しており、明示的な検証が不足しています。

**推奨対策**:

##### next.config.mjs
```javascript
export default {
  experimental: {
    serverActions: {
      bodySizeLimit: '2mb',
      // CSRF検証を有効化
    },
  },
}
```

##### 追加のCSRFトークン検証（オプション）
```typescript
// lib/csrf.ts
import { headers } from 'next/headers'

export async function verifyCsrfToken(): Promise<boolean> {
  const headersList = await headers()
  const csrfToken = headersList.get('x-csrf-token')

  // トークン検証ロジック
  // ...

  return true
}
```

**ステータス**: 部分対応（Next.jsデフォルト保護のみ）

---

### 🟠 Medium（中）

#### 3. レート制限の実装

**問題**:
フロントエンド・バックエンドともにレート制限が実装されていません。

**推奨対策**:

##### フロントエンド側
```typescript
// lib/rateLimit.ts
import { LRUCache } from 'lru-cache'

const rateLimitCache = new LRUCache({
  max: 500,
  ttl: 60000, // 1分
})

export async function checkRateLimit(
  identifier: string,
  limit: number = 10
): Promise<boolean> {
  const key = `ratelimit:${identifier}`
  const current = rateLimitCache.get(key) as number || 0

  if (current >= limit) {
    return false
  }

  rateLimitCache.set(key, current + 1)
  return true
}
```

##### バックエンド側（より重要）
```python
# packages/backend/src/app/middleware/rate_limit.py

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def create_user(...):
    ...
```

**ステータス**: 未対応

---

#### 4. 監査ログの実装

**問題**:
セキュリティイベント（ユーザー作成/更新/削除）の監査ログが記録されていません。

**推奨実装**:
```python
# packages/backend/src/infrastructure/logging/audit_logger.py

async def log_audit_event(
    action: str,
    user_id: int,
    organization_id: int,
    metadata: dict = None
):
    await audit_log_repo.create({
        'action': action,
        'user_id': user_id,
        'organization_id': organization_id,
        'metadata': metadata,
        'timestamp': datetime.utcnow(),
        'ip_address': request.client.host,
        'user_agent': request.headers.get('user-agent'),
    })
```

**ステータス**: 未対応

---

### 🟢 Low（低）

#### 5. Content Security Policy（CSP）の強化

**現状**: 基本的なCSPは実装済み（middleware.ts）

**推奨強化**:
```typescript
// next.config.mjs
headers: [
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval' 'unsafe-inline'",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: https:",
      "font-src 'self' data:",
      "connect-src 'self' https://api.example.com",
      "frame-ancestors 'none'",
      "base-uri 'self'",
      "form-action 'self'",
    ].join('; '),
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY',
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin',
  },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=()',
  },
]
```

**ステータス**: 部分対応

---

## セキュリティテストチェックリスト

### 実施すべきテスト

- [ ] **IDOR脆弱性テスト**: 他の組織のユーザーデータにアクセス試行
- [ ] **CSRF攻撃テスト**: 偽造リクエストでユーザー操作を試行
- [ ] **XSS攻撃テスト**: スクリプトタグを含むユーザー入力を試行
- [ ] **SQLインジェクションテスト**: 特殊文字を含む入力を試行（バックエンド）
- [ ] **レート制限テスト**: 短時間に大量リクエストを送信
- [ ] **パスワードポリシーテスト**: 弱いパスワードで登録試行
- [ ] **認証バイパステスト**: トークンなしでAPIアクセス試行
- [ ] **権限昇格テスト**: 一般ユーザーが管理者操作を試行

### テスト実装例

```typescript
// __tests__/security/idor.test.ts
describe('IDOR Protection', () => {
  it('should reject access to other organization users', async () => {
    // 組織Aのユーザーが組織Bのユーザーにアクセス試行
    const result = await getUserList(999) // 不正な組織ID
    expect(result.success).toBe(false)
    expect(result.error).toContain('アクセス権限がありません')
  })
})
```

---

## セキュリティインシデント対応

### インシデント発生時の対応フロー

1. **検知**: エラーログ、監査ログを監視
2. **初動対応**: 影響範囲の特定、被害の封じ込め
3. **調査**: ログ分析、原因究明
4. **復旧**: 脆弱性修正、パッチ適用
5. **報告**: ステークホルダーへの報告
6. **再発防止**: セキュリティ強化策の実施

### 緊急連絡先

- セキュリティ担当: [TODO: 連絡先を記載]
- インフラ担当: [TODO: 連絡先を記載]

---

## 定期的なセキュリティレビュー

### 推奨スケジュール

- **毎月**: 依存関係の脆弱性スキャン（`npm audit`, `pip audit`）
- **四半期ごと**: セキュリティコードレビュー
- **半年ごと**: ペネトレーションテスト
- **年1回**: セキュリティ監査

### セキュリティツール

- **フロントエンド**:
  - `npm audit`: 依存関係の脆弱性スキャン
  - ESLint Security Plugin: 静的解析
  - OWASP ZAP: 動的解析

- **バックエンド**:
  - `bandit`: Pythonセキュリティスキャナー
  - `safety`: 依存関係チェック
  - SonarQube: コード品質・セキュリティ分析

---

## 参考資料

### セキュリティ基準
- OWASP Top 10 2021
- NIST SP 800-63B（パスワードガイドライン）
- CWE/SANS Top 25

### 内部ドキュメント
- CodeGuardルール: `ai-docs/security/codeguard-*.md`
- 開発規約: `ai-docs/skills/frontend.md`, `ai-docs/skills/backend.md`

---

最終更新: 2025-11-16
作成者: Claude Code（CodeGuard Security Reviewer）
