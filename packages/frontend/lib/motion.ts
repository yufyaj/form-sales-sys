/**
 * Framer Motion ユーティリティ
 * プロジェクト全体で使用する共通のアニメーション設定
 */

import type { Variants, Transition } from 'framer-motion'

/**
 * トランジション設定
 */
export const transitions = {
  /** デフォルトのスムーズなトランジション */
  smooth: {
    type: 'spring',
    stiffness: 400,
    damping: 30,
  } as Transition,

  /** 弾力のあるトランジション */
  bouncy: {
    type: 'spring',
    stiffness: 300,
    damping: 20,
  } as Transition,

  /** イージングトランジション */
  ease: {
    duration: 0.3,
    ease: [0.4, 0, 0.2, 1],
  } as Transition,

  /** 素早いトランジション */
  fast: {
    duration: 0.15,
    ease: [0.4, 0, 0.2, 1],
  } as Transition,

  /** ゆっくりとしたトランジション */
  slow: {
    duration: 0.5,
    ease: [0.4, 0, 0.2, 1],
  } as Transition,
}

/**
 * フェードイン バリアント
 */
export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: transitions.ease,
  },
  exit: {
    opacity: 0,
    transition: transitions.fast,
  },
}

/**
 * フェードインアップ バリアント
 */
export const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: transitions.smooth,
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: transitions.fast,
  },
}

/**
 * フェードインダウン バリアント
 */
export const fadeInDown: Variants = {
  hidden: { opacity: 0, y: -20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: transitions.smooth,
  },
  exit: {
    opacity: 0,
    y: 20,
    transition: transitions.fast,
  },
}

/**
 * スケールフェードイン バリアント
 */
export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: transitions.smooth,
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: transitions.fast,
  },
}

/**
 * スライドインレフト バリアント
 */
export const slideInLeft: Variants = {
  hidden: { opacity: 0, x: -20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: transitions.smooth,
  },
  exit: {
    opacity: 0,
    x: 20,
    transition: transitions.fast,
  },
}

/**
 * スライドインライト バリアント
 */
export const slideInRight: Variants = {
  hidden: { opacity: 0, x: 20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: transitions.smooth,
  },
  exit: {
    opacity: 0,
    x: -20,
    transition: transitions.fast,
  },
}

/**
 * ステガードコンテナ バリアント
 * 子要素を順番にアニメーションさせる
 */
export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      staggerChildren: 0.05,
      staggerDirection: -1,
    },
  },
}

/**
 * ステガードアイテム バリアント
 */
export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: transitions.smooth,
  },
  exit: {
    opacity: 0,
    y: -10,
    transition: transitions.fast,
  },
}

/**
 * ページトランジション バリアント
 */
export const pageTransition: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: [0.4, 0, 0.2, 1],
    },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: {
      duration: 0.3,
      ease: [0.4, 0, 1, 1],
    },
  },
}

/**
 * ホバーエフェクト
 */
export const hoverScale = {
  scale: 1.05,
  transition: transitions.fast,
}

export const hoverLift = {
  y: -4,
  transition: transitions.smooth,
}

export const hoverGlow = {
  boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)',
  transition: transitions.smooth,
}

/**
 * タップエフェクト
 */
export const tapScale = {
  scale: 0.95,
  transition: transitions.fast,
}
