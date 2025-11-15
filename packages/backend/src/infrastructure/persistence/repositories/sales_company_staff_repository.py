"""
営業支援会社担当者リポジトリの実装

ISalesCompanyStaffRepositoryインターフェースの具体的な実装。
SQLAlchemyを使用してデータベース操作を行います。
"""
import logging
from datetime import datetime, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.sales_company_staff_entity import SalesCompanyStaffEntity
from src.domain.exceptions import SalesCompanyStaffNotFoundError
from src.domain.interfaces.sales_company_staff_repository import (
    ISalesCompanyStaffRepository,
)
from src.infrastructure.persistence.models.sales_company_staff import (
    SalesCompanyStaff,
)

# セキュリティログ用のロガー
logger = logging.getLogger(__name__)


class SalesCompanyStaffRepository(ISalesCompanyStaffRepository):
    """
    営業支援会社担当者リポジトリの実装

    SQLAlchemyを使用して営業支援会社担当者の永続化を行います。
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: データベースセッション
        """
        self._session = session

    async def create(
        self,
        user_id: int,
        organization_id: int,
        department: str | None = None,
        position: str | None = None,
        employee_number: str | None = None,
        notes: str | None = None,
    ) -> SalesCompanyStaffEntity:
        """営業支援会社担当者を作成"""
        staff = SalesCompanyStaff(
            user_id=user_id,
            organization_id=organization_id,
            department=department,
            position=position,
            employee_number=employee_number,
            notes=notes,
        )

        self._session.add(staff)
        await self._session.flush()
        await self._session.refresh(staff)

        # セキュリティログ: 担当者作成成功
        logger.info(
            "Sales company staff created successfully",
            extra={
                "event_type": "sales_company_staff_created",
                "staff_id": staff.id,
                "user_id": user_id,
                "organization_id": organization_id,
                "department": department,
                "position": position,
            },
        )

        return self._to_entity(staff)

    async def find_by_id(
        self,
        staff_id: int,
        requesting_organization_id: int,
    ) -> SalesCompanyStaffEntity | None:
        """IDで営業支援会社担当者を検索（マルチテナント対応・IDOR脆弱性対策）"""
        stmt = select(SalesCompanyStaff).where(
            SalesCompanyStaff.id == staff_id,
            SalesCompanyStaff.organization_id == requesting_organization_id,
            SalesCompanyStaff.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        staff = result.scalar_one_or_none()

        # IDOR攻撃検出ログ
        if staff is None:
            # 実際にスタッフが存在するか確認（IDOR試行の検出）
            check_stmt = select(SalesCompanyStaff).where(
                SalesCompanyStaff.id == staff_id,
                SalesCompanyStaff.deleted_at.is_(None),
            )
            check_result = await self._session.execute(check_stmt)
            actual_staff = check_result.scalar_one_or_none()

            if actual_staff is not None:
                # スタッフは存在するが、別組織からのアクセス試行 = IDOR攻撃の可能性
                logger.warning(
                    "Potential IDOR attack detected: cross-tenant access attempt",
                    extra={
                        "event_type": "idor_attack_detected",
                        "attack_type": "sales_company_staff_access",
                        "staff_id": staff_id,
                        "requesting_organization_id": requesting_organization_id,
                        "actual_organization_id": actual_staff.organization_id,
                    },
                )

        return self._to_entity(staff) if staff else None

    async def find_by_user_id(
        self,
        user_id: int,
        requesting_organization_id: int,
    ) -> SalesCompanyStaffEntity | None:
        """ユーザーIDで営業支援会社担当者を検索（マルチテナント対応・IDOR脆弱性対策）"""
        stmt = select(SalesCompanyStaff).where(
            SalesCompanyStaff.user_id == user_id,
            SalesCompanyStaff.organization_id == requesting_organization_id,
            SalesCompanyStaff.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        staff = result.scalar_one_or_none()

        if staff is None:
            return None

        return self._to_entity(staff)

    async def list_by_organization(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[SalesCompanyStaffEntity]:
        """営業支援会社に属する担当者の一覧を取得"""
        conditions = [
            SalesCompanyStaff.organization_id == organization_id,
        ]
        if not include_deleted:
            conditions.append(SalesCompanyStaff.deleted_at.is_(None))

        stmt = (
            select(SalesCompanyStaff)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(SalesCompanyStaff.created_at.desc())
        )

        result = await self._session.execute(stmt)
        staff_list = result.scalars().all()

        return [self._to_entity(s) for s in staff_list]

    async def count_by_organization(
        self,
        organization_id: int,
        include_deleted: bool = False,
    ) -> int:
        """営業支援会社に属する担当者の総件数を取得"""
        conditions = [
            SalesCompanyStaff.organization_id == organization_id,
        ]
        if not include_deleted:
            conditions.append(SalesCompanyStaff.deleted_at.is_(None))

        stmt = select(func.count()).select_from(SalesCompanyStaff).where(and_(*conditions))

        result = await self._session.execute(stmt)
        count = result.scalar_one()

        return count

    async def update(
        self,
        staff: SalesCompanyStaffEntity,
        requesting_organization_id: int,
    ) -> SalesCompanyStaffEntity:
        """営業支援会社担当者情報を更新（マルチテナント対応・IDOR脆弱性対策）"""
        stmt = select(SalesCompanyStaff).where(
            SalesCompanyStaff.id == staff.id,
            SalesCompanyStaff.organization_id == requesting_organization_id,
            SalesCompanyStaff.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        db_staff = result.scalar_one_or_none()

        if db_staff is None:
            # IDOR攻撃検出: 実際にスタッフが存在するか確認
            check_stmt = select(SalesCompanyStaff).where(
                SalesCompanyStaff.id == staff.id,
                SalesCompanyStaff.deleted_at.is_(None),
            )
            check_result = await self._session.execute(check_stmt)
            actual_staff = check_result.scalar_one_or_none()

            if actual_staff is not None:
                # スタッフは存在するが、別組織からの更新試行 = IDOR攻撃の可能性
                logger.warning(
                    "Potential IDOR attack detected: cross-tenant update attempt",
                    extra={
                        "event_type": "idor_attack_detected",
                        "attack_type": "sales_company_staff_update",
                        "staff_id": staff.id,
                        "requesting_organization_id": requesting_organization_id,
                        "actual_organization_id": actual_staff.organization_id,
                    },
                )

            raise SalesCompanyStaffNotFoundError(staff.id)

        # 更新前の値を保存（監査ログ用）
        old_values = {
            "department": db_staff.department,
            "position": db_staff.position,
            "employee_number": db_staff.employee_number,
        }

        # エンティティの値でモデルを更新
        db_staff.department = staff.department
        db_staff.position = staff.position
        db_staff.employee_number = staff.employee_number
        db_staff.notes = staff.notes

        await self._session.flush()
        await self._session.refresh(db_staff)

        # セキュリティログ: 担当者更新成功
        logger.info(
            "Sales company staff updated successfully",
            extra={
                "event_type": "sales_company_staff_updated",
                "staff_id": staff.id,
                "organization_id": requesting_organization_id,
                "old_values": old_values,
                "new_values": {
                    "department": staff.department,
                    "position": staff.position,
                    "employee_number": staff.employee_number,
                },
            },
        )

        return self._to_entity(db_staff)

    async def soft_delete(
        self,
        staff_id: int,
        requesting_organization_id: int,
    ) -> None:
        """営業支援会社担当者を論理削除（ソフトデリート）（マルチテナント対応・IDOR脆弱性対策）"""
        stmt = select(SalesCompanyStaff).where(
            SalesCompanyStaff.id == staff_id,
            SalesCompanyStaff.organization_id == requesting_organization_id,
            SalesCompanyStaff.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        staff = result.scalar_one_or_none()

        if staff is None:
            # IDOR攻撃検出: 実際にスタッフが存在するか確認
            check_stmt = select(SalesCompanyStaff).where(
                SalesCompanyStaff.id == staff_id,
                SalesCompanyStaff.deleted_at.is_(None),
            )
            check_result = await self._session.execute(check_stmt)
            actual_staff = check_result.scalar_one_or_none()

            if actual_staff is not None:
                # スタッフは存在するが、別組織からの削除試行 = IDOR攻撃の可能性
                logger.warning(
                    "Potential IDOR attack detected: cross-tenant delete attempt",
                    extra={
                        "event_type": "idor_attack_detected",
                        "attack_type": "sales_company_staff_delete",
                        "staff_id": staff_id,
                        "requesting_organization_id": requesting_organization_id,
                        "actual_organization_id": actual_staff.organization_id,
                    },
                )

            raise SalesCompanyStaffNotFoundError(staff_id)

        staff.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()

        # セキュリティログ: 担当者削除成功
        logger.info(
            "Sales company staff soft deleted successfully",
            extra={
                "event_type": "sales_company_staff_deleted",
                "staff_id": staff_id,
                "user_id": staff.user_id,
                "organization_id": requesting_organization_id,
            },
        )

    def _to_entity(self, staff: SalesCompanyStaff) -> SalesCompanyStaffEntity:
        """
        SQLAlchemyモデルをドメインエンティティに変換

        インフラストラクチャの実装詳細をドメイン層から隠蔽します。
        """
        return SalesCompanyStaffEntity(
            id=staff.id,
            user_id=staff.user_id,
            organization_id=staff.organization_id,
            department=staff.department,
            position=staff.position,
            employee_number=staff.employee_number,
            notes=staff.notes,
            created_at=staff.created_at,
            updated_at=staff.updated_at,
            deleted_at=staff.deleted_at,
        )
