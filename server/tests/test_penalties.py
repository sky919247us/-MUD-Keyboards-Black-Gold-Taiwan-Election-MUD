"""
邊界懲罰機制測試
"""
from app.engine.penalties import checkAndApplyPenalties, checkForceActionPenalty
from app.models.entity import BasicInfo, CoreAttributes, PoliticalEntity, Resources


def test_fameZeroPenalty():
    """知名度歸零觸發『政治透明人』"""
    entity = PoliticalEntity(
        basicInfo=BasicInfo(name="透明人"),
        coreAttributes=CoreAttributes(fame=0),
    )
    events = checkAndApplyPenalties(entity)
    assert any("政治透明人" in e for e in events)


def test_favorabilityZeroPenalty():
    """好感度歸零觸發『信賴危機』"""
    entity = PoliticalEntity(
        basicInfo=BasicInfo(name="危機候選人"),
        coreAttributes=CoreAttributes(favorability=0),
    )
    events = checkAndApplyPenalties(entity)
    assert any("信賴危機" in e for e in events)


def test_fundsZeroPenalty():
    """獻金歸零觸發『糧草斷絕』：AP歸零"""
    entity = PoliticalEntity(
        basicInfo=BasicInfo(name="破產候選人"),
        resources=Resources(politicalFunds=0, staffAp=50),
    )
    events = checkAndApplyPenalties(entity)
    assert any("糧草斷絕" in e for e in events)
    assert entity.resources.staffAp == 0


def test_legalRiskExplosion():
    """法務風險值滿載觸發沒收獻金"""
    entity = PoliticalEntity(
        basicInfo=BasicInfo(name="法務爆炸"),
        resources=Resources(politicalFunds=10_000_000),
    )
    entity.hiddenStats.legalRiskIndex = 100
    events = checkAndApplyPenalties(entity)
    assert any("法規懲罰引爆" in e for e in events)
    assert entity.resources.politicalFunds == 5_000_000  # 沒收 50%


def test_forceActionWhenApZero():
    """AP為零時強行行動有 75% 災難機率"""
    entity = PoliticalEntity(
        basicInfo=BasicInfo(name="過勞候選人"),
        resources=Resources(staffAp=0),
    )
    # 跑多次確認機制運作
    disasterCount = 0
    for _ in range(100):
        # 重置好感度以避免 clamp
        entity.coreAttributes.favorability = 5000
        entity.coreAttributes.fame = 5000
        isDisaster, _ = checkForceActionPenalty(entity)
        if isDisaster:
            disasterCount += 1
    # 統計上應接近 75%（容許 55%-95% 的範圍）
    assert 55 <= disasterCount <= 95
