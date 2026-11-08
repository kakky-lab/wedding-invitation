#!/usr/bin/env python3
"""公式LINEから一斉配信する。送る前に必ず --dry-run で中身を確認すること。

  python3 broadcast.py --list                 台本の一覧を見る
  python3 broadcast.py 前日 --dry-run         送らずに宛先と本文を確認する
  python3 broadcast.py 前日 --send            実際に送る

チャネルアクセストークンは環境変数 WEDDING_LINE_TOKEN から読む。
配信通数は料金プランの無料枠を消費する（応答メッセージは消費しない）。
"""
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.expanduser('~/.gsheets'))
import gs  # noqa: E402

SS = '10QQrOyDKassdp7K3qd7ewaxNORoqUj8ufDwUrDnmmj8'
HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.join(HERE, 'messages.json')
PLACEHOLDER = '【ここに'


def token():
    t = os.environ.get('WEDDING_LINE_TOKEN', '').strip()
    if not t:
        raise RuntimeError('環境変数 WEDDING_LINE_TOKEN にチャネルアクセストークンを入れてください')
    return t


def load_plan():
    with open(PLAN, encoding='utf-8') as fh:
        return {k: v for k, v in json.load(fh).items() if not k.startswith('_')}


def registry():
    """LINE登録者シートから [(userId, 名前)] を返す。"""
    rows = gs.get(SS, 'LINE登録者!A2:E200')
    return [(str(r[1]).strip(), str(r[2]).strip())
            for r in rows if len(r) > 2 and str(r[1]).strip()]


def nijikai_names():
    """招待リストで二次会が出席の人の名前（照合名も含む）を集合で返す。"""
    out = set()
    for r in gs.get(SS, '招待リスト!B4:N90'):
        r = (list(r) + [''] * 13)[:13]
        if str(r[12]).strip() == '出席':
            for key in (r[0], r[9]):
                if str(key).strip():
                    out.add(str(key).strip())
    return out


def recipients(target):
    reg = registry()
    if target == 'all':
        return reg
    if target == '二次会':
        names = nijikai_names()
        return [x for x in reg if x[1] in names]
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
    push([u for u, _ in people], item['text'], token())
    print('✅ %d 名へ送信しました。' % len(people))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('ERROR:', exc, file=sys.stderr)
        sys.exit(1)
