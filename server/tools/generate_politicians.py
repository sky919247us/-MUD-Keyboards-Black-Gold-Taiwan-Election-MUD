import json
from pathlib import Path

# 定義各層級人物清單與其屬性
RAW_DATA = [
    # ==== 總統 / 副總統 / 院長級 ====
    ("pol_lai", "賴清德", "賴威廉", "DPF", "PAN_GREEN", "PRESIDENT", ["賴神", "清德宗", "威廉", "功德", "賴副"]),
    ("pol_tsai", "蔡英文", "小英", "DPF", "PAN_GREEN", "PRESIDENT", ["辣台妹", "英皇", "蔡總統", "讀稿機"]),
    ("pol_hsiao", "蕭美琴", "戰貓", "DPF", "PAN_GREEN", "PRESIDENT", ["美琴", "駐美代表", "副總統"]),
    ("pol_su", "蘇貞昌", "電火球", "DPF", "PAN_GREEN", "PREMIER", ["衝衝衝", "光頭", "蘇院長"]),
    ("pol_chen_cj", "陳建仁", "大仁哥", "DPF", "PAN_GREEN", "PREMIER", ["聖騎士", "陳院長"]),
    ("pol_cho", "卓榮泰", "大師兄", "DPF", "PAN_GREEN", "PREMIER", ["卓院長", "榮泰"]),
    ("pol_han", "韓國瑜", "韓總機", "NCA", "PAN_BLUE", "LEGISLATOR", ["國瑜", "韓導", "發大財", "韓總", "院長", "睡到中午"]),
    ("pol_ma", "馬英九", "馬邦伯", "NCA", "PAN_BLUE", "PRESIDENT", ["死亡之握", "小馬哥", "馬前總統"]),
    ("pol_chu", "朱立倫", "精算師", "NCA", "PAN_BLUE", "PRESIDENTIAL_CANDIDATE", ["正常倫", "保護傘", "朱主席", "換柱"]),

    # ==== 縣市首長 ====
    ("pol_chiang", "蔣萬安", "萬安公子", "NCA", "PAN_BLUE", "MAYOR", ["蔣市長", "公子", "台北市長"]),
    ("pol_hou", "侯友宜", "侯探長", "NCA", "PAN_BLUE", "MAYOR", ["探長", "侯侯", "侯警長", "友宜", "新北市長"]),
    ("pol_chang", "張善政", "張善後", "NCA", "PAN_BLUE", "MAYOR", ["善哥", "桃園市長", "善政"]),
    ("pol_lu", "盧秀燕", "媽媽市長", "NCA", "PAN_BLUE", "MAYOR", ["燕子", "盧媽", "台中市長"]),
    ("pol_huang_wj", "黃偉哲", "西瓜市長", "DPF", "PAN_GREEN", "MAYOR", ["偉哲", "台南市長", "全糖市長"]),
    ("pol_chen_km", "陳其邁", "暖男市長", "DPF", "PAN_GREEN", "MAYOR", ["其邁", "邁邁", "高雄市長", "緊緊緊"]),
    ("pol_kao", "高虹安", "斐陶斐", "NAP", "WHITE", "MAYOR", ["安安市長", "高市長", "新竹市長", "大秘寶"]),
    ("pol_hsieh", "謝國樑", "鐵柱市長", "NCA", "PAN_BLUE", "MAYOR", ["國樑", "基隆市長", "Gogoro"]),
    ("pol_kao_mn", "高閔琳", "閔琳", "DPF", "PAN_GREEN", "MAYOR", ["高雄市官員"]), # Example
    ("pol_chung", "鍾東錦", "砂石縣長", "IND", "PAN_BLUE", "MAYOR", ["東錦", "鍾縣長", "切腹", "苗栗國"]),
    ("pol_hsu", "徐榛蔚", "花蓮后", "NCA", "PAN_BLUE", "MAYOR", ["榛蔚", "花蓮縣長", "傅太大"]),
    ("pol_lin_jm", "林姿妙", "妙妙姐", "NCA", "PAN_BLUE", "MAYOR", ["姿妙", "宜蘭縣長", "看不懂公文"]),
    ("pol_jao", "饒慶鈴", "慶鈴", "NCA", "PAN_BLUE", "MAYOR", ["台東縣長"]),
    ("pol_wang_hm", "王惠美", "惠美", "NCA", "PAN_BLUE", "MAYOR", ["彰化縣長", "阿美"]),
    ("pol_chang_lc", "張麗善", "雲林姑", "NCA", "PAN_BLUE", "MAYOR", ["麗善", "雲林縣長"]),
    ("pol_huang_mm", "黃敏惠", "敏惠", "NCA", "PAN_BLUE", "MAYOR", ["嘉義市長", "勇媽"]),
    ("pol_yung", "翁章梁", "章梁", "DPF", "PAN_GREEN", "MAYOR", ["嘉義縣長", "農工大縣"]),
    ("pol_chou", "周春米", "春米", "DPF", "PAN_GREEN", "MAYOR", ["屏東縣長", "小米"]),
    ("pol_chen_gh", "陳光復", "光復", "DPF", "PAN_GREEN", "MAYOR", ["澎湖縣長"]),
    ("pol_yang_wc", "楊文科", "文科", "NCA", "PAN_BLUE", "MAYOR", ["新竹縣長"]),

    # ==== 焦點立委 (藍綠白) ====
    ("pol_ker", "柯建銘", "老柯", "DPF", "PAN_GREEN", "LEGISLATOR", ["建銘", "總召", "喬王"]),
    ("pol_huang_kc", "黃國昌", "咆哮帝", "NAP", "WHITE", "LEGISLATOR", ["國昌", "戰神", "太離譜了", "蔥哥"]),
    ("pol_huang_ss", "黃珊珊", "33", "NAP", "WHITE", "LEGISLATOR", ["珊珊", "黃副市長", "前副市長"]),
    ("pol_hsu_cc", "徐巧芯", "蜜獾", "NCA", "PAN_BLUE", "LEGISLATOR", ["巧芯", "早餐店女孩", "徐禁評", "900芯"]),
    ("pol_huang_j", "黃捷", "白眼女神", "DPF", "PAN_GREEN", "LEGISLATOR", ["捷哥", "翻白眼"]),
    ("pol_wang_sj", "王世堅", "恰吉", "DPF", "PAN_GREEN", "LEGISLATOR", ["世堅", "堅哥", "跳海", "送禮大師"]),
    ("pol_fu", "傅崐萁", "花蓮王", "NCA", "PAN_BLUE", "LEGISLATOR", ["崐萁", "傅總召", "崑萁"]),
    ("pol_lo", "羅智強", "小強", "NCA", "PAN_BLUE", "LEGISLATOR", ["智強", "戰將"]),
    ("pol_woo", "吳思瑤", "思瑤", "DPF", "PAN_GREEN", "LEGISLATOR", ["吳總召", "愛台十二建設"]),
    ("pol_pum", "洪孟楷", "孟楷", "NCA", "PAN_BLUE", "LEGISLATOR", ["書記長"]),
    ("pol_lin_cc", "林楚茵", "楚茵", "DPF", "PAN_GREEN", "LEGISLATOR", ["林委員"]),
    ("pol_shen", "沈伯洋", "黑熊", "DPF", "PAN_GREEN", "LEGISLATOR", ["Puma", "伯洋", "黑熊學院"]),
    ("pol_ko_cw", "柯志恩", "志恩", "NCA", "PAN_BLUE", "LEGISLATOR", ["柯委員"]),
    ("pol_hsieh_lc", "謝龍介", "龍介仙", "NCA", "PAN_BLUE", "LEGISLATOR", ["龍介", "台南阿伯", "一生監督你一人"]),
    ("pol_wang_hy", "王鴻薇", "鴻薇", "NCA", "PAN_BLUE", "LEGISLATOR", ["王委員", "女戰神"]),
    ("pol_lai_sy", "賴士葆", "費鴻泰", "NCA", "PAN_BLUE", "LEGISLATOR", ["士葆", "財委會"]),
    ("pol_chuang", "莊瑞雄", "瑞雄", "DPF", "PAN_GREEN", "LEGISLATOR", ["莊委員"]),
    ("pol_tsai_yc", "蔡易餘", "易餘", "DPF", "PAN_GREEN", "LEGISLATOR", ["蔡委員", "小胖"]),
    ("pol_lin_tf", "林岱樺", "岱樺", "DPF", "PAN_GREEN", "LEGISLATOR", ["林委員"]),
    ("pol_wang_dy", "王定宇", "定宇", "DPF", "PAN_GREEN", "LEGISLATOR", ["王委員", "八千"]),
    ("pol_kuo_kc", "郭國文", "國文", "DPF", "PAN_GREEN", "LEGISLATOR", ["郭委員", "搶文件"]),
    ("pol_su_cc", "蘇巧慧", "巧慧", "DPF", "PAN_GREEN", "LEGISLATOR", ["蘇委員", "公主"]),
    ("pol_wu_pc", "吳沛憶", "沛憶", "DPF", "PAN_GREEN", "LEGISLATOR", ["吳委員", "萬華"]),
    ("pol_lin_sj", "林淑芬", "淑芬", "DPF", "PAN_GREEN", "LEGISLATOR", ["林委員", "孤鳥"]),
    ("pol_mai", "麥玉珍", "玉珍", "NAP", "WHITE", "LEGISLATOR", ["麥委員", "新住民"]),
    ("pol_lin_ku", "林憶君", "憶君", "NAP", "WHITE", "LEGISLATOR", ["林委員", "藥師"]),

    # ==== 知名議員與地方派系 / 政府官員 ====
    ("pol_miao", "苗博雅", "阿苗", "TSP", "LEFT_WING", "CITY_COUNCILOR", ["博雅", "苗議員"]),
    ("pol_lin_ys", "林雍昇", "雍昇", "DPF", "PAN_GREEN", "CITY_COUNCILOR", ["林議員"]),
    ("pol_jen", "顏清標", "冬瓜標", "IND", "PAN_BLUE", "LOCAL_BOSS", ["標哥", "顏董", "消波塊", "鎮瀾宮", "海線大佬"]),
    ("pol_jen_ku", "顏寬恒", "寬恒", "NCA", "PAN_BLUE", "LEGISLATOR", ["小標", "顏委員", "水餃"]),
    ("pol_chen_mw", "陳明文", "三百萬", "DPF", "PAN_GREEN", "LOCAL_BOSS", ["明文", "嘉義王", "高鐵三百萬", "囡仔仙"]),
    ("pol_kuo_tm", "郭台銘", "郭董", "IND", "WHITE", "PRESIDENTIAL_CANDIDATE", ["果凍", "台銘", "首富", "BNT"]),
    ("pol_ko", "柯文哲", "阿北", "NAP", "WHITE", "PRESIDENTIAL_CANDIDATE", ["柯P", "文哲大A", "師父", "阿伯", "KP", "老三"]),
    ("pol_wang_wl", "王婉諭", "燈泡媽", "TSP", "LEFT_WING", "LEGISLATOR", ["婉諭", "小燈泡媽媽", "時力黨主席"]),
    ("pol_chiu", "邱顯智", "邱大律師", "TSP", "LEFT_WING", "LEGISLATOR", ["顯智", "新竹人", "邱委員"]),
    ("pol_chao", "趙少康", "戰鬥藍", "NFP", "PAN_BLUE_EXTREME", "PRESIDENTIAL_CANDIDATE", ["少康", "金童", "少康戰情室"]),
    ("pol_hung", "洪秀柱", "小辣椒", "NFP", "PAN_BLUE_EXTREME", "PRESIDENTIAL_CANDIDATE", ["柱柱姐", "一中同表"]),
    ("pol_chen_sb", "陳水扁", "海角七億", "TPP", "PAN_GREEN_EXTREME", "PRESIDENT", ["阿扁", "扁維拉", "保外就醫", "勇哥"]),
    ("pol_lin_fc", "林飛帆", "林九萬", "DPF", "PAN_GREEN", "LOCAL_BOSS", ["飛帆", "九萬", "太陽花"]),
    ("pol_huang_jc", "黃捷", "白眼女神", "DPF", "PAN_GREEN", "LEGISLATOR", ["捷哥", "翻白眼", "黃委員"]),
    ("pol_ku_ky", "顧立雄", "顧律師", "DPF", "PAN_GREEN", "MINISTER", ["立雄", "國防部長", "金管會主委", "國安會秘書長"]),
    ("pol_wang_mw", "王美花", "美花", "DPF", "PAN_GREEN", "MINISTER", ["經濟部長", "美花部長"]),
    ("pol_chen_cc", "陳吉仲", "吉仲", "DPF", "PAN_GREEN", "MINISTER", ["農業部長", "小英男孩", "超思"]),
    ("pol_wang_bc", "王必勝", "必勝", "DPF", "PAN_GREEN", "MINISTER", ["指揮官", "衛福部", "小三"]),
    ("pol_chen_sz", "陳時中", "時中", "DPF", "PAN_GREEN", "MINISTER", ["阿中", "防疫指揮官", "紅酒", "跌倒"]),
    ("pol_lin_cw", "林佳龍", "佳龍", "DPF", "PAN_GREEN", "MINISTER", ["外交部長", "交通部長", "正國會"]),
    ("pol_cheng_ly", "鄭麗君", "麗君", "DPF", "PAN_GREEN", "PREMIER", ["文化部長", "副揆"]),
]

def main():
    politicians = []
    
    for pid, rname, ig_name, party, camp, level, ali in RAW_DATA:
        politicians.append({
            "id": pid,
            "real_name": rname,
            "in_game_name": ig_name,
            "party_code": party,
            "camp": camp,
            "level": level,
            "aliases": ali
        })
    
    output = {"politicians": politicians}
    
    target_path = Path(__file__).parent.parent / "app" / "data" / "politicians.json"
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        
    print(f"成功生成 {len(politicians)} 位政治實體資料至 {target_path}")

if __name__ == "__main__":
    main()
