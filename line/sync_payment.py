#!/usr/bin/env python3
"""招待リストの入金確認欄を読み、ご祝儀ページ用の照会ファイルを書き出す。

  python3 line/sync_payment.py          状況を表示して line/payment.json を更新
  python3 line/sync_payment.py --dry    書き出さずに内容だけ見る

公開される payment.json にお名前は入らない。お名前を正規化してソルトを
付けたハッシュだけを並べるので、ファイル単体では誰のものか分からない。
入金確認（U列）にチェックを入れたあと、これを実行して push すると反映される。
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.expanduser('~/.gsheets'))

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'payment.json')
SS = '10QQrOyDKassdp7K3qd7ewaxNORoqUj8ufDwUrDnmmj8'
SALT = 'iseyama-2026-1122'

COL = {'名前': 1, '回答名': 10, '披露宴': 12, 'お支払い': 14,
       '照合キー': 18, '入金確認': 20, '入金メモ': 21}
OLD, NEW = '髙﨑濱邊邉瀨齋藤栁冨', '高崎浜辺辺瀬斎藤柳富'


def norm(s):
    """表記ゆれを吸収する。line/gift の JS と同じ規則にそろえてある。"""
    v = str(s or '')
    out, depth = [], 0
    for ch in v:
        if ch in '（(':
            depth += 1
        elif ch in '）)':
            depth = max(0, depth - 1)
        elif depth == 0:
            out.append(ch)
    v = ''.join(out)
    v = ''.join(c for c in v if not c.isspace() and c != '　')
    for suf in ('様', 'さま', 'さん', 'くん', '君', 'ちゃん', '氏'):
        if v.endswith(suf) and len(v) > len(suf):
            v = v[:-len(suf)]
            break
    return ''.join(NEW[OLD.index(c)] if c in OLD else c for c in v)


def key(name):
    """正規化したお名前からハッシュを作る。"""
    n = norm(name)
    if not n:
        return ''
    return hashlib.sha256((SALT + '|' + n).encode('utf-8')).hexdigest()[:12]


def cell(row, name):
    i = COL[name]
    return str(row[i]).strip() if len(row) > i else ''


def aliases(gs):
    """LINE別名シートから「別名 → 正式名」を読む。"""
    try:
        rows = gs.get(SS, 'LINE別名!A2:B200')
    except Exception as exc:
        print('  別名シートが読めませんでした:', exc, file=sys.stderr)
        return []
    return [(r[0].strip(), r[1].strip()) for r in rows
            if len(r) > 1 and str(r[0]).strip() and str(r[1]).strip()]


def status_of(row):
    """0=事前振込（未確認） 1=事前振込（確認済） 2=当日受付。対象外は None。"""
    if cell(row, '披露宴') == '欠席':
        return None
    if cell(row, 'お支払い') != '事前振込':
        return 2
    return 1 if cell(row, '入金確認').upper() == 'TRUE' else 0


def collect(gs):
    """招待リストと別名シートから、ハッシュと状況の対応表を作る。"""
    rows = gs.get(SS, '招待リスト!A4:V80')
    alias = aliases(gs)
    entries, people = {}, []
    for row in rows:
        canon = cell(row, '照合キー') or cell(row, '名前')
        state = status_of(row)
        if not canon or state is None:
            continue
        names = {canon, cell(row, '名前'), cell(row, '回答名')}
        names |= {a for a, official in alias if norm(official) == norm(canon)}
        rec = {'s': state}
        memo = cell(row, '入金メモ')
        if state == 1 and memo:
            rec['d'] = memo
        for n in names:
            k = key(n)
            if k:
                entries[k] = rec
        people.append((canon, state, len(names)))
    return entries, people


def main():
    import gs
    entries, people = collect(gs)
    done = sum(1 for _, s, _ in people if s == 1)
    wait = sum(1 for _, s, _ in people if s == 0)
    day = sum(1 for _, s, _ in people if s == 2)
    print('事前振込  確認済 %d名 ／ 未確認 %d名' % (done, wait))
    print('当日受付  %d名' % day)
    print('照会キー  %d件（別名・旧姓ふくむ）' % len(entries))
    if wait:
        print('\n未確認のまま:')
        for name, s, _ in people:
            if s == 0:
                print('  -', name)
    if '--dry' in sys.argv:
        print('\n--dry のため書き出していません。')
        return
    body = {'updated': __import__('datetime').date.today().isoformat(),
            'entries': entries}
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(body, fh, ensure_ascii=False, separators=(',', ':'))
    print('\n書き出しました: line/payment.json')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('ERROR:', exc, file=sys.stderr)
        sys.exit(1)
