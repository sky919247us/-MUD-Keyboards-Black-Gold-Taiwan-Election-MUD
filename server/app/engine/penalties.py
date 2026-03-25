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
    AP 透支機制：
    - AP > 0：正常行動，無懲罰
    - AP == 0：第一次透支，輕度負面效果（好感 -200，仇恨 +150）
    - AP < 0 且 > -100：第二次透支，重度負面效果（好感 -500，仇恨 +400，法務風險 +10）
    - AP <= -100：完全禁止行動
    回傳 (是否禁止行動, 訊息描述)。
    """
    ap = entity.resources.staffAp

    # 正常狀態：AP 充足，無懲罰
    if ap > 0:
        return False, None

    # 完全禁止：已透支 2 次（AP <= -100），不允許再行動
    if ap <= -100:
        return True, (
            "🚫【團隊崩潰】幕僚已連續透支 2 次（AP: {ap}），身心狀態極度惡化！\n"
            "所有行動已被凍結，請等待 AP 自然恢復後再行動。"
        ).format(ap=ap)

    # 第二次透支：AP 在 -99 ~ -1 之間
    if ap < 0:
        disasters = [
            "內部群組對話外洩：幕僚怒噴候選人的私聊被截圖",
            "記者會失控：疲憊的發言人口出驚人言論",
            "財務錯誤：過勞導致帳目混亂被會計師揭發",
            "行程大撞車：同時答應兩場衝突的公開活動",
        ]
        desc = random.choice(disasters)
        entity.applyAttributeChange(favorability=-500, aggro=400)
        entity.hiddenStats.legalRiskIndex = min(100, entity.hiddenStats.legalRiskIndex + 10)
        return False, (
            f"🚨【嚴重過勞・第 2 次透支】幕僚在極限狀態下勉強執行任務！\n"
            f"⚠ 觸發重大事故：{desc}\n"
            f"💔 好感度 -500 / 😡 仇恨值 +400 / ⚖️ 法務風險 +10"
        )

    # 第一次透支：AP 剛好 == 0
    disasters = [
        "幕僚打瞌睡：簡報投影片出現錯字",
        "行程遲到：候選人遲到 30 分鐘引發小插曲",
        "社群失誤：深夜發文語氣不當被截圖流傳",
    ]
    desc = random.choice(disasters)
    entity.applyAttributeChange(favorability=-200, aggro=150)
    return False, (
        f"⚠️【團隊過勞・第 1 次透支】幕僚 AP 已歸零，仍強行執行任務！\n"
        f"⚠ 小型事故：{desc}\n"
        f"💔 好感度 -200 / 😡 仇恨值 +150\n"
        f"⚡ 再透支 1 次後團隊將完全崩潰！"
    )

