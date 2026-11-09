#!/usr/bin/env python3
"""公式LINEのリッチメニュー画像を作り、LINEに登録して既定メニューにする。

  python3 richmenu.py            画像だけ作る（line-setup/richmenu.png）
  python3 richmenu.py --upload   画像を作ってLINEへ登録し、既定メニューに設定する

トークンは ~/.wedding-line/token か、環境変数 WEDDING_LINE_TOKEN から読む。
"""
import json
import os
import sys
import urllib.error
import urllib.request

from PIL import Image, ImageDraw, ImageFont

W, H = 2500, 1686
COLS, ROWS = 3, 2
SS = 2  # 書き出し前に縮小するための拡大率
MINCHO = '/System/Library/Fonts/ヒラギノ明朝 ProN.ttc'
GOTHIC = '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'richmenu.png')

TOKEN_FILE = os.path.expanduser('~/.wedding-line/token')


def read_token():
    """チャネルアクセストークンを ~/.wedding-line/token か環境変数から読む。"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, encoding='utf-8') as fh:
            tok = fh.read().strip()
        if tok:
            return tok
    tok = os.environ.get('WEDDING_LINE_TOKEN', '').strip()
    if not tok:
        raise RuntimeError(
            'トークンが見つかりません。次のどちらかで渡してください。\n'
            '  1) printf %s \'トークン\' > ~/.wedding-line/token\n'
            '  2) export WEDDING_LINE_TOKEN=\'トークン\'')
    return tok

# (ラベル, 補助文, タップで送られる文字, アイコン種別)
TILES = [
    ('お席の確認', 'あなたの卓と席番号', '席', 'seat'),
    ('当日の流れ', '受付・挙式・披露宴', '流れ', 'clock'),
    ('会場への行き方', '桜木町からシャトルバス', '行き方', 'pin'),
    ('よくある質問', '服装・ご祝儀・持ち物', '質問', 'question'),
    ('写真・動画', '共有アルバム', '写真', 'camera'),
    ('受付（当日）', '着いたら押してください', '受付', 'check'),
]

TIFFANY = (129, 216, 208)
DEEP = (77, 192, 181)
DARK = (31, 122, 114)


def gradient(size):
    """ティファニーブルーの斜めグラデーションを作る。"""
    w, h = size
    img = Image.new('RGB', size)
    px = img.load()
    for y in range(h):
        for x in range(0, w, 8):
            t = (x / w * 0.55 + y / h * 0.45)
            c = tuple(int(DEEP[i] + (DARK[i] - DEEP[i]) * t) for i in range(3))
            for dx in range(min(8, w - x)):
                px[x + dx, y] = c
    return img


def icon(d, kind, cx, cy, r, color, lw):
    """タイルのアイコンを線画で描く。"""
    box = (cx - r, cy - r, cx + r, cy + r)
    if kind == 'seat':
        d.ellipse(box, outline=color, width=lw)
        d.ellipse((cx - r * .22, cy - r * .22, cx + r * .22, cy + r * .22), fill=color)
    elif kind == 'clock':
        d.ellipse(box, outline=color, width=lw)
        d.line((cx, cy, cx, cy - r * .55), fill=color, width=lw)
        d.line((cx, cy, cx + r * .42, cy + r * .2), fill=color, width=lw)
    elif kind == 'pin':
        d.ellipse((cx - r * .62, cy - r, cx + r * .62, cy + r * .24), outline=color, width=lw)
        d.polygon([(cx - r * .3, cy + r * .05), (cx + r * .3, cy + r * .05), (cx, cy + r)], fill=color)
        d.ellipse((cx - r * .2, cy - r * .5, cx + r * .2, cy - r * .1), outline=color, width=lw)
    elif kind == 'question':
        d.ellipse(box, outline=color, width=lw)
        d.arc((cx - r * .34, cy - r * .62, cx + r * .34, cy + r * .06), 170, 20, fill=color, width=lw)
        d.line((cx, cy - r * .06, cx, cy + r * .24), fill=color, width=lw)
        d.ellipse((cx - r * .07, cy + r * .44, cx + r * .07, cy + r * .58), fill=color)
    elif kind == 'camera':
        d.rounded_rectangle((cx - r, cy - r * .62, cx + r, cy + r * .72), r * .22,
                            outline=color, width=lw)
        d.ellipse((cx - r * .34, cy - r * .3, cx + r * .34, cy + r * .38), outline=color, width=lw)
        d.rounded_rectangle((cx - r * .4, cy - r * .86, cx - r * .02, cy - r * .58), r * .1,
                            outline=color, width=lw)
    elif kind == 'check':
        d.ellipse(box, outline=color, width=lw)
        d.line((cx - r * .42, cy + r * .04, cx - r * .08, cy + r * .4), fill=color, width=int(lw * 1.4))
        d.line((cx - r * .08, cy + r * .4, cx + r * .46, cy - r * .36), fill=color, width=int(lw * 1.4))


def centered(d, text, font, cx, y, fill):
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=font)
    d.text((cx - (x1 - x0) / 2 - x0, y), text, font=font, fill=fill)
    return y1 - y0


def draw_menu():
    img = gradient((W * SS, H * SS)).convert('RGB')
    d = ImageDraw.Draw(img)
    f_main = ImageFont.truetype(MINCHO, 76 * SS)
    f_sub = ImageFont.truetype(GOTHIC, 40 * SS)
    tw, th = W * SS // COLS, H * SS // ROWS

    for i, (label, sub, _, kind) in enumerate(TILES):
        cx = (i % COLS) * tw + tw // 2
        top = (i // COLS) * th
        icon(d, kind, cx, top + int(th * .34), int(th * .145), (255, 255, 255), 7 * SS)
        centered(d, label, f_main, cx, top + int(th * .56), (255, 255, 255))
        centered(d, sub, f_sub, cx, top + int(th * .745), (226, 247, 244))

    for c in range(1, COLS):
        d.line((c * tw, 0, c * tw, H * SS), fill=(255, 255, 255, 60), width=3 * SS)
    d.line((0, th, W * SS, th), fill=(255, 255, 255, 60), width=3 * SS)

    img = img.resize((W, H), Image.LANCZOS)
    img.save(OUT, 'PNG', optimize=True)
    return OUT


def menu_body():
    tw, th = W // COLS, H // ROWS
    areas = []
    for i, (label, _, send, _) in enumerate(TILES):
        areas.append({
            'bounds': {'x': (i % COLS) * tw, 'y': (i // COLS) * th, 'width': tw, 'height': th},
            'action': {'type': 'message', 'label': label[:20], 'text': send},
        })
    return {'size': {'width': W, 'height': H}, 'selected': True,
            'name': '結婚式ゲスト用メニュー', 'chatBarText': 'メニュー', 'areas': areas}


def api(method, url, body=None, ctype='application/json', token=None, raw=None):
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(url, data=data, method=method, headers={
        'Authorization': 'Bearer ' + token, 'Content-Type': ctype})
    try:
        with urllib.request.urlopen(req) as res:
            text = res.read().decode()
            return json.loads(text) if text.strip().startswith('{') else {}
    except urllib.error.HTTPError as err:
        raise RuntimeError('%s %s -> %s %s' % (method, url, err.code, err.read().decode()[:400]))


def upload(path, token):
    menu = api('POST', 'https://api.line.me/v2/bot/richmenu', menu_body(), token=token)
    rid = menu['richMenuId']
    api('POST', 'https://api-data.line.me/v2/bot/richmenu/%s/content' % rid,
        ctype='image/png', token=token, raw=open(path, 'rb').read())
    api('POST', 'https://api.line.me/v2/bot/user/all/richmenu/%s' % rid, token=token)
    return rid


def main():
    path = draw_menu()
    print('画像を書き出しました:', path)
    if '--upload' not in sys.argv:
        print('LINEへ登録するには --upload を付けて実行してください。')
        return
    print('登録しました。richMenuId =', upload(path, read_token()))
    print('既定のリッチメニューに設定しました。')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('ERROR:', exc, file=sys.stderr)
        sys.exit(1)
