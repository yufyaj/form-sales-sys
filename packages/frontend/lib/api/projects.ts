import { get, post, patch, del } from '@/lib/api-client'

/**
 * プロジェクトAPI型定義
 */

export type ProjectStatus = 'planning' | 'active' | 'completed' | 'cancelled'

export interface Project {
  id: number
  name: string
  client_organization_id: number
  sales_support_organization_id: number
  status: ProjectStatus
  start_date: string | null
  end_date: string | null
  description: string | null
  created_at: string
  updated_at: string
  deleted_at: string | null
}

export interface ProjectCreateRequest {
  name: string
  client_organization_id: number
  status?: ProjectStatus
  start_date?: string | null
  end_date?: string | null
  description?: string | null
}

export interface ProjectUpdateRequest {
  name?: string
  client_organization_id?: number
  status?: ProjectStatus
  start_date?: string | null
  end_date?: string | null
  description?: string | null
}

export interface ProjectListParams {
  status?: ProjectStatus
  client_organization_id?: number
  skip?: number
  limit?: number
}

export interface ProjectListResponse {
  projects: Project[]
  total: number
  skip: number
  limit: number
}

/**
 * プロジェクト一覧を取得
 */
export async function listProjects(
  params?: ProjectListParams
): Promise<ProjectListResponse> {
  const searchParams = new URLSearchParams()

  if (params?.status) {
    searchParams.append('status', params.status)
  }
  if (params?.client_organization_id) {
    searchParams.append('client_organization_id', params.client_organization_id.toString())
  }
  if (params?.skip !== undefined) {
    searchParams.append('skip', params.skip.toString())
  }
  if (params?.limit !== undefined) {
    searchParams.append('limit', params.limit.toString())
  }

  const url = `/api/v1/projects${searchParams.toString() ? `?${searchParams.toString()}` : ''}`
  return get<ProjectListResponse>(url)
}

/**
 * プロジェクト詳細を取得
 */
export async function getProject(projectId: number): Promise<Project> {
  return get<Project>(`/api/v1/projects/${projectId}`)
}

/**
 * プロジェクトを作成
 */
export async function createProject(
  data: ProjectCreateRequest
): Promise<Project> {
  return post<Project>('/api/v1/projects', data)
}

/**
 * プロジェクトを更新
 */
export async function updateProject(
  projectId: number,
  data: ProjectUpdateRequest
): Promise<Project> {
  return patch<Project>(`/api/v1/projects/${projectId}`, data)
}

/**
 * プロジェクトを削除
 */
export async function deleteProject(projectId: number): Promise<void> {
  return del<void>(`/api/v1/projects/${projectId}`)
}

/**
 * 顧客企業別のプロジェクト一覧を取得
 */
export async function listProjectsByClient(
  clientOrganizationId: number,
  params?: Omit<ProjectListParams, 'client_organization_id'>
): Promise<ProjectListResponse> {
  const searchParams = new URLSearchParams()

  if (params?.status) {
    searchParams.append('status', params.status)
  }
  if (params?.skip !== undefined) {
    searchParams.append('skip', params.skip.toString())
  }
  if (params?.limit !== undefined) {
    searchParams.append('limit', params.limit.toString())
  }

  const url = `/api/v1/projects/client/${clientOrganizationId}${searchParams.toString() ? `?${searchParams.toString()}` : ''}`
  return get<ProjectListResponse>(url)
}
