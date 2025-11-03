import { redirect } from 'next/navigation'

/**
 * ルートページ
 * ログインページにリダイレクト
 */
export default function HomePage() {
  redirect('/login')
}
