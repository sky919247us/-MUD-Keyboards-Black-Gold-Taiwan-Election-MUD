import random
import logging
from collections import deque
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class Stock(BaseModel):
    symbol: str
    name: str
    price: int
    trend: str = "平" # 漲/跌/平

class BlackMarket:
    """全服黑市與地下經濟實作（深化版）"""
    def __init__(self):
        self.stocks = {
            "G2330": Stock(symbol="G2330", name="科技集團", price=800),
            "G2881": Stock(symbol="G2881", name="金融集團", price=120),
            "G1301": Stock(symbol="G1301", name="傳產集團", price=85),
            "G2542": Stock(symbol="G2542", name="營建公會", price=45),
        }
        self.launder_rate = 0.7  # 洗錢保留比例（70%）
        # 股價歷史（每支股票保留最近 50 Tick 的價格快照）
        self.price_history: dict[str, deque[int]] = {
            sym: deque([s.price], maxlen=50)
            for sym, s in self.stocks.items()
        }

    def tick_market(self, server_aggro: int = 0, real_market_delta: float = 0.0,
                    entity_count: int = 0, avg_legal_risk: float = 0.0):
        """
        每回合推進市場行情。
        參數：
        - server_aggro: 全服總仇恨值
        - real_market_delta: 現實台股漲跌幅（如 -0.035 = -3.5%）
        - entity_count: 活躍實體數量（越多洗錢越危險）
        - avg_legal_risk: 全服平均法務風險值
        """
        # 洗錢折損率：多因素計算
        base_rate = 0.8
        aggro_penalty = min(0.2, server_aggro / 100_000.0)
        entity_penalty = min(0.1, entity_count / 500.0)
        legal_penalty = min(0.15, avg_legal_risk / 200.0)
        self.launder_rate = max(0.3, base_rate - aggro_penalty - entity_penalty - legal_penalty)

        # 股市隨機波動（受現實台股影響）
        for symbol, stock in self.stocks.items():
            # 基礎隨機漫步 (-5% ~ 5.5%，長期微漲)
            base_change = random.uniform(-0.05, 0.055)
            # 現實台股連動（權重 30%）
            real_influence = real_market_delta * 0.3 if real_market_delta else 0
            change_percent = base_change + real_influence

            old_price = stock.price
            stock.price = max(10, int(stock.price * (1 + change_percent)))
            if stock.price > old_price:
                stock.trend = "漲 🔺"
            elif stock.price < old_price:
                stock.trend = "跌 🔻"
            else:
                stock.trend = "平 ➖"

            # 記錄歷史價格
            self.price_history[symbol].append(stock.price)
        
        logger.debug(f"[Market] 行情更新。洗錢折算率: {self.launder_rate*100:.1f}%")

    def get_stock_history(self, symbol: str) -> list[int]:
        """取得某支股票的歷史價格列表（最近 50 Tick）"""
        return list(self.price_history.get(symbol, []))

# 全域單例
market = BlackMarket()
