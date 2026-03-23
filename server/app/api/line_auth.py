"""
LINE 帳號綁定 API
透過 LIFF 取得的 LINE Profile 建立或查詢遊戲角色對應關係。
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db.session import AsyncSessionLocal
from app.db.async_repo import getEntityById
from sqlalchemy import text

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/line", tags=["LINE Auth"])


class LineProfile(BaseModel):
    """LINE LIFF 傳入的使用者資料"""
    line_user_id: str   # LINE userId
    display_name: str   # LINE 顯示名稱
    picture_url: Optional[str] = None  # LINE 大頭貼 URL


class LineBindResponse(BaseModel):
    """綁定結果回應"""
    entity_id: Optional[str] = None   # 若已有角色回傳 entityId，否則 None
    is_new_user: bool                  # 是否為新使用者
    display_name: str                  # LINE 顯示名稱


@router.post("/bind", response_model=LineBindResponse)
async def bind_line_account(profile: LineProfile) -> LineBindResponse:
    """
    LINE 帳號綁定端點。
    - 若 LINE userId 已對應到遊戲角色，回傳該角色的 entity_id。
    - 若為新使用者，回傳 is_new_user=True 讓前端引導角色建立流程。
    """
    uid = profile.line_user_id
    logger.info("LINE 綁定請求：userId=%s, name=%s", uid, profile.display_name)

    async with AsyncSessionLocal() as session:
        try:
            # 查詢 LINE userId 是否已對應遊戲角色
            # NOTE: 使用 entities 表的 line_user_id 欄位進行查詢
            result = await session.execute(
                text("SELECT entity_id FROM entities WHERE line_user_id = :uid"),
                {"uid": uid}
            )
            row = result.fetchone()

            if row:
                entity_id = row[0]
                logger.info("LINE 帳號已綁定，entity_id=%s", entity_id)
                return LineBindResponse(
                    entity_id=entity_id,
                    is_new_user=False,
                    display_name=profile.display_name
                )
            else:
                logger.info("LINE 帳號未綁定，引導建立角色")
                return LineBindResponse(
                    entity_id=None,
                    is_new_user=True,
                    display_name=profile.display_name
                )
        except Exception as e:
            # NOTE: 若 line_user_id 欄位不存在（舊資料庫），當作新用戶處理
            logger.warning("line_user_id 欄位查詢失敗（可能尚未 migrate）：%s", e)
            return LineBindResponse(
                entity_id=None,
                is_new_user=True,
                display_name=profile.display_name
            )
