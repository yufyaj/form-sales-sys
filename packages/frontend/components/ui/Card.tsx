'use client'

import * as React from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'
import { fadeInUp } from '@/lib/motion'

/**
 * カードコンポーネント
 * コンテンツをグループ化するためのモダンなコンテナ
 *
 * @example
 * ```tsx
 * <Card>
 *   <CardHeader>
 *     <CardTitle>タイトル</CardTitle>
 *     <CardDescription>説明文</CardDescription>
 *   </CardHeader>
 *   <CardContent>
 *     <p>カードの本文</p>
 *   </CardContent>
 *   <CardFooter>
 *     <Button>アクション</Button>
 *   </CardFooter>
 * </Card>
 * ```
 */
export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * フェードインアニメーションを有効にする
   * @default false
   */
  animate?: boolean
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, animate = false, ...props }, ref) => {
    if (animate) {
      const MotionDiv = motion.div as any
      return (
        <MotionDiv
          ref={ref}
          className={cn(
            'rounded-lg border bg-card text-card-foreground shadow-sm',
            'transition-all duration-base hover:shadow-md',
            className
          )}
          initial="hidden"
          animate="visible"
          variants={fadeInUp}
          {...props}
        />
      )
    }

    return (
      <div
        ref={ref}
        className={cn(
          'rounded-lg border bg-card text-card-foreground shadow-sm',
          'transition-all duration-base hover:shadow-md',
          className
        )}
        {...props}
      />
    )
  }
)
Card.displayName = 'Card'

/**
 * カードヘッダーコンポーネント
 */
const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col space-y-1.5 p-6', className)}
    {...props}
  />
))
CardHeader.displayName = 'CardHeader'

/**
 * カードタイトルコンポーネント
 */
const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      'text-2xl font-semibold leading-none tracking-tight',
      className
    )}
    {...props}
  />
))
CardTitle.displayName = 'CardTitle'

/**
 * カード説明コンポーネント
 */
const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm text-muted-foreground', className)}
    {...props}
  />
))
CardDescription.displayName = 'CardDescription'

/**
 * カードコンテンツコンポーネント
 */
const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />
))
CardContent.displayName = 'CardContent'

/**
 * カードフッターコンポーネント
 */
const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex items-center p-6 pt-0', className)}
    {...props}
  />
))
CardFooter.displayName = 'CardFooter'

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
export default Card
