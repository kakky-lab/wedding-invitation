#!/usr/bin/env python3
"""席次表2 から、LINEで配れる席次表の画像を作る。

  python3 seatchart.py        line-setup/seatchart.png を書き出す

卓の記号と顔ぶれの一覧です。会場内の配置図ではありません。
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.expanduser('~/.gsheets'))
import gs  # noqa: E402

SS = '10QQrOyDKassdp7K3qd7ewaxNORoqUj8ufDwUrDnmmj8'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seatchart.png')
MINCHO = '/System/Library/Fonts/ヒラギノ明朝 ProN.ttc'
GOTHIC = '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'

# 卓 → [(席コード列, 名前列)], 先頭行（1始まり）
BLOCKS = [
    ('A', [(2, 3), (4, 5)], 3), ('B', [(7, 8), (9, 10)], 3),
    ('C', [(17, 18), (19, 20)], 3), ('D', [(22, 23), (24, 25)], 3),
    ('E', [(7, 8), (9, 10)], 10), ('F', [(12, 13), (14, 15)], 10),
    ('G', [(17, 18), (19, 20)], 10), ('H', [(7, 8), (9, 10)], 17),
    ('J', [(17, 18), (19, 20)], 17),
]
LABELS = {
    'A': 'SPACE WALKER の皆さま', 'B': '早稲田広研 同期', 'C': '本郷・新卒の友人',
    'D': '大学時代の友人', 'E': '早稲田広研 先輩', 'F': '早稲田広研 同期',
    'G': 'redish の皆さま', 'H': '新郎 ご親族', 'J': '新婦 ご親族',
}
CREAM, INK, DEEP, MIST, SUB = (251, 254, 253), (44, 62, 61), (77, 192, 181), (234, 247, 245), (92, 124, 121)
W, COLS, SS_ = 1600, 3, 2


def seat_order(member):
    """A1, A2 ... A10 の順に並べる（文字列順だと A10 が A2 より前に来てしまう）。"""
    code = member[0]
    digits = ''.join(ch for ch in code if ch.isdigit())
    return (''.join(ch for ch in code if not ch.isdigit()), int(digits) if digits else 0)


def read_tables():
    grid = gs.get(SS, '席次表2!A1:AC25')

    def cell(r, c):
        row = grid[r - 1] if r - 1 < len(grid) else []
        return str(row[c - 1]).strip() if c - 1 < len(row) else ''

    tables = []
    for table, pairs, top in BLOCKS:
        members = []
        for r in range(top, top + 5):
            for ccode, cname in pairs:
                name = cell(r, cname)
                if name:
                    members.append((cell(r, ccode), name))
        members.sort(key=seat_order)
        tables.append((table, members))
    return tables


def card(d, x, y, w, h, table, members, fonts):
    f_tag, f_grp, f_name = fonts
    d.rounded_rectangle((x, y, x + w, y + h), 18 * SS_, fill=(255, 255, 255),
                        outline=MIST, width=2 * SS_)
    d.rounded_rectangle((x, y, x + w, y + 70 * SS_), 18 * SS_, fill=MIST)
    d.rectangle((x, y + 50 * SS_, x + w, y + 70 * SS_), fill=MIST)
    d.text((x + 22 * SS_, y + 16 * SS_), '%s 卓' % table, font=f_tag, fill=(31, 122, 114))
    d.text((x + 110 * SS_, y + 26 * SS_), LABELS.get(table, ''), font=f_grp, fill=SUB)
    ty = y + 88 * SS_
    for code, name in members:
        d.text((x + 24 * SS_, ty), code, font=f_grp, fill=DEEP)
        d.text((x + 86 * SS_, ty - 4 * SS_), name, font=f_name, fill=INK)
        ty += 40 * SS_


def main():
    tables = read_tables()
    rows = (len(tables) + COLS - 1) // COLS
    cw, pad, head = 480 * SS_, 26 * SS_, 150 * SS_
    ch = 88 * SS_ + 40 * SS_ * max(len(m) for _, m in tables) + 26 * SS_
    width, height = COLS * cw + (COLS + 1) * pad, head + rows * (ch + pad) + pad + 70 * SS_

    img = Image.new('RGB', (width, height), CREAM)
    d = ImageDraw.Draw(img)
    f_title = ImageFont.truetype(MINCHO, 46 * SS_)
    f_date = ImageFont.truetype(GOTHIC, 26 * SS_)
    fonts = (ImageFont.truetype(MINCHO, 38 * SS_), ImageFont.truetype(GOTHIC, 22 * SS_),
             ImageFont.truetype(MINCHO, 32 * SS_))

    d.rectangle((0, 0, width, head - 30 * SS_), fill=(47, 136, 128))
    d.text((pad + 10 * SS_, 32 * SS_), '席次のご案内', font=f_title, fill=(255, 255, 255))
    d.text((pad + 12 * SS_, 92 * SS_), '2026年11月22日（日）　伊勢山ヒルズ　ヴェネチア グランデ',
           font=f_date, fill=(226, 247, 244))

    for i, (table, members) in enumerate(tables):
        x = pad + (i % COLS) * (cw + pad)
        y = head + (i // COLS) * (ch + pad)
        card(d, x, y, cw, ch, table, members, fonts)

    d.text((pad + 10 * SS_, height - 56 * SS_),
           '※ 卓の記号と顔ぶれの一覧です。会場内の配置は当日、係の者がご案内します。',
           font=f_date, fill=SUB)

    img.resize((width // SS_, height // SS_), Image.LANCZOS).save(OUT, 'PNG', optimize=True)
    print('書き出しました:', OUT)
    print('合計 %d 名 / %d 卓' % (sum(len(m) for _, m in tables), len(tables)))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('ERROR:', exc, file=sys.stderr)
        sys.exit(1)
