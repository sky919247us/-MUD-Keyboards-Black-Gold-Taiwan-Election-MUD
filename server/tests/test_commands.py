import pytest
from app.game.commands import handleCommand
from app.models.entity import PoliticalEntity, BasicInfo

from unittest.mock import AsyncMock, patch

@pytest.fixture
def entity() -> PoliticalEntity:
    return PoliticalEntity(
        entityId="test_001",
        basicInfo=BasicInfo(
            name="測試玩家",
            partyAffiliation="無黨籍",
            title="候選人",
            campAlignment="無黨籍"
        ),
    )

@pytest.fixture(autouse=True)
def mock_game_world(entity):
    with patch("app.game.commands.gameWorld.repo.get_entity_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = entity
        yield mock_get

@pytest.mark.asyncio
async def test_process_action_unknown_command(entity):
    # 給予未知的指令，應該穩定攔截並回覆錯誤，而非崩潰
    result = await handleCommand("test_001", "/unknown_xyz")
    # 根據現有的程式邏輯，handleCommand 可能會回傳廣播包或是文字
    # 這裡我們確認他有回傳東西且不是拋出例外
    assert result is not None
    
    # 通常字串或字典
    if isinstance(result, str):
        assert "無此指令" in result or "未知" in result or "不支援" in result or "請輸入指令" in result

@pytest.mark.asyncio
async def test_process_action_empty_command(entity):
    # 測試空字串防護
    result = await handleCommand("test_001", "  ")
    # 空字串通常回覆請輸入指令
    assert result is not None

@pytest.mark.asyncio
async def test_process_action_malformed_attack(entity):
    # 參數不正確的攻擊指令
    result = await handleCommand("test_001", "/attack")
    assert result is not None
    if isinstance(result, str):
        assert "用法" in result or "目標" in result or "格式" in result

def test_action_cooldown_manager():
    from app.game.session import ActionCooldownManager
    import time
    
    cdm = ActionCooldownManager()
    
    # 第一次執行 /act，應通過
    ready, remaining = cdm.check_cooldown("entity_cd_test", "/act")
    assert ready is True
    
    # 紀錄使用
    cdm.record_usage("entity_cd_test", "/act")
    
    # 立即再次執行，應被擋下
    ready2, remaining2 = cdm.check_cooldown("entity_cd_test", "/act")
    assert ready2 is False
    assert remaining2 > 0
    
    # 測其他指令的預設冷卻 (1.0秒)
    ready3, _ = cdm.check_cooldown("entity_cd_test", "/status")
    assert ready3 is True
    cdm.record_usage("entity_cd_test", "/status")
    
    ready4, _ = cdm.check_cooldown("entity_cd_test", "/status")
    assert ready4 is False
