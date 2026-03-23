"""
新聞情感分析 API（Phase1：模擬資料）
台電即時電力 API（Phase1：模擬資料）
水利署水位 API（Phase1：模擬資料）
環境部 AQI API（Phase1：模擬資料）

統一將其他 4 個 API 以精簡方式放在同一個檔案，
Phase2 再各自拆分至獨立模組串接真實API。
"""
from __future__ import annotations

import logging
import random
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# ── 新聞情感分析 ─────────────────────────────────────────────
@dataclass
class NewsSentiment:
    """新聞情感快照"""
    weightedSentiment: float = 0.0   # -1.0 ~ +1.0
    volumeWeight: float = 0.0        # 聲量熱度 0~100
    topKeyword: str = ""


async def fetchNewsSentiment() -> NewsSentiment:
    """Phase1：模擬"""
    return NewsSentiment(
        weightedSentiment=round(random.uniform(-1.0, 1.0), 2),
        volumeWeight=round(random.uniform(0, 100), 1),
        topKeyword=random.choice(["弊案", "減稅", "軍售", "缺電", "颱風假", "物價", "AI產業"]),
    )


# ── 台電即時電力 ─────────────────────────────────────────────
@dataclass
class TaipowerSnapshot:
    """台電電力快照"""
    reserveMarginPercent: float = 10.0  # 備轉容量率
    hasBlackout: bool = False
    blackoutAreas: list[str] | None = None


async def fetchTaipowerData() -> TaipowerSnapshot:
    """Phase1：模擬"""
    margin = round(random.uniform(2.0, 15.0), 1)
    blackout = margin < 5.0 and random.random() < 0.3
    areas = random.sample(["中山區", "板橋區", "三重區", "台中西屯"], k=1) if blackout else None
    return TaipowerSnapshot(reserveMarginPercent=margin, hasBlackout=blackout, blackoutAreas=areas)


# ── 水利署水位 ───────────────────────────────────────────────
@dataclass
class WaterLevelSnapshot:
    """水位快照"""
    stationName: str = ""
    currentLevel: float = 0.0
    warningLevel: float = 5.0
    isAboveWarning: bool = False


async def fetchWaterLevel() -> WaterLevelSnapshot:
    """Phase1：模擬"""
    level = round(random.uniform(1.0, 8.0), 2)
    warning = 5.0
    station = random.choice(["大甲溪-豐原站", "濁水溪-西螺站", "高屏溪-里嶺站"])
    return WaterLevelSnapshot(
        stationName=station, currentLevel=level,
        warningLevel=warning, isAboveWarning=level > warning,
    )


# ── 環境部 AQI ───────────────────────────────────────────────
@dataclass
class AqiSnapshot:
    """AQI 快照"""
    areaName: str = ""
    aqiValue: int = 50
    status: str = "良好"    # 良好/普通/對敏感族群不健康/不健康/非常不健康/危害


async def fetchAqiData() -> AqiSnapshot:
    """Phase1：模擬"""
    aqi = random.randint(20, 200)
    area = random.choice(["高雄左營", "台中西屯", "嘉義太保", "屏東潮州"])
    if aqi <= 50:
        st = "良好"
    elif aqi <= 100:
        st = "普通"
    elif aqi <= 150:
        st = "對敏感族群不健康"
    elif aqi <= 200:
        st = "不健康"
    else:
        st = "非常不健康"
    return AqiSnapshot(areaName=area, aqiValue=aqi, status=st)
