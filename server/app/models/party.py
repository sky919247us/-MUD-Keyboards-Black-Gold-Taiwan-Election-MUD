"""
虛擬政黨與地方派系定義
對應 00-game-architecture.md 第六章。
"""
from __future__ import annotations

from enum import StrEnum
from typing import NamedTuple


class ApiSensitivity(StrEnum):
    """API 敏感度分類"""
    STOCK = "台股大盤"
    WEATHER = "天氣"
    PTT = "PTT/GoogleTrends"
    INTL_NEWS = "國際新聞"
    LOCAL_NEWS = "地方新聞"
    TAIPOWER = "台電電力"
    AQI = "空氣品質"
    WATER = "水利水位"
    POLICE = "警政治安"


class VirtualParty(NamedTuple):
    """虛擬政黨"""
    code: str
    name: str
    shortName: str
    realWorldRef: str
    primarySensitivity: ApiSensitivity
    secondarySensitivity: ApiSensitivity | None = None


class LocalFaction(NamedTuple):
    """地方派系/黑金勢力"""
    code: str
    name: str
    factionType: str
    primarySensitivity: ApiSensitivity
    description: str


# ── 7 大虛擬政黨 ──────────────────────────────────────────────
PARTIES: list[VirtualParty] = [
    VirtualParty(
        code="DPF",
        name="民主進步陣線",
        shortName="民進陣",
        realWorldRef="執政黨",
        primarySensitivity=ApiSensitivity.STOCK,
        secondarySensitivity=ApiSensitivity.WEATHER,
    ),
    VirtualParty(
        code="NCA",
        name="國家保守聯盟",
        shortName="國保盟",
        realWorldRef="最大在野黨",
        primarySensitivity=ApiSensitivity.WEATHER,
    ),
    VirtualParty(
        code="NAP",
        name="新世代覺醒黨",
        shortName="新覺黨",
        realWorldRef="新興第三勢力",
        primarySensitivity=ApiSensitivity.PTT,
    ),
    VirtualParty(
        code="TBF",
        name="時代制衡力量",
        shortName="時衡力",
        realWorldRef="左翼勞工政黨",
        primarySensitivity=ApiSensitivity.PTT,
    ),
    VirtualParty(
        code="RNF",
        name="激進本土陣線",
        shortName="激本陣",
        realWorldRef="深綠側翼政黨",
        primarySensitivity=ApiSensitivity.INTL_NEWS,
    ),
    VirtualParty(
        code="PPU",
        name="小民生活參政聯盟",
        shortName="小民盟",
        realWorldRef="基層女性政黨",
        primarySensitivity=ApiSensitivity.LOCAL_NEWS,
    ),
    VirtualParty(
        code="EGP",
        name="生態永續綠黨",
        shortName="永續綠黨",
        realWorldRef="環保微型政黨",
        primarySensitivity=ApiSensitivity.WEATHER,
        secondarySensitivity=ApiSensitivity.AQI,
    ),
]


# ── 6 大地方派系 / 黑金勢力 ───────────────────────────────────
FACTIONS: list[LocalFaction] = [
    LocalFaction(
        code="SAND",
        name="海線砂石互助會",
        factionType="黑道土方",
        primarySensitivity=ApiSensitivity.WEATHER,
        description="掌控偏鄉與海岸線的實體動員力；豪雨→違法工程崩塌→黑金反噬",
    ),
    LocalFaction(
        code="BUILDER",
        name="都會重劃區建商同業會",
        factionType="財團金主",
        primarySensitivity=ApiSensitivity.STOCK,
        description="都市選舉最大金主；股災→獻金縮水→爛尾樓連累候選人",
    ),
    LocalFaction(
        code="TEMPLE",
        name="大甲/鯤鯓宗親宮廟聯盟",
        factionType="宗教派系",
        primarySensitivity=ApiSensitivity.PTT,
        description="極高樁腳忠誠度鐵票部隊；最怕網路炎上抉擇年輕票vs鐵票",
    ),
    LocalFaction(
        code="AGRI",
        name="農漁水利產銷總會",
        factionType="農漁系統",
        primarySensitivity=ApiSensitivity.WEATHER,
        description="中南部農村命脈；旱災/寒害→未爭取農補→忠誠度瞬間歸零",
    ),
    LocalFaction(
        code="EAST_CLAN",
        name="東部後山家族鐵衛軍",
        factionType="區域霸主",
        primarySensitivity=ApiSensitivity.WEATHER,
        description="免疫空戰負面新聞；地震/颱風孤島效應→依賴中央救災經費",
    ),
    LocalFaction(
        code="SOLAR",
        name="南台灣綠能光電開發協進會",
        factionType="新型政商複合體",
        primarySensitivity=ApiSensitivity.PTT,
        description="農地變更與光電利益；弊案爆發→全域醜聞拖累執政黨",
    ),
]


def getPartyByCode(code: str) -> VirtualParty | None:
    """依代碼查找政黨"""
    return next((p for p in PARTIES if p.code == code), None)


def getFactionByCode(code: str) -> LocalFaction | None:
    """依代碼查找派系"""
    return next((f for f in FACTIONS if f.code == code), None)
