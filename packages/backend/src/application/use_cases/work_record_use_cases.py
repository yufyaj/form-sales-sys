"""
作業記録ユースケース

作業記録のCRUD操作とビジネスロジックを実行します。
送信制御ロジックを含みます。
"""
from datetime import datetime

from src.application.schemas.work_record import (
    WorkRecordCreateRequest,
    WorkRecordUpdateRequest,
)
from src.domain.entities.work_record_entity import WorkRecordEntity
from src.domain.exceptions import WorkRecordNotFoundError
from src.domain.interfaces.work_record_repository import IWorkRecordRepository
from src.domain.interfaces.no_send_setting_repository import INoSendSettingRepository
from src.domain.services.send_control_service import SendControlService
from src.infrastructure.persistence.models.work_record import WorkRecordStatus


class WorkRecordUseCases:
    """作業記録ユースケースクラス"""

    def __init__(
        self,
        work_record_repository: IWorkRecordRepository,
        no_send_setting_repository: INoSendSettingRepository,
    ) -> None:
        """
        Args:
            work_record_repository: 作業記録リポジトリ
            no_send_setting_repository: 送信禁止設定リポジトリ
        """
        self._work_record_repo = work_record_repository
        self._no_send_setting_repo = no_send_setting_repository

    async def create_work_record(
        self,
        request: WorkRecordCreateRequest,
        list_id: int,
    ) -> WorkRecordEntity:
        """
        作業記録を作成

        Args:
            request: 作業記録作成リクエスト
            list_id: リストID（送信制御チェック用）

        Returns:
            作成された作業記録エンティティ
        """
        # 送信禁止設定のチェック（送信済みの場合のみ）
        if request.status == WorkRecordStatus.SENT:
            await self._validate_send_timing(list_id, request.completed_at)

        # form_submission_resultをdictに変換
        form_submission_result_dict = None
        if request.form_submission_result is not None:
            form_submission_result_dict = request.form_submission_result.model_dump()

        # リポジトリで永続化
        work_record = await self._work_record_repo.create(
            assignment_id=request.assignment_id,
            worker_id=request.worker_id,
            status=request.status,
            started_at=request.started_at,
            completed_at=request.completed_at,
            form_submission_result=form_submission_result_dict,
            cannot_send_reason_id=request.cannot_send_reason_id,
            notes=request.notes,
        )
        return work_record

    async def _validate_send_timing(
        self,
        list_id: int,
        check_datetime: datetime,
    ) -> None:
        """
        送信タイミングが禁止時間帯・曜日・日付に該当しないかチェック

        Args:
            list_id: リストID
            check_datetime: チェック対象の日時

        Raises:
            SendTimingViolationError: 送信禁止時間帯・曜日・日付に該当する場合
        """
        # 送信禁止設定を取得
        settings = await self._no_send_setting_repo.find_by_list_id(
            list_id=list_id,
            include_deleted=False,
        )

        # 送信制御サービスで判定
        can_send, reason = SendControlService.can_send_at(settings, check_datetime)

        if not can_send:
            from src.domain.exceptions import SendTimingViolationError
            raise SendTimingViolationError(reason=reason or "送信禁止時間帯です")

    async def get_work_record(
        self,
        record_id: int,
        requesting_worker_id: int,
        requesting_organization_id: int,
    ) -> WorkRecordEntity:
        """
        作業記録を取得（アクセス権限チェック付き）

        Args:
            record_id: 作業記録ID
            requesting_worker_id: リクエストしているワーカーID
            requesting_organization_id: リクエストしている組織ID

        Returns:
            作業記録エンティティ

        Raises:
            WorkRecordNotFoundError: 作業記録が見つからない、またはアクセス権限がない場合
        """
        record = await self._work_record_repo.find_by_id_with_access_check(
            record_id=record_id,
            requesting_worker_id=requesting_worker_id,
            requesting_organization_id=requesting_organization_id,
        )
        if record is None:
            raise WorkRecordNotFoundError(record_id=record_id)
        return record

    async def list_work_records_by_worker(
        self,
        worker_id: int,
        status: WorkRecordStatus | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[WorkRecordEntity], int]:
        """
        ワーカーの作業記録一覧を取得

        Args:
            worker_id: ワーカーID
            status: フィルタ用のステータス
            start_date: 検索開始日時
            end_date: 検索終了日時
            skip: スキップする件数
            limit: 取得する最大件数

        Returns:
            (作業記録リスト, 総件数)のタプル
        """
        records = await self._work_record_repo.find_by_worker_id(
            worker_id=worker_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit,
            include_deleted=False,
        )
        total = await self._work_record_repo.count_by_worker_id(
            worker_id=worker_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            include_deleted=False,
        )
        return records, total

    async def update_work_record(
        self,
        record_id: int,
        request: WorkRecordUpdateRequest,
        requesting_worker_id: int,
        requesting_organization_id: int,
    ) -> WorkRecordEntity:
        """
        作業記録を更新

        Args:
            record_id: 作業記録ID
            request: 更新リクエスト
            requesting_worker_id: リクエストしているワーカーID
            requesting_organization_id: リクエストしている組織ID

        Returns:
            更新された作業記録エンティティ

        Raises:
            WorkRecordNotFoundError: 作業記録が見つからない、またはアクセス権限がない場合
        """
        # 作業記録を取得（アクセス権限チェック付き）
        record = await self.get_work_record(
            record_id=record_id,
            requesting_worker_id=requesting_worker_id,
            requesting_organization_id=requesting_organization_id,
        )

        # フィールドを更新（リクエストに含まれるフィールドのみ）
        if request.status is not None:
            record.status = request.status

        if request.started_at is not None:
            record.started_at = request.started_at

        if request.completed_at is not None:
            record.completed_at = request.completed_at

        if request.form_submission_result is not None:
            record.form_submission_result = request.form_submission_result.model_dump()

        if request.cannot_send_reason_id is not None:
            record.cannot_send_reason_id = request.cannot_send_reason_id

        if request.notes is not None:
            record.notes = request.notes

        # リポジトリで永続化
        updated_record = await self._work_record_repo.update(record)
        return updated_record

    async def delete_work_record(
        self,
        record_id: int,
        requesting_worker_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        作業記録を論理削除

        Args:
            record_id: 作業記録ID
            requesting_worker_id: リクエストしているワーカーID
            requesting_organization_id: リクエストしている組織ID

        Raises:
            WorkRecordNotFoundError: 作業記録が見つからない、またはアクセス権限がない場合
        """
        # アクセス権限チェック
        await self.get_work_record(
            record_id=record_id,
            requesting_worker_id=requesting_worker_id,
            requesting_organization_id=requesting_organization_id,
        )

        # 論理削除
        await self._work_record_repo.soft_delete(record_id)
