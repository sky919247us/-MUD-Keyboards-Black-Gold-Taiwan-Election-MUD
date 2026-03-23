"""
安全性模組：處理 WebSocket Token 簽發與驗證
為了避免不必要的外部套件相依，這裡實作基於 HMAC 的簡易 Token 機制。
"""
import hmac
import hashlib
import time
import base64
from typing import Optional

from app.config import settings

# 使用獨立的 WS 簽章密鑰（生產環境必須設定 WS_SECRET_KEY 環境變數）
if not settings.WS_SECRET_KEY:
    import logging as _log
    _log.getLogger(__name__).warning(
        "未設定 WS_SECRET_KEY，使用開發用預設金鑰。生產環境請務必設定！"
    )
SECRET_KEY = settings.WS_SECRET_KEY or "tw_mud_dev_only_key_change_me"

def generate_ws_token(user_id: str, entity_id: str, expire_seconds: int = 300) -> str:
    """
    產生供 WebSocket 認證用的短期 Token
    格式: base64(userId:entityId:expireTime:signature)
    """
    expire_time = int(time.time()) + expire_seconds
    payload = f"{user_id}:{entity_id}:{expire_time}"
    
    # 建立簽章
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'), 
        payload.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    
    token_str = f"{payload}:{signature}"
    return base64.urlsafe_b64encode(token_str.encode('utf-8')).decode('utf-8')

def verify_ws_token(token: str, expected_entity_id: str) -> Optional[str]:
    """
    驗證 WebSocket Token，成功回傳 user_id，失敗回傳 None。
    """
    try:
        token_str = base64.urlsafe_b64decode(token.encode('utf-8')).decode('utf-8')
        parts = token_str.split(':')
        if len(parts) != 4:
            return None
            
        user_id, entity_id, str_expire, signature = parts
        
        # 1. 檢查 Entity ID
        if entity_id != expected_entity_id:
            return None
            
        # 2. 檢查過期
        if int(str_expire) < time.time():
            return None
            
        # 3. 檢查簽章
        payload = f"{user_id}:{entity_id}:{str_expire}"
        expected_sig = hmac.new(
            SECRET_KEY.encode('utf-8'), 
            payload.encode('utf-8'), 
            hashlib.sha256
        ).hexdigest()
        
        if hmac.compare_digest(signature, expected_sig):
            return user_id
            
    except Exception:
        pass
        
    return None
