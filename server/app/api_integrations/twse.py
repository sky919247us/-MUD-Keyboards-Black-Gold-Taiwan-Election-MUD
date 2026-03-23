"""
台股 TWSE API 串接（Phase1：模擬資料）
Phase2 將串接真實 TWSE開放API：https://openapi.twse.com.tw/
"""
from __future__ import annotations

import logging
import random
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class StockSnapshot:
    """股市快照"""
    indexValue: float         # 目前大盤指數
    previousClose: float      # 昨日收盤
    changePercent: float       # 漲跌幅百分比
    isMarketOpen: bool = True


async def fetchStockData() -> StockSnapshot:
    """
    取得台股大盤資料。
    Phase1：回傳模擬資料（±5% 隨機波動）。
    """
    # TODO: Phase2 替換為真實 TWSE API 呼叫
    baseIndex = 22000.0
    change = random.uniform(-5.0, 5.0)
    currentIndex = baseIndex * (1 + change / 100)

    snapshot = StockSnapshot(
        indexValue=round(currentIndex, 2),
        previousClose=baseIndex,
        changePercent=round(change, 2),
    )
    logger.info(f"[TWSE 模擬] 大盤 {snapshot.indexValue:.0f}（{snapshot.changePercent:+.2f}%）")
    return snapshot


def evaluateStockImpact(snapshot: StockSnapshot) -> dict:
    """
    評估股市對遊戲的影響。
    回傳影響描述字典。
    """
    effects: dict = {"type": "stock", "raw": snapshot}

    if snapshot.changePercent <= -3.0:
        # 股災級別
        effects["severity"] = "crash"
        effects["incumbentFavPenalty"] = int(500 * abs(snapshot.changePercent))
        effects["globalFundDecay"] = 0.4   # 全域獻金衰減 40%
        effects["oppositionAtkBuff"] = 1.5  # 在野黨攻擊力 ×150%
        effects["narrative"] = f"台股重挫 {snapshot.changePercent:.1f}%，經濟恐慌蔓延！"
    elif snapshot.changePercent >= 3.0:
        effects["severity"] = "boom"
        effects["incumbentFavBonus"] = int(200 * snapshot.changePercent)
        effects["narrative"] = f"台股大漲 {snapshot.changePercent:.1f}%，執政黨迎來經濟紅利"
    else:
        effects["severity"] = "normal"
        effects["narrative"] = f"台股小幅波動 {snapshot.changePercent:+.1f}%"

    return effects


async def fetchMarketDelta() -> float:
    """
    取得台股大盤當日漲跌幅，以小數形式回傳（例如 -0.035 代表 -3.5%）。
    供 tick.py 與 crisis_engine.py 使用。
    """
    snapshot = await fetchStockData()
    return snapshot.changePercent / 100.0
