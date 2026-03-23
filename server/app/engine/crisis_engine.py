"""
政治危機事件引擎
依照設計文件「政治危機事件設計與觸發機制.md」實作。
每次 Tick 結算後由 tick.py 呼叫，根據天氣/股市/法務風險觸發突發危機。
"""
from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.entity import PoliticalEntity

from app.models.entity import CampAlignment

logger = logging.getLogger(__name__)

# ── 政黨陣營常數 ──────────────────────────────────────────────
RULING_CAMP = CampAlignment.PAN_GREEN
OPPOSITION_CAMP = CampAlignment.PAN_BLUE


def checkAndApplyCrises(
    entities: list[PoliticalEntity],
    weatherImpact: dict,
    marketDelta: float = 0.0,
) -> list[str]:
    """
    對所有實體檢查並觸發政治危機事件。
    回傳全服事件廣播字串列表。

    參數：
    - entities: 所有政治實體
    - weatherImpact: 來自 weather.evaluateWeatherImpact() 的天氣影響字典
    - marketDelta: 台股大盤單日漲跌幅（百分比，如 -0.035 代表 -3.5%）
    """
    events: list[str] = []

    severity = weatherImpact.get("severity", "normal")
    weatherType = weatherImpact.get("type", "")
    hasRain = "rain" in weatherType or "typhoon" in weatherType
    hasTyphoon = "typhoon" in weatherType
    hasHighTemp = "heat" in weatherType

    for entity in entities:
        entityEvents = _checkEntityCrises(
            entity, severity, hasRain, hasTyphoon, hasHighTemp, marketDelta
        )
        events.extend(entityEvents)

    return events


def _checkEntityCrises(
    entity: PoliticalEntity,
    severity: str,
    hasRain: bool,
    hasTyphoon: bool,
    hasHighTemp: bool,
    marketDelta: float,
) -> list[str]:
    """單一實體的危機事件檢查（含 RNG，非必觸發）"""
    events: list[str] = []
    camp = entity.basicInfo.campAlignment
    hidden = entity.hiddenStats
    # 放寬建商判定：regionCode 或 bossId 含「建商/construction/營建」
    has_builders = any(
        any(kw in b.regionCode or kw in b.bossId.lower()
            for kw in ["建商", "construction", "營建", "開發"])
        for b in entity.arraysAssets.localBosses
    ) or len(entity.arraysAssets.localBosses) >= 3  # 樁腳過多也有風險

    # ──────────────────────────────────────────────────────────
    # 危機 1：基礎設施跳電（高溫天氣 + RNG）
    # ──────────────────────────────────────────────────────────
    if hasHighTemp and severity in ("warning", "emergency"):
        if random.random() < 0.15:  # 15% 機率觸發
            if camp == RULING_CAMP:
                damage = random.randint(500, 1200)
                entity.applyAttributeChange(favorability=-damage, aggro=300)
                events.append(
                    f"⚡【跳電危機】{entity.name} 轄區高溫跳電！"
                    f"民怨四起，好感度 -{damage}，仇恨值 +300。"
                    f"（可消耗 AP 發聲明止血）"
                )
                logger.info(f"[Crisis 1] 跳電危機觸發：{entity.name}")

    # ──────────────────────────────────────────────────────────
    # 危機 2：豆腐渣工程現形（豪雨 + 有建商樁腳）
    # ──────────────────────────────────────────────────────────
    if hasRain and severity in ("warning", "emergency") and has_builders:
        if random.random() < 0.25:  # 25% 觸發率
            aggroDmg = random.randint(800, 2000)
            entity.applyAttributeChange(aggro=aggroDmg, favorability=-500)

            # 切割判定 RNG（若玩家無主動切割，20% 機率自動觸發小幅切割但全損獻金）
            cut_msg = ""
            if random.random() < 0.2:
                cut_loss = int(entity.resources.politicalFunds * 0.1)
                entity.resources.politicalFunds -= cut_loss
                cut_msg = f"建商樁腳被迫切割，獻金損失 ${cut_loss:,}。"

            events.append(
                f"🏗️【豆腐渣工程】{entity.name} 暴雨後工程崩塌！"
                f"仇恨值 +{aggroDmg}。{cut_msg}"
            )
            logger.info(f"[Crisis 2] 豆腐渣工程觸發：{entity.name}")

    # ──────────────────────────────────────────────────────────
    # 危機 3：股災引發經濟恐慌（台股跌幅 > 3%）
    # ──────────────────────────────────────────────────────────
    if marketDelta < -0.03:
        if camp == RULING_CAMP:
            # 執政黨受創更重
            damage = int(abs(marketDelta) * 10000)  # 跌幅越大，扣好感越多
            damage = min(damage, 2000)
            entity.applyAttributeChange(favorability=-damage)

            # 未來 3 Tick 獻金衰減（以立即一次性模擬，暫不實作狀態標記）
            fund_cut = int(entity.resources.politicalFunds * 0.05)
            entity.applyAttributeChange(politicalFunds=-fund_cut)

            events.append(
                f"📉【股災經濟恐慌】台股重挫 {abs(marketDelta)*100:.1f}%！"
                f"{entity.name} 好感度 -{damage}，"
                f"政治獻金緊縮 ${fund_cut:,}。"
            )
            logger.info(f"[Crisis 3] 股災危機觸發：{entity.name}")
        elif camp == OPPOSITION_CAMP:
            # 在野黨網軍攻擊力加成 20%（提升知名度與仇恨值，並發放經濟動能）
            boost_fame = random.randint(30, 100)
            boost_aggro = random.randint(10, 50)
            boost_funds = random.randint(5000, 20000)
            entity.applyAttributeChange(fame=boost_fame, aggro=boost_aggro, politicalFunds=boost_funds)
            events.append(
                f"📣【在野黨出擊】台股崩盤，{entity.name} 展開經濟炎上攻勢！"
                f"知名度 +{boost_fame}，網路募捐獲得 ${boost_funds:,}。"
            )

    # ──────────────────────────────────────────────────────────
    # 危機 4：1450 側翼反串翻車（網軍隱蔽度不足時高機率發生）
    # ──────────────────────────────────────────────────────────
    busted_armies = [n for n in entity.arraysAssets.cyberArmyAccounts if n.stealthRating <= 20]
    if busted_armies and random.random() < 0.4:  # 40% 機率引爆醜聞
        # 全部網軍隱蔽度現在歸零（多數已是 0 了）
        total_output = sum(n.outputPower for n in busted_armies)
        aggroPenalty = total_output * 2
        favPenalty = len(busted_armies) * 200

        entity.applyAttributeChange(
            aggro=min(int(aggroPenalty), 3000),
            favorability=-min(int(favPenalty), 2000)
        )
        events.append(
            f"🚨【網軍翻車】{entity.name} 的 {len(busted_armies)} 個側翼帳號被鄉民抓包！"
            f"仇恨值暴增 +{min(int(aggroPenalty), 3000)}，"
            f"好感度 -{min(int(favPenalty), 2000)}。"
            f"需犧牲高階幕僚辭職止血！"
        )
        logger.info(f"[Crisis 4] 網軍翻車觸發：{entity.name}")

    # ──────────────────────────────────────────────────────────
    # 危機 5：颱風假決策政治豪賭（颱風警報邊緣觸發）
    # ──────────────────────────────────────────────────────────
    if hasTyphoon and severity == "warning":
        # 邊緣值：50% 機率觸發（模擬宣布/不宣布颱風假的政治豪賭）
        if random.random() < 0.5:
            damage = random.randint(2000, 4000)
            entity.applyAttributeChange(favorability=-damage)
            events.append(
                f"🌀【颱風假豪賭】{entity.name} 颱風假決策失誤！"
                f"民眾暴怒，好感度瞬間 -{damage}。"
                f"（可花費 500 萬獻金購買媒體版面挽救 60% 傷害）"
            )
            logger.info(f"[Crisis 5] 颱風假危機觸發：{entity.name}")

    # ──────────────────────────────────────────────────────────
    # 複合危機：法務風險爆表 + 負面輿論 → 政獻金法查核
    # ──────────────────────────────────────────────────────────
    if hidden.legalRiskIndex >= 60 and marketDelta < -0.02 and random.random() < 0.3:
        freeze_ratio = 0.3
        frozen = int(entity.resources.politicalFunds * freeze_ratio)
        entity.resources.politicalFunds -= frozen
        events.append(
            f"⚖️【政治獻金法查核】{entity.name} 法務風險值 {hidden.legalRiskIndex} + 股市下挫，"
            f"檢調介入調查！獻金池暫凍結 30%（${frozen:,}）。"
        )
        logger.info(f"[Crisis Composite] 法務查核觸發：{entity.name}")

    return events
