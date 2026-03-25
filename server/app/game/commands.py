"""
MUD 指令解析與路由
處理玩家輸入的文字指令，分發至對應的引擎函式。
"""
from __future__ import annotations

import logging
from typing import Any

from app.ai.settlement_engine import settleAction, generateCombatNarrative
from app.engine.combat import attemptBossFlip, launchCyberAttack
from app.engine.penalties import checkForceActionPenalty
from app.engine.events import get_crisis_by_id
from app.game.world import gameWorld
from app.models.entity import PoliticalEntity, LocalBoss, CyberArmyAccount, Platform
from app.game.economy import market
import random

logger = logging.getLogger(__name__)

async def _handleResolveCrisis(entity: PoliticalEntity, args: list[str]) -> str:
    """處理玩家決策危機：/resolve_crisis <crisis_id> <option_id>"""
    if len(args) < 2:
        return "❌ 參數錯誤 (需提供危機 ID 與 選項 ID)"
    
    crisis_id = args[0]
    opt_id = args[1]
    
    crisis = get_crisis_by_id(crisis_id)
    if not crisis:
        return f"❌ 找不到對應的危機 ({crisis_id})"
        
    option = next((o for o in crisis["options"] if o["id"] == opt_id), None)
    if not option:
        return f"❌ 找不到該決策選項 ({opt_id})"

    # 檢查 AP 與資金
    if entity.resources.staffAp < option["cost_ap"]:
        return f"❌ 幕僚行動力不足 (需要 {option['cost_ap']} AP)"
    if entity.resources.politicalFunds < option["cost_funds"]:
        return f"❌ 政治獻金不足 (需要 {option['cost_funds']} 元)"

    # 扣除成本
    entity.resources.staffAp -= option["cost_ap"]
    entity.resources.politicalFunds -= option["cost_funds"]
        
    # 套用影響
    entity.applyAttributeChange(
        favorability=option.get("effect_fav", 0),
        aggro=option.get("effect_aggro", 0)
    )
    
    await gameWorld.repo.save_entity(entity)
    
    # 組合回傳結果
    lines = [
        f"決策已執行：{option['desc']}",
        f"消耗：AP -{option['cost_ap']}, 資金 -{option['cost_funds']}",
        f"影響：好感度 {option.get('effect_fav', 0):+d}, 仇恨值 {option.get('effect_aggro', 0):+d}"
    ]
    return "\n".join(lines)


def _generate_boss_name() -> str:
    surnames = ["李", "王", "張", "陳", "林", "黃", "吳", "劉", "蔡", "楊", "高", "郭", "洪"]
    titles = ["董", "哥", "大仔", "姊", "代表", "頭目", "主任"]
    return random.choice(surnames) + random.choice(titles)

def _generate_army_name() -> str:
    prefixes = ["側翼", "狂人", "綠色", "藍色", "白色", "覺青", "小草", "公關", "打手"]
    suffixes = ["粉專", "情報局", "連線", "出征軍", "戰士", "後援會", "同盟"]
    return random.choice(prefixes) + random.choice(suffixes)

async def _handleRecruitBoss(entity: PoliticalEntity, args: list[str]) -> str:
    cost = 1_000_000
    if entity.resources.politicalFunds < cost:
        return f"❌ 政治獻金不足 (需要 ${cost:,})"
    entity.resources.politicalFunds -= cost
    new_boss = LocalBoss(name=_generate_boss_name(), mobilizationPower=500, loyalty=50)
    entity.arraysAssets.localBosses.append(new_boss)
    await gameWorld.repo.save_entity(entity)
    return f"🤝 成功花費 ${cost:,} 結盟了新樁腳：{new_boss.name}"

async def _handleRecruitArmy(entity: PoliticalEntity, args: list[str]) -> str:
    cost = 500_000
    if entity.resources.politicalFunds < cost:
        return f"❌ 政治獻金不足 (需要 ${cost:,})"
    entity.resources.politicalFunds -= cost
    new_army = CyberArmyAccount(name=_generate_army_name(), outputPower=300, stealthRating=80)
    entity.arraysAssets.cyberArmyAccounts.append(new_army)
    await gameWorld.repo.save_entity(entity)
    return f"💻 成功花費 ${cost:,} 建立了新網軍節點：{new_army.name}"

async def _handleUpgradeBoss(entity: PoliticalEntity, args: list[str]) -> str:
    if not args:
        return "❌ 參數錯誤 (需提供樁腳 ID)"
    boss_id = args[0]
    boss = next((b for b in entity.arraysAssets.localBosses if b.bossId == boss_id), None)
    if not boss:
        return f"❌ 找不到該樁腳 ({boss_id})"
    cost = boss.mobilizationPower * 100
    if entity.resources.politicalFunds < cost:
        return f"❌ 政治獻金不足 (需要 ${cost:,})"
    entity.resources.politicalFunds -= cost
    boss.mobilizationPower += 50
    await gameWorld.repo.save_entity(entity)
    return f"📈 成功花費 ${cost:,} 提升樁腳 {boss.name} 的動員力至 {boss.mobilizationPower}"

async def _handleUpgradeArmy(entity: PoliticalEntity, args: list[str]) -> str:
    if not args:
        return "❌ 參數錯誤 (需提供網軍 ID)"
    army_id = args[0]
    army = next((a for a in entity.arraysAssets.cyberArmyAccounts if a.nodeId == army_id), None)
    if not army:
        return f"❌ 找不到該網軍帳號 ({army_id})"
    cost = army.outputPower * 50
    if entity.resources.politicalFunds < cost:
        return f"❌ 政治獻金不足 (需要 ${cost:,})"
    entity.resources.politicalFunds -= cost
    army.outputPower += 50
    await gameWorld.repo.save_entity(entity)
    return f"🚀 成功花費 ${cost:,} 升級網軍 {army.name} 的攻擊力至 {army.outputPower}"


async def handleCommand(entityId: str, rawInput: str) -> str:
    """
    處理玩家原始指令，回傳結果文字。
    支援的指令：
        /status         - 查看自身狀態
        /look           - 查看遊戲世界概覽
        /attack <目標>  - 對目標發動網軍攻擊
        /flip <目標> <樁腳ID> - 拔樁行動
        /act <行動描述> - 自由行動（交給 AI 引擎結算）
        /help           - 指令說明
    """
    parts = rawInput.strip().split(maxsplit=2)
    if not parts:
        return "請輸入指令。輸入 /help 查看說明。"

    cmd = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []

    entity = await gameWorld.repo.get_entity_by_id(entityId)
    if entity is None:
        return "❌ 找不到你的候選人實體。請先建立角色。"

    match cmd:
        case "/status":
            return _formatStatus(entity)
        case "/look":
            return await _formatWorldOverview(args)
        case "/attack":
            return await _handleAttack(entity, args)
        case "/flip":
            return await _handleFlip(entity, args)
        case "/invest":
            return await _handleInvest(entity, args)
        case "/launder":
            return await _handleLaunder(entity, args)
        case "/act":
            return await _handleAction(entity, args)
        case "/resolve_crisis":
            return await _handleResolveCrisis(entity, args)
        case "/recruit_boss":
            return await _handleRecruitBoss(entity, args)
        case "/recruit_army":
            return await _handleRecruitArmy(entity, args)
        case "/upgrade_boss":
            return await _handleUpgradeBoss(entity, args)
        case "/upgrade_army":
            return await _handleUpgradeArmy(entity, args)
        case "/help":
            return _formatHelp()
        case _:
            return f"❓ 未知指令「{cmd}」。輸入 /help 查看說明。"


def _formatStatus(entity: PoliticalEntity) -> str:
    """格式化角色狀態顯示"""
    a = entity.coreAttributes
    r = entity.resources
    h = entity.hiddenStats
    bosses = entity.arraysAssets.localBosses
    armies = entity.arraysAssets.cyberArmyAccounts
    medias = entity.arraysAssets.mediaChannels

    lines = [
        f"╔══════════════════════════════════════╗",
        f"║ 候選人：{entity.name:<20s}     ║",
        f"║ 政黨：{entity.basicInfo.partyAffiliation}｜{entity.basicInfo.campAlignment}          ║",
        f"║ 層級：{entity.basicInfo.level}                       ║",
        f"╠══════════════════════════════════════╣",
        f"║ 知名度：{a.fame:>6,} / 10,000              ║",
        f"║ 好感度：{a.favorability:>7,} / 10,000             ║",
        f"║ 仇恨值：{a.aggro:>6,} / 10,000              ║",
        f"╠══════════════════════════════════════╣",
        f"║ 合法獻金：${r.politicalFunds:>13,}          ║",
        f"║ 非法黑金：${r.unlaunderedFunds:>13,}          ║",
        f"║ 持有股票：{sum(r.stockPortfolio.values()):>5} 股                    ║",
        f"║ 幕僚 AP：{r.staffAp:>3} / 100                  ║",
        f"╠══════════════════════════════════════╣",
        f"║ 樁腳：{len(bosses)} 個節點                        ║",
        f"║ 網軍：{len(armies)} 個帳號                        ║",
        f"║ 自媒體：{len(medias)} 個頻道                      ║",
        f"║ 🔒 法務風險：{h.legalRiskIndex}/100               ║",
        f"╚══════════════════════════════════════╝",
    ]
    return "\n".join(lines)


async def _formatWorldOverview(args: list[str] = None) -> str:
    """遊戲世界概覽（支援 /look top、/look [政黨代碼] 篩選）"""
    entities = await gameWorld.repo.get_all_entities()
    
    # 依知名度排序
    sorted_entities = sorted(entities, key=lambda e: e.fame, reverse=True)
    
    # 篩選模式
    filter_label = ""
    if args:
        sub_cmd = args[0].upper()
        if sub_cmd == "TOP":
            sorted_entities = sorted_entities[:10]
            filter_label = "（前 10 名）"
        elif sub_cmd == "ALL":
            filter_label = "（全伺服器候選人）"
        else:
            # 視為政黨代碼篩選
            sorted_entities = [e for e in sorted_entities if e.basicInfo.partyAffiliation.upper() == sub_cmd]
            filter_label = f"（{sub_cmd} 陣營）"
    else:
        # 預設只顯示前 10 名
        sorted_entities = sorted_entities[:10]
        filter_label = "（前 10 名，輸入 /look all 或 /look [政黨] 篩選）"

    lines = [
        f"=== 台灣選戰 MUD ===",
        f"Tick #{gameWorld.tickCount}｜賽季：{gameWorld.currentPhase}",
        f"全服候選人數：{len(entities)}{filter_label}",
        "─" * 50,
    ]
    for i, e in enumerate(sorted_entities, 1):
        lines.append(
            f"  #{i} {e.name}（{e.basicInfo.partyAffiliation}）"
            f"知名度 {e.fame:,} ┃ 好感 {e.favorability:,} ┃ 仇恨 {e.aggro:,}"
        )
    if not sorted_entities:
        lines.append("  （無符合條件的候選人）")
    return "\n".join(lines)


async def _handleAttack(entity: PoliticalEntity, args: list[str]) -> str:
    """網軍攻擊指令"""
    if not args:
        return "用法: /attack <對手名稱>"

    # 檢查 AP 為零時的強行行動風險
    isDisaster, disasterMsg = checkForceActionPenalty(entity)
    if isDisaster and disasterMsg:
        return disasterMsg

    targetName = args[0]
    target = await gameWorld.repo.get_entity_by_name(targetName)
    if target is None:
        return f"❌ 找不到名為「{targetName}」的候選人"

    success, result_data = launchCyberAttack(entity, target)
    
    # 型別為字串代表系統阻擋（費用不足等）
    if isinstance(result_data, str):
        return result_data

    # 型別為字典代表戰鬥已執行，取得參數
    kwargs = result_data
    
    # 儲存雙方狀態
    await gameWorld.repo.save_entity(entity)
    await gameWorld.repo.save_entity(target)

    # 決定事件類型並呼叫敘事引擎
    event_type = "attack_fail" if kwargs.get("busted") else "attack_success"
    narrative = await generateCombatNarrative(event_type, kwargs)

    # 全服廣播判定
    if success and not kwargs.get("busted") and random.random() < 0.3:
        import asyncio
        asyncio.create_task(gameWorld.trigger_news_flash(
            attacker_name=entity.name,
            defender_name=target.name,
            event="網軍大規模突襲",
            damage_desc="網路聲量大幅動盪"
        ))
    
    # 格式化輸出
    lines = [
        "📺 " + narrative.get("news_report", ""),
        "",
        "── PTT 鄉民反應 ──",
    ]
    for comment in narrative.get("ptt_comments", []):
        lines.append(f"  {comment}")
    lines.append("")
    lines.append(f"[結算] 對方好感度 -{kwargs.get('favDamage', 0)}，仇恨值 +{kwargs.get('aggroDamage', 0)}")

    return "\n".join(lines)


async def _handleFlip(entity: PoliticalEntity, args: list[str]) -> str:
    """拔樁指令"""
    if len(args) < 2:
        return "用法: /flip <對手名稱> <樁腳ID>"

    targetName = args[0]
    bossId = args[1]
    target = await gameWorld.repo.get_entity_by_name(targetName)
    if target is None:
        return f"❌ 找不到名為「{targetName}」的候選人"

    success, result_data = attemptBossFlip(entity, target, bossId)
    
    if isinstance(result_data, str):
        return result_data

    kwargs = result_data
    
    # 儲存雙方狀態
    await gameWorld.repo.save_entity(entity)
    await gameWorld.repo.save_entity(target)
    
    event_type = "flip_fail" if kwargs.get("is_narrative_fail") else "flip_success"
    narrative = await generateCombatNarrative(event_type, kwargs)

    # 拔樁成功必上新聞
    if success:
        import asyncio
        asyncio.create_task(gameWorld.trigger_news_flash(
            attacker_name=entity.name,
            defender_name=target.name,
            event="樁腳倒戈背叛",
            damage_desc="地方基層勢力遭遇大洗牌"
        ))

    # 格式化輸出
    lines = [
        "📺 " + narrative.get("news_report", ""),
        "",
        "── PTT 鄉民反應 ──",
    ]
    for comment in narrative.get("ptt_comments", []):
        lines.append(f"  {comment}")
    lines.append("")
    if success:
        lines.append(f"[結算] 成功策反區域 {kwargs.get('boss_region')}，動員力 +{kwargs.get('mobilization_power')}")
    else:
        lines.append(f"[結算] 拔樁失敗 (成功率 {kwargs.get('success_rate', 0):.1%})")

    return "\n".join(lines)


async def _handleAction(entity: PoliticalEntity, args: list[str]) -> str:
    """自由行動（AI 結算）"""
    if not args:
        return "用法: /act <行動描述>"

    actionDesc = " ".join(args)

    # 檢查強行行動風險
    isDisaster, forceActionWarning = checkForceActionPenalty(entity)
    if isDisaster and forceActionWarning:
        return forceActionWarning

    # 呼叫 AI 結算引擎（注入當前現實 API 快照）
    realityApi: dict = {}
    try:
        from app.api_integrations.weather import fetchWeatherData, evaluateWeatherImpact
        from app.api_integrations.twse import fetchStockData, evaluateStockImpact
        weatherAlert = await fetchWeatherData()
        weatherImpact = evaluateWeatherImpact(weatherAlert)
        stockSnapshot = await fetchStockData()
        stockImpact = evaluateStockImpact(stockSnapshot)
        realityApi = {
            "weather": {
                "severity": weatherImpact.get("severity", "normal"),
                "narrative": weatherImpact.get("narrative", ""),
                "type": weatherImpact.get("type", ""),
            },
            "stock": {
                "indexValue": stockSnapshot.indexValue,
                "changePercent": stockSnapshot.changePercent,
                "severity": stockImpact.get("severity", "normal"),
                "narrative": stockImpact.get("narrative", ""),
            },
        }
    except Exception as e:
        logger.warning(f"[Act] 無法取得 API 快照，使用預設值: {e}")

    result = await settleAction(
        playerState=entity.model_dump(),
        realityApi=realityApi,
        playerAction=actionDesc,
    )

    # 套用狀態變動小於零確保數值邏輯正常
    changes = result.get("state_changes", {})
    entity.applyAttributeChange(
        fame=changes.get("fame", 0),
        favorability=changes.get("favorability", 0),
        aggro=changes.get("aggro", 0),
        politicalFunds=changes.get("political_funds", 0),
        staffAp=changes.get("staff_ap", 0),
    )
    
    # 保存進資料庫!!!
    await gameWorld.repo.save_entity(entity)

    # 格式化輸出
    lines = [
        "📺 " + result.get("news_report", ""),
        "",
        "── PTT 鄉民反應 ──",
    ]
    for comment in result.get("ptt_comments", []):
        lines.append(f"  {comment}")
    lines.append("")
    lines.append(f"[結算] 好感度 {changes.get('favorability', 0):+d}，"
                 f"仇恨值 {changes.get('aggro', 0):+d}，"
                 f"知名度 {changes.get('fame', 0):+d}")
                 
    # 判斷區域關鍵字並增加區域影響力
    regions = {
        "台北": "TPE", "新北": "NWT", "桃園": "TAO", 
        "台中": "TXG", "台南": "TNN", "高雄": "KHH"
    }
    for r_name, r_code in regions.items():
        if r_name in actionDesc:
            # 以好感度加知名度之和作為區域影響力，基礎保底為0
            influence_gain = max(0, changes.get("fame", 0) + changes.get("favorability", 0))
            if influence_gain > 0:
                entity.coreAttributes.regionalInfluence[r_code] += influence_gain
                lines.append(f"[地盤] {r_name} ({r_code}) 區影響力 +{influence_gain}")
            break # 單次行動只發配一個主要縣市
                 
    if not isDisaster and forceActionWarning:
        lines.append("")
        lines.append(forceActionWarning)

    return "\n".join(lines)


async def _handleInvest(entity: PoliticalEntity, args: list[str]) -> str:
    """投資股市指令"""
    if len(args) < 3:
        return "用法: /invest <buy|sell> <股票代號> <股數>\n代號: G2330(科技), G2881(金融), G1301(傳產), G2542(營建)"
    
    action, symbol, amount_str = args[0].lower(), args[1].upper(), args[2]
    try:
        amount = int(amount_str)
        if amount <= 0: return "❌ 股數必須大於 0"
    except ValueError:
        return "❌ 股數格式錯誤"

    if symbol not in market.stocks:
        return f"❌ 找不到股票代號 {symbol}"
    
    stock = market.stocks[symbol]
    
    if action == "buy":
        cost = stock.price * amount
        if entity.resources.politicalFunds < cost:
            return f"❌ 資金不足。目前合法獻金為 ${entity.resources.politicalFunds:,}，需要 ${cost:,}"
        entity.resources.politicalFunds -= cost
        entity.resources.stockPortfolio[symbol] = entity.resources.stockPortfolio.get(symbol, 0) + amount
        await gameWorld.repo.save_entity(entity)
        return f"📈 成功買入 {amount} 股 [{stock.name}] (代號 {symbol})。單價: ${stock.price}，花費: ${cost:,}，剩餘合法獻金: ${entity.resources.politicalFunds:,}"
    
    elif action == "sell":
        current_amount = entity.resources.stockPortfolio.get(symbol, 0)
        if current_amount < amount:
            return f"❌ 股數不足。目前僅持有 {current_amount} 股"
        revenue = stock.price * amount
        entity.resources.politicalFunds += revenue
        entity.resources.stockPortfolio[symbol] -= amount
        await gameWorld.repo.save_entity(entity)
        return f"📉 成功賣出 {amount} 股 [{stock.name}] (代號 {symbol})。單價: ${stock.price}，進帳: ${revenue:,}，剩餘合法獻金: ${entity.resources.politicalFunds:,}"
    
    else:
        return "❌ 只能輸入 buy 或 sell"


async def _handleLaunder(entity: PoliticalEntity, args: list[str]) -> str:
    """黑金洗錢指令"""
    if not args:
        return "用法: /launder <金額>\n(將黑金透過地下匯兌洗白，當前折損率、查扣風險會隨風聲變化)"
        
    try:
        amount = int(args[0])
        if amount <= 0: return "❌ 洗錢金額必須大於 0"
    except ValueError:
        return "❌ 洗錢金額格式錯誤"
        
    if entity.resources.unlaunderedFunds < amount:
        return f"❌ 非法獻金不足。目前只有 ${entity.resources.unlaunderedFunds:,}"
        
    # 如果抓得很緊，有可能直接被查扣 (風聲 penalty 大於某個值)
    risk = (1.0 - market.launder_rate) * 0.5
    if random.random() < risk:
        # 被抓到，沒收黑金並引爆核彈級公關危機
        entity.resources.unlaunderedFunds -= amount
        entity.coreAttributes.aggro += 1500
        entity.coreAttributes.favorability -= 2000
        await gameWorld.repo.save_entity(entity)
        return f"🚨🚨 醜聞爆發！您試圖透過地下黑市洗錢 ${amount:,} 時遭檢調查獲，全數充公，仇恨值暴增！"
        
    # 洗錢成功
    entity.resources.unlaunderedFunds -= amount
    laundered_amount = int(amount * market.launder_rate)
    entity.resources.politicalFunds += laundered_amount
    await gameWorld.repo.save_entity(entity)
    return f"💼 洗錢成功！透過白手套轉換，非法資金 ${amount:,} 已變為合法獻金 ${laundered_amount:,} (折損率 {(1-market.launder_rate)*100:.1f}%)"


def _formatHelp() -> str:
    """指令說明"""
    return """
╔══════════════════════════════════════╗
║       《鍵盤與黑金》指令說明         ║
╠══════════════════════════════════════╣
║ /status              查看自身狀態   ║
║ /look                前 20 名排行   ║
║ /look top            前 10 強排行   ║
║ /look <政黨>         篩選特定陣營   ║
║ /attack <對手>       發動網軍攻擊   ║
║ /flip <對手> <樁腳ID> 拔樁行動      ║
║ /invest <buy/sell> <代號> <股數>    ║
║ /launder <金額>      洗白非法獻金   ║
║ /act <行動描述>      自由行動結算   ║
║ /help                顯示本說明     ║
╚══════════════════════════════════════╝
""".strip()
