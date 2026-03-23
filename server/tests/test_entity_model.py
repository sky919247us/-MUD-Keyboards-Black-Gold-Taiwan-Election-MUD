"""
政治實體模型測試
"""
import pytest
from app.models.entity import (
    BasicInfo, CoreAttributes, CyberArmyAccount, EntityLevel,
    LocalBoss, MediaChannel, MediaAlignmentType, Platform, PoliticalEntity,
)


def test_createEntityWithDefaults():
    """測試以預設值建立實體"""
    entity = PoliticalEntity(
        basicInfo=BasicInfo(name="測試候選人"),
    )
    assert entity.name == "測試候選人"
    assert entity.fame == 1000
    assert entity.favorability == 500
    assert entity.aggro == 0
    assert entity.resources.politicalFunds == 5_000_000
    assert entity.resources.staffAp == 100


def test_fameBoundary():
    """知名度不可超過 10000"""
    entity = PoliticalEntity(
        basicInfo=BasicInfo(name="高知名度"),
        coreAttributes=CoreAttributes(fame=9500),
    )
    actual = entity.applyAttributeChange(fame=1000)
    assert entity.fame == 10000
    assert actual["fame"] == 500  # 實際只加了 500


def test_favorabilityCanBeNegative():
    """好感度允許負值"""
    entity = PoliticalEntity(
        basicInfo=BasicInfo(name="低好感"),
        coreAttributes=CoreAttributes(favorability=-5000),
    )
    assert entity.favorability == -5000
    entity.applyAttributeChange(favorability=-6000)
    assert entity.favorability == -10000  # 被 clamp


def test_aggroBoundary():
    """仇恨值不可為負"""
    entity = PoliticalEntity(
        basicInfo=BasicInfo(name="仇恨測試"),
        coreAttributes=CoreAttributes(aggro=100),
    )
    entity.applyAttributeChange(aggro=-200)
    assert entity.aggro == 0


def test_fundsClamp():
    """政治獻金不可為負"""
    entity = PoliticalEntity(
        basicInfo=BasicInfo(name="窮候選人"),
    )
    entity.applyAttributeChange(politicalFunds=-100_000_000)
    assert entity.resources.politicalFunds == 0


def test_totalMediaSubscribers():
    """自媒體總訂閱數計算"""
    entity = PoliticalEntity(
        basicInfo=BasicInfo(name="媒體大亨"),
    )
    entity.arraysAssets.mediaChannels = [
        MediaChannel(subscribers=50000),
        MediaChannel(subscribers=30000),
    ]
    assert entity.totalMediaSubscribers == 80000


def test_pydanticValidation():
    """Pydantic 驗證：fame 不可為負"""
    with pytest.raises(Exception):
        CoreAttributes(fame=-1)
