"""
選舉日計票結算邏輯
對應選舉結算公式與 PvP 攻防藍圖.md 第一章。
"""
from __future__ import annotations

import logging
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.entity import PoliticalEntity

logger = logging.getLogger(__name__)


def calculateVotes(
    entity: PoliticalEntity,
    regionPopulation: int,
    turnoutRate: float,
    ironVoteIndex: float,
    swingVoteIndex: float,
) -> int:
    """
    計算單一行政區的得票數。

    公式：V = P × T × A × W
    - P = 該區域歷年選民數
    - T = 投票率（受天氣 API 影響）
    - A = 陣營傾向（鐵票指數 × 好感度正態分布計算）
    - W = 最終修正權重（知名度溢出 + 仇恨值反噬）
    """
    attrs = entity.coreAttributes

    # 陣營傾向 A：以好感度為中心的正態分布，再乘以鐵票指數
    # NOTE: 好感度 0–10000 映射為 0.0–1.0 的基礎傾向
    baseFavorability = (attrs.favorability + 10000) / 20000  # 正規化到 0~1
    alignmentFactor = baseFavorability * ironVoteIndex + (1 - ironVoteIndex) * swingVoteIndex

    # 最終修正權重 W
    weightMultiplier = 1.0

    # 知名度溢出加成：fame > 8000 → 西瓜效應 ×1.1
    if attrs.fame > 8000:
        weightMultiplier *= 1.1

    # 仇恨值反噬：aggro > 8000 → 中間選民投對手機率提升 30%
    if attrs.aggro > 8000:
        weightMultiplier *= 0.7

    # 最終得票
    votes = regionPopulation * turnoutRate * alignmentFactor * weightMultiplier
    return max(0, int(votes))


def settleElection(
    candidates: list[PoliticalEntity],
    regionPopulation: int = 100_000,
    turnoutRate: float = 0.65,
    ironVoteIndices: dict[str, float] | None = None,
) -> list[dict]:
    """
    結算選舉結果。
    回傳依得票數排序的候選人結果列表。
    """
    if ironVoteIndices is None:
        ironVoteIndices = {}

    results = []
    for candidate in candidates:
        partyCode = candidate.basicInfo.partyAffiliation
        ironIndex = ironVoteIndices.get(partyCode, 0.5)
        swingIndex = 1.0 - ironIndex

        votes = calculateVotes(
            entity=candidate,
            regionPopulation=regionPopulation,
            turnoutRate=turnoutRate,
            ironVoteIndex=ironIndex,
            swingVoteIndex=swingIndex,
        )

        results.append({
            "entityId": candidate.entityId,
            "name": candidate.name,
            "party": partyCode,
            "votes": votes,
        })

    # 依得票數排序
    results.sort(key=lambda r: r["votes"], reverse=True)

    # 標記當選者
    if results:
        results[0]["elected"] = True
        for r in results[1:]:
            r["elected"] = False

    return results
