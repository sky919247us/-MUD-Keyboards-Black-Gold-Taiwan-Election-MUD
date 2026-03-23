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
) -> tuple[bool, str]:
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
        msg = (
            f"【拔樁成功】{attacker.name} 成功策反 {defender.name} 的樁腳 "
            f"（區域 {targetBoss.regionCode}，動員力 {targetBoss.mobilizationPower}）"
        )
        logger.info(msg)
        return True, msg
    else:
        msg = f"【拔樁失敗】{attacker.name} 嘗試拔樁失敗（成功率 {successRate:.1%}，擲骰 {roll:.2f}）"
        return False, msg


def launchCyberAttack(
    attacker: PoliticalEntity,
    defender: PoliticalEntity,
    platform: str = "PTT",
    apCost: int = 15,
    fundsCost: int = 200_000,
) -> tuple[bool, str]:
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
    bustedMsg = ""
    if bustedNodes:
        bustedMsg = f"；⚠ {len(bustedNodes)} 個帳號隱蔽度歸零，面臨「被抓包」風險！"
        # 反噬：攻擊方好感度下降，防守方獲得悲情牌加成
        attacker.applyAttributeChange(favorability=-300)
        defender.applyAttributeChange(favorability=200, fame=100)

    msg = (
        f"【網軍攻擊】{attacker.name} 在 {platform} 發動側翼攻擊 → "
        f"{defender.name} 好感度 -{favDamage}，仇恨值 +{aggroDamage}"
        f"{bustedMsg}"
    )
    return True, msg
