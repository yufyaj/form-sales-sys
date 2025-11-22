import '@testing-library/jest-dom'

// Framer Motionのモック - アニメーションを無効化
jest.mock('framer-motion', () => ({
  ...jest.requireActual('framer-motion'),
  motion: new Proxy(
    {},
    {
      get: (_, prop) => {
        return jest.fn(({ children, ...props }) => {
          const React = require('react')
          return React.createElement(prop, props, children)
        })
      },
    }
  ),
  AnimatePresence: ({ children }) => children,
}))
