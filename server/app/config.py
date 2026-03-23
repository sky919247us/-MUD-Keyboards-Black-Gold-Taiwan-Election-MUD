"""
應用程式設定模組
從環境變數載入所有設定，確保金鑰不寫死在程式碼中。
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """應用程式設定"""

    # 伺服器
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Tick 間隔（秒）
    # NOTE: 生產環境為 600 秒（10 分鐘），測試環境可設為 30 秒
    TICK_INTERVAL_SECONDS: int = int(os.getenv("TICK_INTERVAL", "30"))

    # AI 結算引擎
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "mock")  # mock / openai / gemini
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # 現實 API 金鑰
    CWA_API_KEY: str = os.getenv("CWA_API_KEY", "")  # 中央氣象署授權金鑰

    # WebSocket 簽章密鑰（必須設定，否則安全性不足）
    WS_SECRET_KEY: str = os.getenv("WS_SECRET_KEY", "")

    # 資料庫（Phase 2）
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./tw_mud.db")


settings = Settings()
