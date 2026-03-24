"""
PostgreSQL 非同步資料存取層
封裝了 Users 與 Entities 資料表的 CRUD 操作。
"""
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schema import EntityModel, UserModel
from app.models.entity import PoliticalEntity
from app.models.character import PlayerCharacter
from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

class AsyncRepository:
    """無狀態，整合操作 Users 與 Entities 的資料層"""
    
    # =================
    # Entity 相關操作
    # =================
    async def save_entity(self, entity: PoliticalEntity) -> None:
        """儲存或更新政治實體 (UPSERT)"""
        state_data = entity.model_dump()
        async with AsyncSessionLocal() as session:
            stmt = select(EntityModel).where(EntityModel.entity_id == entity.entityId)
            result = await session.execute(stmt)
            db_entity = result.scalars().first()
            
            if db_entity:
                db_entity.state_data = state_data
                db_entity.entity_name = entity.basicInfo.name
            else:
                new_entity = EntityModel(
                    entity_id=entity.entityId,
                    entity_name=entity.basicInfo.name,
                    entity_type="politician",
                    state_data=state_data
                )
                session.add(new_entity)
                
            await session.commit()

    async def get_entity_by_id(self, entity_id: str) -> Optional[PoliticalEntity]:
        """依 ID 取得政治實體"""
        async with AsyncSessionLocal() as session:
            stmt = select(EntityModel).where(EntityModel.entity_id == entity_id)
            result = await session.execute(stmt)
            db_entity = result.scalars().first()
            
            if db_entity:
                return PoliticalEntity(**db_entity.state_data)
        return None

    async def get_entity_by_name(self, name: str) -> Optional[PoliticalEntity]:
        """依名稱搜尋實體"""
        async with AsyncSessionLocal() as session:
            # 由於 JSONB 內部欄位搜尋較耗能，若是 SQLite 的 JSON 用 text 比較或在程式內篩選
            # 最精確的做法是：撈出全部 or 如果有建立 String 欄位。這裡簡單全撈比對。
            stmt = select(EntityModel)
            result = await session.execute(stmt)
            entities = result.scalars().all()
            for e in entities:
                if e.state_data.get("basicInfo", {}).get("name") == name:
                    return PoliticalEntity(**e.state_data)
        return None

    async def get_all_entities(self) -> list[PoliticalEntity]:
        """取得所有實體 (用於 Tick 計算)"""
        async with AsyncSessionLocal() as session:
            stmt = select(EntityModel)
            result = await session.execute(stmt)
            entities = result.scalars().all()
            return [PoliticalEntity(**e.state_data) for e in entities]
            
    async def count_entities(self) -> int:
        """實體數量"""
        async with AsyncSessionLocal() as session:
            stmt = select(EntityModel.entity_id)
            result = await session.execute(stmt)
            return len(result.all())

    async def batch_save_entities(self, entities: list[PoliticalEntity]) -> None:
        """批量儲存多個政治實體（單一 Transaction）"""
        if not entities:
            return
        async with AsyncSessionLocal() as session:
            # 先撈出目標清單的現有紀錄
            entity_ids = [e.entityId for e in entities]
            stmt = select(EntityModel).where(EntityModel.entity_id.in_(entity_ids))
            result = await session.execute(stmt)
            existing = {e.entity_id: e for e in result.scalars().all()}

            for entity in entities:
                state_data = entity.model_dump()
                db_entity = existing.get(entity.entityId)
                if db_entity:
                    db_entity.state_data = state_data
                    db_entity.entity_name = entity.basicInfo.name
                else:
                    session.add(EntityModel(
                        entity_id=entity.entityId,
                        entity_name=entity.basicInfo.name,
                        entity_type="politician",
                        state_data=state_data,
                    ))
            await session.commit()

    # =================
    # User 相關操作
    # =================
    async def save_user(self, player: PlayerCharacter) -> None:
        """儲存玩家角色進度"""
        async with AsyncSessionLocal() as session:
            stmt = select(UserModel).where(UserModel.user_id == player.userId)
            result = await session.execute(stmt)
            db_user = result.scalars().first()
            
            if db_user:
                db_user.entity_id = player.entityId
                db_user.identity_data = player.identity
            else:
                new_user = UserModel(
                    user_id=player.userId,
                    entity_id=player.entityId,
                    identity_data=player.identity
                )
                session.add(new_user)
                
            await session.commit()

    async def get_user_by_id(self, user_id: str) -> Optional[PlayerCharacter]:
        """讀取玩家角色"""
        async with AsyncSessionLocal() as session:
            stmt = select(UserModel).where(UserModel.user_id == user_id)
            result = await session.execute(stmt)
            db_user = result.scalars().first()
            
            if db_user:
                return PlayerCharacter(
                    userId=db_user.user_id,
                    entityId=db_user.entity_id,
                    identity=db_user.identity_data
                )
        return None

    async def delete_user(self, user_id: str) -> None:
        """刪除玩家角色資料（支援重新選擇陣營）"""
        async with AsyncSessionLocal() as session:
            stmt = select(UserModel).where(UserModel.user_id == user_id)
            result = await session.execute(stmt)
            db_user = result.scalars().first()
            if db_user:
                await session.delete(db_user)
                await session.commit()
