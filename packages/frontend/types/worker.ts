/**
 * ワーカー関連の型定義
 *
 * バックエンドのワーカースキーマに対応するフロントエンドの型定義
 */

/**
 * ワーカーステータス
 */
export enum WorkerStatus {
  PENDING = "pending",
  ACTIVE = "active",
  INACTIVE = "inactive",
  SUSPENDED = "suspended",
}

/**
 * スキルレベル
 */
export enum SkillLevel {
  BEGINNER = "beginner",
  INTERMEDIATE = "intermediate",
  ADVANCED = "advanced",
  EXPERT = "expert",
}

/**
 * ワーカー情報
 */
export interface Worker {
  id: number;
  userId: number;
  organizationId: number;
  status: WorkerStatus;
  skillLevel: SkillLevel | null;
  experienceMonths: number | null;
  specialties: string | null;
  maxTasksPerDay: number | null;
  availableHoursPerWeek: number | null;
  completedTasksCount: number;
  successRate: number | null;
  averageTaskTimeMinutes: number | null;
  rating: number | null;
  notes: string | null;
  createdAt: string;
  updatedAt: string;
  deletedAt: string | null;
}

/**
 * ワーカー作成リクエスト
 */
export interface WorkerCreateRequest {
  userId: number;
  status?: WorkerStatus;
  skillLevel?: SkillLevel | null;
  experienceMonths?: number | null;
  specialties?: string | null;
  maxTasksPerDay?: number | null;
  availableHoursPerWeek?: number | null;
  notes?: string | null;
}

/**
 * ワーカー更新リクエスト
 */
export interface WorkerUpdateRequest {
  status?: WorkerStatus | null;
  skillLevel?: SkillLevel | null;
  experienceMonths?: number | null;
  specialties?: string | null;
  maxTasksPerDay?: number | null;
  availableHoursPerWeek?: number | null;
  completedTasksCount?: number | null;
  successRate?: number | null;
  averageTaskTimeMinutes?: number | null;
  rating?: number | null;
  notes?: string | null;
}

/**
 * ワーカー一覧レスポンス
 */
export interface WorkerListResponse {
  workers: Worker[];
  total: number;
  skip: number;
  limit: number;
}

/**
 * ユーザー情報を含むワーカー情報
 */
export interface WorkerWithUser extends Worker {
  userEmail: string;
  userFullName: string;
  userPhone: string | null;
  userIsActive: boolean;
}

/**
 * ワーカーステータスの日本語ラベル
 */
export const WorkerStatusLabel: Record<WorkerStatus, string> = {
  [WorkerStatus.PENDING]: "承認待ち",
  [WorkerStatus.ACTIVE]: "稼働中",
  [WorkerStatus.INACTIVE]: "休止中",
  [WorkerStatus.SUSPENDED]: "停止中",
};

/**
 * スキルレベルの日本語ラベル
 */
export const SkillLevelLabel: Record<SkillLevel, string> = {
  [SkillLevel.BEGINNER]: "初級",
  [SkillLevel.INTERMEDIATE]: "中級",
  [SkillLevel.ADVANCED]: "上級",
  [SkillLevel.EXPERT]: "エキスパート",
};
