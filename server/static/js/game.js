        let currentWarRoomTab = 'rank';

        function openEconomy() {
            document.getElementById('economyModal').style.display = 'flex';
            updateEconomyData();
        }

        function closeEconomy() {
            document.getElementById('economyModal').style.display = 'none';
        }

        async function updateEconomyData() {
            const content = document.getElementById('economy-content');
            try {
                const res = await fetch('/api/v1/economy/market');
                const data = await res.json();
                
                let html = `
                    <div style="background:#222; padding:15px; border-radius:8px;">
                        <h3 style="margin-top:0; color:#e74c3c;">🚨 跨國地下匯兌</h3>
                        <div style="font-size:1.2em; margin-bottom:10px;">當前洗錢保留率：<span style="color:#f1c40f; font-weight:bold;">${(data.launder_rate * 100).toFixed(1)}%</span></div>
                        <p style="color:#aaa; font-size:0.9em; line-height:1.4;">指令：<code>/launder &lt;金額&gt;</code><br>將非法黑金透過人頭帳戶洗白。保留率越低代表檢警查緝越緊，洗錢失敗遭沒收的機率大幅提升！</p>
                    </div>
                    
                    <div style="background:#222; padding:15px; border-radius:8px; flex:1;">
                        <h3 style="margin-top:0; color:#3498db;">📈 百大集團概念股</h3>
                        <p style="color:#aaa; font-size:0.9em; margin-bottom:15px;">指令：<code>/invest buy|sell &lt;代號&gt; &lt;股數&gt;</code></p>
                        <div style="display:flex; flex-direction:column; gap:10px;">
                `;
                
                data.stocks.forEach(s => {
                    const trendColor = s.trend.includes("漲") ? "#e74c3c" : s.trend.includes("跌") ? "#2ecc71" : "#aaa";
                    html += `
                        <div style="display:flex; justify-content:space-between; align-items:center; background:#333; padding:12px; border-radius:6px; border-left:4px solid ${trendColor};">
                            <div>
                                <div style="font-weight:bold; font-size:1.1em;">${s.name}</div>
                                <div style="font-size:0.8em; color:#888;">代號: ${s.symbol}</div>
                            </div>
                            <div style="text-align:right;">
                                <div style="font-size:1.2em; font-weight:bold;">$${s.price.toLocaleString()}</div>
                                <div style="font-size:0.9em; color:${trendColor};">${s.trend}</div>
                            </div>
                        </div>
                    `;
                });
                
                html += `</div></div>`;
                content.innerHTML = html;
            } catch (e) {
                content.innerHTML = '<p style="color:red;">通訊中斷，無法取得市場行情。</p>';
            }
        }

        function openWarRoom() {
            document.getElementById('warroomModal').style.display = 'block';
            updateWarRoomData();
        }

        function closeWarRoom() {
            document.getElementById('warroomModal').style.display = 'none';
        }

        function switchWarRoomTab(tab) {
            currentWarRoomTab = tab;
            const btns = document.querySelectorAll('.tab-btn');
            btns.forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
            updateWarRoomData();
        }

        async function updateWarRoomData() {
            const content = document.getElementById('warroom-content');
            content.innerHTML = '<p>同步衛星數據中...</p>';

            try {
                if (currentWarRoomTab === 'rank') {
                    const res = await fetch('/api/v1/leaderboard');
                    const data = await res.json();
                    let html = '<div style="font-weight:bold; padding-bottom:10px;">🏆 全國聲量前 10 強</div>';
                    data.forEach((e, i) => {
                        html += `
                            <div class="data-row">
                                <div style="width:30px; color:#aaa;">#${i+1}</div>
                                <div style="flex:1">
                                    <span class="party-tag tag-${e.party}">${e.party}</span>
                                    <span style="font-weight:bold;">${e.name}</span>
                                    <span style="font-size:0.8em; color:#888;">| ${e.title}</span>
                                </div>
                                <div style="color:var(--primary-color); font-weight:bold;">${e.fame.toLocaleString()}</div>
                            </div>
                        `;
                    });
                    content.innerHTML = html;
                } else {
                    const res = await fetch('/api/v1/world/status');
                    const data = await res.json();
                    let html = '<div style="font-weight:bold; padding-bottom:10px;">🗺️ 區域領先勢力 (知名度統計)</div>';
                    for (const [region, info] of Object.entries(data)) {
                        html += `
                            <div class="data-row">
                                <div style="width:80px; font-weight:bold;">${region}</div>
                                <div style="flex:1">
                                    <span class="party-tag tag-${info.leading_party}">${info.leading_party} 領跑</span>
                                </div>
                                <div style="font-size:0.9em; color:#aaa;">總量 ${info.total_fame.toLocaleString()}</div>
                            </div>
                        `;
                    }
                    content.innerHTML = html;
                }
            } catch (e) {
                content.innerHTML = '<p style="color:red;">通訊中斷，無法取得選情資訊。</p>';
            }
        }

        // --- 全域變數 ---
        const LIFF_ID = "2009558875-PiJYcJDN"; 
        let userId = null;
        let ws = null;
        let selectedParty = null;

        // UI 元素
        const screenLoading = document.getElementById('screen-loading');
        const screenCreation = document.getElementById('screen-creation');
        const screenGame = document.getElementById('screen-game');
        const output = document.getElementById('output');
        const partyList = document.getElementById('party-list');
        const btnCreateRole = document.getElementById('btn-create-role');

        // --- PWA Service Worker 註冊 ---
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/sw.js')
                .then(reg => console.log('SW registered!', reg))
                .catch(err => console.error('SW failed', err));
        }

        // --- 啟動與登入流程 ---
        async function initializeApp() {
            try {
                // 🚧 本機開發測試用：繞過 LIFF 登入
                userId = "dev_user_001";
                appendMsg(`[系統] 開發模式：已繞過 LINE 登入。UID: ${userId}`, 'system');
                checkCharacterData(userId);

                /* 原本的 LIFF 登入邏輯先註解保留
                await liff.init({ liffId: LIFF_ID });
                if (liff.isLoggedIn()) {
                    const profile = await liff.getProfile();
                    userId = profile.userId;
                    appendMsg(`[系統] 已透過 LINE 登入：${profile.displayName}`, 'system');
                    checkCharacterData(userId);
                } else {
                    liff.login();
                }
                */
            } catch (err) {
                console.error("LIFF Init error", err);
                appendMsg("LIFF 初始化失敗，請在 LINE 中開啟", "error");
            }
        }

        async function checkCharacterData(uid) {
            // 呼叫後端 API 檢查是否已有角色
            try {
                const res = await fetch(`/api/v1/user/${uid}/character`);
                if (res.status === 404) {
                    showCreationScreen();
                } else if (res.ok) {
                    const data = await res.json();
                    enterGame(data.entityId);
                } else {
                    alert("取得角色資料失敗");
                }
            } catch (e) {
                console.error("API error", e);
                // 開發階段 fallback
                showCreationScreen();
            }
        }

        // --- 畫面切換 ---
        function showCreationScreen() {
            screenLoading.style.display = 'none';
            screenCreation.style.display = 'block';
            loadParties();
        }

        async function loadParties() {
            // 從後端拉取 7 大政黨
            try {
                const res = await fetch('/api/v1/parties');
                const parties = await res.json();
                
                partyList.innerHTML = '';
                parties.forEach(p => {
                    const div = document.createElement('div');
                    div.className = 'party-card';
                    div.innerHTML = `<div class="party-title">${p.name}（${p.shortName}）</div><div style="font-size:0.9em;color:#aaa">${p.realWorldRef}</div>`;
                    div.onclick = () => selectParty(div, p.code);
                    partyList.appendChild(div);
                });
            } catch (e) {
                console.error("Failed to load parties", e);
            }
        }

        function selectParty(element, code) {
            document.querySelectorAll('.party-card').forEach(el => el.classList.remove('selected'));
            element.classList.add('selected');
            selectedParty = code;
            btnCreateRole.style.display = 'block';
        }

        btnCreateRole.onclick = async () => {
            if (!selectedParty) return;
            btnCreateRole.disabled = true;
            btnCreateRole.textContent = "資料生成中...";

            try {
                const res = await fetch(`/api/v1/user/${userId}/create_character`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ party_code: selectedParty })
                });
                
                if (res.ok) {
                    const data = await res.json();
                    alert(`✅ 身分指派成功！\n\n你是 ${data.boss_name} 的 ${data.role_title}\n陣營：${data.party_name}`);
                    enterGame(data.entityId);
                } else {
                    alert("角色建立失敗");
                    btnCreateRole.disabled = false;
                    btnCreateRole.textContent = "確定陣營，抽取身分";
                }
            } catch (e) {
                console.error("Create error", e);
            }
        };

        // --- 遊戲介面與 WebSocket ---
        let trendingChart = null;

        async function updateTrendingChart(eid) {
            try {
                const res = await fetch(`/api/v1/entities/${eid}/history`);
                if (!res.ok) return;
                const data = await res.json();
                
                if (!trendingChart) {
                    const ctx = document.getElementById('trendingChart').getContext('2d');
                    trendingChart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: data.labels.map(l => `Tick ${l}`),
                            datasets: [
                                {
                                    label: '知名度',
                                    data: data.fame,
                                    borderColor: '#00ff41',
                                    tension: 0.3,
                                    borderWidth: 2,
                                    pointRadius: 0
                                },
                                {
                                    label: '好感度',
                                    data: data.favorability,
                                    borderColor: '#ffdd00',
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
                                y: {
                                    beginAtZero: false,
                                    grid: { color: '#333' }
                                },
                                x: {
                                    grid: { display: false }
                                }
                            },
                            plugins: {
                                legend: {
                                    display: true,
                                    labels: { color: '#fff', boxWidth: 10 }
                                }
                            }
                        }
                    });
                } else {
                    trendingChart.data.labels = data.labels.map(l => `Tick ${l}`);
                    trendingChart.data.datasets[0].data = data.fame;
                    trendingChart.data.datasets[1].data = data.favorability;
                    trendingChart.update('none'); // 使用無動畫更新以節省效能
                }
            } catch (e) {
                console.error("Chart update error", e);
            }
        }

        function showNewsFlash(text) {
            const marquee = document.getElementById('news-marquee');
            const newsText = document.getElementById('news-text');
            newsText.innerText = text;
            marquee.style.display = 'flex';
            
            // 震動特效
            document.body.classList.add('shake-effect');
            setTimeout(() => document.body.classList.remove('shake-effect'), 500);

            // 5秒後自動隱藏
            setTimeout(() => {
                marquee.style.display = 'none';
            }, 8000);
        }

        async function enterGame(eid) {
            screenLoading.style.display = 'none';
            screenCreation.style.display = 'none';
            screenGame.style.display = 'flex';
            
            // 取得 WebSocket Token
            let token = "";
            try {
                const tokenRes = await fetch(`/api/v1/user/${userId}/token`);
                if (tokenRes.ok) {
                    const tokenData = await tokenRes.json();
                    token = tokenData.token;
                } else {
                    appendMsg("警告：無法取得身分 Token，連線可能會被伺服器拒絕。", "error");
                }
            } catch (e) {
                console.error("Token fetch error", e);
            }
            
            // 啟動 WebSocket
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws/${eid}`);
            
            ws.onopen = () => {
                // 第一幀傳送 Token 進行身分驗證
                ws.send(JSON.stringify({ type: "auth", token: token }));
                appendMsg('連線穩定，加密通道已立。', 'system');
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
                    }
                } catch(e) {
                    appendMsg(event.data);
                }
            };

            ws.onclose = () => {
                appendMsg("[系統] 連線已中斷，請重新整理頁面。", "error");
            };

            // 啟動圖表輪詢 (Phase 7)
            updateTrendingChart(eid);
            setInterval(() => updateTrendingChart(eid), 30000);
        }

        function sendAction(cmd, label) {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                appendMsg('連線錯誤', 'error');
                return;
            }

            if (cmd === '/attack') {
                const target = prompt("⚔ 網軍出征\n請輸入你要攻擊的對手陣營或候選人名稱：");
                if (!target) return;
                cmd = `/attack ${target}`;
            } else if (cmd === '/flip') {
                const target = prompt("🤝 拔樁行動\n請輸入對手名稱：");
                if (!target) return;
                const bossId = prompt("請輸入欲策反的樁腳ID：");
                if (!bossId) return;
                cmd = `/flip ${target} ${bossId}`;
            }

            if (label) {
                appendMsg(`> 執行行動：[${label}]`, 'system');
            } else {
                appendMsg(`> ${cmd}`, 'system');
            }
            
            ws.send(cmd);
        }

        function appendMsg(text, cls) {
            const div = document.createElement('div');
            
            // 系統自動語意標記 (戰情室特效)
            if (!cls) {
                if (text.includes("🚨") || text.includes("⚠") || text.includes("⛈")) {
                    cls = "msg-alert";
                    // 天災發生：全螢幕震動
                    document.body.classList.add('shake-effect');
                    setTimeout(() => document.body.classList.remove('shake-effect'), 400);
                } else if (text.includes("【網軍") || text.includes("【拔樁")) {
                    cls = "msg-combat";
                    // 戰鬥事件：受擊紅光閃爍
                    document.body.classList.add('hit-flash');
                    setTimeout(() => document.body.classList.remove('hit-flash'), 300);
                } else if (text.includes("🛡️") || text.includes("❌")) {
                    cls = "msg-combat";
                } else if (text.includes("[Tick]")) {
                    cls = "msg-tick";
                }
            }

            if (cls) div.className = cls;
            
            // 支援基本的多行換行
            div.innerHTML = text.replace(/\n/g, "<br>");
            output.appendChild(div);
            // 捲動到底部
            setTimeout(() => {
                output.scrollTop = output.scrollHeight;
            }, 50);
        }

        // 啟動
        initializeApp();

