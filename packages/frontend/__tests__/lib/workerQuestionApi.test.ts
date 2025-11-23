/**
 * workerQuestionApi のテスト
 *
 * APIクライアント関数の動作を検証
 */

import {
  fetchWorkerQuestions,
  fetchWorkerQuestion,
  createWorkerQuestion,
  updateWorkerQuestion,
  addAnswerToWorkerQuestion,
  deleteWorkerQuestion,
  fetchUnreadQuestionCount,
  fetchWorkerQuestionsByWorker,
} from '@/lib/workerQuestionApi'
import { apiClient } from '@/lib/api'
import { QuestionStatus, QuestionPriority } from '@/types/workerQuestion'

// apiClientをモック
jest.mock('@/lib/api')

describe('workerQuestionApi', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('fetchWorkerQuestions', () => {
    it('パラメータなしで質問一覧を取得する', async () => {
      const mockResponse = {
        questions: [],
        total: 0,
        skip: 0,
        limit: 20,
      }

      ;(apiClient.get as jest.Mock).mockResolvedValue(mockResponse)

      const result = await fetchWorkerQuestions()

      expect(apiClient.get).toHaveBeenCalledWith('/worker-questions')
      expect(result).toEqual(mockResponse)
    })

    it('ステータスフィルタ付きで質問一覧を取得する', async () => {
      const mockResponse = {
        questions: [],
        total: 0,
        skip: 0,
        limit: 20,
      }

      ;(apiClient.get as jest.Mock).mockResolvedValue(mockResponse)

      await fetchWorkerQuestions({ status: QuestionStatus.PENDING })

      expect(apiClient.get).toHaveBeenCalledWith(
        '/worker-questions?status=pending'
      )
    })

    it('優先度フィルタ付きで質問一覧を取得する', async () => {
      const mockResponse = {
        questions: [],
        total: 0,
        skip: 0,
        limit: 20,
      }

      ;(apiClient.get as jest.Mock).mockResolvedValue(mockResponse)

      await fetchWorkerQuestions({ priority: QuestionPriority.HIGH })

      expect(apiClient.get).toHaveBeenCalledWith(
        '/worker-questions?priority=high'
      )
    })

    it('複数のパラメータで質問一覧を取得する', async () => {
      const mockResponse = {
        questions: [],
        total: 0,
        skip: 0,
        limit: 20,
      }

      ;(apiClient.get as jest.Mock).mockResolvedValue(mockResponse)

      await fetchWorkerQuestions({
        status: QuestionStatus.PENDING,
        priority: QuestionPriority.URGENT,
        workerId: 123,
        skip: 20,
        limit: 50,
      })

      expect(apiClient.get).toHaveBeenCalledWith(
        '/worker-questions?status=pending&priority=urgent&worker_id=123&skip=20&limit=50'
      )
    })
  })

  describe('fetchWorkerQuestion', () => {
    it('質問IDを指定して質問詳細を取得する', async () => {
      const questionId = 1
      const mockQuestion = {
        id: questionId,
        workerId: 1,
        organizationId: 1,
        clientOrganizationId: null,
        title: 'テスト質問',
        content: '質問内容',
        status: QuestionStatus.PENDING,
        priority: QuestionPriority.MEDIUM,
        answer: null,
        answeredByUserId: null,
        answeredAt: null,
        tags: null,
        internalNotes: null,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
        deletedAt: null,
      }

      ;(apiClient.get as jest.Mock).mockResolvedValue(mockQuestion)

      const result = await fetchWorkerQuestion(questionId)

      expect(apiClient.get).toHaveBeenCalledWith(`/worker-questions/${questionId}`)
      expect(result).toEqual(mockQuestion)
    })
  })

  describe('createWorkerQuestion', () => {
    it('新しい質問を作成する', async () => {
      const createData = {
        title: '新しい質問',
        content: '質問内容',
        priority: QuestionPriority.HIGH,
      }

      const mockCreatedQuestion = {
        id: 1,
        workerId: 1,
        organizationId: 1,
        clientOrganizationId: null,
        ...createData,
        status: QuestionStatus.PENDING,
        answer: null,
        answeredByUserId: null,
        answeredAt: null,
        tags: null,
        internalNotes: null,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
        deletedAt: null,
      }

      ;(apiClient.post as jest.Mock).mockResolvedValue(mockCreatedQuestion)

      const result = await createWorkerQuestion(createData)

      expect(apiClient.post).toHaveBeenCalledWith('/worker-questions', createData)
      expect(result).toEqual(mockCreatedQuestion)
    })
  })

  describe('updateWorkerQuestion', () => {
    it('質問を更新する', async () => {
      const questionId = 1
      const updateData = {
        status: QuestionStatus.IN_REVIEW,
        internalNotes: '内部メモ',
      }

      const mockUpdatedQuestion = {
        id: questionId,
        workerId: 1,
        organizationId: 1,
        clientOrganizationId: null,
        title: 'テスト質問',
        content: '質問内容',
        priority: QuestionPriority.MEDIUM,
        ...updateData,
        answer: null,
        answeredByUserId: null,
        answeredAt: null,
        tags: null,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
        deletedAt: null,
      }

      ;(apiClient.patch as jest.Mock).mockResolvedValue(mockUpdatedQuestion)

      const result = await updateWorkerQuestion(questionId, updateData)

      expect(apiClient.patch).toHaveBeenCalledWith(
        `/worker-questions/${questionId}`,
        updateData
      )
      expect(result).toEqual(mockUpdatedQuestion)
    })
  })

  describe('addAnswerToWorkerQuestion', () => {
    it('質問に回答を追加する', async () => {
      const questionId = 1
      const answerData = {
        answer: 'これが回答です',
      }

      const mockAnsweredQuestion = {
        id: questionId,
        workerId: 1,
        organizationId: 1,
        clientOrganizationId: null,
        title: 'テスト質問',
        content: '質問内容',
        status: QuestionStatus.ANSWERED,
        priority: QuestionPriority.MEDIUM,
        answer: answerData.answer,
        answeredByUserId: 1,
        answeredAt: '2024-01-01T12:00:00Z',
        tags: null,
        internalNotes: null,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T12:00:00Z',
        deletedAt: null,
      }

      ;(apiClient.post as jest.Mock).mockResolvedValue(mockAnsweredQuestion)

      const result = await addAnswerToWorkerQuestion(questionId, answerData)

      expect(apiClient.post).toHaveBeenCalledWith(
        `/worker-questions/${questionId}/answer`,
        answerData
      )
      expect(result).toEqual(mockAnsweredQuestion)
    })
  })

  describe('deleteWorkerQuestion', () => {
    it('質問を削除する', async () => {
      const questionId = 1

      ;(apiClient.delete as jest.Mock).mockResolvedValue(undefined)

      await deleteWorkerQuestion(questionId)

      expect(apiClient.delete).toHaveBeenCalledWith(`/worker-questions/${questionId}`)
    })
  })

  describe('fetchUnreadQuestionCount', () => {
    it('未読質問数を取得する', async () => {
      const mockResponse = {
        unreadCount: 5,
      }

      ;(apiClient.get as jest.Mock).mockResolvedValue(mockResponse)

      const result = await fetchUnreadQuestionCount()

      expect(apiClient.get).toHaveBeenCalledWith(
        '/worker-questions/stats/unread-count'
      )
      expect(result).toEqual(mockResponse)
    })
  })

  describe('fetchWorkerQuestionsByWorker', () => {
    it('ワーカーIDを指定して質問一覧を取得する', async () => {
      const workerId = 123
      const mockResponse = {
        questions: [],
        total: 0,
        skip: 0,
        limit: 20,
      }

      ;(apiClient.get as jest.Mock).mockResolvedValue(mockResponse)

      const result = await fetchWorkerQuestionsByWorker(workerId)

      expect(apiClient.get).toHaveBeenCalledWith(
        `/worker-questions/workers/${workerId}`
      )
      expect(result).toEqual(mockResponse)
    })

    it('ワーカーIDとフィルタを指定して質問一覧を取得する', async () => {
      const workerId = 123
      const mockResponse = {
        questions: [],
        total: 0,
        skip: 0,
        limit: 20,
      }

      ;(apiClient.get as jest.Mock).mockResolvedValue(mockResponse)

      await fetchWorkerQuestionsByWorker(workerId, {
        status: QuestionStatus.ANSWERED,
        skip: 10,
        limit: 30,
      })

      expect(apiClient.get).toHaveBeenCalledWith(
        `/worker-questions/workers/${workerId}?status=answered&skip=10&limit=30`
      )
    })
  })

  describe('エラーハンドリング', () => {
    it('API呼び出しエラーを適切に伝播する', async () => {
      const errorMessage = 'ネットワークエラー'

      ;(apiClient.get as jest.Mock).mockRejectedValue(new Error(errorMessage))

      await expect(fetchWorkerQuestions()).rejects.toThrow(errorMessage)
    })
  })
})
