import '@testing-library/jest-dom'
import { TextEncoder, TextDecoder } from 'util'
import { ReadableStream } from 'stream/web'

// Node.js環境にWeb API用のポリフィルを追加（Next.js用）
global.TextEncoder = TextEncoder
global.TextDecoder = TextDecoder
global.ReadableStream = ReadableStream

// Request/Response APIのモック
global.Request = class Request {
  constructor(input, init) {
    this.url = typeof input === 'string' ? input : input.url
    this.method = init?.method || 'GET'
    this.headers = new Map(Object.entries(init?.headers || {}))
    this.body = init?.body
  }
}

global.Response = class Response {
  constructor(body, init) {
    this.body = body
    this.status = init?.status || 200
    this.statusText = init?.statusText || 'OK'
    this.headers = new Map(Object.entries(init?.headers || {}))
    this.ok = this.status >= 200 && this.status < 300
  }

  async json() {
    return JSON.parse(this.body)
  }

  async text() {
    return this.body
  }
}

// Framer Motionのモック - アニメーションを無効化
jest.mock('framer-motion', () => ({
  ...jest.requireActual('framer-motion'),
  motion: new Proxy(
    {},
    {
      get: (_, prop) => {
        // forwardRefでラップして、refを正しく処理
        const React = require('react')
        return React.forwardRef(({ children, whileTap, transition, ...props }, ref) => {
          // whileTapとtransitionは除外して、残りのpropsを全て渡す
          return React.createElement(prop, { ref, ...props }, children)
        })
      },
    }
  ),
  AnimatePresence: ({ children }) => children,
}))
