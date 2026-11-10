#!/usr/bin/env python3
"""公式LINEのリッチメニューを登録する。

  python3 line-setup/richmenu.py            送信用の画像を作って確認するだけ
  python3 line-setup/richmenu.py --upload   LINEへ登録し、既定のメニューにする

絵柄は line-setup/richmenu.png（増田さん作成）をそのまま使う。
LINEは1MBまでなので、送る前にJPEGへ落としてから渡す。
トークンは ~/.wedding-line/token か、環境変数 WEDDING_LINE_TOKEN から読む。
"""
import io
import json
import os
import sys
import urllib.error
import urllib.request

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, 'richmenu.png')
SEND = os.path.join(HERE, 'richmenu-send.jpg')
TOKEN_FILE = os.path.expanduser('~/.wedding-line/token')

W, H = 2500, 1686
MAX_BYTES = 950 * 1024

HUB = 'https://kakky-lab.github.io/wedding-invitation/line/'

# 絵柄の枠を実測した位置に合わせ、すき間も取りこぼさないよう広げてある。
# 上段のまん中は見出し（WEDDING RECEPTION）なので、押しても何も起きない。
TILES = [
    ('スケジュール', 'schedule/', (0, 0, 865, 835)),
    ('アクセス', 'access/', (1633, 0, 867, 835)),
    ('席次表', 'seat/', (0, 835, 865, 851)),
    ('御祝儀・お振込状況', 'gift/', (865, 835, 768, 851)),
    ('写真＆動画共有', 'photo/', (1633, 835, 867, 851)),
]


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
            "  1) printf %s 'トークン' > ~/.wedding-line/token\n"
            "  2) export WEDDING_LINE_TOKEN='トークン'")
    return tok


def prepare():
    """絵柄を2500×1686に整え、1MB未満のJPEGにして送信用に書き出す。"""
    if not os.path.exists(ART):
        raise RuntimeError('絵柄が見つかりません: %s' % ART)
    img = Image.open(ART).convert('RGB')
    if img.size != (W, H):
        print('  %dx%d を %dx%d に合わせます' % (img.size[0], img.size[1], W, H))
        img = img.resize((W, H), Image.LANCZOS)
    for quality in (95, 92, 90, 88, 85, 80, 75):
        buf = io.BytesIO()
        img.save(buf, 'JPEG', quality=quality, optimize=True, subsampling=0)
        if buf.tell() <= MAX_BYTES:
            with open(SEND, 'wb') as fh:
                fh.write(buf.getvalue())
            print('  送信用: %s  品質%d  %.0f KB' % (
                os.path.basename(SEND), quality, buf.tell() / 1024))
            return SEND
    raise RuntimeError('1MB未満にできませんでした。絵柄を見直してください。')


def menu_body():
    """タップ領域の定義。URLを開くだけなのでWebhookが無くても動く。"""
    areas = []
    for label, path, (x, y, w, h) in TILES:
        areas.append({
            'bounds': {'x': x, 'y': y, 'width': w, 'height': h},
            'action': {'type': 'uri', 'label': label[:20], 'uri': HUB + path},
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


def clear_old(token, keep):
    """古いリッチメニューを消す。残しておくと一覧が散らかるため。"""
    try:
        menus = api('GET', 'https://api.line.me/v2/bot/richmenu/list', token=token)
    except RuntimeError as exc:
        print('  古いメニューの確認に失敗しました:', exc, file=sys.stderr)
        return 0
    gone = 0
    for menu in menus.get('richmenus', []):
        rid = menu.get('richMenuId')
        if not rid or rid == keep:
            continue
        try:
            api('DELETE', 'https://api.line.me/v2/bot/richmenu/%s' % rid, token=token)
            gone += 1
        except RuntimeError as exc:
            print('  %s を消せませんでした: %s' % (rid, exc), file=sys.stderr)
    return gone


def upload(path, token):
    """登録して既定のメニューにし、古いものを片づける。"""
    menu = api('POST', 'https://api.line.me/v2/bot/richmenu', menu_body(), token=token)
    rid = menu['richMenuId']
    with open(path, 'rb') as fh:
        api('POST', 'https://api-data.line.me/v2/bot/richmenu/%s/content' % rid,
            ctype='image/jpeg', token=token, raw=fh.read())
    api('POST', 'https://api.line.me/v2/bot/user/all/richmenu/%s' % rid, token=token)
    print('  古いメニューを %d 件消しました' % clear_old(token, rid))
    return rid


def main():
    path = prepare()
    print('タップ領域:')
    for label, dest, (x, y, w, h) in TILES:
        print('  %-10s (%4d,%4d) %4d×%4d  -> %s' % (label, x, y, w, h, dest))
    if '--upload' not in sys.argv:
        print('\nLINEへ登録するには --upload を付けて実行してください。')
        return
    print('\n登録しました。richMenuId =', upload(path, read_token()))
    print('既定のリッチメニューに設定しました。')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('ERROR:', exc, file=sys.stderr)
        sys.exit(1)
