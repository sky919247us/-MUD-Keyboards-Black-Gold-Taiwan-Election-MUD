import pytest
from app.ai.settlement_engine import _mockSettle, settleAction
from app.models.entity import PoliticalEntity, BasicInfo

@pytest.fixture
def entity() -> PoliticalEntity:
    return PoliticalEntity(
        entityId="test_ai_001",
        basicInfo=BasicInfo(
            name="測試玩家",
            partyAffiliation="無黨籍",
            title="候選人",
            campAlignment="無黨籍"
        ),
        fame=5000,
        favorability=5000,
        resources={"money": 1000000, "staff": 50, "influence": 100},
    )

@pytest.mark.asyncio
async def test_mock_settle(entity):
    # 測試 _mockSettle() 回傳的結構是否符合 JSON Pydantic 預期
    # 注意 _mockSettle 不是 async，且參數為 playerState(dict), realityApi(dict), playerAction(str)
    result_dict = _mockSettle(entity.model_dump(), {}, "發動大型掃街造勢")
    
    # _mockSettle 應回傳一個包含 state_changes 的字典
    assert isinstance(result_dict, dict)
    assert 'state_changes' in result_dict
    changes = result_dict['state_changes']
    assert 'fame' in changes
    assert 'favorability' in changes
    assert 'aggro' in changes

@pytest.mark.asyncio
async def test_settle_action_with_mock_provider(entity, monkeypatch):
    # 透過 monkeypatch 強制將環境變數/設定的 AI_PROVIDER 改為 mock
    from app.config import settings
    monkeypatch.setattr(settings, "AI_PROVIDER", "mock")
    
    # settleAction 是 async 函式
    result_dict = await settleAction(entity.model_dump(), {}, "舉辦慈善晚會")
    
    # 執行過後應該要有事件廣播字串回傳 (或狀態字典)
    assert isinstance(result_dict, dict)
    assert "news_report" in result_dict
