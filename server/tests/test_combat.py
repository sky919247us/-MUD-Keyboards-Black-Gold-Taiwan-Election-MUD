import pytest
from app.engine.combat import launchCyberAttack, attemptBossFlip
from app.models.entity import PoliticalEntity, BasicInfo, ArraysAssets, CyberArmyAccount, LocalBoss, CoreAttributes, Resources

@pytest.fixture
def attacker() -> PoliticalEntity:
    ent = PoliticalEntity(
        entityId="attacker_001",
        basicInfo=BasicInfo(
            name="攻擊方",
            partyAffiliation="KMT",
            title="立委",
            campAlignment="泛藍",
            region="台北市",
            bossId=None
        ),
        coreAttributes=CoreAttributes(fame=5000, favorability=5000, aggro=0),
        resources=Resources(politicalFunds=1000000, staffAp=50, unlaunderedFunds=0, stockPortfolio={}),
    )
    ent.arraysAssets = ArraysAssets(
        cyberArmyAccounts=[
            CyberArmyAccount(platform="PTT", outputPower=2000, stealthRating=50)
        ],
        localBosses=[]
    )
    return ent

@pytest.fixture
def defender() -> PoliticalEntity:
    ent = PoliticalEntity(
        entityId="defender_001",
        basicInfo=BasicInfo(
            name="防守方",
            partyAffiliation="DPP",
            title="立委",
            campAlignment="泛綠",
            region="台北市",
            bossId=None
        ),
        coreAttributes=CoreAttributes(fame=8000, favorability=6000, aggro=0),
        resources=Resources(politicalFunds=2000000, staffAp=100, unlaunderedFunds=0, stockPortfolio={}),
    )
    # 為防守方建立測試用樁腳與提供防禦裝甲 (subscribers=500000 => armor=500)
    from app.models.entity import MediaChannel
    ent.arraysAssets = ArraysAssets(
        cyberArmyAccounts=[],
        localBosses=[
            LocalBoss(bossId="boss_tpe_01", regionCode="TPE", mobilizationPower=3000, loyalty=20)
        ],
        mediaChannels=[
            MediaChannel(subscribers=500000)
        ]
    )
    return ent

def test_launch_cyber_attack_success(attacker, defender):
    orig_favor = defender.favorability
    
    # 攻擊方 Output2000, 防守方防護 500, 實際傷害 1500, 好感度扣一半 = 750
    result, msg = launchCyberAttack(attacker, defender, platform="PTT")

    assert result is True
    assert defender.favorability == orig_favor - 750
    assert attacker.arraysAssets.cyberArmyAccounts[0].stealthRating == 40  # 攻擊消耗 10

def test_attempt_boss_flip_success(attacker, defender):
    # 備妥足夠資金
    attacker.resources.politicalFunds = 5000000
    
    orig_boss_count = len(defender.arraysAssets.localBosses)
    
    # Boss flip 是機率計算，為了穩定測試，可以把 Random 蓋掉，這裡先單純執行它確保不會噴錯
    # 或者我們只測試傳入正確 ID 不得報錯
    result, msg = attemptBossFlip(attacker, defender, targetBossId="boss_tpe_01")
    
    # 因為是機率事件，至少它必須回傳 Tuple[bool, str] 且不能是 ID Not Found 錯誤
    assert isinstance(result, bool)
    assert isinstance(msg, str)
    assert "不存在" not in msg

def test_attempt_boss_flip_fail_funds(attacker, defender):
    # 資金為 0 必定觸發資金不足
    attacker.resources.politicalFunds = 0
    result, msg = attemptBossFlip(attacker, defender, targetBossId="boss_tpe_01")
    
    assert result is False
    assert "政治獻金不足" in msg
