"""
SQLAlchemy ORM 資料表定義
我們使用 JSONB 直接快取複雜的 Pydantic 架構，免除大量拆表的痛點。
"""
from datetime import datetime

from sqlalchemy import Column, String, DateTime, JSON

from app.db.session import Base

class UserModel(Base):
    """
    玩家資料表 (對應 PlayerCharacter)
    綁定真實登入者與其遊戲內的虛擬分身關聯。
    """
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True, comment="真實通訊軟體 ID (如 LINE UserID)")
    entity_id = Column(String, nullable=False, index=True, comment="其所屬/伺候的 PoliticalEntity ID")
    
    # 存放 CharacterIdentity 的細節 (boss_name, role_title, gender, party_code)
    identity_data = Column(JSON, nullable=False, server_default='{}')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EntityModel(Base):
    """
    政治實體資料表 (對應 PoliticalEntity / NPC)
    將所有的資金、知名度、好感度狀態封裝在 state_data 欄位中。
    """
    __tablename__ = "entities"

    entity_id = Column(String, primary_key=True, index=True)
    entity_name = Column(String, index=True, nullable=True, comment="角色/實體名稱以利搜尋")
    entity_type = Column(String, nullable=False, server_default="politician", comment="pol/corp")
    
    # 整包 PoliticalEntity Pydantic 型別直接轉 dict 存入
    state_data = Column(JSON, nullable=False, server_default='{}')
    
    # LINE Auth 相關欄位
    line_user_id = Column(String, index=True, nullable=True, comment="綁定的 LINE 帳號 ID")
    line_display_name = Column(String, nullable=True, comment="綁定的 LINE 顯示名稱")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
