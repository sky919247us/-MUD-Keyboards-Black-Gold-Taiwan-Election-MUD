import pytest
from app.main import ConnectionManager

class MockWebSocket:
    def __init__(self):
        self.sent_messages = []
        self.accepted = False
        
    async def accept(self):
        self.accepted = True
        
    async def send_text(self, data: str):
        self.sent_messages.append(data)
        
    async def send_json(self, data: dict):
        # main.py 的 ConnectionManager 目前是透過 send_text
        pass

@pytest.fixture
def manager():
    return ConnectionManager()

@pytest.mark.asyncio
async def test_ws_manager_connect_and_disconnect(manager):
    ws1 = MockWebSocket()
    ws2 = MockWebSocket()
    
    # 測試綁定到同一個 entityId
    await manager.connect(ws1, "entity_001")
    await manager.connect(ws2, "entity_001")
    
    assert len(manager.activeConnections["entity_001"]) == 2
    assert ws1.accepted is True
    assert ws2.accepted is True

    # 模擬斷線一個
    manager.disconnect(ws1, "entity_001")
    assert len(manager.activeConnections["entity_001"]) == 1
    
    # 模擬斷線第二個 (List 應清空或被刪除)
    manager.disconnect(ws2, "entity_001")
    # 如果設計上會移除 key 則用 dict get 檢查
    assert not manager.activeConnections.get("entity_001")

@pytest.mark.asyncio
async def test_ws_manager_send_personal_broadcast(manager):
    ws1 = MockWebSocket()
    ws2 = MockWebSocket()
    
    await manager.connect(ws1, "test_target")
    await manager.connect(ws2, "test_target")
    
    # 對此實體廣播個人訊息
    await manager.sendPersonal("test_target", "【私人通知】您有一筆政治獻金入帳。")
    
    # 兩個端點都應收到
    assert len(ws1.sent_messages) == 1
    assert len(ws2.sent_messages) == 1
    assert "入帳" in ws1.sent_messages[0]
    assert "入帳" in ws2.sent_messages[0]

@pytest.mark.asyncio
async def test_ws_manager_broadcast(manager):
    ws1 = MockWebSocket()
    ws2 = MockWebSocket()
    
    await manager.connect(ws1, "entity_a")
    await manager.connect(ws2, "entity_b")
    
    # 全服廣播
    await manager.broadcast("【系統公告】伺服器即將維護")
    
    assert len(ws1.sent_messages) == 1
    assert len(ws2.sent_messages) == 1
    assert "維護" in ws1.sent_messages[0]
