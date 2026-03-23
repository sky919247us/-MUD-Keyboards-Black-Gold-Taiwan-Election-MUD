import asyncio
import logging
from typing import NamedTuple, Optional

import feedparser

from app.data.npc_db import npc_db

logger = logging.getLogger(__name__)

# Yahoo 政治新聞 RSS
YAHOO_POLITICS_RSS = "https://tw.news.yahoo.com/rss/politics"

class NewsMatchResult(NamedTuple):
    entity_id: str
    entity_type: str  # "politician" or "corporation"
    news_title: str
    news_link: str

async def fetch_latest_news() -> list[dict]:
    """抓取最新新聞，回傳 dict 列表包含 title 與 link"""
    # feedparser.parse 屬於同步阻塞操作，所以用 asyncio.to_thread 跑
    feed = await asyncio.to_thread(feedparser.parse, YAHOO_POLITICS_RSS)
    results = []
    
    if feed.entries:
        for entry in feed.entries[:10]:  # 取最新 10 則
            results.append({
                "title": entry.title,
                "link": entry.link
            })
    return results

def match_entities_in_text(text: str) -> list[tuple[str, str]]:
    """在文本中尋找符合 dict 的實體，回傳 [(entity_id, type)]"""
    matches = []
    
    # 比對政治人物
    for pol in npc_db.politicians:
        keywords = [pol["real_name"], pol["in_game_name"]] + pol.get("aliases", [])
        if any(kw in text for kw in keywords):
            matches.append((pol["id"], "politician"))

    # 比對企業
    for corp in npc_db.corporations:
        keywords = [corp["real_name"], corp["in_game_name"]] + corp.get("aliases", [])
        if any(kw in text for kw in keywords):
            matches.append((corp["id"], "corporation"))
            
    return matches

async def scan_news_for_entities() -> list[NewsMatchResult]:
    """整合流程：抓新聞 -> NER 實體比對 -> 回傳結果"""
    news_list = await fetch_latest_news()
    matched_events = []
    
    for news in news_list:
        entities = match_entities_in_text(news["title"])
        for entity_id, entity_type in entities:
            matched_events.append(NewsMatchResult(
                entity_id=entity_id,
                entity_type=entity_type,
                news_title=news["title"],
                news_link=news["link"]
            ))
            logger.info(f"[NER] 標題「{news['title']}」比對到實體: {entity_id}")
            
    return matched_events
