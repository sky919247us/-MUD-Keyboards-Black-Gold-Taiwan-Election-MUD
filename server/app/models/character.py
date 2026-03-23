"""
玩家角色模型與生成器
處理 LINE 使用者與遊戲內政治實體（PoliticalEntity）的綁定。
"""
from __future__ import annotations

import random
from typing import NamedTuple

from pydantic import BaseModel, Field

from app.data.npc_db import npc_db
from app.models.entity import BasicInfo, CampAlignment, EntityLevel, PoliticalEntity
from app.models.party import getPartyByCode


class CharacterIdentity(NamedTuple):
    """分配到的角色身分"""
    party_code: str
    boss_name: str
    boss_real_name: str
    role_title: str
    gender: str


class PlayerCharacter(BaseModel):
    """玩家角色（對應單一 LINE 使用者）"""
    userId: str = Field(description="LINE User ID (或測試用 ID)")
    entityId: str = Field(description="綁定的 PoliticalEntity ID")
    identity: dict = Field(default_factory=dict, description="角色身分詳情")


def _fallback_boss_info(partyCode: str):
    return (
        f"{random.choice(['陳', '林', '王'])}{random.choice(['神', '董', '總'])}",
        None,
        EntityLevel.CITY_COUNCILOR,
        "INDEPENDENT"
    )

async def generateCharacter(userId: str, partyCode: str, repo) -> PlayerCharacter:
    """
    根據選擇的政黨，從實體資料庫中抽選固定的 NPC 作為玩家老闆，並與現有遊戲世界實體綁定。
    回傳 玩家角色資料。
    """
    party = getPartyByCode(partyCode)
    if not party:
        raise ValueError(f"無效的政黨代碼: {partyCode}")

    # ===== 從 NPC DB 撈取該黨設定人物 =====
    candidates = npc_db.get_politicians_by_party(partyCode)
    if not candidates:
        bossName, bossRealName, bossLevel, campStr = _fallback_boss_info(partyCode)
    else:
        # 該黨有人物資料，抽取一位
        bossData = random.choice(candidates)
        bossName = bossData.get("in_game_name")
        bossRealName = bossData.get("real_name")
        try:
            bossLevel = EntityLevel[bossData.get("level", "LEGISLATOR")]
        except KeyError:
            bossLevel = EntityLevel.LEGISLATOR
            
        campStr = bossData.get("camp", "INDEPENDENT")

    try:
        camp = CampAlignment[campStr]
    except KeyError:
        camp = CampAlignment.INDEPENDENT

    # 決定玩家身分與性別
    roles = ["辦公室主任", "發言人", "法務特助", "社群操盤手", "幕僚長"]
    roleTitle = random.choice(roles)
    gender = random.choice(["男", "女"])

    identity = CharacterIdentity(
        party_code=partyCode,
        boss_name=bossName,
        boss_real_name=bossRealName,
        role_title=roleTitle,
        gender=gender,
    )

    # 從 DB 中尋找這名 Boss 的真實實體
    entity = await repo.get_entity_by_name(bossName)
    
    if not entity:
        # 極端特例：世界剛初始化失敗或 NPC DB 不同步，只好生一個新的補救
        entity = PoliticalEntity(
            basicInfo=BasicInfo(
                name=bossName,
                level=bossLevel,
                partyAffiliation=party.name,
                campAlignment=camp,
                incumbent=False,
            )
        )
        await repo.save_entity(entity)

    # 建立玩家映射
    player = PlayerCharacter(
        userId=userId,
        entityId=entity.entityId,
        identity=identity._asdict(),
    )

    return player
