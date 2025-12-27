import os
import zipfile

NOVELS_DIR = "novels"
OUTPUT_DIR = "output/site"
ZIP_PATH = "output/novel_site.zip"
LINES_PER_CHAPTER = 40

os.makedirs(OUTPUT_DIR, exist_ok=True)

novels = []

# ---------- 自动读取 TXT ----------
for filename in os.listdir(NOVELS_DIR):
    if not filename.endswith(".txt"):
        continue

    path = os.path.join(NOVELS_DIR, filename)

    with open(path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    if not lines:
        continue

    title = lines[0]              # 第一行 = 小说名
    content_lines = lines[1:]     # 剩余 = 正文

    novel_id = os.path.splitext(filename)[0]

    novels.append({
        "id": novel_id,
        "title": title,
        "lines": content_lines
    })

# ---------- 小说列表首页 ----------
with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write("""<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>小说在线阅读</title>
</head>
<body>
<font size="4">
<b>📚 小说列表</b><br><br>
""")
    for n in novels:
        f.write(f'<a href="{n["id"]}/index.html">{n["title"]}</a><br>\n')

    f.write("""
<br>
适配老人机浏览器
</font>
</body>
</html>
""")

# ---------- 生成每本小说 ----------
for n in novels:
    novel_dir = os.path.join(OUTPUT_DIR, n["id"])
    os.makedirs(novel_dir, exist_ok=True)

    chapters = [
        n["lines"][i:i + LINES_PER_CHAPTER]
        for i in range(0, len(n["lines"]), LINES_PER_CHAPTER)
    ]

    total = len(chapters)

    # 小说首页
    with open(os.path.join(novel_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>{n["title"]}</title>
</head>
<body>
<font size="4">

<b>{n["title"]}</b><br><br>

<a href="001.html">▶ 开始阅读</a><br><br>

<a href="../index.html">返回小说列表</a>

</font>
</body>
</html>
""")

    # 章节页
    for i, content in enumerate(chapters, start=1):
        num = str(i).zfill(3)
        prev_page = f"{str(i-1).zfill(3)}.html" if i > 1 else "index.html"
        next_page = f"{str(i+1).zfill(3)}.html" if i < total else "index.html"

        with open(os.path.join(novel_dir, f"{num}.html"), "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>第{num}章</title>
</head>
<body>
<font size="4">

<b>第{num}章</b><br><br>
""")
            for line in content:
                f.write(line + "<br><br>\n")

            f.write(f"""
<a href="{prev_page}">上一章</a><br>
<a href="{next_page}">下一章</a><br>
<a href="index.html">返回本书</a>

</font>
</body>
</html>
""")

# ---------- 打包 ZIP ----------
with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(OUTPUT_DIR):
        for file in files:
            full = os.path.join(root, file)
            zipf.write(full, arcname=full.replace(OUTPUT_DIR + "/", ""))

print("✅ 已自动读取小说名并生成整站 ZIP：", ZIP_PATH)

