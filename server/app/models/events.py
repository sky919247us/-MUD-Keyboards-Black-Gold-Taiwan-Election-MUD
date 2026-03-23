"""
危機事件資料模型
對應政治危機事件設計與觸發機制.md。
"""
from __future__ import annotations

from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field


class CrisisType(StrEnum):
    """危機事件類型"""
    POWER_OUTAGE = "基礎設施跳電"
    TOFU_PROJECT = "豆腐渣工程現形"
    ECONOMIC_PANIC = "經濟恐慌無薪假風暴"
    CYBER_ARMY_BUSTED = "1450側翼反串翻車"
    TYPHOON_GAMBLE = "颱風假決策政治豪賭"
    DISASTER_RESPONSE = "消防車陷阱"
    POLICE_CRACKDOWN = "掃黑連累黑金反噬"
    BLACKOUT_NUKE = "缺電政治核彈"
    FLOOD_CORRUPTION = "積淹水官商勾結風暴"
    AQI_COLLAPSE = "空污選票崩盤"


class CrisisEvent(BaseModel):
    """突發政治危機事件"""
    crisisType: CrisisType
    triggerApis: list[str] = Field(
        description="觸發此危機的 API 組合，如 ['weather', 'ptt']",
    )
    description: str = Field(description="事件描述文字")
    impactFavorability: int = Field(default=0, description="好感度變動")
    impactAggro: int = Field(default=0, description="仇恨值變動")
    impactFame: int = Field(default=0, description="知名度變動")
    impactFunds: int = Field(default=0, description="政治獻金變動")
    impactStaffAp: int = Field(default=0, description="幕僚行動力變動")
    arrayEvent: Optional[str] = Field(
        default=None,
        description="對陣列資產的特殊影響描述",
    )
    targetParties: list[str] = Field(
        default_factory=list,
        description="受影響的政黨代碼列表（空=全體）",
    )
    incumbentOnly: bool = Field(
        default=False,
        description="是否僅影響現任者",
    )
    durationTicks: int = Field(
        default=1,
        description="效果持續的 Tick 數",
    )


class ResponseOption(BaseModel):
    """危機應對選項"""
    label: str
    apCost: int = 0
    fundsCost: int = 0
    damageReduction: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="傷害吸收百分比 0.0~1.0",
    )
    sideEffect: Optional[str] = None
    legalRiskIncrease: int = 0
