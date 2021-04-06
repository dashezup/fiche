"""Generate highlighted html for fiche pastes

requirements.txt:
- Pillow
- Pygments
"""
import os
import asyncio
import argparse
import subprocess
from PIL import Image
from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.formatters import HtmlFormatter, ImageFormatter

DOC_HTML = '''\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Paste | ezup.dev/p</title>
<meta property="og:title" content="Paste | ezup.dev/p" />
<meta property="og:description" \
content="Upload your pastes through netcat/bash/zsh - https://ezup.dev/p" />
<meta property="og:image" content="preview.png" />
<meta property="og:image:width" content="{width}">
<meta property="og:image:height" content="{height}">
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:dnt" content="on"/>
<link rel="stylesheet" href="../styles.css" type="text/css" />
</head>
<body>
<h2>&gt; <a href="../">ezpaste</a>: {fiche_id}</h2>
{code_html}
</body>
</html>
'''


async def generate_html_and_png(fiche_dir, fiche_id):
    fiche_paste = os.path.join(fiche_dir, fiche_id)
    txt = os.path.join(fiche_paste, 'index.txt')
    html = os.path.join(fiche_paste, 'index.html')
    png = os.path.join(fiche_paste, 'preview.png')
    with open(txt) as f_txt, open(png, 'wb') as f_png:
        code = f_txt.read()
        preview_code = "\n".join(code.split('\n')[:79])
        lexer = guess_lexer(code)
        image_formatter = ImageFormatter(
            font_name="Fira Mono",
            line_number_bg="#073642",
            line_number_fg="#586e75",
            style="solarized-dark"
        )
        f_png.write(highlight(preview_code, lexer, image_formatter))
    with open(html, 'w') as f_html, Image.open(png) as im:
        width, height = im.size
        formatter = HtmlFormatter(linenos=True, full=False, style="stata-dark")
        code_html = highlight(code, lexer, formatter)
        full_html = DOC_HTML.format(
            fiche_id=fiche_id,
            code_html=code_html,
            width=width,
            height=height
        )
        f_html.write(full_html)


async def main(args):
    log_tail = subprocess.Popen(
        ['tail', '-n0', '-f', args.log],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    try:
        while True:
            line = log_tail.stdout.readline().strip().decode('utf-8')
            if not line:
                print('- Empty line or file truncated')
                continue
            fiche_id = line.split()[0]
            print(fiche_id)
            await generate_html_and_png(args.dir, fiche_id)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Generate HTML and image preview for fiche pastes'
    )
    parser.add_argument('dir', help="fiche output directory")
    parser.add_argument('log', help="fiche log file")
    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args))
