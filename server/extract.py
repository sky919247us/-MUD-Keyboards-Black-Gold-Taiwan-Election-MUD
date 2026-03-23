import os

file_path = r"d:\《鍵盤與黑金：台灣選戰 MUD》 (Keyboards & Black Gold Taiwan Election MUD)\server\templates\index.html"
js_path = r"d:\《鍵盤與黑金：台灣選戰 MUD》 (Keyboards & Black Gold Taiwan Election MUD)\server\static\js\game.js"

os.makedirs(os.path.dirname(js_path), exist_ok=True)

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

script_start = -1
script_end = -1
for i in range(len(lines)):
    line = lines[i].strip()
    if line == "<script>":
        script_start = i
    elif line == "</script>" and script_start != -1:
        script_end = i
        break

if script_start != -1 and script_end != -1:
    js_content = "".join(lines[script_start+1:script_end])
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js_content)
    
    new_html = "".join(lines[:script_start]) + '    <script src="/static/js/game.js?v=2"></script>\n' + "".join(lines[script_end+1:])
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_html)
    print("JS extracted successfully.")
else:
    print(f"Failed to find script tags. Start: {script_start}, End: {script_end}")
