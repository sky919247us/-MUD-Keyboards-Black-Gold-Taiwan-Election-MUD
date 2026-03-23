"""
玩家行動冷卻管理
- 提供 per-entity 指令冷卻機制，防止玩家速連刷指令。
"""
from __future__ import annotations

import logging
import time

logger = logging.getLogger(__name__)


class ActionCooldownManager:
    """
    行動冷卻管理器。
    每個 entityId 對特定指令有冷卻時間，冷卻期間拒絕重複操作。
    """
    # 各指令的冷卻秒數
    COOLDOWN_MAP: dict[str, float] = {
        "/act": 10.0,      # AI 結算最耗資源，冷卻 10 秒
        "/attack": 5.0,
        "/flip": 5.0,
        "/invest": 3.0,
        "/launder": 5.0,
    }
    DEFAULT_COOLDOWN = 1.0  # 其餘指令的預設冷卻
    # 超過此秒數未使用的紀錄將被清理
    _CLEANUP_THRESHOLD = 3600.0

    def __init__(self) -> None:
        # (entityId, command) -> 上次執行時間戳
        self._last_used: dict[tuple[str, str], float] = {}
        self._last_cleanup: float = time.time()

    def check_cooldown(self, entityId: str, command: str) -> tuple[bool, float]:
        """
        檢查指令是否仍在冷卻中。
        回傳 (is_ready, remaining_seconds)。
        """
        self._maybe_cleanup()
        cd = self.COOLDOWN_MAP.get(command, self.DEFAULT_COOLDOWN)
        key = (entityId, command)
        last = self._last_used.get(key, 0.0)
        elapsed = time.time() - last
        if elapsed < cd:
            return False, round(cd - elapsed, 1)
        return True, 0.0

    def record_usage(self, entityId: str, command: str) -> None:
        """記錄指令使用時間"""
        self._last_used[(entityId, command)] = time.time()

    def _maybe_cleanup(self) -> None:
        """定期清除超過 1 小時未活躍的冷卻紀錄，避免記憶體洩漏"""
        now = time.time()
        if now - self._last_cleanup < 600:  # 每 10 分鐘最多清一次
            return
        self._last_cleanup = now
        stale_keys = [k for k, v in self._last_used.items() if now - v > self._CLEANUP_THRESHOLD]
        for k in stale_keys:
            del self._last_used[k]
        if stale_keys:
            logger.debug(f"[Cooldown] 清理了 {len(stale_keys)} 筆過期冷卻紀錄")


cooldownManager = ActionCooldownManager()
