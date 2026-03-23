"""
AI 結算引擎
接收 Player_State + Reality_API + Player_Action，輸出固定 JSON。
整合 OpenAI 與 Gemini API，並支援 Structure Outputs 保證數值格式。
"""
from __future__ import annotations

import asyncio
import json
import logging
import random
from typing import Any

from pydantic import BaseModel, Field
from app.config import settings

logger = logging.getLogger(__name__)

# 全域 AI Client 快取（避免每次呼叫重建連線）
_gemini_client = None
_openai_client = None

# ── 結算結果 Schema ──────────────────────────────────────────────
class StateChanges(BaseModel):
    favorability: int = Field(description="-1000 到 1000 之間的好感度變動")
    aggro: int = Field(description="-1000 到 1000 之間的仇恨值變動")
    fame: int = Field(description="0 到 1000 之間的知名度增減")
    political_funds: int = Field(description="-1000000 到 1000000 之間的政治獻金變動")
    staff_ap: int = Field(description="-100 到 0 之間的幕僚體力消耗 (通常為負整數)")
    array_events: str = Field(default="", description="附帶的陣列事件描述，無則留空")

class SettlementResult(BaseModel):
    news_report: str = Field(description="100-150字台灣新聞台快訊旁白，語氣煽動")
    ptt_comments: list[str] = Field(description="包含推文、噓文、箭頭的3-4則PTT推文模擬，需符合鄉民文化")
    state_changes: StateChanges


# ── System Prompt（固定模板） ──────────────────────────────────
SYSTEM_PROMPT = """你現在是《台灣現代選戰 MUD》的核心 AI 結算引擎。
你的職責是接收玩家現有狀態、發生的現實API事件與玩家的行動指令，結算出擬真的結果。

風格要求：
1. 文字風格必須還原台灣新聞媒體的聳動語氣與 PTT 酸民文化
2. 善用政治網路術語：1450、小草、側翼、芒果乾、大撒幣、送暖、炎上等
3. 嚴格根據玩家狀態與行為合理推算數值變動：危險舉動會大扣好感、大增仇恨；正面舉動會增好感、扣資金與體力。
4. 結算結果必須完全符合要求的 JSON Schema。"""


async def settleAction(
    playerState: dict[str, Any],
    realityApi: dict[str, Any],
    playerAction: str,
) -> dict[str, Any]:
    """
    呼叫 AI 結算引擎處理玩家行動。
    依 settings.AI_PROVIDER 決定使用真實 LLM 或 mock。
    """
    if settings.AI_PROVIDER == "gemini":
        return await _geminiSettle(playerState, realityApi, playerAction)
    elif settings.AI_PROVIDER == "openai":
        return await _openaiSettle(playerState, realityApi, playerAction)
    
    # 預設：Mock
    return _mockSettle(playerState, realityApi, playerAction)


async def _geminiSettle(
    playerState: dict[str, Any],
    realityApi: dict[str, Any],
    playerAction: str,
) -> dict[str, Any]:
    """使用 Gemini API 進行非同步結算（含 10 秒超時保護）"""
    global _gemini_client
    if not settings.GEMINI_API_KEY:
        logger.error("未設定 GEMINI_API_KEY，退回 mock 模式")
        return _mockSettle(playerState, realityApi, playerAction)

    try:
        from google import genai
        from google.genai import types

        if _gemini_client is None:
            _gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        prompt = (
            f"【玩家狀態】\n{json.dumps(playerState, ensure_ascii=False, indent=2)}\n\n"
            f"【現實事件/時空背景】\n{json.dumps(realityApi, ensure_ascii=False, indent=2)}\n\n"
            f"【玩家近期行動】\n{playerAction}\n\n"
            "請根據以上資訊，進行結算並回傳 JSON 格式結果。"
        )

        async def _call_gemini():
            return await _gemini_client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=SettlementResult,
                    temperature=0.8,
                ),
            )

        # 10 秒超時保護
        response = await asyncio.wait_for(_call_gemini(), timeout=10.0)

        result_json = json.loads(response.text)
        logger.info(f"[Gemini Settle] 結算成功: {result_json['state_changes']}")
        return result_json

    except asyncio.TimeoutError:
        logger.error("[Gemini Settle] API 呼叫超時(10s)，退回 mock 模式")
        return _mockSettle(playerState, realityApi, playerAction)
    except Exception as e:
        logger.error(f"[Gemini Settle] API 呼叫失敗: {e}，退回 mock 模式")
        return _mockSettle(playerState, realityApi, playerAction)


async def _openaiSettle(
    playerState: dict[str, Any],
    realityApi: dict[str, Any],
    playerAction: str,
) -> dict[str, Any]:
    """使用 OpenAI API 進行非同步結算"""
    if not settings.OPENAI_API_KEY:
        logger.error("未設定 OPENAI_API_KEY，退回 mock 模式")
        return _mockSettle(playerState, realityApi, playerAction)

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        prompt = (
            f"【玩家狀態】\n{json.dumps(playerState, ensure_ascii=False)}\n\n"
            f"【現實事件/時空背景】\n{json.dumps(realityApi, ensure_ascii=False)}\n\n"
            f"【玩家近期行動】\n{playerAction}"
        )

        response = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format=SettlementResult,
            temperature=0.8
        )
        
        result_json = response.choices[0].message.parsed.model_dump()
        logger.info(f"[OpenAI Settle] 結算成功: {result_json['state_changes']}")
        return result_json

    except Exception as e:
        logger.error(f"[OpenAI Settle] API 呼叫失敗: {e}，退回 mock 模式")
        return _mockSettle(playerState, realityApi, playerAction)


def _mockSettle(
    playerState: dict[str, Any],
    realityApi: dict[str, Any],
    playerAction: str,
) -> dict[str, Any]:
    """
    Mock 結算引擎：產生合理的模擬結果，用於開發與測試。
    """
    name = playerState.get("basicInfo", {}).get("name", "某候選人")

    # 簡單模擬：根據行動關鍵字決定影響方向
    isAggressive = any(kw in playerAction for kw in ["攻擊", "酸", "抹黑", "開砲", "嗆"])
    isPositive = any(kw in playerAction for kw in ["掃街", "拜票", "捐款", "政見", "公益"])
    isDangerous = any(kw in playerAction for kw in ["無視", "暴雨", "堅持", "風險"])

    favChange = random.randint(-500, 300) if isAggressive else random.randint(-100, 500)
    aggroChange = random.randint(200, 800) if isAggressive else random.randint(-100, 200)
    fameChange = random.randint(50, 300)
    fundsChange = random.randint(-200000, -10000)
    apChange = random.randint(-25, -5)

    if isDangerous:
        favChange -= 500
        aggroChange += 500

    result = {
        "news_report": (
            f"〔Mock 結算〕為您插播最新選情！{name}今日{playerAction[:20]}..."
            f"引發各界議論。政治評論員認為此舉{'大膽但有風險' if isDangerous else '值得肯定'}，"
            f"對手陣營發言人則痛批其不知民間疾苦。"
        ),
        "ptt_comments": [
            f"{'噓' if isAggressive else '推'}: 這咖又在{'作秀' if isAggressive else '認真做事'}了",
            f"{'推' if isPositive else '噓'}: {'選舉到了才來' if not isPositive else '值得鼓勵給推'}",
            "→: 吃瓜看戲中，坐等後續發展",
        ],
        "state_changes": {
            "favorability": favChange,
            "aggro": aggroChange,
            "fame": fameChange,
            "political_funds": fundsChange,
            "staff_ap": apChange,
            "array_events": "",
        },
    }
    return result


# ── 全服新聞快訊 Schema ──────────────────────────────────────
class NewsFlash(BaseModel):
    title: str = Field(description="5-10字極其聳動的新聞標題，例如：爆！某大老竟然...")
    content: str = Field(description="20-40字摘要報導，需具備媒體渲染力")

async def generateNewsFlash(
    attacker_name: str,
    defender_name: str,
    event_type: str,
    damage_desc: str
) -> NewsFlash:
    """
    產生全伺服器廣播的新聞快訊。
    """
    if settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        return await _geminiGenerateNewsFlash(attacker_name, defender_name, event_type, damage_desc)
    
    return _mockGenerateNewsFlash(attacker_name, defender_name, event_type, damage_desc)

async def _geminiGenerateNewsFlash(
    attacker: str, defender: str, event: str, damage: str
) -> NewsFlash:
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        prompt = (
            f"情境：選戰白熱化。{attacker} 發動了 {event}，對 {defender} 造成了 {damage}。\n"
            "請以台灣媒體（如三立、東森、中天風格）寫一則極其辛辣、聳動的新聞快訊標題與內容。\n"
            "標題必須語不驚人死不休。內容需包含雙方名稱。"
        )

        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="你是一個專門寫聳動政治新聞的AI，熟悉台灣政治術語與新聞語氣。",
                response_mime_type="application/json",
                response_schema=NewsFlash,
                temperature=0.9,
            ),
        )

        return NewsFlash.model_validate_json(response.text)
    except Exception as e:
        logger.error(f"[NewsFlash] AI 失敗: {e}")
        return _mockGenerateNewsFlash(attacker, defender, event, damage)

def _mockGenerateNewsFlash(
    attacker: str, defender: str, event: str, damage: str
) -> NewsFlash:
    titles = ["【爆料】", "【震驚】", "【獨家】", "【直擊】", "【突發】"]
    t = random.choice(titles)
    return NewsFlash(
        title=f"{t} {attacker} 狠戳 {defender} 痛點！",
        content=f"消息傳出 {attacker} 發動 {event}，{defender} 被爆 {damage}，在地支持度恐受重創！"
    )

async def analyzeNewsSentiment_LLM(news_title: str) -> bool:
    """使用輕量級 LLM 分析新聞標題對當事人是正向還是負向"""
    if not settings.GEMINI_API_KEY or settings.AI_PROVIDER == "mock":
        return random.random() > 0.45

    global _gemini_client
    try:
        from google import genai
        if _gemini_client is None:
            _gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
        prompt = f"判斷以下台灣政治新聞標題是對當事人有利（正向）還是有害（負向）。只能回答「正向」或「負向」：\n\n標題：{news_title}"
        
        async def _call():
            return await _gemini_client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=genai.types.GenerateContentConfig(temperature=0.1)
            )
            
        import asyncio
        response = await asyncio.wait_for(_call(), timeout=5.0)
        text = response.text if response.text else ""
        return "正向" in text
    except Exception as e:
        logger.error(f"LLM 情感分析失敗: {e}")
        return random.random() > 0.45
