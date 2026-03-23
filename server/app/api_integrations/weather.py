"""
中央氣象署 API 串接（Phase1：模擬資料）
Phase2 串接 W-C0034-001 颱風消息與警報資料集。
"""
from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class WeatherAlert:
    """天氣警報快照"""
    hasAlert: bool = False
    category: str = ""            # Met（氣象）
    areaDesc: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
import time
import httpx
from app.config import settings

_weather_cache: WeatherAlert | None = None
_weather_cache_time: float = 0

async def fetchWeatherData() -> WeatherAlert:
    """從中央氣象署 (CWA) 獲取即時天氣警報 (W-C0033-001) 與颱風警報 (W-C0034-001)"""
    global _weather_cache, _weather_cache_time
    
    # 快取機制：600 秒 (10 分鐘) 內不重新抓取
    if _weather_cache and (time.time() - _weather_cache_time < 600):
        logger.debug("使用天氣快取資料，距離上次更新未滿 10 分鐘")
        return _weather_cache

    if not settings.CWA_API_KEY:
        logger.warning("未設定 CWA_API_KEY，略過天氣檢查")
        return WeatherAlert()

    try:
        async with httpx.AsyncClient() as client:
            # 1. 先查颱風警報 W-C0034-001
            typhoon_url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/W-C0034-001?Authorization={settings.CWA_API_KEY}&format=JSON"
            res_typhoon = await client.get(typhoon_url, timeout=5.0)
            if res_typhoon.status_code == 200:
                data = res_typhoon.json()
                infos = data.get("records", {}).get("info", [])
                for info in infos:
                    headline = info.get("headline", "")
                    if "解除" not in headline and "颱風" in headline:
                        _weather_cache = WeatherAlert(
                            hasAlert=True, 
                            category="Met", 
                            areaDesc=["全台"], 
                            keywords=["颱風"], 
                            severity="emergency"
                        )
                        _weather_cache_time = time.time()
                        return _weather_cache
            
            # 2. 查一般天氣警報 W-C0033-001
            warn_url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/W-C0033-001?Authorization={settings.CWA_API_KEY}&format=JSON"
            res_warn = await client.get(warn_url, timeout=5.0)
            if res_warn.status_code == 200:
                data = res_warn.json()
                locations = data.get("records", {}).get("location", [])
                
                affected_areas = []
                keywords = set()
                
                for loc in locations:
                    hazards = loc.get("hazardConditions", {}).get("hazards", [])
                    active_hazards = [h.get("info", {}).get("phenomena") for h in hazards if h.get("info", {}).get("significance")]
                    if active_hazards:
                        affected_areas.append(loc["locationName"])
                        for ah in active_hazards:
                            if ah: keywords.add(ah)
                
                if affected_areas:
                    # 判斷嚴重度（若有超大豪雨等則升級）
                    severity = "warning"
                    if any("大豪雨" in kw or "超大豪雨" in kw for kw in keywords):
                        severity = "emergency"
                        
                    _weather_cache = WeatherAlert(
                        hasAlert=True,
                        category="Met",
                        areaDesc=affected_areas,
                        keywords=list(keywords),
                        severity=severity
                    )
                    _weather_cache_time = time.time()
                    return _weather_cache
                    
    except Exception as e:
        logger.error(f"[CWA API] 取得氣象資料失敗: {e}")

    _weather_cache = WeatherAlert()
    _weather_cache_time = time.time()
    return _weather_cache


def evaluateWeatherImpact(alert: WeatherAlert) -> dict:
    """評估天氣對遊戲的影響"""
    effects: dict = {"type": "weather", "raw": alert}

    if not alert.hasAlert:
        effects["severity"] = "clear"
        effects["narrative"] = "天氣穩定，選情正常運作"
        return effects

    effects["affectedAreas"] = alert.areaDesc
    effects["keywords"] = alert.keywords

    if alert.severity == "emergency":
        effects["severity"] = "emergency"
        effects["narrative"] = f"⚠ 颱風警報！影響區域：{'、'.join(alert.areaDesc)}"
        effects["forcedDisasterMode"] = True
        effects["apRecoveryPenalty"] = 0.5
    else:
        effects["severity"] = "warning"
        effects["narrative"] = f"⛈ 大雨特報：{'、'.join(alert.areaDesc)}（{'、'.join(alert.keywords)}）"

    return effects
