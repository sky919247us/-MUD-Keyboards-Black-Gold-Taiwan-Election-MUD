"""
記憶體資料存取層
Phase1 使用 dict 儲存實體；Phase2 替換為 PostgreSQL/MongoDB。
"""
from __future__ import annotations

import logging
from typing import Optional

from app.models.entity import PoliticalEntity

logger = logging.getLogger(__name__)


class EntityRepository:
    """政治實體記憶體存取層"""

    def __init__(self) -> None:
        self._store: dict[str, PoliticalEntity] = {}

    def save(self, entity: PoliticalEntity) -> None:
        """儲存或更新實體"""
        self._store[entity.entityId] = entity
        logger.debug(f"[repo] 儲存實體 {entity.name}（{entity.entityId}）")

    def getById(self, entityId: str) -> Optional[PoliticalEntity]:
        """依 ID 取得實體"""
        return self._store.get(entityId)

    def getByName(self, name: str) -> Optional[PoliticalEntity]:
        """依名稱搜尋實體"""
        for entity in self._store.values():
            if entity.basicInfo.name == name:
                return entity
        return None

    def getAll(self) -> list[PoliticalEntity]:
        """取得所有實體"""
        return list(self._store.values())

    def delete(self, entityId: str) -> bool:
        """刪除實體"""
        if entityId in self._store:
            del self._store[entityId]
            return True
        return False

    def count(self) -> int:
        """實體數量"""
        return len(self._store)
