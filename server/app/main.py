"""
《鍵盤與黑金：台灣選戰 MUD》FastAPI 主入口 (PWA Version)
"""
from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.config import settings
from app.engine.tick import executeTick, executeTickAsync
from app.game.commands import handleCommand
from app.game.menu_actions import handleMenuAction
from app.game.session import cooldownManager
from app.game.world import gameWorld
from app.game.economy import market
from app.models.character import generateCharacter
from app.models.party import PARTIES, getPartyByCode
from app.db.session import engine, Base
from app.core.security import generate_ws_token, verify_ws_token
from app.api import line_auth

# ── 日誌 ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)-5s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── 連線管理 ──────────────────────────────────────────────────
class ConnectionManager:
    """WebSocket 連線管理器 (依 entityId 掛載，支援同陣營多玩家)"""

    def __init__(self) -> None:
        # 一個 entityId 可以對應多個 WebSocket（陣營共享機制）
        self.activeConnections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, entityId: str) -> None:
        await websocket.accept()
        if entityId not in self.activeConnections:
            self.activeConnections[entityId] = []
        self.activeConnections[entityId].append(websocket)
        logger.info(f"WebSocket 連線：{entityId}（當前同陣營 {len(self.activeConnections[entityId])} 人）")

    def disconnect(self, websocket: WebSocket, entityId: str) -> None:
        conns = self.activeConnections.get(entityId, [])
        if websocket in conns:
            conns.remove(websocket)
        if not conns:
            self.activeConnections.pop(entityId, None)
        logger.info(f"WebSocket 斷線：{entityId}")

    async def sendPersonal(self, entityId: str, message: str) -> None:
        """發送訊息給該 entityId 下的所有連線"""
        conns = self.activeConnections.get(entityId, [])
        dead: list[WebSocket] = []
        for ws in conns:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        # 清理已斷線的連線
        for ws in dead:
            conns.remove(ws)

    async def broadcast(self, message: str) -> None:
        dead_pairs: list[tuple[str, WebSocket]] = []
        for eid, conns in self.activeConnections.items():
            for ws in conns:
                try:
                    await ws.send_text(message)
                except Exception:
                    dead_pairs.append((eid, ws))
        for eid, ws in dead_pairs:
            conns = self.activeConnections.get(eid, [])
            if ws in conns:
                conns.remove(ws)


manager = ConnectionManager()


# ── Tick 排程 ─────────────────────────────────────────────────
async def tickJob() -> None:
    """每個 Tick 執行的排程工作"""
    gameWorld.advanceTick()
    entities = await gameWorld.repo.get_all_entities()
    
    # 使用包含新聞的非同步 Tick
    events = await executeTickAsync(entities)

    if events:
        bulletin = f"\n{'═' * 50}\n📢 系統 Tick #{gameWorld.tickCount} 結算報告\n{'═' * 50}\n"
        bulletin += "\n".join(events)
        bulletin += f"\n{'═' * 50}\n"
        await manager.broadcast(bulletin)
        logger.info(f"Tick #{gameWorld.tickCount} 完成，{len(events)} 事件")


# ── Lifespan ──────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """啟動前初始化遊戲世界、排程器與資料庫"""
    # 建立資料庫表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    await gameWorld.initialize()

    # 注入廣播回呼函式，讓 world.trigger_news_flash 可以廣播給所有玩家
    gameWorld.set_broadcast_callback(manager.broadcast)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        tickJob,
        "interval",
        seconds=settings.TICK_INTERVAL_SECONDS,
        id="tick_engine",
    )
    scheduler.start()
    logger.info(f"Tick 排程啟動：每 {settings.TICK_INTERVAL_SECONDS} 秒結算")

    yield

    scheduler.shutdown()
    logger.info("伺服器關閉")


# ── FastAPI App ───────────────────────────────────────────────
app = FastAPI(
    title="《鍵盤與黑金：台灣選戰 MUD》",
    description="台灣現代選戰硬核文字 MUD 政治模擬遊戲",
    version="0.2.0",
    lifespan=lifespan,
)

# 掛載靜態檔案與模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(line_auth.router)

# ── 路由 (PWA 頁面) ──────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """PWA 主頁面對應角色建立與遊戲畫面"""
    return templates.TemplateResponse(
        request=request, name="index.html", context={}
    )


@app.get("/intro", response_class=HTMLResponse)
async def intro(request: Request):
    """遊戲介紹頁面（官方網站）"""
    return templates.TemplateResponse(
        request=request, name="intro.html", context={}
    )


@app.get("/offline.html", response_class=HTMLResponse)
async def offline(request: Request):
    """離線頁面"""
    return templates.TemplateResponse(
        request=request, name="offline.html", context={}
    )


# ── 路由 (API) ────────────────────────────────────────────────
@app.get("/api/v1/parties")
async def listParties():
    """取得可選陣營列表"""
    return [
        {
            "code": p.code,
            "name": p.name,
            "shortName": p.shortName,
            "realWorldRef": p.realWorldRef,
        }
        for p in PARTIES
    ]


@app.get("/api/v1/user/{userId}/character")
async def getCharacter(userId: str):
    """取得玩家角色資料"""
    player = await gameWorld.repo.get_user_by_id(userId)
    if not player:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Character not found")
    return player.model_dump()


class CharacterCreateReq(BaseModel):
    party_code: str


@app.post("/api/v1/user/{userId}/create_character")
async def createCharacter(userId: str, req: CharacterCreateReq):
    """建立新角色"""
    player = await gameWorld.repo.get_user_by_id(userId)
    if player:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Character already exists")
    
    try:
        newPlayer = await generateCharacter(userId, req.party_code, gameWorld.repo)
        # 儲存玩家 session 至資料庫
        await gameWorld.repo.save_user(newPlayer)
        
        return {
            "userId": newPlayer.userId,
            "entityId": newPlayer.entityId,
            "boss_name": newPlayer.identity.get("boss_name"),
            "role_title": newPlayer.identity.get("role_title"),
            "party_name": getPartyByCode(newPlayer.identity.get("party_code")).name,
            "gender": newPlayer.identity.get("gender"),
        }
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/entities/{entityId}/history")
async def getEntityHistory(entityId: str):
    """取得實體歷史數據趨勢"""
    history = gameWorld.history.get_history(entityId)
    if not history:
        return {"labels": [], "fame": [], "favorability": [], "aggro": []}
    
    return {
        "labels": [h.tick for h in history],
        "fame": [h.fame for h in history],
        "favorability": [h.favorability for h in history],
        "aggro": [h.aggro for h in history],
        "timestamps": [h.timestamp.isoformat() for h in history]
    }


@app.get("/api/v1/leaderboard")
async def getLeaderboard():
    """全服知名度排行榜"""
    entities = await gameWorld.repo.get_all_entities()
    # 依知名度排序，取前 10
    top_entities = sorted(entities, key=lambda e: e.fame, reverse=True)[:10]
    return [
        {
            "id": e.id,
            "name": e.name,
            "party": e.basicInfo.partyAffiliation,
            "title": e.basicInfo.title,
            "fame": e.fame,
            "camp": e.basicInfo.campAlignment
        } for e in top_entities
    ]


@app.get("/api/v1/world/status")
async def getWorldStatus():
    """22 縣市勢力板圖統計"""
    from collections import defaultdict
    entities = await gameWorld.repo.get_all_entities()
    
    # counties[縣市名稱][政黨代碼] = 總知名度
    counties = defaultdict(lambda: defaultdict(int))
    
    for e in entities:
        # 如果是地方實體（縣市首長/議員），依 region 分類
        region = e.basicInfo.region or "全國"
        if region == "全國":
            continue
        
        party = e.basicInfo.partyAffiliation
        counties[region][party] += e.fame

    # 格式化為前端友善格式：每個縣市最強勢的黨
    result = {}
    for region, parties in counties.items():
        if not parties:
            continue
        # 找該縣市最強黨
        top_party = max(parties.items(), key=lambda x: x[1])
        result[region] = {
            "leading_party": top_party[0],
            "total_fame": top_party[1],
            "all_parties": dict(parties)
        }
    
    return result


@app.get("/api/v1/economy/market")
async def get_market_status():
    """取得黑市與股市當前行情"""
    return {
        "launder_rate": market.launder_rate,
        "stocks": [s.model_dump() for s in market.stocks.values()]
    }


@app.get("/api/v1/entities")
async def listEntities():
    """列出所有政治實體（用於 Debug/Admin）"""
    entities = await gameWorld.repo.get_all_entities()
    return [e.model_dump() for e in entities]


@app.get("/api/v1/user/{userId}/token")
async def get_ws_token(userId: str):
    """換發 WebSocket 短期 Token"""
    player = await gameWorld.repo.get_user_by_id(userId)
    if not player:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Player not found")
    
    token = generate_ws_token(userId, player.entityId)
    return {"token": token, "entityId": player.entityId}


# ── 路由 (WebSocket) ──────────────────────────────────────────
@app.websocket("/ws/{entityId}")
async def websocketEndpoint(websocket: WebSocket, entityId: str):
    """WebSocket MUD 入口"""
    # NOTE: 不在此處 accept，由 manager.connect() 統一 accept
    await websocket.accept()

    # 1. 接收第一幀 Token 驗證
    try:
        auth_msg = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
        auth_data = json.loads(auth_msg)
        token = auth_data.get("token")
        
        user_id = verify_ws_token(token, entityId)
        if not user_id:
            await websocket.send_text("❌ 身分驗證失敗：Token 無效或已過期。")
            await websocket.close(code=1008)
            return
            
    except (asyncio.TimeoutError, json.JSONDecodeError):
        await websocket.send_text("❌ 連線超時或格式錯誤。")
        await websocket.close(code=1008)
        return

    # 確認實體是否存在
    entity = await gameWorld.repo.get_entity_by_id(entityId)
    if entity is None:
        await websocket.send_text("❌ 無效的連線憑證。")
        await websocket.close(code=1008)
        return

    # 已在上方 accept，直接加入連線池（跳過 manager 內部 accept）
    if entityId not in manager.activeConnections:
        manager.activeConnections[entityId] = []
    manager.activeConnections[entityId].append(websocket)
    logger.info(f"WebSocket 連線：{entityId}（當前同陣營 {len(manager.activeConnections[entityId])} 人）")

    welcome = (
        f"\n{'═' * 50}\n"
        f"  系統登入完成\n"
        f"  身分認證：{user_id}\n"
        f"  陣營：{entity.basicInfo.partyAffiliation}\n"
        f"  鎖定對象：{entity.name} 陣營\n"
        f"  當前 Tick #{gameWorld.tickCount} ｜ 賽季：{gameWorld.currentPhase}\n"
        f"{'═' * 50}\n"
    )
    await manager.sendPersonal(entityId, welcome)

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                # If not JSON, treat as plain text command
                data = {"text": raw_data}
            
            # 解析指令
            text = data.get("text", "").strip()
            if not text:
                continue

            # 提取指令名稱（取第一個 token）
            cmd_name = text.split()[0].lower() if text.startswith("/") else ""

            # 行動冷卻檢查
            if cmd_name:
                is_ready, remaining = cooldownManager.check_cooldown(entityId, cmd_name)
                if not is_ready:
                    await manager.sendPersonal(
                        entityId,
                        f"⏳ 指令冷卻中，請在 {remaining} 秒後再試。"
                    )
                    continue
            
            # 支援 PWA 介面的選單快捷按鈕邏輯
            if text.startswith("/act "):
                response = await handleMenuAction(entity, text)
            else:
                response = await handleCommand(entityId, text)

            # 記錄指令冷卻
            if cmd_name:
                cooldownManager.record_usage(entityId, cmd_name)
            
            await manager.sendPersonal(entityId, response)
    except WebSocketDisconnect:
        manager.disconnect(websocket, entityId)
