"""
政治危機事件引擎測試
"""
from app.engine.crisis_engine import checkAndApplyCrises
from app.models.entity import BasicInfo, CampAlignment, LocalBoss, PoliticalEntity, Resources


def test_crisis_stock_crash_ruling_party():
    """測試股災對執政黨的影響"""
    entity = PoliticalEntity(
        basicInfo=BasicInfo(name="執政黨市長", campAlignment=CampAlignment.PAN_GREEN),
        resources=Resources(politicalFunds=1_000_000),
    )
    
    # 模擬台股大跌 4% (-0.04)
    market_delta = -0.04
    weather_impact = {"severity": "normal", "type": ""}
    
    events = checkAndApplyCrises([entity], weather_impact, market_delta)
    
    # 確認事件觸發
    assert any("股災經濟恐慌" in e for e in events)
    # 預設好感度 = 500。扣除 (4% * 10000 = 400)，剩 100
    assert entity.coreAttributes.favorability == 100
    # 確認扣獻金 (5%，1,000,000 * 0.05 = 50,000)
    assert entity.resources.politicalFunds == 950_000


def test_crisis_stock_crash_opposition_party():
    """測試股災對在野黨的影響（不扣好感度，增加網軍攻擊力提示）"""
    entity = PoliticalEntity(
        basicInfo=BasicInfo(name="在野黨議員", campAlignment=CampAlignment.PAN_BLUE),
        resources=Resources(politicalFunds=1_000_000),
    )
    
    market_delta = -0.04
    weather_impact = {"severity": "normal", "type": ""}
    
    events = checkAndApplyCrises([entity], weather_impact, market_delta)
    
    assert any("在野黨出擊" in e for e in events)
    # 預設好感度 500 不變
    assert entity.coreAttributes.favorability == 500
    assert entity.resources.politicalFunds > 1_000_000


def test_crisis_typhoon_gamble():
    """測試颱風假豪賭（需要 RNG，利用 mock 或直接檢查有機率發生的情況）"""
    import random
    random.seed(42)  # 固定 seed 確保測試穩定

    entity = PoliticalEntity(
        basicInfo=BasicInfo(name="豪賭市長", campAlignment=CampAlignment.INDEPENDENT),
    )
    
    market_delta = 0.0
    weather_impact = {"severity": "warning", "type": "typhoon"}
    
    # 因為有 50% 機率，跑幾次確保觸發
    triggered = False
    for _ in range(10):
        entity.coreAttributes.favorability = 0
        events = checkAndApplyCrises([entity], weather_impact, market_delta)
        if any("颱風假豪賭" in e for e in events):
            triggered = True
            assert entity.coreAttributes.favorability < 0
            break
            
    assert triggered, "颱風假豪賭事件未能在 10 次內觸發"
