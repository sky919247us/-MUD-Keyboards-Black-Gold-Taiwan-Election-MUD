"""
遊戲靜態語料庫 (Mock Database)
當沒有 AI 連線，或使用快速 API 時，提供隨機且豐富的台灣選舉情境文本。
支援 Python f-string 格式的變數替換，如 {attacker}, {defender}, {action}, {name}, {boss_region} 等。
"""

import random

# ==========================================
# 📺 新聞快訊標題庫
# ==========================================

# --- 戰鬥成功 (20 條) ---
NEWS_TITLES_COMBAT_SUCCESS = [
    "【獨家】{attacker} 網軍發威！{defender} 粉絲專頁遭海量留言灌爆",
    "【快訊】選情大地震！{attacker} 側翼猛攻，{defender} 陣營急切割被抓包",
    "【震驚】PTT 炎上！{defender} 遭爆黑料，{attacker} 民調看漲？",
    "【內幕】{defender} 苦吞敗仗！{attacker} 空戰部隊勢如破竹",
    "【選戰焦點】{attacker} 網軍帶風向成功！{defender} 發言人結巴回應",
    "【直擊】網路上吵成一團！{attacker} 粉絲狂攻，{defender} 宣傳車遭蛋洗",
    "【快報】{defender} 聲量暴跌！{attacker} 側翼粉專連夜趕工狂做梗圖",
    "【獨家解析】{attacker} 網軍大戰全勝！{defender} 網路好感度崩盤",
    "【爆料】{attacker} 出重手！{defender} 過去言論遭挖出，網軍狂洗版",
    "【選戰秘辛】{defender} 遭網路霸凌？{attacker} 陣營否認操作側翼",
    "【獨家】網路戰開打！{attacker} 網軍攻勢猛烈，{defender} 無力招架",
    "【突發】{defender} 粉專被灌爆！{attacker} 網軍發動聯合攻擊",
    "【熱門新聞】{attacker} 網路戰傳捷報！{defender} 支持度重挫",
    "【選情報導】{attacker} 側翼發威！{defender} 深陷公關危機",
    "【焦點觀察】{defender} 遭網軍夾擊！{attacker} 陣營暗自竊喜",
    "【快訊】{attacker} 網紅助陣！{defender} 網路好感度雪崩式下滑",
    "【獨家直擊】{defender} 競總氣氛低迷！{attacker} 網軍攻勢讓對手吃不消",
    "【選戰解析】{attacker} 網路戰略奏效！{defender} 遭邊緣化",
    "【突發事件】{defender} 發言人崩潰！{attacker} 網軍留言攻勢太驚人",
    "【熱門焦點】{attacker} 網軍戰力驚人！{defender} 網路聲量敬陪末座",
]

# --- 戰鬥失敗 (20 條) ---
NEWS_TITLES_COMBAT_FAIL = [
    "【翻車現場】{attacker} 網軍被抓包！同 IP 猛發文遭 PTT 鄉民起底",
    "【快訊】糗了！{attacker} 側翼帶風向失敗，反成網路笑柄",
    "【選戰花絮】{attacker} 攻擊指令下錯？網軍出征竟迷路，{defender} 發文嘲諷",
    "【獨家】偷雞不著蝕把米！{attacker} 抹黑文遭秒打臉，防彈衣竟是厚臉皮",
    "【熱門】{attacker} 網軍大型翻車！{defender} 支持者反串成功",
    "【焦點新聞】{attacker} 網軍預算打水漂？攻擊 {defender} 毫無成效",
    "【獨家調查】{attacker} 網軍戰力被高估？{defender} 網路好感度不降反升",
    "【快報】{attacker} 側翼粉專遭檢舉停權！{defender} 陣營大聲叫好",
    "【選戰笑料】{attacker} 網軍迷路跑到自己人粉專留言！{defender} 笑而不語",
    "【內幕】{attacker} 網軍操盤手引咎辭職！攻擊 {defender} 徹底失敗",
    "【獨家快訊】{attacker} 網軍 IP 來自國外？遭批認知作戰翻車",
    "【熱門話題】{attacker} 側翼帶風向惹怒中間選民！{defender} 漁翁得利",
    "【選戰焦點】{attacker} 網軍攻擊力零！{defender} 支持者冷嘲熱諷",
    "【突發】{attacker} 內部群組流出！網軍帶風向指令曝光，引發譁然",
    "【獨家報導】{attacker} 網路戰略失靈！{defender} 展現強大路人防禦力",
    "【選情快遞】{attacker} 側翼粉專小編崩潰！留言全被 {defender} 粉絲洗版",
    "【焦點人物】{attacker} 網軍戰鬥力低落遭質疑！{defender} 老神在在",
    "【快報】{attacker} 網軍出征卻變笑話！{defender} 粉絲製作迷因圖瘋傳",
    "【獨家內幕】{attacker} 網軍預算去哪了？攻擊 {defender} 毫無水花",
    "【熱搜新聞】{attacker} 網軍大型車禍現場！{defender} 陣營趁機狂發文",
]

# --- 拔樁成功 (20 條) ---
NEWS_TITLES_FLIP_SUCCESS = [
    "【選戰核彈】拔樁成功！{defender} 鐵票倉鬆動，{boss_region} 樁腳轉投 {attacker}",
    "【快訊】基層大地震！{boss_region} 意見領袖倒戈，{attacker} 陣營歡聲雷動",
    "【獨家】深夜密會曝光！{attacker} 成功拔走 {defender} 重要樁腳",
    "【震撼彈】地方勢力洗牌！{boss_region} 樁腳證實棄暗投明支持 {attacker}",
    "【選情急轉】{defender} 後院著火！心腹大將帶槍投靠 {attacker}",
    "【焦點新聞】{attacker} 拔樁神操作！{defender} 陣營驚呼不可思議",
    "【獨家報導】{boss_region} 樁腳表態相挺！{attacker} 選情吃下定心丸",
    "【快報】{defender} 樁腳大逃亡！{attacker} 陣營門庭若市",
    "【內幕】{attacker} 誠意打動 {boss_region} 樁腳！{defender} 失去重要據點",
    "【選戰觀察】{attacker} 拔樁成功率百分百！{defender} 根基動搖",
    "【突發快訊】{boss_region} 樁腳現身 {attacker} 造勢晚會！{defender} 陣營傻眼",
    "【獨家直擊】{attacker} 團隊密訪 {boss_region} 樁腳大成功！{defender} 遭背叛",
    "【熱門焦點】{attacker} 善用資源拔樁！{defender} 地方實力大減",
    "【選情分析】{boss_region} 樁腳倒戈效應擴大！{attacker} 聲勢看漲",
    "【焦點人物】{attacker} 拔樁大將發功！{defender} 陣營陷入恐慌",
    "【快訊】{defender} 樁腳紛紛跳船！{attacker} 歡喜接收",
    "【獨家內幕】{boss_region} 樁腳為何倒戈？傳 {attacker} 給出超優條件",
    "【熱門話題】{attacker} 拔樁速度驚人！{defender} 地方組織面臨瓦解",
    "【選戰快遞】{boss_region} 樁腳改掛 {attacker} 看板！{defender} 表示遺憾",
    "【焦點報導】{attacker} 拔樁戰術奏效！{defender} 選情告急",
]

# --- 拔樁失敗 (15 條) ---
NEWS_TITLES_FLIP_FAIL = [
    "【選戰直擊】{attacker} 拔樁碰壁！{boss_region} 樁腳無情拒絕",
    "【獨家】{attacker} 拿錢砸人慘遭打臉！{defender} 樁腳忠心耿耿",
    "【快訊】策反失敗！{attacker} 陣營幕僚遭轟出門，地方大佬力挺 {defender}",
    "【內幕】{attacker} 試圖策反暗樁失敗，惹怒地方大老發不自殺聲明",
    "【焦點新聞】{attacker} 拔樁吃閉門羹！{boss_region} 樁腳不為所動",
    "【獨家報導】{attacker} 拔樁預算報銷！{defender} 樁腳拒絕見面",
    "【快報】{attacker} 拔樁行動搞烏龍！差點引發地方衝突，{defender} 隔空喊話",
    "【選戰花絮】{attacker} 拔樁幕僚走錯地方！{boss_region} 樁腳笑稱太瞎",
    "【內幕】{attacker} 拔樁條件太差？{defender} 樁腳大笑拒絕",
    "【熱門話題】{attacker} 拔樁踢到鐵板！{defender} 地方實力堅若磐石",
    "【選戰焦點】{attacker} 拔樁不成反被酸！{boss_region} 樁腳公開力挺 {defender}",
    "【突發快訊】{attacker} 拔樁引發眾怒！{defender} 樁腳大罵不要臉",
    "【獨家直擊】{attacker} 拔樁幕僚落荒而逃！{boss_region} 樁腳驅離不速之客",
    "【選情報導】{attacker} 拔樁行動大挫敗！{defender} 陣營士氣大振",
    "【焦點觀察】{attacker} 拔樁戰術失效！{defender} 樁腳忠誠度通過考驗",
]

# --- 一般正向行動 (50 條) ---
NEWS_TITLES_GENERAL_POSITIVE = [
    "【快訊】{name} {action} 獲滿堂彩！地方阿伯大讚：這憨孫有氣魄",
    "【選情看板】{name} 深耕基層有成，{action} 現場萬人空巷",
    "【綜合報導】網路聲量大漲！{name} 靠 {action} 成功收服年輕選票",
    "【直擊】感動！{name} {action} 展現親民作風，婆媽搶合照",
    "【焦點】{name} 推出 {action}，網友盛讚：終於有人在做事",
    "【獨家】{name} {action} 超乎預期！民調一路狂飆",
    "【熱門話題】{name} {action} 引發熱烈討論！網讚：政治界清流",
    "【選戰快遞】{name} 靠 {action} 成功逆轉！支持者歡呼",
    "【焦點新聞】{name} {action} 誠意滿滿！地方大老紛紛點頭",
    "【快報】{name} {action} 創造驚人氣勢！對手陣營備感壓力",
    "【獨家報導】{name} {action} 深入民心！選民直呼：就決定是你了",
    "【選情解析】{name} {action} 策略精準！成功吸引中間選民",
    "【突發快訊】{name} {action} 現場塞爆！民眾熱情響應",
    "【焦點人物】{name} 憑藉 {action} 聲勢大漲！成為選戰最亮眼黑馬",
    "【熱門趨勢】{name} {action} 成網路熱搜！網友瘋狂轉發",
    "【選戰直擊】{name} {action} 展現過人體力！基層反應熱烈",
    "【內幕】{name} {action} 背後有高人指點？成效好到令人咋舌",
    "【快訊】{name} {action} 獲跨黨派肯定！政治版圖擴大",
    "【獨家觀察】{name} {action} 穩紮穩打！選戰節奏掌握得宜",
    "【焦點報導】{name} {action} 引發共鳴！支持者自發性宣傳",
    "【選戰花絮】{name} {action} 展現幽默感！網友大讚：被政治耽誤的喜劇演員",
    "【熱門焦點】{name} {action} 成功化解危機！展現政治智慧",
    "【快報】{name} {action} 獲得意見領袖背書！聲勢如虹",
    "【獨家直擊】{name} {action} 現場氣氛嗨翻天！宛如跨年晚會",
    "【選情專題】{name} {action} 展現強大執行力！選民信心大增",
    "【話題人物】{name} {action} 引領風潮！成為選戰最新指標",
    "【突發新聞】{name} {action} 意外獲得巨大成功！幕僚跌破眼鏡",
    "【選戰快訊】{name} {action} 誠懇態度打動選民！支持度穩定成長",
    "【獨家解析】{name} {action} 完美結合線上線下！選戰策略堪稱教科書",
    "【熱門搜尋】{name} {action} 成網路最夯話題！網友：好想去現場",
    "【焦點透視】{name} {action} 展現領袖魅力！吸引大批鐵粉",
    "【快報】{name} {action} 獲青年學子熱烈回響！成功年輕化",
    "【獨家報導】{name} {action} 引發社會關注！議題設定能力一流",
    "【選情雷達】{name} {action} 成功鞏固基本盤！防禦無懈可擊",
    "【話題焦點】{name} {action} 展現過人親和力！婆媽粉瘋狂",
    "【突發消息】{name} {action} 現場驚喜不斷！選民直呼太用心",
    "【選戰搶先報】{name} {action} 創造空前聲量！對手難以望其項背",
    "【獨家專訪】{name} 暢談 {action} 理念！選民大讚有遠見",
    "【焦點快訊】{name} {action} 成功弭平爭議！展現政治手腕",
    "【熱門新聞】{name} {action} 獲各界好評！聲勢持續攀升",
    "【選戰最前線】{name} {action} 展現過人體能！鐵人行程不喊累",
    "【快報】{name} {action} 發揮母雞帶小雞效應！全黨士氣大振",
    "【獨家評論】{name} {action} 堪稱神來一筆！選戰再創高潮",
    "【話題追蹤】{name} {action} 引發網友熱烈討論！讚聲不斷",
    "【焦點人物】{name} {action} 展現卓越溝通能力！化解對立",
    "【突發快報】{name} {action} 現場萬人響應！氣勢驚人",
    "【選情報導】{name} {action} 成功突圍！打破選戰僵局",
    "【獨家觀察】{name} {action} 展現真性情！選民直呼好感度破表",
    "【熱門話題】{name} {action} 成為街頭巷尾討論焦點！熱度不減",
    "【選戰快遞】{name} {action} 完美收官！為選戰打下堅實基礎",
]

# --- 一般負向行動 (50 條) ---
NEWS_TITLES_GENERAL_NEGATIVE = [
    "【快報】{name} {action} 慘遭噓爆！民眾怒嗆：別來這套",
    "【獨家】作秀過頭？{name} {action} 引發地方反感",
    "【選戰花絮】{name} {action} 現場超尷尬，台下民眾滑手機不理不睬",
    "【爭議】{name} {action} 誠意不足？對手陣營痛批：根本是鬧劇",
    "【焦點新聞】{name} {action} 大翻車！公關危機持續延燒",
    "【獨家報導】{name} {action} 內容空洞！選民直呼太失望",
    "【熱門話題】{name} {action} 引發網友群嘲！梗圖滿天飛",
    "【選戰快遞】{name} {action} 弄巧成拙！支持度不增反減",
    "【快報】{name} {action} 惹怒基層！地方人士揚言抵制",
    "【內幕】{name} {action} 決策錯誤？幕僚互推責任",
    "【突發快訊】{name} {action} 現場爆發衝突！場面一度失控",
    "【焦點人物】{name} {action} 展現傲慢態度！選民大呼反感",
    "【獨家直擊】{name} {action} 門可羅雀！人氣慘澹不忍直視",
    "【選情分析】{name} {action} 策略大失敗！白白浪費資源",
    "【熱門焦點】{name} {action} 遭質疑浪費公帑！引發社會撻伐",
    "【快訊】{name} {action} 慘遭意見領袖批評！聲勢受挫",
    "【獨家內幕】{name} {action} 背後有利益輸送？遭檢調盯上",
    "【選戰觀察】{name} {action} 暴露能力不足缺點！對手趁機猛攻",
    "【話題焦點】{name} {action} 引發炎上！網友要求道歉",
    "【焦點報導】{name} {action} 徹底失敗！選戰節奏大亂",
    "【突發消息】{name} {action} 現場遭抗議民眾包圍！尷尬離場",
    "【選戰搶先報】{name} {action} 展現無知一面！選民哭笑不得",
    "【獨家專訪】{name} 對 {action} 避重就輕！選民直批沒誠意",
    "【熱搜新聞】{name} {action} 成為選戰最大笑話！",
    "【快報】{name} {action} 遭自家人切割！黨內同志不挺",
    "【獨家解析】{name} {action} 完全搞錯重點！選情雪上加霜",
    "【選情透視】{name} {action} 展現政客嘴臉！選民大失所望",
    "【話題人物】{name} {action} 屢屢失言！公關團隊瀕臨崩潰",
    "【焦點快訊】{name} {action} 引發巨大連漪！負面聲量創歷史新高",
    "【突發快報】{name} {action} 現場狀況百出！幕僚緊急中斷直播",
    "【選戰最前線】{name} {action} 毫無亮點！選民表示想睡覺",
    "【獨家評論】{name} {action} 堪稱災難級演出！",
    "【熱門話題】{name} {action} 遭網友起底造假！誠信破產",
    "【焦點觀察】{name} {action} 暴露出團隊準備不足！",
    "【快報】{name} {action} 引發社會撕裂！遭批製造對立",
    "【獨家直擊】{name} {action} 現場民眾嗆聲不斷！氣氛火爆",
    "【選情報導】{name} {action} 無法挽救低迷選情！大勢已去",
    "【話題追蹤】{name} {action} 爭議持續延燒！恐怕難以脫身",
    "【焦點報導】{name} {action} 成為選戰負面教材！",
    "【突發新聞】{name} {action} 遭批不知民間疾苦！與基層脫節",
    "【選戰雷達】{name} {action} 讓中間選民卻步！支持度嚴重流失",
    "【熱門焦點】{name} {action} 引發政治風暴！後座力驚人",
    "【獨家內幕】{name} {action} 是誰出的餿主意？幕僚團隊大地震",
    "【快報】{name} {action} 無人關注！完全被邊緣化",
    "【選情解析】{name} {action} 暴露其政治歷練不足！",
    "【焦點人物】{name} {action} 成為全國笑柄！",
    "【獨家專題】{name} {action} 徹底搞砸大好局面！",
    "【話題熱議】{name} {action} 引發民眾強烈不滿！怒火難平",
    "【突發快訊】{name} {action} 黯然收場！留下滿地爛攤子",
    "【選戰快遞】{name} {action} 慘遭選民唾棄！",
]


# ==========================================
# 💬 PTT 鄉民推文庫
# ==========================================

# --- 戰鬥成功 (20 條) ---
PTT_COMMENTS_ATTACK_SUCCESS = [
    "推: 太神啦！{attacker} 這波操作我給滿分",
    "推: {defender} 下去啦，真的笑死",
    "→: 側翼動起來囉，看來又有一波好戲",
    "推: 幫 {defender} QQ，被 {attacker} 網軍洗成這樣",
    "噓: 雖然討厭 {defender}，但 {attacker} 網軍也太囂張了吧",
    "推: {defender} 防火牆跟紙糊的一樣 XDD",
    "→: 這篇明顯帶風向，不過 {defender} 真的爛",
    "推: 看到 {defender} 被洗臉就是爽",
    "推: {attacker} 的公關公司很強欸，戰鬥力破表",
    "→: 坐等 {defender} 發言人出來崩潰",
    "推: {defender} 這下真的要下神壇了",
    "噓: 網軍治國，可悲的台灣選舉",
    "推: {attacker} 終於醒了，早該這樣打了",
    "→: 這波火力太猛，{defender} 真的擋不住",
    "推: 幫高調！讓更多人看到 {defender} 的真面目",
    "噓: {attacker} 只會靠網軍，有種出來單挑啊",
    "推: {defender} 的粉專已經變戰場了，超好笑",
    "→: 這波帶風向很成功，{attacker} 穩了穩了",
    "推: 看到側翼狂咬 {defender} 就是舒壓",
    "推: {attacker} 加油！打倒 {defender}！",
]

# --- 戰鬥失敗 (20 條) ---
PTT_COMMENTS_ATTACK_FAIL = [
    "噓: {attacker} 網軍大型翻車現場，朝聖",
    "噓: 帶風向失敗，笑死",
    "推: 幫高調！{attacker} 側翼被抓包了吧",
    "噓: 1450 又發作了，公關公司不用扣錢嗎",
    "→: {attacker} 陣營的公關公司可以換了，戰鬥力有夠差",
    "推: {defender} 躺著也加分，{attacker} 根本豬隊友",
    "噓: 只有這點程度也敢出來帶風向？",
    "噓: {attacker} 網軍是不是沒領便當啊，這麼沒戰力",
    "推: 朝聖 {attacker} 豬隊友，笑死我了",
    "→: {defender} 這次根本什麼都沒做就贏了",
    "噓: 這種低級抹黑也拿得出來，{attacker} 陣營沒人才了？",
    "推: {attacker} 網軍崩潰中，好可憐",
    "噓: 被 {defender} 粉絲反殺，真丟臉",
    "→: 這波操作太瞎，連自己人都挺不下去",
    "噓: {attacker} 只會耍小手段，結果還失敗，笑死",
    "推: 看到 {attacker} 吃鱉就是爽",
    "噓: 沒錢請好一點的公關公司嗎？",
    "→: {defender} 完全無視這波攻擊，高下立判",
    "噓: {attacker} 網軍回家多練練吧",
    "推: 大型車禍現場，幫 {attacker} QQ",
]

# --- 拔樁成功 (15 條) ---
PTT_COMMENTS_FLIP_SUCCESS = [
    "推: {boss_region} 居然被拔了！{defender} 塊陶啊",
    "推: 拔草測風向，看來 {attacker} 穩了",
    "→: {defender} 後院起火囉，連自己人都搞不定",
    "推: 錢砸下去當然倒戈啊，這就是選舉",
    "噓: 台灣選舉只剩拔樁跟黑金，悲哀",
    "推: {attacker} 拔樁有一套，這下 {defender} 難過了",
    "→: 地方大老也看風向的啦，{defender} 沒搞頭了",
    "推: {defender} 連自己的樁腳都顧不好，選屁啊",
    "推: {attacker} 這招狠，直接斷 {defender} 糧草",
    "噓: 利益交換罷了，有什麼好看的",
    "推: {boss_region} 的票我看 {defender} 是別想拿了",
    "→: 政治本來就是這樣，沒什麼好意外的",
    "推: {attacker} 厲害，這局我押你贏",
    "推: {defender} 準備打包回家啦",
    "噓: 樁腳政治，台灣民主的悲哀",
]

# --- 拔樁失敗 (15 條) ---
PTT_COMMENTS_FLIP_FAIL = [
    "噓: {attacker} 拔樁失敗笑死，當人家要飯的喔",
    "推: {defender} 樁腳夠硬！不被金錢誘惑",
    "→: 被掃地出門了吧，{attacker} 真可撥",
    "噓: 以為花錢就買得到票？懂不懂在地啊",
    "推: 這樁腳很純喔，幫 {defender} 點讚",
    "→: {attacker} 踢到鐵板了，好痛喔",
    "噓: 只會撒錢，結果人家不領情，笑死",
    "推: {defender} 平常有在經營啦，哪是那麼好拔的",
    "噓: {attacker} 連拔樁都不會，洗洗睡吧",
    "推: 看到 {attacker} 吃癟就是爽",
    "→: 地方實力不是一天兩天建立的",
    "噓: {attacker} 以為自己是誰啊，人家根本不鳥你",
    "推: {defender} 穩了，樁腳這麼挺",
    "噓: 這操作太尷尬，自己人看了都搖頭",
    "推: {boss_region} 的人有骨氣！",
]

# --- 一般正向行動 (80 條) ---
PTT_COMMENTS_POSITIVE = [
    "推: 這咖又在認真做事了，給推",
    "推: 雖然是選舉到了才來，但有做事就推",
    "推: {name} 真的有心欸，比對手好多了",
    "推: 唯一支持 {name}！",
    "→: 觀望中，但這波有加分",
    "推: 現場有發便當嗎？有的話我一定投",
    "推: {name} 加油，台灣需要你這樣的人",
    "推: 這才是我們想看到的政治人物",
    "→: 看來 {name} 這次是真的拚了",
    "推: 把對手按在地上摩擦，爽",
    "推: {name} 真的接地氣，懂民眾要什麼",
    "推: 看到 {name} 這麼拚，我都想去幫忙拉票了",
    "噓: 雖然討厭他，但這次真的做得不錯",
    "推: {name} 穩了穩了，準備慶祝",
    "→: 這政策滿有建設性的，給過",
    "推: 終於有人願意處理這問題了，推一個",
    "推: {name} 的執行力沒話說",
    "推: 看到這畫面真的滿感動的",
    "→: 這次選舉我就投 {name} 了",
    "推: 不用選了啦，{name} 直接當選",
    "推: {name} 的幕僚滿強的，企劃做很好喔",
    "推: 這波操作有打中我的點",
    "噓: 又在神化 {name} 了，不過這次我買單",
    "推: 台灣有一線希望了",
    "推: 對手完全神隱，高下立判",
    # 以下為更多正向擴充
    "推: {name} 表現真不錯，支持啦",
    "→: 選民眼睛是雪亮的，這波操作漂亮",
    "推: {name} 這次真的是政壇清流",
    "推: 感動到哭了，台灣有 {name} 真好",
    "推: 把票投給有做事的人",
    "→: 至少比那個只會說空話的好太多",
    "推: {name} 懂年輕人要什麼",
    "推: {name} 的口條真的好，演講超有感染力",
    "噓: 網軍又在吹了... 但這次我真的覺得不錯",
    "推: 政策務實，不畫大餅，讚",
    "推: 難得看到這麼踏實的候選人",
    "→: 再觀察看看，但目前給高分",
    "推: 現場氣氛超好，可惜沒去到",
    "推: 挺 {name} 到底，不管別人怎麼說",
    "推: 真的有在傾聽民意，不是只有選舉才出現",
    "推: 把對手打到不敢還手，猛",
    "→: 這招有創意，讓人眼睛一亮",
    "推: {name} 值得信賴，唯一選擇",
    "推: 一步一腳印，這才是對的",
    "推: 看到 {name} 的努力，我決定投他一票",
    "推: {name} 讚啦！台灣價值！",
    "推: 這種優質候選人不支持不行",
    "→: {name} 的聲勢越來越強了",
    "推: 對手瑟瑟發抖中",
    "推: 這局我押 {name} 贏",
    "推: 期待 {name} 未來的表現",
    "推: 認真的政治人物不會被埋沒",
    "噓: 雖然 {name} 很討厭，但這件事做得對",
    "推: {name} 就是強，沒得嫌",
    "推: 這根本是無死角攻擊，對手怎麼玩",
    "推: 我全家都投 {name} 啦",
    "→: {name} 這次選舉穩扎穩打",
    "推: 沒想到 {name} 這麼有料",
    "推: 被圈粉了，{name} 加油",
    "推: 台灣的未來交給 {name} 了",
    "推: {name} 的政見真的很有遠見",
    "→: 這才是選戰該有的樣子",
    "推: {name} 魅力無法擋",
    "推: 給 {name} 一個讚",
    "推: 這種行動力，不當選沒天理",
    "推: 看好 {name} 翻盤",
    "推: {name} 一枝獨秀，對手全變配角",
    "→: 這次選舉最亮眼的就是 {name} 了",
    "推: 支持做事的人，推 {name}",
    "推: {name} 連基層都顧得這麼好，太佛了",
    "推: 對手已經放棄治療了吧",
    "推: 滿滿的誠意，選民都感受到了",
    "推: {name} 絕對是台灣未來的希望",
    "→: 這波操作可以直接進教科書了",
    "推: 讓 {name} 高票當選啦",
]

# --- 一般負向行動 (80 條) ---
PTT_COMMENTS_NEGATIVE = [
    "噓: 又在作秀了，可悲",
    "噓: {name} 別演了啦，大家都知道你在想什麼",
    "→: 吃瓜看戲中，看 {name} 還能演多久",
    "噓: 這操作太尷尬了吧，我都替他感到丟臉",
    "噓: 垃圾不分藍綠，拒絕投票",
    "噓: 把選民當白痴嗎？這什麼爛企劃",
    "噓: {name} 真的嫌票太多欸",
    "→: 幕僚是不是內鬼啊？這種行程也排得出來",
    "噓: 看到 {name} 的嘴臉就反胃",
    "噓: 講一堆廢話，重點是什麼？",
    "噓: 浪費社會資源，滾回家吧",
    "推: 幫 {name} QQ，大型翻車現場",
    "噓: 這種人選得上我把頭剁下來",
    "噓: {name} 不要再出來丟人現眼了",
    "→: 這公關危機處理零分",
    "噓: 下去啦！沒人在乎",
    "噓: {name} 的下限真的深不見底",
    "推: 笑死，看 {name} 崩潰就是爽",
    "噓: 完全不知所云，{name} 是不是沒料了",
    "噓: 怎麼有臉講這種話，噁心",
    "噓: 把台灣搞砸的罪魁禍首",
    "→: 選情是不是告急了，才搞這種爛招",
    "噓: 這種政見連小學生都不會買單",
    "噓: 原來 {name} 只有這種程度",
    "噓: 不要再刷存在感了，很煩",
    # 以下為更多負向擴充
    "噓: {name} 真的沒救了",
    "噓: 滿滿的作秀味，看了就倒胃口",
    "→: {name} 是不是以為自己很幽默？",
    "噓: 這種素質也想出來選？",
    "噓: 無能又愛演，可憐哪",
    "噓: 對手什麼都沒做就贏了，{name} 太慘",
    "推: 看到 {name} 被酸爆我就放心了",
    "噓: 越看越覺得 {name} 虛偽",
    "噓: {name} 講話都沒邏輯，怎麼護航",
    "→: 幕僚群可能已經在寫履歷找新工作了",
    "噓: 史上最爛候選人，沒有之一",
    "噓: {name} 的下作真是沒有極限",
    "噓: 完全把選民當提款機",
    "推: {name} 繼續鬧啊，好久沒看到這麼好笑的喜劇了",
    "噓: {name} 以為大家都會忘記他以前做過的事嗎？",
    "噓: 說話不算話的政客",
    "→: 慘，連自家人都挺不下去",
    "噓: 看到 {name} 就想轉台",
    "噓: 只會搞對立，一點建設性都沒有",
    "噓: {name} 的腦袋裡裝什麼啊？",
    "噓: 這種程度也想出來騙選票",
    "推: 朝聖，來看 {name} 秀下限",
    "噓: 真的有夠丟臉，拜託退選啦",
    "噓: 原來這就是 {name} 的水準，受教了",
    "→: 其實 {name} 是對手派來的臥底吧？",
    "噓: 都不覺得尷尬嗎？我都替他尷尬了",
    "噓: 全世界都欠 {name} 一個影帝獎座",
    "噓: 這種政見根本就是在騙小孩",
    "噓: {name} 的假面具被拆穿了",
    "推: 這波公關危機處理得真是一場災難",
    "噓: 下架 {name}，台灣才會好",
    "噓: 看到 {name} 真的會生氣",
    "→: 早點認輸吧，別丟人現眼了",
    "噓: {name} 的臉皮到底有多厚？",
    "噓: 這種人怎麼還有臉出來選",
    "噓: 完全沒有中心思想的變色龍",
    "推: {name} 完美詮釋什麼叫政治小丑",
    "噓: {name} 就是個只會打嘴砲的草包",
    "噓: 這招已經爛透了，換點新把戲好嗎",
    "→: 真的是爛泥扶不上牆",
    "噓: {name} 的存在就是台灣政治的污點",
    "噓: 浪費大家時間",
    "噓: {name} 到底在公三小",
    "噓: 給 {name} 零分都嫌多",
    "推: 看到 {name} 崩潰，大家今天晚餐多吃一碗",
]


# ==========================================
# 🎲 核心生成函式
# ==========================================

def get_news_and_ptt(event_type: str, kwargs: dict) -> dict:
    """
    依照事件類型，隨機抽取新聞標題與數則 PTT 留言，並替換參數。
    
    event_type 支援:
    - attack_success
    - attack_fail
    - flip_success
    - flip_fail
    - general_positive
    - general_negative
    """
    news_pool = []
    ptt_pool = []
    
    if event_type == "attack_success":
        news_pool = NEWS_TITLES_COMBAT_SUCCESS
        ptt_pool = PTT_COMMENTS_ATTACK_SUCCESS
    elif event_type == "attack_fail":
        news_pool = NEWS_TITLES_COMBAT_FAIL
        ptt_pool = PTT_COMMENTS_ATTACK_FAIL
    elif event_type == "flip_success":
        news_pool = NEWS_TITLES_FLIP_SUCCESS
        ptt_pool = PTT_COMMENTS_FLIP_SUCCESS
    elif event_type == "flip_fail":
        news_pool = NEWS_TITLES_FLIP_FAIL
        ptt_pool = PTT_COMMENTS_FLIP_FAIL
    elif event_type == "general_positive":
        news_pool = NEWS_TITLES_GENERAL_POSITIVE
        ptt_pool = PTT_COMMENTS_POSITIVE
    else:
        news_pool = NEWS_TITLES_GENERAL_NEGATIVE
        ptt_pool = PTT_COMMENTS_NEGATIVE

    # 抽取 1 則新聞，3 則 PTT
    raw_news = random.choice(news_pool)
    raw_ptts = random.sample(ptt_pool, min(3, len(ptt_pool)))
    
    # 參數替換
    # 使用 {kw_name} 替換
    try:
        formatted_news = raw_news.format(**kwargs)
    except KeyError:
        # 容錯處理：如果有變數沒傳進來，就原樣輸出或塞預設字串
        formatted_news = raw_news
        
    formatted_ptts = []
    for p in raw_ptts:
        try:
            formatted_ptts.append(p.format(**kwargs))
        except KeyError:
            formatted_ptts.append(p)
    
    return {
        "news_report": formatted_news,
        "ptt_comments": formatted_ptts
    }
