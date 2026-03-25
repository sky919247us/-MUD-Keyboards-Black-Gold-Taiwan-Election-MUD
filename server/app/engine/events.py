"""
突發危機事件引擎
負責任機率觸發危機並抽出正確層級的事件
"""

import random
import logging
from app.data.crises import CRISIS_DB

logger = logging.getLogger(__name__)

def get_random_crisis() -> dict | None:
    """
    依照層級機率抽取出一個隨機的突發危機。
    S級：5%、A級：20%、B級：35%、C級：40%
    """
    if not CRISIS_DB:
        return None

    roll = random.random()
    if roll < 0.05:
        target_tier = "S"
    elif roll < 0.25:
        target_tier = "A"
    elif roll < 0.60:
        target_tier = "B"
    else:
        target_tier = "C"

    # 過濾出對應層級的事件
    tier_events = [e for e in CRISIS_DB if e["tier"] == target_tier]
    
    # 如果某個層級剛好空了，就退回抽所有
    if not tier_events:
        tier_events = CRISIS_DB

    return random.choice(tier_events)


def get_crisis_by_id(crisis_id: str) -> dict | None:
    for e in CRISIS_DB:
        if e["id"] == crisis_id:
            return e
    return None
