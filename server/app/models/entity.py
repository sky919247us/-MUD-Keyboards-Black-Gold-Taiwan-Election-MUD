"""
政治實體資料模型
核心 JSON Schema 的 Pydantic v2 實作，對應 00-game-architecture.md 第三章。
所有欄位皆帶有邊界驗證，確保數值永遠落在合法區間內。
"""
from __future__ import annotations

import uuid
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field


# ── 列舉型別 ──────────────────────────────────────────────────
class EntityLevel(StrEnum):
    """政治實體層級"""
    PRESIDENT = "President"
    MAYOR = "Mayor"
    LEGISLATOR = "Legislator"
    CITY_COUNCILOR = "City_Councilor"
    LOCAL_BOSS = "Local_Boss"


class CampAlignment(StrEnum):
    """陣營色彩"""
    PAN_GREEN = "泛綠"
    PAN_BLUE = "泛藍"
    WHITE = "白色力量"
    INDEPENDENT = "無黨籍"


class Platform(StrEnum):
    """社群平台"""
    PTT = "PTT"
    FACEBOOK = "Facebook"
    THREADS = "Threads"
    YOUTUBE = "YouTube"
    TIKTOK = "TikTok"
    INSTAGRAM = "Instagram"


class MediaAlignmentType(StrEnum):
    """自媒體結盟型態"""
    OWNED = "Owned"       # 自有頻道，無損傳遞政見
    ALLIED = "Allied"     # 理念結盟，負面事件時有切割機率
    PAID = "Paid"         # 業配，需持續消耗獻金


# ── 子模型：陣列資產 ──────────────────────────────────────────
class LocalBoss(BaseModel):
    """地方樁腳節點"""
    bossId: str = Field(default_factory=lambda: f"boss_{uuid.uuid4().hex[:8]}")
    regionCode: str = Field(..., description="管轄行政區代碼，如 TPE-DA")
    mobilizationPower: int = Field(default=500, ge=0, description="動員力")
    loyalty: int = Field(default=50, ge=0, le=100, description="忠誠度")


class CyberArmyAccount(BaseModel):
    """網軍側翼帳號節點"""
    nodeId: str = Field(default_factory=lambda: f"army_{uuid.uuid4().hex[:8]}")
    platform: Platform = Platform.PTT
    stealthRating: int = Field(default=80, ge=0, le=100, description="隱蔽度")
    outputPower: int = Field(default=300, ge=0, description="聲量製造力")


class MediaChannel(BaseModel):
    """自媒體頻道節點"""
    channelId: str = Field(default_factory=lambda: f"ch_{uuid.uuid4().hex[:8]}")
    platform: Platform = Platform.YOUTUBE
    subscribers: int = Field(default=10000, ge=0, description="訂閱數")
    alignmentType: MediaAlignmentType = MediaAlignmentType.ALLIED


# ── 子模型：結構化屬性群 ──────────────────────────────────────
class BasicInfo(BaseModel):
    """基本資訊"""
    name: str
    level: EntityLevel = EntityLevel.CITY_COUNCILOR
    partyAffiliation: str = "無黨籍"
    campAlignment: CampAlignment = CampAlignment.INDEPENDENT
    incumbent: bool = Field(default=False, description="現任者標記，承受執政包袱")
    region: Optional[str] = Field(default=None, description="所在縣市，如 '台北市'")
    title: str = Field(default="", description="頭銜，如 '市長候選人'")


class CoreAttributes(BaseModel):
    """
    核心三維屬性
    - fame: 知名度 0–10000
    - favorability: 好感度 -10000–10000（唯一允許負值）
    - aggro: 仇恨值 0–10000
    """
    fame: int = Field(default=1000, ge=0, le=10000)
    favorability: int = Field(default=500, ge=-10000, le=10000)
    aggro: int = Field(default=0, ge=0, le=10000)


class Resources(BaseModel):
    """資源池"""
    politicalFunds: int = Field(
        default=5_000_000, ge=0, le=2_000_000_000,
        description="政治獻金（新台幣）",
    )
    unlaunderedFunds: int = Field(
        default=0, ge=0, le=2_000_000_000,
        description="非法政治獻金（待洗白的黑金）",
    )
    staffAp: int = Field(
        default=100, ge=0, le=100,
        description="幕僚行動力",
    )
    stockPortfolio: dict[str, int] = Field(
        default_factory=dict,
        description="持股代號與數量",
    )


class ArraysAssets(BaseModel):
    """陣列資產（非對稱作戰力量）"""
    localBosses: list[LocalBoss] = Field(default_factory=list)
    cyberArmyAccounts: list[CyberArmyAccount] = Field(default_factory=list)
    mediaChannels: list[MediaChannel] = Field(default_factory=list)


class HiddenStats(BaseModel):
    """隱藏狀態"""
    legalRiskIndex: int = Field(
        default=0, ge=0, le=100,
        description="法務風險值，暗盤收受獻金時累積",
    )
    godModeActive: bool = Field(
        default=False,
        description="造神運動狀態，好感度極高時觸發",
    )
    godModeThreshold: int = Field(
        default=8000,
        description="觸發造神運動的好感度門檻",
    )


# ── 主模型：政治實體 ──────────────────────────────────────────
class PoliticalEntity(BaseModel):
    """
    台灣選戰 MUD 政治實體狀態機
    對應 00-game-architecture.md 第三章 JSON Schema。
    每個候選人/陣營都是一個獨立的實例。
    """
    entityId: str = Field(
        default_factory=lambda: f"entity_{uuid.uuid4().hex[:12]}",
        description="政府 OID 或系統自定義 UUID",
    )
    basicInfo: BasicInfo
    coreAttributes: CoreAttributes = Field(default_factory=CoreAttributes)
    resources: Resources = Field(default_factory=Resources)
    arraysAssets: ArraysAssets = Field(default_factory=ArraysAssets)
    hiddenStats: HiddenStats = Field(default_factory=HiddenStats)

    # ── 便捷屬性 ──────────────────────────────────────────────
    @property
    def id(self) -> str:
        """為 leaderboard / world status API 提供的 id 別名"""
        return self.entityId

    @property
    def name(self) -> str:
        return self.basicInfo.name

    @property
    def isIncumbent(self) -> bool:
        return self.basicInfo.incumbent

    @property
    def fame(self) -> int:
        return self.coreAttributes.fame

    @property
    def favorability(self) -> int:
        return self.coreAttributes.favorability

    @property
    def aggro(self) -> int:
        return self.coreAttributes.aggro

    @property
    def totalMediaSubscribers(self) -> int:
        """自媒體陣列總訂閱數，作為輿論防禦裝甲"""
        return sum(ch.subscribers for ch in self.arraysAssets.mediaChannels)

    # ── 安全數值修改 ──────────────────────────────────────────
    def applyAttributeChange(
        self,
        *,
        fame: int = 0,
        favorability: int = 0,
        aggro: int = 0,
        politicalFunds: int = 0,
        staffAp: int = 0,
    ) -> dict[str, int]:
        """
        安全地套用屬性變動，自動 clamp 在合法區間內。
        回傳實際生效的變動值。
        """
        actual: dict[str, int] = {}

        if fame:
            old = self.coreAttributes.fame
            self.coreAttributes.fame = max(0, min(10000, old + fame))
            actual["fame"] = self.coreAttributes.fame - old

        if favorability:
            old = self.coreAttributes.favorability
            self.coreAttributes.favorability = max(-10000, min(10000, old + favorability))
            actual["favorability"] = self.coreAttributes.favorability - old

        if aggro:
            old = self.coreAttributes.aggro
            self.coreAttributes.aggro = max(0, min(10000, old + aggro))
            actual["aggro"] = self.coreAttributes.aggro - old

        if politicalFunds:
            old = self.resources.politicalFunds
            self.resources.politicalFunds = max(0, min(2_000_000_000, old + politicalFunds))
            actual["politicalFunds"] = self.resources.politicalFunds - old

        if staffAp:
            old = self.resources.staffAp
            self.resources.staffAp = max(0, min(100, old + staffAp))
            actual["staffAp"] = self.resources.staffAp - old

        return actual
