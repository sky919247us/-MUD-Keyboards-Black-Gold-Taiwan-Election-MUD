import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# JSON 檔案路徑設定
DATA_DIR = Path(__file__).parent
POLITICIANS_FILE = DATA_DIR / "politicians.json"
CORPORATIONS_FILE = DATA_DIR / "corporations.json"

class NpcDatabase:
    """實體映射資料庫 (NER Database)"""

    def __init__(self):
        self.politicians: list[dict] = []
        self.corporations: list[dict] = []
        self.load_data()

    def load_data(self):
        """從靜態 JSON 載入所有實體"""
        try:
            if POLITICIANS_FILE.exists():
                with open(POLITICIANS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.politicians = data.get("politicians", [])
            else:
                logger.warning(f"檔案不存在: {POLITICIANS_FILE}")

            if CORPORATIONS_FILE.exists():
                with open(CORPORATIONS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.corporations = data.get("corporations", [])
            else:
                logger.warning(f"檔案不存在: {CORPORATIONS_FILE}")
            
            logger.info(f"[NPC DB] 載入 {len(self.politicians)} 位政治實體與 {len(self.corporations)} 家企業")
            
        except Exception as e:
            logger.error(f"實體資料庫載入失敗: {e}")

    def get_politicians_by_party(self, party_code: str) -> list[dict]:
        """透過政黨代碼取得該黨所屬政治人物"""
        return [p for p in self.politicians if p.get("party_code") == party_code]

    def get_politician_by_id(self, pol_id: str) -> Optional[dict]:
        """透過實體 ID 找人"""
        for p in self.politicians:
            if p.get("id") == pol_id:
                return p
        return None

# 全域單子實例
npc_db = NpcDatabase()
