import {
  listWorkRecords,
  getWorkRecord,
  createWorkRecord,
  updateWorkRecord,
} from '@/lib/api/workRecords'
import * as apiClient from '@/lib/api-client'

// api-clientのモック
jest.mock('@/lib/api-client')

describe('workRecords API', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('listWorkRecords', () => {
    it('パラメータなしで作業記録一覧を取得できる', async () => {
      const mockResponse = {
        workRecords: [
          {
            id: 1,
            assignmentId: 100,
            workerId: 1,
            status: 'sent',
            startedAt: '2025-01-01T10:00:00Z',
            completedAt: '2025-01-01T10:30:00Z',
            createdAt: '2025-01-01T10:30:00Z',
            updatedAt: '2025-01-01T10:30:00Z',
          },
        ],
        total: 1,
      }

      ;(apiClient.get as jest.Mock).mockResolvedValue(mockResponse)

      const result = await listWorkRecords()

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/work-records')
      expect(result).toEqual(mockResponse)
    })

    it('workerId パラメータで作業記録をフィルタできる', async () => {
      const mockResponse = {
        workRecords: [],
        total: 0,
      }

      ;(apiClient.get as jest.Mock).mockResolvedValue(mockResponse)

      await listWorkRecords({ workerId: 123 })

      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/v1/work-records?worker_id=123'
      )
    })

    it('assignmentId パラメータで作業記録をフィルタできる', async () => {
      const mockResponse = {
        workRecords: [],
        total: 0,
      }

      ;(apiClient.get as jest.Mock).mockResolvedValue(mockResponse)

      await listWorkRecords({ assignmentId: 456 })

      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/v1/work-records?assignment_id=456'
      )
    })

    it('複数のパラメータを組み合わせて作業記録を取得できる', async () => {
      const mockResponse = {
        workRecords: [],
        total: 0,
      }

      ;(apiClient.get as jest.Mock).mockResolvedValue(mockResponse)

      await listWorkRecords({
        workerId: 123,
        assignmentId: 456,
        page: 2,
        pageSize: 20,
      })

      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/v1/work-records?worker_id=123&assignment_id=456&page=2&page_size=20'
      )
    })
  })

  describe('getWorkRecord', () => {
    it('IDを指定して作業記録詳細を取得できる', async () => {
      const mockWorkRecord = {
        id: 1,
        assignmentId: 100,
        workerId: 1,
        status: 'sent' as const,
        startedAt: '2025-01-01T10:00:00Z',
        completedAt: '2025-01-01T10:30:00Z',
        formSubmissionResult: {
          statusCode: 200,
          message: '送信成功',
          responseTimeMs: 1500,
        },
        notes: '問題なく送信できました',
        createdAt: '2025-01-01T10:30:00Z',
        updatedAt: '2025-01-01T10:30:00Z',
      }

      ;(apiClient.get as jest.Mock).mockResolvedValue(mockWorkRecord)

      const result = await getWorkRecord(1)

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/work-records/1')
      expect(result).toEqual(mockWorkRecord)
    })

    it('IDに特殊文字が含まれていてもエンコードされる', async () => {
      ;(apiClient.get as jest.Mock).mockResolvedValue({})

      await getWorkRecord(999)

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/work-records/999')
    })
  })

  describe('createWorkRecord', () => {
    it('作業記録を作成できる（送信完了）', async () => {
      const requestData = {
        assignmentId: 100,
        workerId: 1,
        status: 'sent' as const,
        startedAt: '2025-01-01T10:00:00Z',
        completedAt: '2025-01-01T10:30:00Z',
        notes: '正常に送信できました',
      }

      const mockResponse = {
        id: 1,
        ...requestData,
        createdAt: '2025-01-01T10:30:00Z',
        updatedAt: '2025-01-01T10:30:00Z',
      }

      ;(apiClient.post as jest.Mock).mockResolvedValue(mockResponse)

      const result = await createWorkRecord(requestData)

      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/v1/work-records',
        requestData
      )
      expect(result).toEqual(mockResponse)
    })

    it('作業記録を作成できる（送信不可）', async () => {
      const requestData = {
        assignmentId: 100,
        workerId: 1,
        status: 'cannot_send' as const,
        startedAt: '2025-01-01T10:00:00Z',
        completedAt: '2025-01-01T10:15:00Z',
        cannotSendReasonId: 1,
        notes: 'フォームが見つかりませんでした',
      }

      const mockResponse = {
        id: 2,
        ...requestData,
        createdAt: '2025-01-01T10:15:00Z',
        updatedAt: '2025-01-01T10:15:00Z',
      }

      ;(apiClient.post as jest.Mock).mockResolvedValue(mockResponse)

      const result = await createWorkRecord(requestData)

      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/v1/work-records',
        requestData
      )
      expect(result).toEqual(mockResponse)
    })

    it('フォーム送信結果を含む作業記録を作成できる', async () => {
      const requestData = {
        assignmentId: 100,
        workerId: 1,
        status: 'sent' as const,
        startedAt: '2025-01-01T10:00:00Z',
        completedAt: '2025-01-01T10:30:00Z',
        formSubmissionResult: {
          statusCode: 200,
          message: '送信成功',
          responseTimeMs: 2000,
          screenshotUrl: 'https://example.com/screenshot.png',
        },
      }

      const mockResponse = {
        id: 3,
        ...requestData,
        createdAt: '2025-01-01T10:30:00Z',
        updatedAt: '2025-01-01T10:30:00Z',
      }

      ;(apiClient.post as jest.Mock).mockResolvedValue(mockResponse)

      const result = await createWorkRecord(requestData)

      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/v1/work-records',
        requestData
      )
      expect(result).toEqual(mockResponse)
    })
  })

  describe('updateWorkRecord', () => {
    it('作業記録を更新できる', async () => {
      const updateData = {
        status: 'sent' as const,
        completedAt: '2025-01-01T11:00:00Z',
        notes: '更新されました',
      }

      const mockResponse = {
        id: 1,
        assignmentId: 100,
        workerId: 1,
        ...updateData,
        startedAt: '2025-01-01T10:00:00Z',
        createdAt: '2025-01-01T10:30:00Z',
        updatedAt: '2025-01-01T11:00:00Z',
      }

      ;(apiClient.patch as jest.Mock).mockResolvedValue(mockResponse)

      const result = await updateWorkRecord(1, updateData)

      expect(apiClient.patch).toHaveBeenCalledWith(
        '/api/v1/work-records/1',
        updateData
      )
      expect(result).toEqual(mockResponse)
    })

    it('部分的な更新ができる', async () => {
      const updateData = {
        notes: '備考を更新',
      }

      const mockResponse = {
        id: 1,
        assignmentId: 100,
        workerId: 1,
        status: 'sent' as const,
        startedAt: '2025-01-01T10:00:00Z',
        completedAt: '2025-01-01T10:30:00Z',
        notes: '備考を更新',
        createdAt: '2025-01-01T10:30:00Z',
        updatedAt: '2025-01-01T11:00:00Z',
      }

      ;(apiClient.patch as jest.Mock).mockResolvedValue(mockResponse)

      const result = await updateWorkRecord(1, updateData)

      expect(apiClient.patch).toHaveBeenCalledWith(
        '/api/v1/work-records/1',
        updateData
      )
      expect(result).toEqual(mockResponse)
    })
  })

  describe('エラーハンドリング', () => {
    it('API呼び出しに失敗した場合はエラーがスローされる', async () => {
      const error = new Error('Network error')
      ;(apiClient.get as jest.Mock).mockRejectedValue(error)

      await expect(listWorkRecords()).rejects.toThrow('Network error')
    })

    it('作成に失敗した場合はエラーがスローされる', async () => {
      const error = new Error('Validation error')
      ;(apiClient.post as jest.Mock).mockRejectedValue(error)

      const requestData = {
        assignmentId: 100,
        workerId: 1,
        status: 'sent' as const,
        startedAt: '2025-01-01T10:00:00Z',
      }

      await expect(createWorkRecord(requestData)).rejects.toThrow(
        'Validation error'
      )
    })
  })
})
