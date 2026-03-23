"""
遊戲選項行動處理器
對應 UI 下方 6 宮格按鈕的邏輯（政見/掃街/攻防/募款/選情/幕僚）。
"""
from __future__ import annotations

import logging
from typing import Any

from app.ai.settlement_engine import settleAction
from app.game.world import gameWorld
from app.models.entity import PoliticalEntity

logger = logging.getLogger(__name__)


async def handleMenuAction(entity: PoliticalEntity, rawInput: str) -> str:
    """處理帶有 /act 前綴的標準主選單行動"""
    # 這裡可以根據具體選項做進一步的分流，
    # Phase2 先統一經過 AI 結算引擎，並附加按鈕類型的 prompt 上下文。

    # 解析後方參數
    actionDesc = rawInput.replace("/act ", "").strip()

    # 注入現實 API 資料，讓 AI 結算引擎能感知天氣與股市
    realityData: dict = {}
    try:
        from app.api_integrations import weather, twse
        w = await weather.fetchWeatherData()
        if w:
            realityData["weather"] = w
        delta = await twse.fetchTWSEDelta()
        if delta is not None:
            realityData["twse_delta"] = delta
    except Exception:
        pass  # 外部 API 失敗不應阻塞遊戲行動

    result = await settleAction(
        playerState=entity.model_dump(),
        realityApi=realityData,
        playerAction=actionDesc,
    )

    # 套用狀態變動並格式化
    changes = result.get("state_changes", {})
    entity.applyAttributeChange(
        fame=changes.get("fame", 0),
        favorability=changes.get("favorability", 0),
        aggro=changes.get("aggro", 0),
        politicalFunds=changes.get("political_funds", 0),
        staffAp=changes.get("staff_ap", 0),
    )
    
    # 儲存回資料庫
    await gameWorld.repo.save_entity(entity)

    lines = [
        "📺 " + result.get("news_report", ""),
        "",
        "── PTT 鄉民反應 ──",
    ]
    for comment in result.get("ptt_comments", []):
        lines.append(f"  {comment}")
    
    lines.append("───────────────────────────")
    lines.append(f"📊 [結算] 好感 {changes.get('favorability', 0):+d} ｜ 仇恨 {changes.get('aggro', 0):+d} ｜ 知名度 {changes.get('fame', 0):+d}")
    if changes.get("political_funds"):
        lines.append(f"💰 獻金變動：{changes.get('political_funds'):+,d} 元")
    if changes.get("staff_ap"):
        lines.append(f"⚡ 幕僚 AP：{changes.get('staff_ap'):+d}")

    return "\n".join(lines)
