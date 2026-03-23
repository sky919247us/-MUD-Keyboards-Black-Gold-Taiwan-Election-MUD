"""
Tick 結算引擎測試
"""
from app.engine.tick import executeEntityTick
from app.models.entity import (
    BasicInfo, CoreAttributes, LocalBoss, MediaChannel,
    MediaAlignmentType, PoliticalEntity, Resources,
)


def test_apRecoveryPerTick():
    """每 Tick AP 自動恢復"""
    entity = PoliticalEntity(
        basicInfo=BasicInfo(name="AP測試"),
        resources=Resources(staffAp=50, politicalFunds=1_000_000),
    )
    events = executeEntityTick(entity)
    assert entity.resources.staffAp == 55  # +5
    assert any("AP 恢復" in e for e in events)


def test_apNoRecoveryWhenBankrupt():
    """獻金歸零時 AP 不恢復"""
    entity = PoliticalEntity(
        basicInfo=BasicInfo(name="破產AP測試"),
        resources=Resources(staffAp=50, politicalFunds=0),
    )
    executeEntityTick(entity)
    # 會被糧草斷絕懲罰歸零
    assert entity.resources.staffAp == 0


def test_passiveBossIncome():
    """樁腳被動募款收入"""
    entity = PoliticalEntity(
        basicInfo=BasicInfo(name="募款測試"),
        coreAttributes=CoreAttributes(fame=5000),
        resources=Resources(politicalFunds=1_000_000),
    )
    entity.arraysAssets.localBosses.append(
        LocalBoss(regionCode="TPE", mobilizationPower=500, loyalty=100)
    )
    executeEntityTick(entity)
    # 預期收入: 5000 × (100/100) = 5000
    assert entity.resources.politicalFunds > 1_000_000


def test_paidMediaConsumption():
    """Paid 媒體消耗獻金"""
    entity = PoliticalEntity(
        basicInfo=BasicInfo(name="媒體測試"),
        resources=Resources(politicalFunds=1_000_000),
    )
    entity.arraysAssets.mediaChannels.append(
        MediaChannel(alignmentType=MediaAlignmentType.PAID, subscribers=10000)
    )
    executeEntityTick(entity)
    assert entity.resources.politicalFunds < 1_000_000


def test_loyaltyDecay():
    """樁腳忠誠度自然衰減"""
    entity = PoliticalEntity(
        basicInfo=BasicInfo(name="衰減測試"),
    )
    entity.arraysAssets.localBosses.append(
        LocalBoss(regionCode="TPE", loyalty=50)
    )
    executeEntityTick(entity)
    assert entity.arraysAssets.localBosses[0].loyalty == 49  # -1
