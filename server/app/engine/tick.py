"""
Tick 結算引擎
每個系統 Tick（預設 10 分鐘 / 測試 30 秒）執行一次，處理：
1. 幕僚行動力（AP）自然恢復
2. 被動收入（樁腳募款 + 自媒體流量）
3. 資源衰減（Paid 媒體持續消耗獻金）
4. 外部 API 觸發檢查
5. 邊界懲罰檢查
"""
from __future__ import annotations

import logging
import random
from collections import deque
from typing import List

from app.api_integrations import weather, twse
from app.api_integrations.news_scraper import scan_news_for_entities
from app.ai.settlement_engine import analyzeNewsSentiment_LLM
from app.engine.penalties import checkAndApplyPenalties
from app.models.entity import PoliticalEntity

logger = logging.getLogger(__name__)

# 紀錄已經推播過的新聞，避免重複發送（上限 500 筆，自動淘汰舊的）
_seen_news_urls: deque[str] = deque(maxlen=500)

# 新聞情意分析關鍵字規則
_NEGATIVE_KEYWORDS = ["抗議", "醜聞", "貪污", "弊案", "爆料", "起訴", "收押",
                      "賄賂", "詐騙", "洗錢", "炎上", "翻車", "道歉", "辭職",
                      "下台", "罷免", "違法", "舞弊", "濫權", "失言"]
_POSITIVE_KEYWORDS = ["表揚", "感謝", "突破", "成功", "獲獎", "捐款", "公益",
                      "建設", "通過", "改革", "滿意度", "支持率", "好評",
                      "創新", "增長", "福利", "補助", "減稅"]

# ── 可調常數 ──────────────────────────────────────────────────
AP_RECOVERY_PER_TICK = 5              # 每 Tick 自動恢復的 AP
PASSIVE_FUND_PER_BOSS = 5_000         # 每位樁腳每 Tick 的小額募款
PASSIVE_FAME_PER_MEDIA_SUB = 0.001    # 每訂閱數每 Tick 的知名度分潤
PAID_MEDIA_COST_PER_TICK = 50_000     # 每個 Paid 媒體每 Tick 消耗的獻金
LOYALTY_DECAY_PER_TICK = 1            # 樁腳忠誠度每 Tick 自然衰減


def executeTick(entities: list[PoliticalEntity], weatherImpact: dict = None) -> list[str]:
    """
    對所有政治實體執行一次 Tick 結算。
    回傳所有事件日誌。
    """
    allEvents: list[str] = []
    
    # 加入全局天氣事件廣播
    if weatherImpact and weatherImpact.get("severity") in ("warning", "emergency"):
        allEvents.append(f"\n{weatherImpact.get('narrative')}\n")

    for entity in entities:
        events = executeEntityTick(entity, weatherImpact)
        allEvents.extend(events)

    return allEvents


def executeEntityTick(entity: PoliticalEntity, weatherImpact: dict = None) -> list[str]:
    """單一實體的 Tick 結算"""
    events: list[str] = []
    res = entity.resources
    arrays = entity.arraysAssets

    # ── 1. AP 自然恢復 ─────────────────────────────────────
    if res.politicalFunds > 0:  # 糧草斷絕時 AP 不恢復
        oldAp = res.staffAp
        recovery = AP_RECOVERY_PER_TICK
        
        # 氣象警報造成的競選活動阻礙 (AP 減半)
        if weatherImpact and weatherImpact.get("severity") in ("warning", "emergency"):
            penalty = weatherImpact.get("apRecoveryPenalty", 0.5)
            recovery = max(1, int(recovery * penalty))

        res.staffAp = min(100, res.staffAp + recovery)
        if res.staffAp > oldAp:
            events.append(f"[Tick] {entity.name} AP 恢復 +{res.staffAp - oldAp}（現 {res.staffAp}）")

    # ── 2. 被動收入：樁腳離線募款 ──────────────────────────
    # NOTE: 知名度歸零時鎖死被動募款
    if entity.coreAttributes.fame > 0:
        bossIncome = sum(
            PASSIVE_FUND_PER_BOSS * (boss.loyalty / 100)
            for boss in arrays.localBosses
        )
        if bossIncome > 0:
            actual = entity.applyAttributeChange(politicalFunds=int(bossIncome))
            events.append(
                f"[Tick] {entity.name} 樁腳被動募款 +{actual.get('politicalFunds', 0):,} 元"
            )

    # ── 3. 被動收入：自媒體流量分潤 ────────────────────────
    totalSubs = entity.totalMediaSubscribers
    fameBump = int(totalSubs * PASSIVE_FAME_PER_MEDIA_SUB)
    if fameBump > 0:
        actual = entity.applyAttributeChange(fame=fameBump)
        events.append(
            f"[Tick] {entity.name} 自媒體流量分潤 → 知名度 +{actual.get('fame', 0)}"
        )

    # ── 4. Paid 媒體持續消耗獻金 ──────────────────────────
    paidChannels = [ch for ch in arrays.mediaChannels if ch.alignmentType == "Paid"]
    if paidChannels:
        totalCost = len(paidChannels) * PAID_MEDIA_COST_PER_TICK
        actual = entity.applyAttributeChange(politicalFunds=-totalCost)
        events.append(
            f"[Tick] {entity.name} 付費媒體維護費 {actual.get('politicalFunds', 0):,} 元"
        )

    # ── 5. 樁腳忠誠度自然衰減 ─────────────────────────────
    for boss in arrays.localBosses:
        boss.loyalty = max(0, boss.loyalty - LOYALTY_DECAY_PER_TICK)

    # ── 6. 邊界懲罰檢查 ──────────────────────────────────
    penaltyEvents = checkAndApplyPenalties(entity)
    events.extend(penaltyEvents)

    return events


async def executeTickAsync(entities: List[PoliticalEntity]) -> List[str]:
    """
    非同步 Tick，除了執行原有的實體 Tick，還會：
    1. 抓取外部天氣/股市 API
    2. 掃描新聞 RSS 並連動實體
    3. 觸發政治危機事件
    4. 執行 NPC AI 自動行為
    """
    # 獲取全域天氣警報
    from app.api_integrations.weather import fetchWeatherData, evaluateWeatherImpact
    alert = await fetchWeatherData()
    weatherImpact = evaluateWeatherImpact(alert)

    # 獲取台股大盤漲跌幅
    marketDelta = 0.0
    try:
        from app.api_integrations.twse import fetchMarketDelta
        marketDelta = await fetchMarketDelta()
    except Exception as e:
        logger.warning(f"[TWSE] 無法取得股市 delta: {e}")

    events = executeTick(entities, weatherImpact)

    # --- 處理真實新聞連動 ---
    try:
        matched_results = await scan_news_for_entities()
        # 篩出還沒處理過的新聞
        new_results = [r for r in matched_results if r.news_link not in _seen_news_urls]

        if new_results:
            affected_ids = {r.entity_id for r in new_results}

            for ent in entities:
                if ent.entityId in affected_ids:
                    my_news = [r for r in new_results if r.entity_id == ent.entityId]
                    for mn in my_news:
                        _seen_news_urls.append(mn.news_link)
                        # 關鍵字規則情意分析
                        title = mn.news_title
                        neg_hits = sum(1 for kw in _NEGATIVE_KEYWORDS if kw in title)
                        pos_hits = sum(1 for kw in _POSITIVE_KEYWORDS if kw in title)
                        is_positive = pos_hits > neg_hits if (pos_hits + neg_hits) > 0 else await analyzeNewsSentiment_LLM(title)
                        if is_positive:
                            ent.applyAttributeChange(fame=50, favorability=15)
                            events.append(f"🚨【即時新聞】{ent.name} 相關報導：{title} (好感度增加)")
                        else:
                            ent.applyAttributeChange(fame=20, favorability=-15, aggro=20)
                            events.append(f"🚨【負面炎上】{ent.name} 相關報導：{title} (仇恨暴增)")
    except Exception as e:
        logger.error(f"[NER News] 爬蟲抓取失敗: {e}")

    # --- 政治危機事件引擎 ---
    try:
        from app.engine.crisis_engine import checkAndApplyCrises
        crisisEvents = checkAndApplyCrises(entities, weatherImpact, marketDelta)
        events.extend(crisisEvents)
    except Exception as e:
        logger.error(f"[CrisisEngine] 危機事件引擎失敗: {e}")

    # --- NPC AI 自動行為 ---
    _executeNpcBehavior(entities, marketDelta, weatherImpact)

    # 將所有變動過的實體批量寫回資料庫（單一 Transaction）
    from app.game.world import gameWorld
    await gameWorld.repo.batch_save_entities(entities)

    return events


def _executeNpcBehavior(
    entities: List[PoliticalEntity],
    marketDelta: float,
    weatherImpact: dict,
) -> None:
    """
    NPC AI 自動行為邏輯（深化版）。
    依照實體層級、陣營、當前狀態做出決策：
    - 好感度過低 → 掃街止血
    - 資金不足 → 募款
    - 知名度過低 → 投放廣告
    - 仇恨值高 → 低調經營
    - 股市大跌 + 在野黨 → 發動輿論攻勢
    - 隨機主動攻擊其他陣營
    """
    from app.models.entity import EntityLevel, CampAlignment

    # 政黨性格加權：好鬥型 vs 穩健型
    AGGRESSIVE_CAMPS = {CampAlignment.PAN_BLUE, CampAlignment.WHITE}

    for entity in entities:
        camp = entity.basicInfo.campAlignment
        level = entity.basicInfo.level
        attrs = entity.coreAttributes
        res = entity.resources
        is_aggressive_party = camp in AGGRESSIVE_CAMPS

        # 每個 NPC 每 Tick 最多執行一個行為（避免過度干預）
        acted = False

        # ── 優先級 1：好感度危機止血（< 200） ──────────────
        if attrs.favorability < 200 and not acted:
            if random.random() < 0.4:  # 40% 機率掃街
                fame_gain = random.randint(10, 30)
                fav_gain = random.randint(50, 150)
                entity.applyAttributeChange(fame=fame_gain, favorability=fav_gain)
                logger.debug(f"[NPC AI] {entity.name} 好感度過低，緊急掃街拜票 (+{fav_gain})")
                acted = True

        # ── 優先級 2：資金不足時募款（< 100 萬） ──────────
        if res.politicalFunds < 1_000_000 and not acted:
            if random.random() < 0.35:
                fundraise = random.randint(200_000, 800_000)
                entity.applyAttributeChange(politicalFunds=fundraise)
                logger.debug(f"[NPC AI] {entity.name} 資金告急，發起募款 (+${fundraise:,})")
                acted = True

        # ── 優先級 3：知名度過低時投廣告（< 2000） ────────
        if attrs.fame < 2000 and res.politicalFunds > 500_000 and not acted:
            if random.random() < 0.25:
                ad_cost = random.randint(100_000, 300_000)
                fame_gain = random.randint(50, 200)
                entity.applyAttributeChange(politicalFunds=-ad_cost, fame=fame_gain)
                logger.debug(f"[NPC AI] {entity.name} 自動投放廣告 (知名度+{fame_gain})")
                acted = True

        # ── 優先級 4：仇恨值過高時低調經營（> 7000） ──────
        if attrs.aggro > 7000 and not acted:
            if random.random() < 0.3:
                fav_gain = random.randint(30, 100)
                entity.applyAttributeChange(favorability=fav_gain)
                logger.debug(f"[NPC AI] {entity.name} 仇恨值過高，低調做公益 (+{fav_gain} 好感)")
                acted = True

        # ── 優先級 5：股市大跌時在野黨/好鬥型主動攻擊 ────
        if marketDelta < -0.03 and is_aggressive_party and not acted:
            if random.random() < 0.3:
                fame_gain = random.randint(30, 120)
                aggro_gain = random.randint(50, 200)
                entity.applyAttributeChange(fame=fame_gain, aggro=aggro_gain)
                logger.debug(f"[NPC AI] {entity.name} 趁股災發動輿論攻勢 (知名度+{fame_gain})")
                acted = True

        # ── 優先級 6：高層級 NPC 有更多主動行為 ──────────
        if level in (EntityLevel.PRESIDENT, EntityLevel.MAYOR) and not acted:
            if random.random() < 0.1:  # 10% 機率發表政見
                fame_gain = random.randint(20, 80)
                fav_change = random.randint(-30, 60)
                entity.applyAttributeChange(fame=fame_gain, favorability=fav_change)
                logger.debug(f"[NPC AI] {entity.name} ({level}) 主動發表政見")
                acted = True

        # ── 優先級 7：好鬥型政黨隨機挑釁 ─────────────────
        if is_aggressive_party and not acted:
            if random.random() < 0.08:  # 8% 機率挑釁
                fame_gain = random.randint(10, 50)
                aggro_gain = random.randint(30, 100)
                entity.applyAttributeChange(fame=fame_gain, aggro=aggro_gain)
                logger.debug(f"[NPC AI] {entity.name} 主動發動輿論攻勢")

