"""
顧客担当者リポジトリの実装

IClientContactRepositoryインターフェースの具体的な実装。
SQLAlchemyを使用してデータベース操作を行います。
"""
from datetime import datetime, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.client_contact_entity import ClientContactEntity
from src.domain.exceptions import ClientContactNotFoundError
from src.domain.interfaces.client_contact_repository import IClientContactRepository
from src.infrastructure.persistence.models.client_contact import ClientContact


class ClientContactRepository(IClientContactRepository):
    """
    顧客担当者リポジトリの実装

    SQLAlchemyを使用して顧客担当者の永続化を行います。
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: データベースセッション
        """
        self._session = session

    async def create(
        self,
        client_organization_id: int,
        full_name: str,
        department: str | None = None,
        position: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        mobile: str | None = None,
        is_primary: bool = False,
        notes: str | None = None,
    ) -> ClientContactEntity:
        """顧客担当者を作成"""
        contact = ClientContact(
            client_organization_id=client_organization_id,
            full_name=full_name,
            department=department,
            position=position,
            email=email,
            phone=phone,
            mobile=mobile,
            is_primary=is_primary,
            notes=notes,
        )

        self._session.add(contact)
        await self._session.flush()
        await self._session.refresh(contact)

        return self._to_entity(contact)

    async def find_by_id(
        self, client_contact_id: int
    ) -> ClientContactEntity | None:
        """IDで顧客担当者を検索"""
        stmt = select(ClientContact).where(
            ClientContact.id == client_contact_id,
            ClientContact.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        contact = result.scalar_one_or_none()

        if contact is None:
            return None

        return self._to_entity(contact)

    async def list_by_client_organization(
        self,
        client_organization_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ClientContactEntity]:
        """顧客組織に属する担当者の一覧を取得"""
        conditions = [
            ClientContact.client_organization_id == client_organization_id,
        ]
        if not include_deleted:
            conditions.append(ClientContact.deleted_at.is_(None))

        stmt = (
            select(ClientContact)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(ClientContact.is_primary.desc(), ClientContact.created_at.desc())
        )

        result = await self._session.execute(stmt)
        contacts = result.scalars().all()

        return [self._to_entity(c) for c in contacts]

    async def find_primary_contact(
        self, client_organization_id: int
    ) -> ClientContactEntity | None:
        """顧客組織の主担当者を取得"""
        stmt = select(ClientContact).where(
            ClientContact.client_organization_id == client_organization_id,
            ClientContact.is_primary.is_(True),
            ClientContact.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        contact = result.scalar_one_or_none()

        if contact is None:
            return None

        return self._to_entity(contact)

    async def update(
        self, client_contact: ClientContactEntity
    ) -> ClientContactEntity:
        """顧客担当者情報を更新"""
        stmt = select(ClientContact).where(
            ClientContact.id == client_contact.id,
            ClientContact.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        db_contact = result.scalar_one_or_none()

        if db_contact is None:
            raise ClientContactNotFoundError(client_contact.id)

        # エンティティの値でモデルを更新
        db_contact.full_name = client_contact.full_name
        db_contact.department = client_contact.department
        db_contact.position = client_contact.position
        db_contact.email = client_contact.email
        db_contact.phone = client_contact.phone
        db_contact.mobile = client_contact.mobile
        db_contact.is_primary = client_contact.is_primary
        db_contact.notes = client_contact.notes

        await self._session.flush()
        await self._session.refresh(db_contact)

        return self._to_entity(db_contact)

    async def soft_delete(self, client_contact_id: int) -> None:
        """顧客担当者を論理削除（ソフトデリート）"""
        stmt = select(ClientContact).where(
            ClientContact.id == client_contact_id,
            ClientContact.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        contact = result.scalar_one_or_none()

        if contact is None:
            raise ClientContactNotFoundError(client_contact_id)

        contact.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()

    def _to_entity(self, contact: ClientContact) -> ClientContactEntity:
        """
        SQLAlchemyモデルをドメインエンティティに変換

        インフラストラクチャの実装詳細をドメイン層から隠蔽します。
        """
        return ClientContactEntity(
            id=contact.id,
            client_organization_id=contact.client_organization_id,
            full_name=contact.full_name,
            department=contact.department,
            position=contact.position,
            email=contact.email,
            phone=contact.phone,
            mobile=contact.mobile,
            is_primary=contact.is_primary,
            notes=contact.notes,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
            deleted_at=contact.deleted_at,
        )
