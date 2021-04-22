from os import name, path
from pathlib import Path
import mysql.connector

# 接続する
connectionInfo = {
  "host": 'localhost',
  "port": 3306,
  "user": 'root',
  "passwd": 'mysql',
  "database": 'ghost',
}

extension = "md"   # Also set markdown
tz = None          # ex) "+0900"

dirspec="%Y%M"     # output directory structure "" means all files in one directory

# 
# note jekyll needs filename yyyy-mm-dd-TITLE.md 
def createMarkdown(outputPath, title, body, publishDate, slug):
  global tz

  dateStr = publishDate.strftime("%Y-%m-%d")

  filepath = path.join(outputPath, f"{dateStr}-{slug}.{extension}")
  print(filepath)

  with open(filepath, 'w', encoding='UTF-8') as f:
    blogDate = publishDate.strftime(f"%Y-%m-%d %H:%M:%S {tz}")

    # header example
    # ---
    # layout: post
    # title:  "Welcome to Jekyll!"
    # date:   2021-04-21 21:44:37 +0900
    # categories: jekyll update
    # ---
    f.write("---\n")
    f.write("layout: post\n")
    f.write(f'title: "{title}"\n')
    f.write(f'date: "{blogDate}"\n')
    f.write(f'categories: \n')
    f.write("---\n")
    f.write(body)


# 出力ディレクトリを作る
# @return 出力ディレクトリ (path-like object)
def createOutputDirectory():
  import datetime
  import os
  dirname = datetime.datetime.today().strftime("%Y%m%d%H%M%S")

  abspath = path.join(os.getcwd(), "output", dirname)
  os.makedirs(abspath)
  return abspath

def main():
  # timezone
  global tz
  if (tz is None or len(tz) == 0):
    import datetime
    tz = datetime.datetime.now().astimezone().strftime("%z")

  with mysql.connector.connect(**connectionInfo) as conn:
    outputPath = createOutputDirectory()
    print(outputPath)

    # カーソルを取得する
    cur = conn.cursor()

    # SQL（データベースを操作するコマンド）を実行する
    # userテーブルから、HostとUser列を取り出す
    sql = "select title, plaintext, published_at, slug from posts"
    cur.execute(sql)


    # 実行結果を取得する
    for row in cur:
      createMarkdown(outputPath, row[0], row[1], row[2], row[3])

    cur.close

main()