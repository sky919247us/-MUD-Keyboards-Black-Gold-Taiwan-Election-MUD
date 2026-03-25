"""
遊戲靜態危機資料庫 (Crisis Database)
存放高達 50 種不同層級（S、A、B、C）的突發政治危機事件。
每個事件包含多個處理選項（耗費金錢、AP，並對好感度與仇恨值造成影響）。
"""

from typing import Any

# 分級說明：
# S 級（核彈級）：好感度懲罰極高（-3000 ~ -5000），仇恨極高，選項代價極高。
# A 級（全國性）：重大爭議事件（-1500 ~ -3000）。
# B 級（地方性）：中等爭議（-500 ~ -1500）。
# C 級（日常性）：日常公關小危機（-100 ~ -500）。

CRISIS_DB: list[dict[str, Any]] = [
    # ==========================
    # S 級危機 (核彈級，5 個)
    # ==========================
    {
        "id": "s_01",
        "tier": "S",
        "title": "⚡ 全國大停電與供電崩潰",
        "description": "備轉容量率跌破底線，連日高溫導致全國電網大規模崩潰。在野黨指控能源政策殺人，網路民怨全面沸騰，您的陣營遭到毀滅性打擊！",
        "options": [
            {"id": "opt1", "desc": "親自開直播鞠躬道歉並承諾賠償（耗 50 AP）", "cost_ap": 50, "cost_funds": 0, "effect_fav": -1000, "effect_aggro": 500},
            {"id": "opt2", "desc": "重金聘請側翼帶風向「是電網老舊非缺電」（耗 500 萬）", "cost_ap": 10, "cost_funds": 5000000, "effect_fav": -2000, "effect_aggro": 1500},
            {"id": "opt3", "desc": "裝死不回應（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -4000, "effect_aggro": 3000},
        ]
    },
    {
        "id": "s_02",
        "tier": "S",
        "title": "💦 防洪破功，暴雨導致市區淹水",
        "description": "連日豪雨導致市區大淹水，對手抓包淹水最嚴重的地方正是您引以為傲的「前瞻治水」示範區，甚至拍到擋土牆是用保麗龍做的！",
        "options": [
            {"id": "opt1", "desc": "穿青蛙裝親赴災區涉水勘災（耗 60 AP）", "cost_ap": 60, "cost_funds": 0, "effect_fav": -500, "effect_aggro": 200},
            {"id": "opt2", "desc": "花錢買下所有新聞版面壓新聞（耗 800 萬）", "cost_ap": 0, "cost_funds": 8000000, "effect_fav": -1000, "effect_aggro": 800},
            {"id": "opt3", "desc": "推給極端氣候（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": -3000, "effect_aggro": 2500},
        ]
    },
    {
        "id": "s_03",
        "tier": "S",
        "title": "💸 股市崩盤與無薪假風暴",
        "description": "受到國際局勢與國內政策失誤影響，台股單日重挫 5%，數家科技大廠宣布無薪假。選民將經濟恐慌的怒火全出在您身上！",
        "options": [
            {"id": "opt1", "desc": "緊急推出百億紓困方案（耗 30 AP，大灑幣）", "cost_ap": 30, "cost_funds": 10000000, "effect_fav": 500, "effect_aggro": 0},
            {"id": "opt2", "desc": "召開國安基金護盤記者會（耗 40 AP）", "cost_ap": 40, "cost_funds": 0, "effect_fav": -1500, "effect_aggro": 500},
            {"id": "opt3", "desc": "發布新聞稿「基本面良好」（耗 5 AP）", "cost_ap": 5, "cost_funds": 0, "effect_fav": -3500, "effect_aggro": 2000},
        ]
    },
    {
        "id": "s_04",
        "tier": "S",
        "title": "🧨 核心幕僚涉及重大貪瀆",
        "description": "週刊爆料，您最信任的核心幕僚被拍到深夜帶著現金出入不正當場所，並疑似收受建商數千萬回扣。司法已介入調查！",
        "options": [
            {"id": "opt1", "desc": "立刻揮淚斬馬謖，開除移送法辦（耗 30 AP）", "cost_ap": 30, "cost_funds": 0, "effect_fav": -800, "effect_aggro": 300},
            {"id": "opt2", "desc": "花錢請頂級律師團並反擊抹黑（耗 500 萬）", "cost_ap": 10, "cost_funds": 5000000, "effect_fav": -1500, "effect_aggro": 1500},
            {"id": "opt3", "desc": "力挺幕僚，高喊政治迫害（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -4500, "effect_aggro": 4000},
        ]
    },
    {
        "id": "s_05",
        "tier": "S",
        "title": "💀 網軍負責人名單外流",
        "description": "大型公關災難！您陣營底下的網軍群組截圖與 IP 名單全數外流，過去半年的抹黑操作全被起底，更被抓包反串對手粉絲！",
        "options": [
            {"id": "opt1", "desc": "低頭認錯，承諾解散網軍（耗 50 AP）", "cost_ap": 50, "cost_funds": 0, "effect_fav": -1500, "effect_aggro": 1000},
            {"id": "opt2", "desc": "砸大錢買一波更大的八卦轉移焦點（耗 800 萬）", "cost_ap": 0, "cost_funds": 8000000, "effect_fav": -500, "effect_aggro": 500},
            {"id": "opt3", "desc": "堅決否認，稱是遭到對手駭客偽造（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": -3500, "effect_aggro": 3500},
        ]
    },

    # ==========================
    # A 級危機 (全國級，15 個)
    # ==========================
    {
        "id": "a_01",
        "tier": "A",
        "title": "🌪️ 颱風假決策失準",
        "description": "鄰近縣市都放颱風假，唯獨您堅持「數據未達標」不放假。結果當天風雨交加，民眾通勤險象環生，臉書被憤怒表情灌爆。",
        "options": [
            {"id": "opt1", "desc": "緊急宣布下午停班停課並致歉（耗 30 AP）", "cost_ap": 30, "cost_funds": 0, "effect_fav": -800, "effect_aggro": 500},
            {"id": "opt2", "desc": "下廣告洗版「尊重氣象專業」（耗 200 萬）", "cost_ap": 0, "cost_funds": 2000000, "effect_fav": -1200, "effect_aggro": 1000},
            {"id": "opt3", "desc": "無視民怨，強調依法行政（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -2500, "effect_aggro": 2000},
        ]
    },
    {
        "id": "a_02",
        "tier": "A",
        "title": "😷 黑心食品廠護航風波",
        "description": "知名食品大廠爆出使用黑心原料，卻被踢爆該集團是您的金主，對手陣營痛批您「包庇奸商、毒害鄉親」。",
        "options": [
            {"id": "opt1", "desc": "親自帶隊查封工廠，展現鐵腕（耗 40 AP）", "cost_ap": 40, "cost_funds": 0, "effect_fav": -300, "effect_aggro": 200},
            {"id": "opt2", "desc": "退回該集團政治獻金並發聲明（耗 20 AP，退款 300 萬）", "cost_ap": 20, "cost_funds": 3000000, "effect_fav": -500, "effect_aggro": 300},
            {"id": "opt3", "desc": "冷處理，等待檢調結果（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -2000, "effect_aggro": 1500},
        ]
    },
    {
        "id": "a_03",
        "tier": "A",
        "title": "📉 民調數據異常暴跌",
        "description": "某具公信力的民調機構發布最新數據，您的支持度無預警暴跌 10%，陣營內部士氣低迷，金主開始觀望。",
        "options": [
            {"id": "opt1", "desc": "召開大型造勢晚會穩固基本盤（耗 20 AP，耗 300 萬）", "cost_ap": 20, "cost_funds": 3000000, "effect_fav": 200, "effect_aggro": 100},
            {"id": "opt2", "desc": "發布內參民調反擊「我們其實領先」（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": -500, "effect_aggro": 500},
            {"id": "opt3", "desc": "無作為，順其自然（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -1500, "effect_aggro": 200},
        ]
    },
    {
        "id": "a_04",
        "tier": "A",
        "title": "🗣️ 失言風波：歧視弱勢",
        "description": "在非公開行程中，您一句輕蔑弱勢族群的玩笑話被偷錄影上傳，引發全國道德撻伐，PTT 狂刷「下台」。",
        "options": [
            {"id": "opt1", "desc": "90度鞠躬道歉並捐款百萬（耗 30 AP，耗 100 萬）", "cost_ap": 30, "cost_funds": 1000000, "effect_fav": -500, "effect_aggro": 300},
            {"id": "opt2", "desc": "強調是「遭惡意剪接抹黑」（耗 20 AP）", "cost_ap": 20, "cost_funds": 0, "effect_fav": -1000, "effect_aggro": 1200},
            {"id": "opt3", "desc": "避風頭，取消三天行程（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -2000, "effect_aggro": 1000},
        ]
    },
    {
        "id": "a_05",
        "tier": "A",
        "title": "🏠 違建豪宅爭議",
        "description": "空拍機拍到您的老家竟然是超大違建，甚至佔用國有地。對手猛打「特權高官」，您的反貪腐人設面臨瓦解。",
        "options": [
            {"id": "opt1", "desc": "立刻派怪手自行拆除（耗 30 AP）", "cost_ap": 30, "cost_funds": 0, "effect_fav": -300, "effect_aggro": 200},
            {"id": "opt2", "desc": "捐出做公益信託（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": -800, "effect_aggro": 600},
            {"id": "opt3", "desc": "反擊對手也有違建（耗 15 AP，需花 100 萬網軍費）", "cost_ap": 15, "cost_funds": 1000000, "effect_fav": -1000, "effect_aggro": 1500},
        ]
    },
    {
        "id": "a_06",
        "tier": "A",
        "title": "🔥 消防安檢黑洞大火",
        "description": "市區鐵皮屋工廠發生大火，造成傷亡。調查發現該廠長年未過安檢卻沒被開罰，質疑您與地方派系利益交換。",
        "options": [
            {"id": "opt1", "desc": "慰問家屬並全市擴大安檢（耗 40 AP）", "cost_ap": 40, "cost_funds": 0, "effect_fav": -400, "effect_aggro": 100},
            {"id": "opt2", "desc": "撥款千萬賠償金平息眾怒（耗 5 AP，耗 1000 萬）", "cost_ap": 5, "cost_funds": 10000000, "effect_fav": -200, "effect_aggro": 50},
            {"id": "opt3", "desc": "將責任推給前朝政府的歷史共業（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": -1500, "effect_aggro": 1800},
        ]
    },
    {
        "id": "a_07",
        "tier": "A",
        "title": "🎭 論文抄襲疑雲",
        "description": "網友比對發現您的碩士論文重複率高達 40%，且多處錯字與他人一模一樣。母校組成學倫會準備調查。",
        "options": [
            {"id": "opt1", "desc": "主動退回學位止血（耗 20 AP）", "cost_ap": 20, "cost_funds": 0, "effect_fav": -600, "effect_aggro": 300},
            {"id": "opt2", "desc": "堅持原創，這是我自己寫的（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": -1200, "effect_aggro": 1500},
            {"id": "opt3", "desc": "全黨挺一人，動員網軍攻擊母校（耗 20 AP，花 200 萬）", "cost_ap": 20, "cost_funds": 2000000, "effect_fav": -2000, "effect_aggro": 2500},
        ]
    },
    {
        "id": "a_08",
        "tier": "A",
        "title": "😷 本土疫情/流感爆發，病床不足",
        "description": "流感重症激增，醫院塞爆，病床一床難求。民眾痛批醫療政策規劃不當，恐慌情緒蔓延。",
        "options": [
            {"id": "opt1", "desc": "坐鎮指揮中心，協調病床（耗 40 AP）", "cost_ap": 40, "cost_funds": 0, "effect_fav": -200, "effect_aggro": 100},
            {"id": "opt2", "desc": "緊急採購並發放醫療物資（耗 10 AP，花 300 萬）", "cost_ap": 10, "cost_funds": 3000000, "effect_fav": 100, "effect_aggro": 0},
            {"id": "opt3", "desc": "呼籲民眾不要恐慌，自主健康管理（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -1800, "effect_aggro": 1200},
        ]
    },
    {
        "id": "a_09",
        "tier": "A",
        "title": "🚌 重大交通事故，道路設計惹議",
        "description": "發生嚴重車禍，路權團體包圍市府，痛批某某路口設計是「行人地獄」，指責政府冷血不作為。",
        "options": [
            {"id": "opt1", "desc": "承諾一個月內改善百大危險路口（耗 30 AP，花 100 萬）", "cost_ap": 30, "cost_funds": 1000000, "effect_fav": -100, "effect_aggro": -100},
            {"id": "opt2", "desc": "加派警力大執法開罰單（耗 20 AP）", "cost_ap": 20, "cost_funds": 0, "effect_fav": -600, "effect_aggro": 800},
            {"id": "opt3", "desc": "僅表示「深表遺憾」無實質作為（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -1500, "effect_aggro": 1500},
        ]
    },
    {
        "id": "a_10",
        "tier": "A",
        "title": "💰 政治獻金假帳風雲",
        "description": "監察院公布政治獻金明細，發現您的陣營疑似虛報多筆高額「公關費」，甚至流入特定私人口袋。",
        "options": [
            {"id": "opt1", "desc": "召開記者會道歉，稱是會計登錄錯誤（耗 30 AP）", "cost_ap": 30, "cost_funds": 0, "effect_fav": -800, "effect_aggro": 500},
            {"id": "opt2", "desc": "花錢請律師團重新查帳（耗 10 AP，花 200 萬律師費）", "cost_ap": 10, "cost_funds": 2000000, "effect_fav": -400, "effect_aggro": 300},
            {"id": "opt3", "desc": "避重就輕，拒絕回應（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -2000, "effect_aggro": 1800},
        ]
    },
    {
        "id": "a_11",
        "tier": "A",
        "title": "🗑️ 垃圾掩埋場抗爭",
        "description": "計畫興建的新垃圾掩埋場引發當地鄉親誓死抵抗，抗議群眾包圍市府，甚至發生丟擲雞蛋的肢體衝突。",
        "options": [
            {"id": "opt1", "desc": "親自出面與自救會溝通協調（耗 40 AP）", "cost_ap": 40, "cost_funds": 0, "effect_fav": -300, "effect_aggro": -100},
            {"id": "opt2", "desc": "發放鉅額地方回饋金平息怒火（耗 10 AP，花 500 萬）", "cost_ap": 10, "cost_funds": 5000000, "effect_fav": 100, "effect_aggro": 0},
            {"id": "opt3", "desc": "強力清場，展現公權力（耗 20 AP）", "cost_ap": 20, "cost_funds": 0, "effect_fav": -1000, "effect_aggro": 2000},
        ]
    },
    {
        "id": "a_12",
        "tier": "A",
        "title": "🐾 動保悲歌，收容所爆發虐案",
        "description": "動保團體踢爆市府公立動物收容所環境惡劣，甚至發生不當人道處理，愛貓愛狗人士在網路上群起攻之。",
        "options": [
            {"id": "opt1", "desc": "嚴懲失職人員並升級收容所（耗 30 AP，花 300 萬）", "cost_ap": 30, "cost_funds": 3000000, "effect_fav": 100, "effect_aggro": -200},
            {"id": "opt2", "desc": "拍攝關懷毛小孩影片轉移焦點（耗 20 AP）", "cost_ap": 20, "cost_funds": 0, "effect_fav": -400, "effect_aggro": 500},
            {"id": "opt3", "desc": "認為只是小事不予理會（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -1500, "effect_aggro": 1800},
        ]
    },
    {
        "id": "a_13",
        "tier": "A",
        "title": "🏫 停辦偏鄉偏校引發抗議",
        "description": "為了節省預算，宣布裁併多所偏鄉小學，引發家長與教育團體反彈，被痛批「扼殺基層教育」。",
        "options": [
            {"id": "opt1", "desc": "暫緩裁撤，重新評估（耗 20 AP）", "cost_ap": 20, "cost_funds": 0, "effect_fav": -200, "effect_aggro": 100},
            {"id": "opt2", "desc": "提供專車補助與高額津貼（耗 10 AP，花 400 萬）", "cost_ap": 10, "cost_funds": 4000000, "effect_fav": -100, "effect_aggro": 50},
            {"id": "opt3", "desc": "堅持政策，強調財政紀律（耗 15 AP）", "cost_ap": 15, "cost_funds": 0, "effect_fav": -1200, "effect_aggro": 1500},
        ]
    },
    {
        "id": "a_14",
        "tier": "A",
        "title": "🔫 惡性槍擊案，治安亮紅燈",
        "description": "市區發生黑道當街開槍事件，民眾人心惶惶，對手嘲諷您的轄區是「慶記之都」。",
        "options": [
            {"id": "opt1", "desc": "雷厲風行大掃黑，連日夜檢（耗 40 AP）", "cost_ap": 40, "cost_funds": 0, "effect_fav": 200, "effect_aggro": -100},
            {"id": "opt2", "desc": "購買新聞版面宣傳除暴政績（耗 10 AP，花 200 萬）", "cost_ap": 10, "cost_funds": 2000000, "effect_fav": -400, "effect_aggro": 300},
            {"id": "opt3", "desc": "稱是單一偶發事件（耗 5 AP）", "cost_ap": 5, "cost_funds": 0, "effect_fav": -1500, "effect_aggro": 1200},
        ]
    },
    {
        "id": "a_15",
        "tier": "A",
        "title": "🚄 捷運/軌道工程大幅延宕",
        "description": "斥資百億的重大軌道工程宣布三度延宕，且預算嚴重超支，被譏笑為「世紀大錢坑」。",
        "options": [
            {"id": "opt1", "desc": "撤換工程局長並公開進度表（耗 30 AP）", "cost_ap": 30, "cost_funds": 0, "effect_fav": -500, "effect_aggro": 200},
            {"id": "opt2", "desc": "追加大筆預算趕工（耗 10 AP，花 800 萬本錢）", "cost_ap": 10, "cost_funds": 8000000, "effect_fav": -300, "effect_aggro": 400},
            {"id": "opt3", "desc": "推托是原物料大漲不可抗力（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -1800, "effect_aggro": 1500},
        ]
    },

    # ==========================
    # B 級危機 (地方級，15 個)
    # ==========================
    {
        "id": "b_01",
        "tier": "B",
        "title": "🎙️ 麥克風沒關的抱怨",
        "description": "您在行程空檔私下碎念選民「要求太多」，結果忘記關麥克風，片段被做成短影音瘋傳。",
        "options": [
            {"id": "opt1", "desc": "親自拍攝道歉短片化解（耗 20 AP）", "cost_ap": 20, "cost_funds": 0, "effect_fav": -200, "effect_aggro": 300},
            {"id": "opt2", "desc": "叫網軍洗出對手更難聽的話（耗 10 AP，花 100 萬）", "cost_ap": 10, "cost_funds": 1000000, "effect_fav": -400, "effect_aggro": 800},
            {"id": "opt3", "desc": "假裝沒這回事（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -800, "effect_aggro": 600},
        ]
    },
    {
        "id": "b_02",
        "tier": "B",
        "title": "💧 自來水混濁變黃",
        "description": "部分區域的自來水突然變成泥黃色，民眾哀聲載道，抱怨連洗澡都不敢洗。",
        "options": [
            {"id": "opt1", "desc": "馬上派水車送水與補償（耗 25 AP，花 50 萬）", "cost_ap": 25, "cost_funds": 500000, "effect_fav": 100, "effect_aggro": 0},
            {"id": "opt2", "desc": "要求自來水公司發布聲明澄清（耗 15 AP）", "cost_ap": 15, "cost_funds": 0, "effect_fav": -300, "effect_aggro": 200},
            {"id": "opt3", "desc": "這歸中央管，不關我的事（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -1000, "effect_aggro": 800},
        ]
    },
    {
        "id": "b_03",
        "tier": "B",
        "title": "🚗 違規停車被抓包",
        "description": "您的宣傳車大喇喇地併排停在紅線上買便當，被民眾拍照檢舉，質疑「只許州官放火」。",
        "options": [
            {"id": "opt1", "desc": "主動繳罰單並嚴厲要求司機（耗 15 AP）", "cost_ap": 15, "cost_funds": 0, "effect_fav": -100, "effect_aggro": 100},
            {"id": "opt2", "desc": "反嗆檢舉達人吃飽太閒（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": -500, "effect_aggro": 600},
            {"id": "opt3", "desc": "置之不理（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -400, "effect_aggro": 300},
        ]
    },
    {
        "id": "b_04",
        "tier": "B",
        "title": "🌳 粗暴修剪行道樹",
        "description": "市府工程單位將整排幾十年的行道樹「剃光頭」砍成電線桿，遭到文史與環保團體痛批。",
        "options": [
            {"id": "opt1", "desc": "承諾檢討修剪規範（耗 20 AP）", "cost_ap": 20, "cost_funds": 0, "effect_fav": -200, "effect_aggro": 100},
            {"id": "opt2", "desc": "花錢買業配文強調是防颱準備（耗 10 AP，花 80 萬）", "cost_ap": 10, "cost_funds": 800000, "effect_fav": -300, "effect_aggro": 300},
            {"id": "opt3", "desc": "為了安全考量，堅持沒錯（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": -600, "effect_aggro": 500},
        ]
    },
    {
        "id": "b_05",
        "tier": "B",
        "title": "📵 競選 App 資安漏洞",
        "description": "白帽駭客指出您的陣營推出的競選 App 存在漏洞，可能外洩支持者個資。",
        "options": [
            {"id": "opt1", "desc": "緊急下架修復並道歉（耗 25 AP）", "cost_ap": 25, "cost_funds": 0, "effect_fav": -200, "effect_aggro": 150},
            {"id": "opt2", "desc": "花重金請資安團隊立刻補牆（耗 5 AP，花 200 萬）", "cost_ap": 5, "cost_funds": 2000000, "effect_fav": 0, "effect_aggro": 0},
            {"id": "opt3", "desc": "淡化處理，稱是抹黑（耗 15 AP）", "cost_ap": 15, "cost_funds": 0, "effect_fav": -800, "effect_aggro": 700},
        ]
    },
    {
        "id": "b_06",
        "tier": "B",
        "title": "🏃 夜市拜票推擠衝突",
        "description": "您在夜市掃街時人潮過於擁擠，不慎推倒一個攤販的架子，被網友惡意剪輯成「囂張砸攤」。",
        "options": [
            {"id": "opt1", "desc": "回去找攤販親自賠償並握手言和（耗 25 AP）", "cost_ap": 25, "cost_funds": 0, "effect_fav": 100, "effect_aggro": -50},
            {"id": "opt2", "desc": "請幕僚代為拿錢處理（耗 10 AP，花 10 萬）", "cost_ap": 10, "cost_funds": 100000, "effect_fav": -200, "effect_aggro": 200},
            {"id": "opt3", "desc": "發新聞稿澄清是被人群推擠（耗 15 AP）", "cost_ap": 15, "cost_funds": 0, "effect_fav": -400, "effect_aggro": 400},
        ]
    },
    {
        "id": "b_07",
        "tier": "B",
        "title": "🍽️ 豪華宵夜引發相對剝奪感",
        "description": "您的 IG 限動發了一桌幾萬元的頂級和牛宵夜慰勞團隊，在經濟不景氣的當下引爆民眾怒火。",
        "options": [
            {"id": "opt1", "desc": "刪文並隨後吃平民小吃補救（耗 20 AP）", "cost_ap": 20, "cost_funds": 0, "effect_fav": -200, "effect_aggro": 300},
            {"id": "opt2", "desc": "花錢帶風向說對手吃得更好（耗 10 AP，花 50 萬）", "cost_ap": 10, "cost_funds": 500000, "effect_fav": -400, "effect_aggro": 500},
            {"id": "opt3", "desc": "嗆酸民「我花自己的錢不行嗎」（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": -900, "effect_aggro": 1000},
        ]
    },
    {
        "id": "b_08",
        "tier": "B",
        "title": "📅 錯過重要法會或公祭",
        "description": "地方上極為重要的宗教活動或大老公祭，您因為行程太滿未出席，引發地方耆老不滿。",
        "options": [
            {"id": "opt1", "desc": "隔日親自拜訪補致意（耗 25 AP）", "cost_ap": 25, "cost_funds": 0, "effect_fav": -100, "effect_aggro": 50},
            {"id": "opt2", "desc": "贊助大筆香油錢/奠儀（耗 5 AP，花 100 萬）", "cost_ap": 5, "cost_funds": 1000000, "effect_fav": 50, "effect_aggro": 0},
            {"id": "opt3", "desc": "派個無名小卒送花籃了事（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -600, "effect_aggro": 300},
        ]
    },
    {
        "id": "b_09",
        "tier": "B",
        "title": "🐕 隨扈驅離流浪狗引發公憤",
        "description": "您的隨扈在活動現場用腳踢開一隻靠近的親人流浪狗，被直播放送，動保人士群起圍攻。",
        "options": [
            {"id": "opt1", "desc": "震怒懲處隨扈並捐助動保協會（耗 20 AP，花 20 萬）", "cost_ap": 20, "cost_funds": 200000, "effect_fav": 100, "effect_aggro": -100},
            {"id": "opt2", "desc": "發聲明解釋是為了保護您的安全（耗 15 AP）", "cost_ap": 15, "cost_funds": 0, "effect_fav": -400, "effect_aggro": 400},
            {"id": "opt3", "desc": "無視（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -800, "effect_aggro": 800},
        ]
    },
    {
        "id": "b_10",
        "tier": "B",
        "title": "🏫 體育館燈光太暗",
        "description": "剛落成的體育館在舉辦首場籃球賽時，燈光昏暗且地板打滑，球員頻頻受傷，被球迷罵翻。",
        "options": [
            {"id": "opt1", "desc": "承諾停用並重新施工（耗 25 AP）", "cost_ap": 25, "cost_funds": 0, "effect_fav": -200, "effect_aggro": 100},
            {"id": "opt2", "desc": "逼迫承包商出來扛責（耗 15 AP）", "cost_ap": 15, "cost_funds": 0, "effect_fav": -400, "effect_aggro": 300},
            {"id": "opt3", "desc": "說是球員不適應場地（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": -900, "effect_aggro": 900},
        ]
    },
    {
        "id": "b_11",
        "tier": "B",
        "title": "🗑️ 宣傳品亂丟破壞環境",
        "description": "造勢大會結束後，滿地的傳單與旗幟未清理，遭環保局開罰，並被路過民眾拍照公審。",
        "options": [
            {"id": "opt1", "desc": "隔天自己帶頭去撿垃圾（耗 30 AP）", "cost_ap": 30, "cost_funds": 0, "effect_fav": 200, "effect_aggro": -100},
            {"id": "opt2", "desc": "花錢請清潔公司火速打掃（耗 5 AP，花 30 萬）", "cost_ap": 5, "cost_funds": 300000, "effect_fav": -100, "effect_aggro": 50},
            {"id": "opt3", "desc": "推給是不理性的支持者亂丟（耗 15 AP）", "cost_ap": 15, "cost_funds": 0, "effect_fav": -500, "effect_aggro": 400},
        ]
    },
    {
        "id": "b_12",
        "tier": "B",
        "title": "📝 發言人跳針，提油救火",
        "description": "您的發言人在政論節目上面對質疑，不斷「跳針」回答不相干的答案，被做成鬼畜影片全網嘲笑。",
        "options": [
            {"id": "opt1", "desc": "把發言人降職，換人止血（耗 20 AP）", "cost_ap": 20, "cost_funds": 0, "effect_fav": -200, "effect_aggro": 100},
            {"id": "opt2", "desc": "發動側翼攻擊政論節目不中立（耗 10 AP，花 80 萬）", "cost_ap": 10, "cost_funds": 800000, "effect_fav": -400, "effect_aggro": 600},
            {"id": "opt3", "desc": "出面力挺發言人（耗 15 AP）", "cost_ap": 15, "cost_funds": 0, "effect_fav": -600, "effect_aggro": 700},
        ]
    },
    {
        "id": "b_13",
        "tier": "B",
        "title": "🎵 競選歌曲爆抄襲",
        "description": "花重金請人寫的競選主題曲，被發現旋律幾乎 100% 抄襲某首外國冷門歌曲。",
        "options": [
            {"id": "opt1", "desc": "立即下架並向原作者道歉（耗 20 AP）", "cost_ap": 20, "cost_funds": 0, "effect_fav": -150, "effect_aggro": 100},
            {"id": "opt2", "desc": "火速花錢買下版權就地合法（耗 5 AP，花 200 萬）", "cost_ap": 5, "cost_funds": 2000000, "effect_fav": 0, "effect_aggro": 0},
            {"id": "opt3", "desc": "堅持是「致敬」與「巧合」（耗 15 AP）", "cost_ap": 15, "cost_funds": 0, "effect_fav": -700, "effect_aggro": 600},
        ]
    },
    {
        "id": "b_14",
        "tier": "B",
        "title": "🚧 廟會繞境交通大打結",
        "description": "特定勢力舉辦大型廟會，癱瘓市區交通數小時，民眾怨聲載道，要求政府管一管。",
        "options": [
            {"id": "opt1", "desc": "出面重申執法底線，開單取締（耗 25 AP）", "cost_ap": 25, "cost_funds": 0, "effect_fav": 200, "effect_aggro": 300},
            {"id": "opt2", "desc": "安撫民眾並贊助廟方交通指引經費（耗 15 AP，花 50 萬）", "cost_ap": 15, "cost_funds": 500000, "effect_fav": -100, "effect_aggro": -50},
            {"id": "opt3", "desc": "不敢得罪廟方，裝死不管（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -600, "effect_aggro": 400},
        ]
    },
    {
        "id": "b_15",
        "tier": "B",
        "title": "📸 後援會送高價贈品疑賄選",
        "description": "某區後援會在活動中發放價值超過 30 元的精美保溫瓶，疑似踩到賄選紅線，檢警放話要查。",
        "options": [
            {"id": "opt1", "desc": "緊急切割，稱是熱心民眾個人行為（耗 20 AP）", "cost_ap": 20, "cost_funds": 0, "effect_fav": -300, "effect_aggro": 200},
            {"id": "opt2", "desc": "花律師費硬拗那是文宣品（耗 10 AP，花 150 萬）", "cost_ap": 10, "cost_funds": 1500000, "effect_fav": -400, "effect_aggro": 400},
            {"id": "opt3", "desc": "嗆檢警是政治辦案（耗 15 AP）", "cost_ap": 15, "cost_funds": 0, "effect_fav": -700, "effect_aggro": 800},
        ]
    },

    # ==========================
    # C 級危機 (日常公關級，15 個)
    # ==========================
    {
        "id": "c_01",
        "tier": "C",
        "title": "📱 臉書小編打錯字",
        "description": "粉絲專頁貼文把地名打錯，被在地人狂虧「到底有沒有來過我們這裡？」",
        "options": [
            {"id": "opt1", "desc": "罰小編抄寫一百遍並搞笑道歉（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": 50, "effect_aggro": 0},
            {"id": "opt2", "desc": "默默修改裝沒事（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -50, "effect_aggro": 0},
            {"id": "opt3", "desc": "怪輸入法不好用（耗 5 AP）", "cost_ap": 5, "cost_funds": 0, "effect_fav": -150, "effect_aggro": 100},
        ]
    },
    {
        "id": "c_02",
        "tier": "C",
        "title": "👕 選舉背心穿反",
        "description": "跑行程太累，被拍到選舉背心穿反，名字在背後，前面空空如也，有點滑稽。",
        "options": [
            {"id": "opt1", "desc": "順水推舟拍短影音自嘲（耗 15 AP）", "cost_ap": 15, "cost_funds": 0, "effect_fav": 100, "effect_aggro": -50},
            {"id": "opt2", "desc": "置之不理（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": 0, "effect_aggro": 0},
            {"id": "opt3", "desc": "怒罵幕僚沒提醒（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": -200, "effect_aggro": 150},
        ]
    },
    {
        "id": "c_03",
        "tier": "C",
        "title": "😴 議會/會議打瞌睡",
        "description": "在冗長的會議中閉目養神，不巧被對手拍到放網路上說您「睡相難看」。",
        "options": [
            {"id": "opt1", "desc": "坦承太累，順勢公佈魔鬼行程表（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": 50, "effect_aggro": 0},
            {"id": "opt2", "desc": "花錢請網軍洗對手也在滑手機的圖（耗 5 AP，花 20 萬）", "cost_ap": 5, "cost_funds": 200000, "effect_fav": -50, "effect_aggro": 50},
            {"id": "opt3", "desc": "硬辯說是在「閉目沉思」（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": -150, "effect_aggro": 150},
        ]
    },
    {
        "id": "c_04",
        "tier": "C",
        "title": "🎤 唱歌大走音",
        "description": "參加社區聯歡晚會被拱上台高歌一曲，結果五音不全大走音，觀眾笑成一片。",
        "options": [
            {"id": "opt1", "desc": "幽默以對，搏君一笑（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": 150, "effect_aggro": -50},
            {"id": "opt2", "desc": "推脫是麥克風設備太差（耗 5 AP）", "cost_ap": 5, "cost_funds": 0, "effect_fav": -100, "effect_aggro": 50},
            {"id": "opt3", "desc": "下次帶專業伴唱帶去（花 5 萬買設備）", "cost_ap": 0, "cost_funds": 50000, "effect_fav": 50, "effect_aggro": 0},
        ]
    },
    {
        "id": "c_05",
        "tier": "C",
        "title": "🍔 吃播挑食被發現",
        "description": "在推廣在地美食的直播中，被眼尖網友發現悄悄把香菜挑掉，惹怒「香菜派」選民。",
        "options": [
            {"id": "opt1", "desc": "開玩笑說這是宗教信仰問題（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": 50, "effect_aggro": 0},
            {"id": "opt2", "desc": "不理會，無聊當有趣（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -50, "effect_aggro": 50},
            {"id": "opt3", "desc": "發起「反香菜聯盟」企劃對決（耗 15 AP）", "cost_ap": 15, "cost_funds": 0, "effect_fav": 100, "effect_aggro": 50},
        ]
    },
    {
        "id": "c_06",
        "tier": "C",
        "title": "🏃 晨跑被超越",
        "description": "您標榜體力過人去晨跑，卻被一位推著嬰兒車的阿嬤輕鬆超車，照片成了今天的熱門搞笑圖。",
        "options": [
            {"id": "opt1", "desc": "發文大讚在地長輩活力充沛（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": 100, "effect_aggro": -20},
            {"id": "opt2", "desc": "請小編刪除不利留言（耗 5 AP，花 5 萬）", "cost_ap": 5, "cost_funds": 50000, "effect_fav": -50, "effect_aggro": 100},
            {"id": "opt3", "desc": "裝作沒事（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -50, "effect_aggro": 0},
        ]
    },
    {
        "id": "c_07",
        "tier": "C",
        "title": "🤝 握手被冷落",
        "description": "菜市場拜票時，遇到一位不爽您的攤商，伸出手被對方無視，場面略顯尷尬。",
        "options": [
            {"id": "opt1", "desc": "微笑縮回手，繼續拜訪下一攤（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": 50, "effect_aggro": 0},
            {"id": "opt2", "desc": "事後派幕僚去買東西捧場（耗 5 AP，花 2 萬）", "cost_ap": 5, "cost_funds": 20000, "effect_fav": 80, "effect_aggro": 0},
            {"id": "opt3", "desc": "背地裡擺臭臉被拍到（耗 5 AP）", "cost_ap": 5, "cost_funds": 0, "effect_fav": -150, "effect_aggro": 200},
        ]
    },
    {
        "id": "c_08",
        "tier": "C",
        "title": "🗣️ 叫錯樁腳名字",
        "description": "在一場地方晚宴上，您敬酒時把重要的里長名字叫錯，惹得對方有些不高興。",
        "options": [
            {"id": "opt1", "desc": "當場喝罰酒三杯賠罪（耗 15 AP）", "cost_ap": 15, "cost_funds": 0, "effect_fav": 50, "effect_aggro": -20},
            {"id": "opt2", "desc": "隔天送上一籃高級水果（耗 5 AP，花 5 萬）", "cost_ap": 5, "cost_funds": 50000, "effect_fav": 20, "effect_aggro": 0},
            {"id": "opt3", "desc": "覺得只是一件小事沒補救（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": -150, "effect_aggro": 100},
        ]
    },
    {
        "id": "c_09",
        "tier": "C",
        "title": "🐕 抱別人的小孩爆哭",
        "description": "為了展現親和力去抱路邊的小嬰兒，結果小孩當場被嚇顇大哭，您手足無措的樣子被截圖。",
        "options": [
            {"id": "opt1", "desc": "轉發截圖自嘲「我長得有這麼恐怖嗎」（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": 100, "effect_aggro": 0},
            {"id": "opt2", "desc": "默默把貼文照片拿掉（耗 5 AP）", "cost_ap": 5, "cost_funds": 0, "effect_fav": -50, "effect_aggro": 50},
            {"id": "opt3", "desc": "責怪幕僚安排不當（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": -150, "effect_aggro": 150},
        ]
    },
    {
        "id": "c_10",
        "tier": "C",
        "title": "☕ 說錯流行語",
        "description": "為了貼近年輕人，在演講中硬塞了個網路流行語，結果用語完全顛倒，反倒成了老人笑話。",
        "options": [
            {"id": "opt1", "desc": "上 Threads 虛心求教正確用法（耗 15 AP）", "cost_ap": 15, "cost_funds": 0, "effect_fav": 120, "effect_aggro": 0},
            {"id": "opt2", "desc": "花錢請網紅合作洗刷老人味（耗 10 AP，花 30 萬）", "cost_ap": 10, "cost_funds": 300000, "effect_fav": 80, "effect_aggro": 0},
            {"id": "opt3", "desc": "堅持自己說的才是對的（耗 5 AP）", "cost_ap": 5, "cost_funds": 0, "effect_fav": -100, "effect_aggro": 100},
        ]
    },
    {
        "id": "c_11",
        "tier": "C",
        "title": "🌧️ 致詞遇到大雨傘壞掉",
        "description": "在戶外致詞時傾盆大雨，傘剛好被怪風吹壞，您淋成落湯雞。",
        "options": [
            {"id": "opt1", "desc": "索性不撐傘，淋雨把話講完（耗 20 AP）", "cost_ap": 20, "cost_funds": 0, "effect_fav": 200, "effect_aggro": -50},
            {"id": "opt2", "desc": "中斷演講躲雨（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": -100, "effect_aggro": 50},
            {"id": "opt3", "desc": "叫幕僚用身體幫忙擋雨（耗 5 AP）", "cost_ap": 5, "cost_funds": 0, "effect_fav": -250, "effect_aggro": 300},
        ]
    },
    {
        "id": "c_12",
        "tier": "C",
        "title": "📸 現實驗證失敗的 P 圖",
        "description": "競選總部發布您視察工地的照片，被抓包陰影方向不對，明顯是合成圖。",
        "options": [
            {"id": "opt1", "desc": "承認小編偷懶，馬上補去現場直播（耗 25 AP）", "cost_ap": 25, "cost_funds": 0, "effect_fav": 50, "effect_aggro": 50},
            {"id": "opt2", "desc": "怪罪給委外設計公司（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": -150, "effect_aggro": 200},
            {"id": "opt3", "desc": "死不承認，狂刪留言（耗 15 AP，花 10 萬洗版）", "cost_ap": 15, "cost_funds": 100000, "effect_fav": -250, "effect_aggro": 400},
        ]
    },
    {
        "id": "c_13",
        "tier": "C",
        "title": "🐶 抱競選吉祥物跌倒",
        "description": "想抱起穿著布偶裝的競選吉祥物造勢，結果重心不穩兩個人一起摔在台上。",
        "options": [
            {"id": "opt1", "desc": "發限動自己做梗圖「仆街也要和你在一起」（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": 150, "effect_aggro": 0},
            {"id": "opt2", "desc": "笑笑拍拍灰塵站起來繼續（耗 5 AP）", "cost_ap": 5, "cost_funds": 0, "effect_fav": 50, "effect_aggro": 0},
            {"id": "opt3", "desc": "臉色大變，對布偶裝工作人員發脾氣（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": -300, "effect_aggro": 400},
        ]
    },
    {
        "id": "c_14",
        "tier": "C",
        "title": "🚗 拜票迷路繞遠路",
        "description": "車隊掃街因為司機不熟路況開進死胡同，進退兩難被路人看笑話。",
        "options": [
            {"id": "opt1", "desc": "直接下車步行拜訪該巷弄住戶（耗 25 AP）", "cost_ap": 25, "cost_funds": 0, "effect_fav": 150, "effect_aggro": -20},
            {"id": "opt2", "desc": "尷尬迴車，默默離開（耗 10 AP）", "cost_ap": 10, "cost_funds": 0, "effect_fav": -50, "effect_aggro": 20},
            {"id": "opt3", "desc": "大聲責罵司機找包（耗 5 AP）", "cost_ap": 5, "cost_funds": 0, "effect_fav": -200, "effect_aggro": 250},
        ]
    },
    {
        "id": "c_15",
        "tier": "C",
        "title": "🍟 消夜文惹公憤",
        "description": "半夜一點發出超罪惡炸雞排消夜文，引發飢餓網民強烈抗議！",
        "options": [
            {"id": "opt1", "desc": "祭出大絕：週末舉辦雞排免費發送會（耗 10 AP，花 20 萬）", "cost_ap": 10, "cost_funds": 200000, "effect_fav": 250, "effect_aggro": 0},
            {"id": "opt2", "desc": "與網民互動鬥嘴（耗 15 AP）", "cost_ap": 15, "cost_funds": 0, "effect_fav": 100, "effect_aggro": 0},
            {"id": "opt3", "desc": "不管他們繼續吃（無消耗）", "cost_ap": 0, "cost_funds": 0, "effect_fav": 0, "effect_aggro": 0},
        ]
    }
]
