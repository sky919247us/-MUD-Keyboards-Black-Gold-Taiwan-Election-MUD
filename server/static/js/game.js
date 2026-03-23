/**
 * 鍵盤與黑金：台灣選戰 MUD — 前端主程式
 * 整合 LINE LIFF 登入、WebSocket 通訊、賽博龐克設計系統
 */

// ===== 全域常數與狀態 =====
const LIFF_ID = "2009558875-PiJYcJDN";

let userId = null;        // LINE userId（或 dev fallback）
let entityId = null;      // 遊戲角色 entityId
let ws = null;            // WebSocket 連線
let selectedParty = null; // 建角時選擇的政黨
let trendingChart = null; // Chart.js 實例
let currentTab = "news";  // 當前頁籤

// ===== UI 元素 =====
const screenLoading  = document.getElementById("screen-loading");
const screenCreation = document.getElementById("screen-creation");
const screenGame     = document.getElementById("screen-game");
const bottomNav      = document.getElementById("bottom-nav");
const fabAction      = document.getElementById("fab-action");
const output         = document.getElementById("output");

// ===== PWA Service Worker 註冊 =====
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/static/sw.js")
    .then(reg => console.log("SW registered!", reg))
    .catch(err => console.error("SW failed", err));
}

// ===== LINE LIFF 登入 =====

/** LIFF 是否已初始化 */
let liffInitialized = false;

/**
 * 頁面載入時自動初始化 LIFF
 * NOTE: 在 LINE App 內開啟時，LIFF 會自動登入並取得使用者資料
 */
async function initLiff() {
  try {
    await liff.init({ liffId: LIFF_ID });
    liffInitialized = true;
    console.log("LIFF 初始化成功, isLoggedIn:", liff.isLoggedIn());
    console.log("LIFF isInClient:", liff.isInClient());

    if (liff.isLoggedIn()) {
      // 已登入，自動取得 Profile 進入遊戲
      await handleLiffLogin();
    }
    // 未登入：等使用者按下「以 LINE 帳號登入」按鈕
  } catch (err) {
    console.warn("LIFF 初始化失敗（可能不在 LINE 環境中）:", err.message);
    // 不彈出任何對話框，讓使用者自行點選按鈕觸發登入
  }
}

/**
 * LIFF 已登入後，取得 Profile 並進入遊戲
 */
async function handleLiffLogin() {
  const btn = document.getElementById("btn-line-login");
  if (btn) {
    btn.textContent = "連接中...";
    btn.disabled = true;
  }

  try {
    const profile = await liff.getProfile();
    userId = profile.userId;
    const displayName = profile.displayName;
    const pictureUrl  = profile.pictureUrl || "";

    // 更新頂部標題顯示使用者名稱
    document.getElementById("header-status").textContent = displayName;

    // 呼叫後端綁定 LINE 帳號並查詢角色
    await bindLineAndCheckCharacter(userId, displayName, pictureUrl);
  } catch (err) {
    console.error("取得 LINE Profile 失敗:", err);
    if (btn) {
      btn.textContent = "以 LINE 帳號登入";
      btn.disabled = false;
    }
  }
}

/**
 * 使用者點擊「以 LINE 帳號登入」按鈕時觸發
 */
async function startLineLogin() {
  const btn = document.getElementById("btn-line-login");
  btn.textContent = "連接中...";
  btn.disabled = true;

  try {
    // 如果 LIFF 尚未初始化，先初始化
    if (!liffInitialized) {
      await liff.init({ liffId: LIFF_ID });
      liffInitialized = true;
    }

    if (liff.isLoggedIn()) {
      // 已登入（例如從 LINE OAuth 回來後），直接取得 Profile
      await handleLiffLogin();
    } else {
      // 未登入，觸發 LINE OAuth 跳轉（回來後 LIFF 會自動帶登入狀態）
      liff.login({ redirectUri: window.location.origin + "/" });
    }
  } catch (err) {
    console.error("LINE 登入失敗:", err);
    btn.textContent = "以 LINE 帳號登入";
    btn.disabled = false;
    alert("LINE 登入失敗，請確認您是在 LINE App 中開啟此頁面，或稍後再試。");
  }
}

// 頁面載入時自動初始化 LIFF
document.addEventListener("DOMContentLoaded", initLiff);

/**
 * 呼叫後端 LINE 帳號綁定 API，取得或建立遊戲角色
 * @param {string} uid - LINE userId
 * @param {string} name - LINE 顯示名稱
 * @param {string} pic  - LINE 大頭貼 URL
 */
async function bindLineAndCheckCharacter(uid, name, pic) {
  try {
    const res = await fetch("/api/line/bind", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ line_user_id: uid, display_name: name, picture_url: pic })
    });

    if (res.ok) {
      const data = await res.json();
      if (data.entity_id) {
        // 已有角色，直接進入遊戲
        await enterGame(data.entity_id);
      } else {
        // 新用戶，引導角色建立
        showCreationScreen();
      }
    } else {
      // API 異常 fallback
      await checkCharacterData(uid);
    }
  } catch (e) {
    console.error("bind API error:", e);
    await checkCharacterData(uid);
  }
}

/**
 * 查詢角色資料（舊版 fallback）
 */
async function checkCharacterData(uid) {
  try {
    const res = await fetch(`/api/v1/user/${uid}/character`);
    if (res.status === 404) {
      showCreationScreen();
    } else if (res.ok) {
      const data = await res.json();
      await enterGame(data.entityId);
    } else {
      showCreationScreen();
    }
  } catch (e) {
    console.error("character API error:", e);
    showCreationScreen();
  }
}

// ===== 畫面切換 =====

/** 顯示角色建立畫面 */
function showCreationScreen() {
  console.log(">>> showCreationScreen 被呼叫了！");
  // 直接用 inline style 控制，避免 CSS class 權重 / 快取問題
  screenLoading.style.display = "none";
  screenCreation.style.display = "block";
  screenLoading.classList.remove("active");
  screenCreation.classList.add("active");
}

/** 選擇政黨 */
function selectParty(el) {
  document.querySelectorAll(".party-card").forEach(c => c.classList.remove("selected"));
  el.classList.add("selected");
  selectedParty = el.dataset.party;
  document.getElementById("btn-create-role").style.display = "flex";
}

/** 確認並建立角色 */
async function createCharacter() {
  if (!selectedParty || !userId) return;
  const btn = document.getElementById("btn-create-role");
  btn.disabled = true;
  btn.innerHTML = `<span class="material-symbols-outlined">hourglass_top</span> 資料生成中...`;

  try {
    const res = await fetch(`/api/v1/user/${userId}/create_character`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ party_code: selectedParty })
    });

    if (res.ok) {
      const data = await res.json();
      await enterGame(data.entityId);
    } else {
      alert("角色建立失敗，請稍後再試。");
      btn.disabled = false;
      btn.innerHTML = `<span class="material-symbols-outlined">double_arrow</span> 確定陣營，抽取幕僚身分`;
    }
  } catch (e) {
    console.error("create_character error:", e);
    btn.disabled = false;
    btn.innerHTML = `<span class="material-symbols-outlined">double_arrow</span> 確定陣營，抽取幕僚身分`;
  }
}

// ===== 進入遊戲 =====

/**
 * 進入主遊戲畫面並建立 WebSocket 連線
 * @param {string} eid - 遊戲角色 entityId
 */
async function enterGame(eid) {
  entityId = eid;

  // 切換畫面
  screenLoading.classList.remove("active");
  screenCreation.classList.remove("active");
  screenGame.classList.add("active");
  bottomNav.style.display = "flex";
  fabAction.style.display = "flex";

  // 取得 WS Token
  let token = "";
  try {
    const tokenRes = await fetch(`/api/v1/user/${userId}/token`);
    if (tokenRes.ok) {
      const tokenData = await tokenRes.json();
      token = tokenData.token;
    }
  } catch (e) {
    console.error("Token fetch error:", e);
  }

  // 建立 WebSocket
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  ws = new WebSocket(`${protocol}//${window.location.host}/ws/${eid}`);

  ws.onopen = () => {
    ws.send(JSON.stringify({ type: "auth", token }));
    appendMsg("〉 連線穩定，加密通道已立。", "system");
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.type === "broadcast") {
        if (data.msg_type === "news") {
          showNewsFlash(data.content);
        } else {
          appendMsg(`[廣播] ${data.content}`, "system");
        }
      } else {
        appendMsg(event.data);
      }
    } catch (e) {
      appendMsg(event.data);
    }
  };

  ws.onclose = () => {
    appendMsg("[系統] 連線已中斷，請重新整理頁面。", "error");
    fabAction.style.display = "none";
  };

  // 啟動趨勢圖輪詢
  updateTrendingChart(eid);
  setInterval(() => updateTrendingChart(eid), 30000);

  // 讀取排行榜與市場資料
  updateRankData();
  updateEconomyData();
}

// ===== 頁籤切換 =====

/**
 * 切換主遊戲頁籤（選情/市場/排行/幕僚）
 * @param {string} tab - 頁籤 ID
 */
function switchTab(tab) {
  currentTab = tab;

  // 頁籤按鈕狀態
  document.querySelectorAll(".nav-tab").forEach(el => {
    el.classList.toggle("active", el.dataset.tab === tab);
  });
  document.querySelectorAll(".nav-item").forEach(el => {
    el.classList.toggle("active", el.dataset.tab === tab);
  });

  // 頁籤內容顯示
  document.querySelectorAll(".tab-pane").forEach(el => {
    el.classList.toggle("active", el.id === `tab-${tab}`);
  });

  // 視需要載入資料
  if (tab === "rank")    updateRankData();
  if (tab === "market")  updateEconomyData();
  if (tab === "profile") updateProfileData();
}

// ===== 行動選單 Bottom Sheet =====

/** 開啟行動選單 */
function openActionSheet() {
  document.getElementById("action-sheet").classList.add("open");
  document.getElementById("action-backdrop").classList.add("open");
}

/** 關閉行動選單 */
function closeActionSheet() {
  document.getElementById("action-sheet").classList.remove("open");
  document.getElementById("action-backdrop").classList.remove("open");
}

/**
 * 執行行動指令（從行動選單觸發）
 * @param {string} cmd   - 指令字串
 * @param {string} label - 顯示名稱
 */
function doAction(cmd, label) {
  closeActionSheet();

  if (cmd === "/attack") {
    const target = prompt("⚔ 網軍出征\n請輸入要攻擊的對手陣營或候選人名稱：");
    if (!target) return;
    cmd = `/attack ${target}`;
  } else if (cmd === "/flip") {
    const target = prompt("🤝 拔樁行動\n請輸入對手名稱：");
    if (!target) return;
    const bossId = prompt("請輸入欲策反的樁腳 ID：");
    if (!bossId) return;
    cmd = `/flip ${target} ${bossId}`;
  }

  appendMsg(`〉 執行行動：[${label}]`, "system");
  sendCommand(cmd);
}

/**
 * 透過 WebSocket 發送指令
 * @param {string} cmd - 指令字串
 */
function sendCommand(cmd) {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    appendMsg("⚠ 連線中斷，請重新整理頁面。", "error");
    return;
  }
  ws.send(cmd);
  switchTab("news"); // 切換至選情 tab 以觀看回傳結果
}

// ===== 訊息顯示 =====

/**
 * 在選情 Tab 追加訊息條目
 * @param {string} text - 訊息內容
 * @param {string} cls  - 訊息樣式類別
 */
function appendMsg(text, cls) {
  if (!output) return;
  const div = document.createElement("div");

  // 自動語意判斷（天災、戰鬥事件等）
  if (!cls) {
    if (text.includes("🚨") || text.includes("⚠") || text.includes("⛈")) {
      cls = "msg-news msg-crisis";
      document.body.style.animation = "none";
      document.body.offsetHeight; // 強制 reflow
      document.body.style.animation = "shake 0.3s ease";
    } else if (text.includes("【網軍") || text.includes("【拔樁")) {
      cls = "msg-news msg-crisis";
    } else if (text.includes("[Tick]") || text.includes("✅")) {
      cls = "msg-news msg-positive";
    } else {
      cls = "msg-news";
    }
  }

  div.className = cls;
  div.innerHTML = text.replace(/\n/g, "<br>");
  output.appendChild(div);

  // 捲動到最新訊息
  setTimeout(() => {
    output.scrollTop = output.scrollHeight;
  }, 50);
}

/** 顯示新聞跑馬燈 */
function showNewsFlash(text) {
  const marquee  = document.getElementById("news-marquee");
  const newsText = document.getElementById("news-text");
  if (!marquee) return;
  newsText.innerText = text;
  marquee.style.display = "flex";
  setTimeout(() => { marquee.style.display = "none"; }, 8000);
}

// ===== 趨勢圖 =====

/** 更新選情趨勢圖（Chart.js） */
async function updateTrendingChart(eid) {
  try {
    const res = await fetch(`/api/v1/entities/${eid}/history`);
    if (!res.ok) return;
    const data = await res.json();

    if (!trendingChart) {
      const ctx = document.getElementById("trendingChart").getContext("2d");
      trendingChart = new Chart(ctx, {
        type: "line",
        data: {
          labels: data.labels.map(l => `T${l}`),
          datasets: [
            {
              label: "知名度",
              data: data.fame,
              borderColor: "#8eff71",
              backgroundColor: "rgba(142, 255, 113, 0.05)",
              tension: 0.3,
              borderWidth: 2,
              pointRadius: 0
            },
            {
              label: "好感度",
              data: data.favorability,
              borderColor: "#99b8fe",
              backgroundColor: "rgba(153, 184, 254, 0.05)",
              tension: 0.3,
              borderWidth: 2,
              pointRadius: 0
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { beginAtZero: false, grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#747579", font: { size: 9 } } },
            x: { grid: { display: false }, ticks: { color: "#747579", font: { size: 9 } } }
          },
          plugins: {
            legend: { labels: { color: "#aaabaf", boxWidth: 8, font: { size: 10 } } }
          }
        }
      });
    } else {
      trendingChart.data.labels = data.labels.map(l => `T${l}`);
      trendingChart.data.datasets[0].data = data.fame;
      trendingChart.data.datasets[1].data = data.favorability;
      trendingChart.update("none");
    }
  } catch (e) {
    console.error("Chart update error:", e);
  }
}

// ===== 排行榜資料 =====

/** 更新全台排行榜 */
async function updateRankData() {
  const content = document.getElementById("warroom-content");
  if (!content) return;
  content.innerHTML = `<p style="color:var(--color-on-surface-dim);font-size:12px;padding:12px 0">同步衛星數據中...</p>`;

  try {
    const res = await fetch("/api/v1/leaderboard");
    const data = await res.json();
    let html = "";
    data.forEach((e, i) => {
      html += `
        <div class="rank-row">
          <div style="width:28px;color:var(--color-on-surface-dim);font-family:var(--font-headline);font-size:11px;font-weight:700">#${i + 1}</div>
          <div style="flex:1">
            <span class="rank-badge badge-${e.party}">${e.party}</span>
            <span style="font-weight:700;font-size:13px">${e.name}</span>
            <span style="font-size:10px;color:var(--color-on-surface-dim)"> | ${e.title || ""}</span>
          </div>
          <div style="color:var(--color-primary);font-family:var(--font-headline);font-weight:700;font-size:13px">${(e.fame || 0).toLocaleString()}</div>
        </div>`;
    });
    content.innerHTML = html || `<p style="color:var(--color-on-surface-dim);font-size:12px;padding:12px 0">尚無排行資料</p>`;
  } catch (e) {
    content.innerHTML = `<p style="color:var(--color-tertiary);font-size:12px;padding:12px 0">⚠ 通訊中斷，無法取得選情資訊。</p>`;
  }
}

// ===== 市場資料 =====

/** 更新地下市場資料 */
async function updateEconomyData() {
  const content = document.getElementById("economy-content");
  if (!content) return;

  try {
    const res = await fetch("/api/v1/economy/market");
    const data = await res.json();

    let html = `
      <div class="card card-danger" style="margin-bottom:8px">
        <div style="font-size:10px;font-weight:700;color:var(--color-tertiary);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px">🚨 跨國地下匯兌</div>
        <div style="font-size:20px;font-family:var(--font-headline);font-weight:900;color:var(--color-on-surface)">
          保留率 <span style="color:var(--color-tertiary)">${(data.launder_rate * 100).toFixed(1)}%</span>
        </div>
        <div style="font-size:10px;color:var(--color-on-surface-dim);margin-top:4px">
          檢警查緝強度影響洗錢保留率。指令：<code style="color:var(--color-primary)">/launder &lt;金額&gt;</code>
        </div>
      </div>`;

    data.stocks.forEach(s => {
      const isUp = s.trend.includes("漲");
      const isDown = s.trend.includes("跌");
      const color = isUp ? "var(--color-tertiary)" : isDown ? "var(--color-primary)" : "var(--color-on-surface-dim)";
      html += `
        <div class="card" style="margin-bottom:4px;display:flex;justify-content:space-between;align-items:center;gap:8px">
          <div>
            <div style="font-weight:700;font-size:13px">${s.name}</div>
            <div style="font-size:9px;color:var(--color-on-surface-dim);font-family:monospace">${s.symbol}</div>
          </div>
          <div style="text-align:right">
            <div style="font-family:var(--font-headline);font-weight:700;font-size:15px">$${s.price.toLocaleString()}</div>
            <div style="font-size:10px;color:${color};font-weight:700">${s.trend}</div>
          </div>
        </div>`;
    });

    content.innerHTML = html;
  } catch (e) {
    content.innerHTML = `<p style="color:var(--color-tertiary);font-size:12px;padding:12px 0">⚠ 無法取得市場行情。</p>`;
  }
}

// ===== 幕僚個人資料 =====

/** 更新幕僚個人資料頁 */
async function updateProfileData() {
  if (!entityId) return;
  const content = document.getElementById("profile-content");
  if (!content) return;

  try {
    const res = await fetch(`/api/v1/entities/${entityId}/status`);
    if (!res.ok) { content.innerHTML = `<p style="color:var(--color-on-surface-dim);font-size:12px;padding:12px 0">讀取失敗</p>`; return; }
    const d = await res.json();

    content.innerHTML = `
      <div class="card" style="margin-bottom:8px">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
          <div style="width:40px;height:40px;border:2px solid var(--color-primary);display:flex;align-items:center;justify-content:center;font-family:var(--font-headline);font-size:18px;font-weight:900;color:var(--color-primary)">
            ${(d.name || "?").slice(0, 1)}
          </div>
          <div>
            <div style="font-family:var(--font-headline);font-weight:700;font-size:16px">${d.name || "未知"}</div>
            <div style="font-size:10px;color:var(--color-on-surface-dim)">${d.title || ""} · <span class="rank-badge badge-${d.party}">${d.party || ""}</span></div>
          </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-family:var(--font-headline)">
          <div class="card card-secondary" style="padding:10px;text-align:center">
            <div style="font-size:9px;color:var(--color-secondary);text-transform:uppercase;margin-bottom:4px">知名度</div>
            <div style="font-size:18px;font-weight:900;color:var(--color-secondary)">${(d.fame || 0).toLocaleString()}</div>
          </div>
          <div class="card" style="padding:10px;text-align:center">
            <div style="font-size:9px;color:var(--color-primary);text-transform:uppercase;margin-bottom:4px">好感度</div>
            <div style="font-size:18px;font-weight:900;color:var(--color-primary)">${(d.favorability || 0).toFixed(1)}</div>
          </div>
          <div class="card" style="padding:10px;text-align:center">
            <div style="font-size:9px;color:var(--color-on-surface-dim);text-transform:uppercase;margin-bottom:4px">政治獻金</div>
            <div style="font-size:14px;font-weight:900">$${(d.money || 0).toLocaleString()}</div>
          </div>
          <div class="card" style="padding:10px;text-align:center">
            <div style="font-size:9px;color:var(--color-on-surface-dim);text-transform:uppercase;margin-bottom:4px">行動力 AP</div>
            <div style="font-size:14px;font-weight:900">${d.ap || 0} / 100</div>
          </div>
        </div>
      </div>`;
  } catch (e) {
    content.innerHTML = `<p style="color:var(--color-tertiary);font-size:12px;padding:12px 0">⚠ 讀取幕僚資料失敗。</p>`;
  }
}

// CSS 震動動畫（動態注入）
const shakeStyle = document.createElement("style");
shakeStyle.textContent = `@keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-4px)} 75%{transform:translateX(4px)} }`;
document.head.appendChild(shakeStyle);

// ===== 啟動 =====
// NOTE: 頁面載入後不自動呼叫 LIFF，由使用者點擊按鈕觸發
// 這樣可以確保完整的 DOM 渲染後再執行
