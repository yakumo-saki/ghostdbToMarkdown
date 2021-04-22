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

exportType = 'hugo'  # available types 'hugo' 'jekyll'

dirspec="%Y%M"     # output directory structure "" means all files in one directory

def isHugo():
  return (exportType == 'hugo')

def isJekyll():
  return (exportType == 'jekyll')

# <h2 id="">前提</h2>
# <ul>
# <li>Linux Mint 20 (Ubuntu 20.04)</li>
# </ul>
# <h3 id="tldr">TL;DR;</h3>
# <ul>
# <li><code>convert henkan-moto.png henkan-saki.pdf</code></li>
# </ul>
# <h3 id="">エラーが出た場合</h3>
# <p>何もしていなければ、以下のエラーが表示されるはず。</p>
# <pre><code>convert-im6.q16: attempt to perform an operation not allowed by the security policy `PDF' @ error/constitute.c/IsCoderAuthorized/408.
# </code></pre>
# <p><code>/etc/ImageMagick-6/policy.xml</code> を編集する。末尾のところに以下のような部分があるのでコメントアウト</p>
# <pre><code>&lt;!--    ←これを追加してコメントアウト
#   &lt;policy domain=&quot;coder&quot; rights=&quot;none&quot; pattern=&quot;EPS&quot; /&gt;
#   &lt;policy domain=&quot;coder&quot; rights=&quot;none&quot; pattern=&quot;PDF&quot; /&gt;
#   &lt;policy domain=&quot;coder&quot; rights=&quot;none&quot; pattern=&quot;XPS&quot; /&gt;
# コメントアウト終わり --&gt;
# </code></pre>
# <p>これで、png -&gt; pdf に変換が可能になる。<br>
# が。別にファイルサイズが縮んだりするわけではない（むしろファイルサイズが大きくなる）</p>
def processBody(htmlBody):
  result = htmlBody

  import re
  # 
  result = result.replace("<!--kg-card-begin: markdown-->", "")
  result = result.replace("<!--kg-card-end: markdown-->", "")

  h1Tag = re.compile('<h1.*?>')
  result = h1Tag.subn("# ", result)[0]

  h2Tag = re.compile('<h2.*?>')
  result = h2Tag.subn("## ", result)[0]

  h3Tag = re.compile('<h3.*?>')
  result = h3Tag.subn("### ", result)[0]

  h4Tag = re.compile('<h4.*?>')
  result = h4Tag.subn("#### ", result)[0]

  h5Tag = re.compile('<h5.*?>')
  result = h5Tag.subn("##### ", result)[0]

  h6Tag = re.compile('<h6.*?>')
  result = h6Tag.subn("###### ", result)[0]

  # 箇条書き  BUG: Need for decide using "*" or "-"
  olTag = re.compile('<ol.*?>')
  result = olTag.subn("", result)[0]

  # 箇条書き
  ulTag = re.compile('<ul.*?>')
  result = ulTag.subn("", result)[0]

  # 箇条書き  BUG: decide "*" or "-" by enclosing HTML tag
  ulTag = re.compile('<li>')
  result = ulTag.subn("* ", result)[0]

  # images
  result = result.replace("__GHOST_URL__/content", "")

  # コード部
  result = result.replace("<code>", "`")
  result = result.replace("</code>", "`")

  # コードブロック
  result = result.replace("<pre>", "```\n")
  result = result.replace("</pre>", "```\n")

  # 強調
  result = result.replace("<strong>", "*")
  result = result.replace("</strong>", "*")

  #
  result = result.replace("<br>", "  \n")

  #
  result = result.replace("<p>", "\n")
  result = result.replace("</p>", "  \n")

  # 
  endtag = re.compile('</.*?>')
  result = endtag.subn('', result)[0]

  # 
  result = result.replace("&gt;", ">")
  result = result.replace("&lt;", "<")
  result = result.replace("&quot;", "\"")
  result = result.replace("&nbsp;", " ")

  return result

# 
# note jekyll needs filename yyyy-mm-dd-TITLE.md 
def createMarkdown(outputPath, title, htmlbodyString, publishDate, slug):
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
    if (isJekyll()):
      f.write(f'categories: blog\n')
    if (isHugo()):
      f.write(f'categories: \n')
      f.write(f'  - blog\n')
    f.write("---\n")
    f.write(processBody(htmlbodyString))


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
    sql = "select title, html, published_at, slug from posts"
    cur.execute(sql)

    # 実行結果を取得する
    for row in cur:
      createMarkdown(outputPath, row[0], row[1], row[2], row[3])

    cur.close

main()