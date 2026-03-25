"""
遊戲世界狀態管理
管理全局狀態、Tick 計數、當前賽季階段等。
"""
from __future__ import annotations

import logging
from collections import deque
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel
from app.models.entity import (
    BasicInfo, CampAlignment, CyberArmyAccount, EntityLevel,
    LocalBoss, MediaChannel, MediaAlignmentType, Platform, PoliticalEntity,
)
from app.repository.async_repo import AsyncRepository
from app.data.npc_db import npc_db
from app.game.economy import market
from app.repositories.player_repo import PlayerRepository
from app.engine.events import get_random_crisis

logger = logging.getLogger(__name__)


class SeasonPhase(StrEnum):
    """賽季階段"""
    WARMUP = "準備期"
    PRIMARIES = "初選期"
    CAMPAIGN = "衝刺期"
    ELECTION_DAY = "投票日"
    SETTLEMENT = "結算期"


class HistorySnapshot(BaseModel):
    """單一 Tick 的數據快照"""
    tick: int
    timestamp: datetime
    fame: int
    favorability: int
    aggro: int

class HistoryManager:
    """記憶體內的歷史數據管理器"""
    def __init__(self, max_ticks: int = 100) -> None:
        # 使用 deque 限制長度，自動拋棄舊數據 (100 ticks 約 50 分鐘)
        # 結構: {entity_id: deque[HistorySnapshot]}
        self._data: dict[str, deque[HistorySnapshot]] = {}
        self.max_ticks = max_ticks

    def record(self, entity_id: str, tick: int, fame: int, favorability: int, aggro: int):
        if entity_id not in self._data:
            self._data[entity_id] = deque(maxlen=self.max_ticks)
        
        snapshot = HistorySnapshot(
            tick=tick,
            timestamp=datetime.now(),
            fame=fame,
            favorability=favorability,
            aggro=aggro
        )
        self._data[entity_id].append(snapshot)
        logger.debug(f"已紀錄實體 {entity_id} 的 Tick {tick} 歷史快照")

    def get_history(self, entity_id: str) -> list[HistorySnapshot]:
        return list(self._data.get(entity_id, []))

class GameWorld:
    """遊戲世界管理器（Singleton pattern）"""

    def __init__(self) -> None:
        self.repo = AsyncRepository()
        self.history = HistoryManager(max_ticks=120) # 紀錄一小時
        self.tickCount: int = 0
        self.currentPhase: SeasonPhase = SeasonPhase.WARMUP
        self._initialized = False
        self._connections: dict[str, Any] = {} # Store active WebSocket connections by entity_id
        self._send_to_entity_callback = None # Callback to send messages to specific entities

    async def initialize(self) -> None:
        """初始化遊戲世界，將所有真實政治實體與企業匯入資料庫"""
        if self._initialized:
            return

        logger.info("正在初始化遊戲世界與本地庫...")
        count = await self.repo.count_entities()
        if count > 0:
            logger.info(f"資料庫已有 {count} 筆實體，略過初始化。")
            # 初始快照 (可選，通常等第一個 Tick)
            self._initialized = True
            return

        # 匯入所有政治人物
        from app.models.party import getPartyByCode
        for data in npc_db.politicians:
            party_code = data.get("party_code", "IND")
            party_info = getPartyByCode(party_code)
            level_str = data.get("level", "MAYOR").upper()
            
            # 從 name 或 aliases 決定稱呼
            name_val = data.get("in_game_name") or data.get("name")
            if not name_val and data.get("aliases"):
                name_val = data["aliases"][0]
                
            entity = PoliticalEntity(
                basicInfo=BasicInfo(
                    name=name_val or "無名氏",
                    level=EntityLevel[level_str] if level_str in EntityLevel.__members__ else EntityLevel.MAYOR,
                    partyAffiliation=party_code,
                    campAlignment=party_info.campAlignment if hasattr(party_info, "campAlignment") else CampAlignment.INDEPENDENT,
                    incumbent=False,
                ),
            )
            # 每個實體給予基礎假資料
            entity.arraysAssets.localBosses.append(
                LocalBoss(regionCode="TPE", mobilizationPower=300, loyalty=50)
            )
            entity.arraysAssets.cyberArmyAccounts.append(
                CyberArmyAccount(platform=Platform.PTT, stealthRating=50, outputPower=200)
            )
            await self.repo.save_entity(entity)

        # 匯入所有企業 (同理轉為 PoliticalEntity 作為地方勢力，但簡單處理)
        for data in npc_db.corporations:
            entity = PoliticalEntity(
                basicInfo=BasicInfo(
                    name=data["name"],
                    level=EntityLevel.LOCAL_BOSS,
                    partyAffiliation="NONE",
                    campAlignment=CampAlignment.INDEPENDENT,
                    incumbent=False,
                ),
            )
            await self.repo.save_entity(entity)

        self._initialized = True
        logger.info(f"世界初始化完成！載入了 {await self.repo.count_entities()} 筆真實實體至 PostgreSQL/SQLite。")

    def advanceTick(self) -> None:
        """推進 Tick 計數"""
        self.tickCount += 1
        # 推動全服黑市與經濟行情 (暫不精算全服總仇恨，以動態 tick 的微小風聲變化模擬查緝情境)
        market.tick_market(server_aggro=self.tickCount * 50)

    def set_broadcast_callback(self, callback) -> None:
        """注入廣播回呼函式（由 main.py 的 ConnectionManager 提供）"""
        self._broadcast_callback = callback

    def set_send_to_entity_callback(self, callback) -> None:
        """注入發送訊息給特定實體的回呼函式（由 main.py 的 ConnectionManager 提供）"""
        self._send_to_entity_callback = callback

    async def _send_to_entity(self, entity_id: str, message: dict) -> None:
        """內部方法，用於發送訊息給特定實體"""
        if self._send_to_entity_callback:
            await self._send_to_entity_callback(entity_id, message)
        else:
            logger.warning(f"send_to_entity_callback 尚未設定，無法發送訊息給 {entity_id}")

    async def _simulation_loop(self) -> None:
        """遊戲世界的核心模擬循環"""
        repo = PlayerRepository() # Use PlayerRepository for player-specific operations
        while True:
            try:
                # 每 30 秒固定結算 AP 等基礎數值
                await repo.process_all_entities_tick()

                # --- 危機事件推播邏輯 ---
                # 遍歷目前在線的所有玩家
                for entity_id in self._connections.keys():
                    entity = await repo.get_entity(entity_id)
                    if entity:
                        # 30% 機率在這個 30 秒 tick 遇到突發危機
                        if random.random() < 0.30:
                            crisis = get_random_crisis()
                            if crisis:
                                # 標記該玩家正在面臨危機（可選擇性加入狀態機阻擋其他行動）
                                await self._send_to_entity(entity_id, {
                                    "type": "crisis",
                                    "data": crisis.model_dump() # Assuming crisis is a Pydantic model
                                })

                await repo.sync_to_db()
            except Exception as e:
                logger.error(f"Simulation tick error: {e}", exc_info=True)

            # 休眠 30 秒
            await asyncio.sleep(30)

    async def trigger_news_flash(
        self,
        attacker_name: str,
        defender_name: str,
        event: str,
        damage_desc: str,
    ) -> None:
        """
        產生全伺服器廣播的新聞快訊，並發送給所有 WebSocket 連線。
        由 commands.py 的攻擊/拔樁成功後呼叫。
        """
        from app.ai.settlement_engine import generateNewsFlash
        callback = getattr(self, "_broadcast_callback", None)
        if callback is None:
            logger.warning("broadcast_callback 尚未設定，跳過新聞快訊廣播")
            return
        try:
            flash = await generateNewsFlash(attacker_name, defender_name, event, damage_desc)
            message = (
                f"\n{'━' * 50}\n"
                f"📡 【全服快訊】{flash.title}\n"
                f"   {flash.content}\n"
                f"{'━' * 50}\n"
            )
            await callback(message)
            logger.info(f"[NewsFlash] 廣播完成：{flash.title}")
        except Exception as e:
            logger.error(f"[NewsFlash] 廣播失敗：{e}")


# 全域單例
gameWorld = GameWorld()
