"""
PvP 攻防邏輯
對應選舉結算公式與 PvP 攻防藍圖.md 第二章。
"""
from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.entity import PoliticalEntity

logger = logging.getLogger(__name__)


def attemptBossFlip(
    attacker: PoliticalEntity,
    defender: PoliticalEntity,
    targetBossId: str,
    apCost: int = 20,
    fundsCost: int = 500_000,
) -> tuple[bool, str | dict]:
    """
    拔樁行動（Local Boss Flipping）
    判定公式：成功率 = (投入獻金 / 100萬) × (100 - 樁腳忠誠度) / 100
    """
    # 找到目標樁腳
    targetBoss = None
    for boss in defender.arraysAssets.localBosses:
        if boss.bossId == targetBossId:
            targetBoss = boss
            break

    if targetBoss is None:
        return False, f"目標樁腳 {targetBossId} 不存在"

    # 消耗 AP 與獻金
    if attacker.resources.staffAp < apCost:
        return False, "幕僚行動力不足"
    if attacker.resources.politicalFunds < fundsCost:
        return False, "政治獻金不足"

    attacker.applyAttributeChange(staffAp=-apCost, politicalFunds=-fundsCost)

    # 忠誠度低於 30 才有機會拔樁
    if targetBoss.loyalty >= 30:
        return False, f"樁腳 {targetBoss.bossId} 忠誠度 {targetBoss.loyalty} ≥ 30，拔樁失敗"

    # 計算成功率
    successRate = (fundsCost / 1_000_000) * (100 - targetBoss.loyalty) / 100
    successRate = min(successRate, 0.95)  # 上限 95%
    roll = random.random()

    if roll < successRate:
        # 拔樁成功：從防守方移除，加入攻擊方
        defender.arraysAssets.localBosses.remove(targetBoss)
        # 以低忠誠度加入攻擊方
        targetBoss.loyalty = 30
        attacker.arraysAssets.localBosses.append(targetBoss)
        return True, {
            "attacker": attacker.name,
            "defender": defender.name,
            "boss_region": targetBoss.regionCode,
            "mobilization_power": targetBoss.mobilizationPower,
        }
    else:
        return False, {
            "attacker": attacker.name,
            "defender": defender.name,
            "boss_region": targetBoss.regionCode,
            "success_rate": successRate,
            "is_narrative_fail": True, # 標記這是敘事上的失敗，而非系統錯誤
        }


def launchCyberAttack(
    attacker: PoliticalEntity,
    defender: PoliticalEntity,
    platform: str = "PTT",
    apCost: int = 15,
    fundsCost: int = 200_000,
) -> tuple[bool, str | dict]:
    """
    網軍側翼抹黑攻擊
    攻擊者的 output_power 對決防守者的自媒體防禦裝甲。
    """
    if attacker.resources.staffAp < apCost:
        return False, "❌ 幕僚行動力不足"
    if attacker.resources.politicalFunds < fundsCost:
        return False, f"❌ 政治獻金不足（需要 ${fundsCost:,}）"

    attacker.applyAttributeChange(staffAp=-apCost, politicalFunds=-fundsCost)

    # 計算該平台的總攻擊力
    attackNodes = [
        node for node in attacker.arraysAssets.cyberArmyAccounts
        if node.platform == platform and node.stealthRating > 0
    ]

    if not attackNodes:
        # 退回資金與 AP 嗎？不用，發動失敗一樣扣
        return False, f"❌ 無可用的 {platform} 網軍帳號（或全部隱蔽度歸零），白白浪費了預算！"

    totalOutput = sum(node.outputPower for node in attackNodes)

    # 防禦裝甲 = 自媒體總訂閱數 / 1000
    defenseArmor = defender.totalMediaSubscribers / 1000
    
    # 攻擊傷害
    rawDamage = max(0, totalOutput - defenseArmor)
    favDamage = int(rawDamage * 0.5)
    aggroDamage = int(rawDamage * 0.3)
    
    # 傷害判定訊息
    shieldMsg = ""
    if defenseArmor >= totalOutput:
        shieldMsg = "🛡️ 對方的自媒體護盾完全瓦解了這波攻勢！"
    elif defenseArmor > 0:
        shieldMsg = f"🛡️ 對方利用自媒體頻道抵擋了部分傷害（-{int(defenseArmor)}）！"

    defender.applyAttributeChange(favorability=-favDamage, aggro=aggroDamage)

    # 攻擊消耗隱蔽度
    for node in attackNodes:
        node.stealthRating = max(0, node.stealthRating - 10)

    # 檢查是否有帳號隱蔽度歸零（翻車風險）
    bustedNodes = [n for n in attackNodes if n.stealthRating == 0]
    is_busted = len(bustedNodes) > 0
    if is_busted:
        # 反噬：攻擊方好感度下降，防守方獲得悲情牌加成
        attacker.applyAttributeChange(favorability=-300)
        defender.applyAttributeChange(favorability=200, fame=100)

    kwargs = {
        "attacker": attacker.name,
        "defender": defender.name,
        "favDamage": favDamage,
        "aggroDamage": aggroDamage,
        "busted": is_busted,
        "busted_count": len(bustedNodes),
        "shield_absorbed": defenseArmor > 0,
    }
    
    # 全部當作 True，但在外層用 busted 判定是 success 還是 fail
    return True, kwargs
