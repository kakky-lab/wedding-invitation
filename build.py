#!/usr/bin/env python3
"""
index.html（全体版）から 一次会のみ / 二次会のみ の2バージョンを生成する。

  python3 build.py

index.html だけを編集すれば 3バージョンすべてに反映される。
サブフォルダへ置くため assets/ と images/ の参照を ../ に書き換えている。
"""
import re, pathlib

ROOT = pathlib.Path(__file__).parent
SRC  = ROOT / 'index.html'

VARIANTS = {
    'ceremony': {
        'title': '増田和也 ・ 加藤さや香 ご結婚式 招待状',
        'desc':  '増田和也・加藤さや香 結婚式のご案内　2026年11月22日（日）伊勢山ヒルズ',
        'og':    '2026年11月22日（日）伊勢山ヒルズ　ご出欠のご回答をお願いいたします',
    },
    'party': {
        'title': '増田和也 ・ 加藤さや香 結婚式二次会 ご案内',
        'desc':  '増田和也・加藤さや香 結婚式二次会のご案内　2026年11月22日（日）バビーズ ランドマークプラザ',
        'og':    '2026年11月22日（日）バビーズ ランドマークプラザ　ご出欠のご回答をお願いいたします',
    },
}

def build(name, meta):
    html = SRC.read_text(encoding='utf-8')
    html = html.replace('data-variant="both"', f'data-variant="{name}"')
    # サブフォルダから見た相対パスへ
    html = html.replace('href="assets/', 'href="../assets/')
    html = html.replace('src="assets/',  'src="../assets/')
    html = html.replace('src="images/',  'src="../images/')
    # メタ情報
    html = re.sub(r'<title>.*?</title>', f'<title>{meta["title"]}</title>', html, count=1)
    html = re.sub(r'(<meta name="description" content=")[^"]*(")', rf'\g<1>{meta["desc"]}\g<2>', html, count=1)
    html = re.sub(r'(<meta property="og:title" content=")[^"]*(")', rf'\g<1>{meta["title"]}\g<2>', html, count=1)
    html = re.sub(r'(<meta property="og:description" content=")[^"]*(")', rf'\g<1>{meta["og"]}\g<2>', html, count=1)

    out = ROOT / name
    out.mkdir(exist_ok=True)
    (out / 'index.html').write_text(html, encoding='utf-8')
    print(f'{name}/index.html  ({len(html)} chars)')

if __name__ == '__main__':
    for name, meta in VARIANTS.items():
        build(name, meta)
