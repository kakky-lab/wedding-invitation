#!/usr/bin/env python3
"""公式LINEから一斉配信する。送る前に必ず --dry-run で中身を確認すること。

  python3 broadcast.py --list                 台本の一覧を見る
  python3 broadcast.py 前日 --dry-run         送らずに宛先と本文を確認する
  python3 broadcast.py 前日 --send            実際に送る

トークンは ~/.wedding-line/token か、環境変数 WEDDING_LINE_TOKEN から読む。
配信通数は料金プランの無料枠を消費する（応答メッセージは消費しない）。
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.expanduser('~/.gsheets'))
import gs  # noqa: E402

SS = '10QQrOyDKassdp7K3qd7ewaxNORoqUj8ufDwUrDnmmj8'
HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.join(HERE, 'messages.json')
PLACEHOLDER = '【ここに'


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


def load_plan():
    with open(PLAN, encoding='utf-8') as fh:
        return {k: v for k, v in json.load(fh).items() if not k.startswith('_')}


def registry():
    """LINE登録者シートから [(userId, 名前)] を返す。"""
    rows = gs.get(SS, 'LINE登録者!A2:E200')
    return [(str(r[1]).strip(), str(r[2]).strip())
            for r in rows if len(r) > 2 and str(r[1]).strip()]


OLD_KANJI, NEW_KANJI = '髙﨑濱邊邉瀨齋藤栁冨', '高崎浜辺辺瀬斎藤柳富'


def norm(s):
    """LineBot.gs の norm_ と同じ正規化。登録者名と招待リスト表記を突き合わせるため。"""
    v = re.sub(r'[（(][^）)]*[）)]', '', str(s or ''))
    v = re.sub(r'[\s\u3000]+', '', v)
    v = re.sub(r'(様|さま|さん|君|くん|ちゃん|氏)$', '', v)
    for o, n in zip(OLD_KANJI, NEW_KANJI):
        v = v.replace(o, n)
    return v


def alias_map():
    """LINE別名シートから {別名: 正式名} を正規化済みで返す。"""
    out = {}
    for row in gs.get(SS, 'LINE別名!A2:B200'):
        if len(row) > 1 and row[0] and row[1]:
            out[norm(row[0])] = norm(row[1])
    return out


def nijikai_keys():
    """二次会にご招待した方の名前を、正規化キーの集合で返す。
       招待リストはニックネーム表記のことがあるため、別名表で正式名へ寄せる。"""
    alias = alias_map()
    keys = set()
    for r in gs.get(SS, '招待リスト!B4:N90'):
        r = (list(r) + [''] * 13)[:13]
        if str(r[12]).strip() != '出席':
            continue
        for raw in (r[0], r[9]):
            k = norm(raw)
            if k:
                keys.add(alias.get(k, k))
    return keys


def recipients(target):
    reg = registry()
    if target == 'all':
        return reg
    if target == '二次会':
        keys = nijikai_keys()
        return [x for x in reg if norm(x[1]) in keys]
    if target == '披露宴':
        return reg  # 席が引けた人＝披露宴出席者なので登録者と同じ
    raise RuntimeError('target が不正です: %s' % target)


def push(user_ids, text, tok):
    """multicast は1回500人まで。結婚式の規模なら1回で収まる。"""
    body = {'to': user_ids[:500], 'messages': [{'type': 'text', 'text': text[:4900]}]}
    req = urllib.request.Request(
        'https://api.line.me/v2/bot/message/multicast',
        data=json.dumps(body).encode(), method='POST',
        headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as err:
        raise RuntimeError('配信に失敗: %s %s' % (err.code, err.read().decode()[:400]))


def show(key, item, people):
    print('=' * 56)
    print('台本: %s   送信予定日: %s   宛先: %s' % (key, item.get('send_on', '-'), item['target']))
    print('宛先 %d 名: %s' % (len(people), '、'.join(n for _, n in people[:8]) +
                              ('… ほか' if len(people) > 8 else '')))
    print('-' * 56)
    print(item['text'])
    print('=' * 56)


def main():
    plan = load_plan()
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = {a for a in sys.argv[1:] if a.startswith('--')}

    if '--list' in flags or not args:
        for k, v in plan.items():
            print('%-10s %s  宛先=%s' % (k, v.get('send_on', '-'), v['target']))
        return

    key = args[0]
    if key not in plan:
        raise RuntimeError('その台本はありません: %s（--list で確認）' % key)
    item = plan[key]
    people = recipients(item['target'])
    show(key, item, people)

    if PLACEHOLDER in item['text']:
        print('⚠️ 本文に未記入の【ここに…】が残っています。messages.json を埋めてください。')
    if not people:
        print('⚠️ 宛先が0名です。まだ誰も友だち追加していないか、名前の登録が済んでいません。')
    if '--send' not in flags:
        print('※ 送信していません。実際に送るには --send を付けてください。')
        return
    if PLACEHOLDER in item['text']:
        raise RuntimeError('未記入の箇所があるため送信を中止しました。')
    push([u for u, _ in people], item['text'], read_token())
    print('✅ %d 名へ送信しました。' % len(people))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('ERROR:', exc, file=sys.stderr)
        sys.exit(1)
