"""
邊界懲罰機制
對應 00-game-architecture.md 第四章：歸零懲罰、造神運動、法務風險。
"""
from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.entity import PoliticalEntity

logger = logging.getLogger(__name__)


def checkAndApplyPenalties(entity: PoliticalEntity) -> list[str]:
    """
    檢查實體是否觸發邊界懲罰，套用效果並回傳事件日誌列表。
    每次 Tick 結算後呼叫。
    """
    events: list[str] = []
    attrs = entity.coreAttributes
    res = entity.resources
    hidden = entity.hiddenStats

    # ── 知名度歸零：政治透明人 ──────────────────────────────
    if attrs.fame == 0:
        events.append(f"【政治透明人】{entity.name} 知名度歸零：新聞稿無自然流量，小額募款鎖死")
        # HACK: 強制鎖定被動收入（在 Tick 引擎中會檢查此狀態）

    # ── 好感度觸底：信賴危機 / 社會性死亡 ──────────────────
    if attrs.favorability == 0:
        events.append(f"【信賴危機】{entity.name} 好感度歸零：幕僚 AP 消耗加倍")

    if attrs.favorability <= -10000:
        # 樁腳忠誠度每小時流失 5 點（在 Tick 中實作）
        events.append(f"【政治社會性死亡】{entity.name} 好感度觸底：樁腳忠誠度加速流失，罷免成功率 95%")
        for boss in entity.arraysAssets.localBosses:
            boss.loyalty = max(0, boss.loyalty - 5)

    # ── 仇恨值歸零：話題絕緣體 ─────────────────────────────
    if attrs.aggro == 0:
        events.append(f"【話題絕緣體】{entity.name} 仇恨值歸零：網軍攻擊無效，基本盤投票意願降低")

    # ── 仇恨值滿載：全國下架運動 ──────────────────────────
    if attrs.aggro >= 10000:
        events.append(f"【全國下架運動】{entity.name} 仇恨值滿載：敵對攻擊獲巨幅系統加成")

    # ── 政治獻金歸零：糧草斷絕 ─────────────────────────────
    if res.politicalFunds == 0:
        events.append(f"【糧草斷絕】{entity.name} 政治獻金歸零：AP 鎖死，付費媒體停播")
        res.staffAp = 0
        # 移除所有 Paid 媒體頻道
        entity.arraysAssets.mediaChannels = [
            ch for ch in entity.arraysAssets.mediaChannels
            if ch.alignmentType != "Paid"
        ]

    # ── 幕僚行動力歸零：團隊過勞 ─────────────────────────
    if res.staffAp == 0:
        events.append(f"【團隊過勞】{entity.name} 行動力歸零：自動防禦關閉，強行行動 75% 觸發公關災難")

    # ── 造神運動檢測 ───────────────────────────────────────
    if attrs.favorability >= hidden.godModeThreshold and not hidden.godModeActive:
        hidden.godModeActive = True
        events.append(f"【造神運動】{entity.name} 好感度極高觸發：道德標準閾值提升，微小負面事件將引發指數崩跌")

    # 造神運動中的額外脆弱性（將在 AI 結算引擎中加權處理）

    # ── 法務風險臨界 ──────────────────────────────────────
    if hidden.legalRiskIndex >= 80:
        events.append(f"【法務危機警告】{entity.name} 法務風險值 {hidden.legalRiskIndex}/100：隨時可能引爆查核懲罰")

    if hidden.legalRiskIndex >= 100:
        # 強制觸發法規懲罰：沒收 50% 獻金 + 刑事標記
        confiscated = res.politicalFunds // 2
        res.politicalFunds -= confiscated
        events.append(
            f"【法規懲罰引爆】{entity.name} 法務風險值達上限！沒收 {confiscated:,} 元獻金，"
            f"面臨 3 年以下有期徒刑風險（Game Over 邊緣）"
        )

    return events


def checkForceActionPenalty(entity: PoliticalEntity) -> tuple[bool, str | None]:
    """
    當 AP 為 0 時玩家強行行動：75% 機率觸發公關災難。
    回傳 (是否災難, 災難描述)。
    """
    if entity.resources.staffAp > 0:
        return False, None

    roll = random.randint(1, 100)
    if roll <= 75:
        disasters = [
            "幕僚失言：發言人在記者會上語出驚人",
            "行程大遲到：候選人遲到 2 小時引發民眾不滿",
            "團隊內鬨外流：內部群組對話被截圖散佈",
            "資料外洩：選民個資遭不當使用被爆料",
        ]
        desc = random.choice(disasters)
        # 套用災難效果
        entity.applyAttributeChange(favorability=-800, fame=-200)
        return True, f"【公關災難】{desc}（好感度 -800，知名度 -200）"

    return False, None
