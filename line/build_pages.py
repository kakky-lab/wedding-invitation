#!/usr/bin/env python3
"""公式LINEのリッチメニューから開く案内ページを、ボタンごとに1枚ずつ書き出す。

  python3 line/build_pages.py

出来るもの: line/index.html と line/{seat,schedule,access,gift,photo,faq}/index.html
中身を直すときは、このファイルの PAGES を編集して実行し直す。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://kakky-lab.github.io/wedding-invitation/line/'
ALBUM = ('https://www.weddingshare.me/weddings/an40deq9tzz7x6sz/'
         'UUT8Wd8jzhvbOCqGVkLdujfRGHOno7JU?openExternalBrowser=1&amp;type=link')

NAV = [
    ('seat', 'お席', 'お席の確認'),
    ('schedule', '当日の流れ', '当日の流れ'),
    ('access', '行き方', '会場への行き方'),
    ('gift', 'ご祝儀', 'ご祝儀・お振込'),
    ('photo', '写真', '写真・動画のご共有'),
    ('faq', 'よくある質問', 'よくあるご質問'),
]

CSS = """*{margin:0;padding:0;box-sizing:border-box}
:root{--tiffany:#81d8d0;--tiffany-deep:#4dc0b5;--tiffany-dark:#1f7a72;--tiffany-mist:#eaf7f5;
 --cream:#fbfefd;--white:#fff;--ink:#2c3e3d;--sub:#5c7c79;--gold:#c9a961;
 --serif-jp:'Shippori Mincho','Hiragino Mincho ProN','Yu Mincho',serif;
 --serif-en:'Cormorant Garamond','Times New Roman',serif}
html{scroll-behavior:smooth}
body{font-family:var(--serif-jp);background:var(--cream);color:var(--ink);line-height:1.9;
 -webkit-font-smoothing:antialiased;overflow-x:hidden}
.wrap{max-width:560px;margin:0 auto;padding:0 16px}
header{background:radial-gradient(ellipse at 50% 30%,#a6e0da 0%,#6bbcb4 50%,#2f8880 100%);
 color:#fff;text-align:center;padding:30px 16px 26px}
header .en{font-family:var(--serif-en);font-style:italic;font-size:.82rem;letter-spacing:.18em;opacity:.9}
header h1{font-size:1.32rem;font-weight:600;letter-spacing:.08em;margin:.35rem 0 .5rem}
header .meta{font-size:.82rem;opacity:.95;letter-spacing:.02em}
main{padding:26px 0 8px}
.lead{font-size:.9rem;color:var(--sub);margin-bottom:1rem}
.card{background:var(--white);border:1px solid var(--tiffany-mist);border-radius:12px;
 padding:18px 16px;margin-bottom:12px;box-shadow:0 1px 3px rgba(31,122,114,.05)}
.card h3{font-size:.98rem;font-weight:600;margin-bottom:.5rem}
.card p,.card li{font-size:.9rem}
.card ul{list-style:none;margin-top:.4rem}
.card ul li{padding-left:1.05em;position:relative;margin-bottom:.3rem}
.card ul li::before{content:'・';position:absolute;left:0;color:var(--tiffany-deep)}
.hero{background:linear-gradient(160deg,#eaf7f5,#fff);border:1px solid var(--tiffany);
 border-radius:14px;padding:22px 18px;text-align:center;margin-bottom:12px}
.hero .big{font-size:1.05rem;font-weight:600;margin-bottom:.6rem}
.hero .how{display:inline-block;background:var(--white);border:1px dashed var(--tiffany-deep);
 border-radius:10px;padding:12px 16px;margin-top:.7rem;font-size:.92rem;text-align:left}
.hero .how b{color:var(--tiffany-dark)}
.tl{position:relative;padding-left:20px;margin-top:.6rem}
.tl::before{content:'';position:absolute;left:4px;top:7px;bottom:7px;width:1px;background:var(--tiffany)}
.tl .row{position:relative;display:flex;gap:.8rem;padding:5px 0;align-items:baseline}
.tl .row::before{content:'';position:absolute;left:-20px;top:13px;width:9px;height:9px;
 border-radius:50%;background:var(--white);border:2px solid var(--tiffany-deep)}
.tl .row.key::before{background:var(--tiffany-deep)}
.tl time{font-family:var(--serif-en);font-size:1rem;color:var(--tiffany-dark);flex:none;width:3.3em}
.tl .what{font-size:.92rem}
.tl .what small{display:block;color:var(--sub);font-size:.8rem;line-height:1.6}
.note{font-size:.82rem;color:var(--sub);background:var(--tiffany-mist);border-radius:8px;
 padding:10px 12px;margin-top:.7rem}
.btn-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:.9rem}
.btn{flex:1 1 auto;min-width:46%;text-align:center;text-decoration:none;font-size:.86rem;
 padding:11px 10px;border-radius:999px;border:1px solid var(--tiffany-deep);
 color:var(--tiffany-dark);background:var(--white)}
.btn.fill{background:var(--tiffany-deep);color:#fff}
.map{border-radius:10px;overflow:hidden;margin-top:.8rem;aspect-ratio:16/10}
.map iframe{width:100%;height:100%;border:0;display:block}
.bank .deadline{display:block;background:var(--tiffany-dark);color:#fff;border-radius:8px;
 padding:9px 12px;font-size:.9rem;text-align:center;margin-bottom:.9rem}
.bank dl{display:grid;grid-template-columns:5.6em 1fr;gap:.35rem .6rem;font-size:.92rem}
.bank dt{color:var(--sub);font-size:.85rem}
.bank dd{font-weight:600;letter-spacing:.02em}
.bank .copy{width:100%;margin-top:.9rem;padding:11px;border-radius:999px;
 border:1px solid var(--tiffany-deep);background:var(--tiffany-deep);color:#fff;
 font-family:inherit;font-size:.88rem;cursor:pointer}
.bank .copy.done{background:var(--white);color:var(--tiffany-dark)}
details{background:var(--white);border:1px solid var(--tiffany-mist);border-radius:10px;
 margin-bottom:8px;overflow:hidden}
summary{padding:13px 15px;font-size:.92rem;font-weight:600;cursor:pointer;list-style:none;
 display:flex;justify-content:space-between;gap:.7rem;align-items:center}
summary::-webkit-details-marker{display:none}
summary::after{content:'＋';color:var(--tiffany-deep);flex:none;font-weight:400}
details[open] summary::after{content:'−'}
details .body{padding:0 15px 14px;font-size:.88rem;color:#3b4f4e}
.more{margin-top:28px;border-top:1px solid var(--tiffany-mist);padding-top:18px}
.more p{font-size:.82rem;color:var(--sub);margin-bottom:.6rem;letter-spacing:.04em}
.more ul{list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:8px}
.more a{display:block;text-align:center;text-decoration:none;font-size:.86rem;padding:12px 8px;
 border-radius:10px;background:var(--white);border:1px solid var(--tiffany-mist);color:var(--tiffany-dark)}
footer{text-align:center;padding:30px 16px 42px;color:var(--sub);font-size:.8rem}
footer .names{font-family:var(--serif-en);font-style:italic;font-size:1rem;
 color:var(--tiffany-dark);margin-bottom:.35rem}
.chk{margin-top:.2rem}
.chk .row{display:flex;gap:8px}
.chk input{flex:1 1 auto;min-width:0;font-family:inherit;font-size:1rem;padding:11px 12px;
 border:1px solid var(--tiffany);border-radius:10px;background:var(--white);color:var(--ink)}
.chk input:focus{outline:2px solid var(--tiffany-deep);outline-offset:-1px}
.chk button{flex:none;padding:11px 18px;border-radius:10px;border:1px solid var(--tiffany-deep);
 background:var(--tiffany-deep);color:#fff;font-family:inherit;font-size:.9rem;cursor:pointer}
.chk button:disabled{opacity:.5;cursor:default}
.chk .out{margin-top:.8rem;border-radius:10px;padding:14px 15px;font-size:.92rem;display:none}
.chk .out.show{display:block}
.chk .out b{display:block;font-size:1rem;margin-bottom:.3rem}
.chk .out small{display:block;color:var(--sub);font-size:.8rem;line-height:1.65;margin-top:.4rem}
.chk .out.ok{background:var(--tiffany-mist);border:1px solid var(--tiffany-deep)}
.chk .out.ok b{color:var(--tiffany-dark)}
.chk .out.wait{background:#fffaf0;border:1px solid #e6cf9a}
.chk .out.wait b{color:#9a7b2f}
.chk .out.none{background:#f7f9f9;border:1px solid var(--tiffany-mist)}
.chk .out .asof{display:block;margin-top:.55rem;padding-top:.5rem;font-size:.76rem;
 color:var(--sub);border-top:1px dotted rgba(92,124,121,.35)}
@media (max-width:360px){.btn{min-width:100%}.more ul{grid-template-columns:1fr}
 .chk .row{flex-wrap:wrap}.chk button{width:100%}}"""

SALT = 'iseyama-2026-1122'
OLD_KANJI, NEW_KANJI = '髙﨑濱邊邉瀨齋藤栁冨', '高崎浜辺辺瀬斎藤柳富'
HONORIFICS = ['様', 'さま', 'さん', 'くん', '君', 'ちゃん', '氏']


# 日本語を uXXXX 形式にしてJSへ埋め込む。手で書き写すと取り違えるため。
def js_str(text):
    esc = chr(92) + 'u%04x'
    return chr(39) + ''.join(esc % ord(c) for c in text) + chr(39)


PAGES = {}

PAGES['seat'] = """<div class="hero">
  <p class="big">お席は受付でご案内します</p>
  <p style="font-size:.88rem;color:var(--sub)">
    受付でお名前をお伝えいただければ、係の者がお席までご案内します。<br>
    卓の番号を覚えていなくても大丈夫です。
  </p>
  <div class="how">
    事前に知りたい方は、このLINEのトークに<br>
    <b>お名前（フルネーム）</b>をお送りください。<br>
    順にお返事します。
  </div>
</div>
<div class="card">
  <h3>受付のお時間</h3>
  <ul>
    <li>ご親族様　<strong>10:15</strong></li>
    <li>ご来賓　　<strong>10:35</strong></li>
  </ul>
  <p class="note">ご親族様とご来賓でお時間が異なります。挙式は 11:00 開始です。</p>
</div>
<div class="card">
  <h3>お席についてのお願い</h3>
  <ul>
    <li>アレルギーや苦手な食材は、挙式の1週間前までにお知らせください</li>
    <li>お子様連れの方は、人数とご年齢をお知らせいただけると助かります</li>
    <li>旧姓でご登録の場合、すぐにお答えできないことがあります</li>
  </ul>
</div>"""

PAGES['schedule'] = """<p class="lead">挙式・披露宴／伊勢山ヒルズ</p>
<div class="card">
  <div class="tl">
    <div class="row"><time>10:15</time><div class="what">ご親族様 受付</div></div>
    <div class="row"><time>10:30</time><div class="what">ご来賓控え室オープン</div></div>
    <div class="row key"><time>10:35</time><div class="what">ご来賓 受付開始<small>桜木町駅からのシャトルバスは 10:20 までにご乗車ください。ウェルカムスペースにイベントをご用意しています</small></div></div>
    <div class="row"><time>10:50</time><div class="what">挙式会場へご移動</div></div>
    <div class="row key"><time>11:00</time><div class="what">挙式（ヒストリア大聖堂）<small>キリスト教式。式の後にフラワーシャワーがあります</small></div></div>
    <div class="row"><time>11:30</time><div class="what">披露宴会場へご移動<small>軽食とドリンクをご用意しています</small></div></div>
    <div class="row"><time>11:45</time><div class="what">披露宴会場オープン</div></div>
    <div class="row key"><time>12:00</time><div class="what">披露宴 開宴<small>会場はヴェネチア グランデ</small></div></div>
    <div class="row"><time>14:10</time><div class="what">お見送り<small>お開きとなります</small></div></div>
  </div>
  <p class="note">受付のお時間がご親族様とご来賓で異なります。時刻は目安です。</p>
</div>
<div class="card">
  <h3>当日の持ち物</h3>
  <ul>
    <li>ご祝儀（事前にお振込みいただいた方は不要です）</li>
    <li>11月下旬の横浜は冷えます。羽織るものがあると安心です</li>
    <li>会場にクロークと更衣室がございます</li>
  </ul>
</div>"""

PAGES['access'] = """<p class="lead">伊勢山ヒルズ／〒220-0031 神奈川県横浜市西区宮崎町58-3</p>
<div class="card">
  <h3>電車とシャトルバス（おすすめ）</h3>
  <ul>
    <li>JR・市営地下鉄「<strong>桜木町駅</strong>」から<strong>無料シャトルバス</strong>で約10分</li>
    <li>乗り場は <strong>南改札（東口）</strong> を出て <strong>YOKOHAMA AIR CABIN 正面の貸切観光バス乗り場</strong></li>
    <li>日曜は <strong>毎時00分から10分間隔</strong> で運行しています</li>
    <li>ご来賓の受付は10:35です。<strong>10:20までのバス</strong>にご乗車ください</li>
  </ul>
  <div class="btn-row">
    <a class="btn fill" href="https://www.google.com/maps/dir/?api=1&amp;destination=%E4%BC%8A%E5%8B%A2%E5%B1%B1%E3%83%92%E3%83%AB%E3%82%BA" target="_blank" rel="noopener">現在地から経路を見る</a>
    <a class="btn" href="https://www.bestbridal.co.jp/yokohama/iseyama-hills/access/" target="_blank" rel="noopener">会場のアクセス案内</a>
  </div>
  <div class="map">
    <iframe src="https://maps.google.com/maps?q=%E4%BC%8A%E5%8B%A2%E5%B1%B1%E3%83%92%E3%83%AB%E3%82%BA%20%E7%A5%9E%E5%A5%88%E5%B7%9D%E7%9C%8C%E6%A8%AA%E6%B5%9C%E5%B8%82%E8%A5%BF%E5%8C%BA%E5%AE%AE%E5%B4%8E%E7%94%BA58-3&amp;z=16&amp;output=embed"
      title="伊勢山ヒルズ 地図" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
  </div>
</div>
<div class="card">
  <h3>徒歩の場合</h3>
  <ul>
    <li>桜木町駅から徒歩で約15分（紅葉坂をのぼります）</li>
    <li>坂道ですので、ヒールの方はシャトルバスをおすすめします</li>
  </ul>
</div>
<div class="card">
  <h3>お車の場合</h3>
  <ul>
    <li>首都高速神奈川1号横羽線「みなとみらい」出口より約500m／県立青少年センター前左手</li>
    <li>駐車場は台数に限りがあり<strong>事前予約制</strong>です。公共交通機関のご利用をおすすめしています</li>
  </ul>
</div>"""

PAGES['gift'] = """<p class="lead">当日の受付でも、事前のお振込でもお受けしています。</p>
<div class="card bank">
  <strong class="deadline">事前にお振込の場合は 11月13日（金）中まで</strong>
  <dl>
    <dt>銀行名</dt><dd>みずほ銀行</dd>
    <dt>支店名</dt><dd>本郷支店（075）</dd>
    <dt>口座種別</dt><dd>普通預金</dd>
    <dt>口座番号</dt><dd>4179333</dd>
    <dt>口座名義</dt><dd>マスダ サヤカ</dd>
  </dl>
  <button class="copy" id="copy-bank" type="button">口座情報をコピー</button>
  <p class="note" style="text-align:left">
    お振込みいただいた方は、当日受付でお名前をお伝えいただくだけで結構です。
    当日お持ちいただいても、もちろん大丈夫です。
    お気持ちだけで十分ですので、ご無理のないようにお願いいたします。
  </p>
</div>
<div class="card chk">
  <h3>お振込状況の確認</h3>
  <p style="font-size:.88rem;color:var(--sub);margin-bottom:.7rem">
    お名前を入れていただくと、こちらで確認できているかどうかが分かります。
  </p>
  <div class="row">
    <input id="chk-name" type="text" inputmode="text" autocomplete="name"
      placeholder="例）増田 和也" aria-label="お名前">
    <button id="chk-go" type="button">確認</button>
  </div>
  <div class="out" id="chk-out" role="status" aria-live="polite"></div>
  <p class="note" style="text-align:left">
    お振込から反映までに数日いただくことがあります。
    行き違いの際は何卒ご容赦ください。うまく出ないときはLINEのトークにお名前をお送りください。
  </p>
</div>"""

PAGES['photo'] = """<p class="lead">当日撮っていただいた写真や動画を、ぜひ分けてください。</p>
<div class="hero">
  <p class="big">共有アルバムができました</p>
  <p style="font-size:.88rem;color:var(--sub)">
    下のボタンから、写真も動画もそのままアップロードできます。<br>
    みなさんが載せてくださったものも、同じ場所でご覧いただけます。
  </p>
  <div class="btn-row">
    <a class="btn fill" href="ALBUM_URL" target="_blank" rel="noopener">写真・動画をアップロードする</a>
    <a class="btn" href="ALBUM_URL" target="_blank" rel="noopener">みんなの写真を見る</a>
  </div>
</div>
<div class="card">
  <h3>使い方</h3>
  <ul>
    <li>アプリのインストールやログインは要りません</li>
    <li>スマートフォンのカメラロールからそのまま選べます</li>
    <li>動画もお送りいただけます</li>
    <li>枚数に制限はありません。何枚でも大歓迎です</li>
  </ul>
  <p class="note">挙式前・当日・二次会、いつのお写真でも構いません。じゃんじゃんお待ちしています。</p>
</div>
<div class="card">
  <h3>撮影のお願い</h3>
  <ul>
    <li>挙式中の撮影は、式の進行の妨げにならない範囲でお願いします</li>
    <li>フラッシュとシャッター音にご配慮いただけますと助かります</li>
    <li>後日、二人からもプロの写真を共有させてください</li>
  </ul>
</div>"""

PAGES['faq'] = """<p class="lead">迷われたときはお気軽にLINEでお尋ねください。</p>
<details><summary>服装はどうしたらよいですか</summary>
  <div class="body">挙式・披露宴にふさわしい服装でお越しください。男性はスーツ、女性はワンピースやセットアップなどが一般的です。11月下旬の横浜は冷えますので、羽織るものがあると安心です。会場内にクロークがございます。</div></details>
<details><summary>ご祝儀はどうすればよいですか</summary>
  <div class="body">当日受付でお預かりしています。事前のお振込をご希望の場合は <strong>11月13日（金）中まで</strong>に、<a href="GIFT_URL">こちらの口座</a>へお願いいたします。お気持ちだけで十分ですので、ご無理のないようにお願いいたします。</div></details>
<details><summary>当日ヘアセットをしたいのですが</summary>
  <div class="body">会場近く（桜木町・みなとみらい周辺）の美容室をご案内できます。LINEのトークに「ヘアセット」とお送りください。式場内の美容室もご予約可能ですので、ご希望の方はお早めにお知らせください。</div></details>
<details><summary>着替える場所はありますか</summary>
  <div class="body">会場に更衣室がございます。遠方からお越しの方、お仕事帰りの方もご利用いただけます。</div></details>
<details><summary>子どもを連れて行っても大丈夫ですか</summary>
  <div class="body">もちろん大歓迎です。お子様向けのお食事や設備のご用意がありますので、人数とお年齢をLINEでお知らせいただけますと助かります。</div></details>
<details><summary>食べられないものがあります</summary>
  <div class="body">アレルギーや苦手なものは、できるだけ早めにLINEでお知らせください。会場と調整いたします。挙式の<strong>1週間前まで</strong>にいただけると確実です。</div></details>
<details><summary>遅れそうなとき・急に行けなくなったとき</summary>
  <div class="body">LINEのトークにそのままお送りください。当日も確認しています。お料理の手配がありますので、わかった時点でお知らせいただけると助かります。</div></details>
<details><summary>駐車場はありますか</summary>
  <div class="body">台数に限りがあり事前予約制です。公共交通機関のご利用をおすすめしています。桜木町駅から無料シャトルバスが出ています。</div></details>"""

COPY_JS = """<script>
(function () {
  var btn = document.getElementById('copy-bank');
  if (!btn || !navigator.clipboard) { if (btn) { btn.style.display = 'none'; } return; }
  var text = 'みずほ銀行 本郷支店（075）普通 4179333 マスダ サヤカ';
  btn.addEventListener('click', function () {
    navigator.clipboard.writeText(text).then(function () {
      btn.textContent = 'コピーしました';
      btn.classList.add('done');
      setTimeout(function () {
        btn.textContent = '口座情報をコピー';
        btn.classList.remove('done');
      }, 2200);
    }).catch(function () { btn.textContent = 'コピーできませんでした'; });
  });
})();
</script>"""


LOOKUP_JS = """<script>
(function () {
  var input = document.getElementById('chk-name');
  var btn = document.getElementById('chk-go');
  var out = document.getElementById('chk-out');
  if (!input || !btn || !out) { return; }
  var SALT = __SALT__;
  var OLD = __OLD__;
  var NEW = __NEW__;
  var SUF = [__SUF__];
  var table = null;
  var asof = '';

  function norm(raw) {
    var v = String(raw || ''), o = '', depth = 0, i, ch;
    for (i = 0; i < v.length; i++) {
      ch = v.charAt(i);
      if (ch === '\uff08' || ch === '(') { depth++; }
      else if (ch === '\uff09' || ch === ')') { depth = Math.max(0, depth - 1); }
      else if (depth === 0) { o += ch; }
    }
    o = o.replace(/[\s\u3000]+/g, '');
    for (i = 0; i < SUF.length; i++) {
      if (o.length > SUF[i].length && o.slice(-SUF[i].length) === SUF[i]) {
        o = o.slice(0, -SUF[i].length);
        break;
      }
    }
    var r = '';
    for (i = 0; i < o.length; i++) {
      var k = OLD.indexOf(o.charAt(i));
      r += k < 0 ? o.charAt(i) : NEW.charAt(k);
    }
    return r;
  }

  function hash(name) {
    var bytes = new TextEncoder().encode(SALT + '|' + name);
    return crypto.subtle.digest('SHA-256', bytes).then(function (buf) {
      var a = Array.prototype.slice.call(new Uint8Array(buf), 0, 6);
      return a.map(function (b) { return ('0' + b.toString(16)).slice(-2); }).join('');
    });
  }

  function show(cls, title, body, note) {
    out.className = 'out show ' + cls;
    out.innerHTML = '<b></b><span></span>' + (note ? '<small></small>' : '');
    out.querySelector('b').textContent = title;
    out.querySelector('span').textContent = body;
    if (note) { out.querySelector('small').textContent = note; }
  }

  function stamp() {
    if (!asof) { return; }
    var p = document.createElement('small');
    p.className = 'asof';
    p.textContent = '\u203b ' + asof + ' \u6642\u70b9\u306e\u60c5\u5831\u3067\u3059';
    out.appendChild(p);
  }

  function render(rec) {
    if (!rec) {
      show('none', '\u304a\u540d\u524d\u304c\u898b\u3064\u304b\u308a\u307e\u305b\u3093\u3067\u3057\u305f',
        '\u6f22\u5b57\u306e\u30d5\u30eb\u30cd\u30fc\u30e0\u3067\u3082\u3046\u4e00\u5ea6\u304a\u8a66\u3057\u304f\u3060\u3055\u3044\u3002',
        '\u65e7\u59d3\u3084\u304a\u547c\u3073\u540d\u3067\u306f\u51fa\u306a\u3044\u3053\u3068\u304c\u3042\u308a\u307e\u3059\u3002\u304a\u624b\u6570\u3067\u3059\u304cLINE\u306e\u30c8\u30fc\u30af\u3078\u304a\u540d\u524d\u3092\u304a\u9001\u308a\u304f\u3060\u3055\u3044\u3002');
      stamp();
      return;
    }
    if (rec.s === 1) {
      show('ok', '\u3054\u5165\u91d1\u3092\u78ba\u8a8d\u3057\u3066\u304a\u308a\u307e\u3059',
        '\u3042\u308a\u304c\u3068\u3046\u3054\u3056\u3044\u307e\u3059\u3002\u5f53\u65e5\u306f\u53d7\u4ed8\u3067\u304a\u540d\u524d\u3092\u304a\u4f1d\u3048\u304f\u3060\u3055\u3044\u3002'
        + (rec.d ? '\uff08' + rec.d + '\uff09' : ''));
    } else if (rec.s === 0) {
      show('wait', '\u307e\u3060\u78ba\u8a8d\u3067\u304d\u3066\u304a\u308a\u307e\u305b\u3093',
        '\u4e8b\u524d\u632f\u8fbc\u3067\u627f\u3063\u3066\u304a\u308a\u307e\u3059\u3002\u671f\u65e5\u306f 11\u670813\u65e5\uff08\u91d1\uff09\u4e2d\u307e\u3067\u3067\u3059\u3002',
        '\u304a\u632f\u8fbc\u307f\u6e08\u307f\u306e\u5834\u5408\u306f\u884c\u304d\u9055\u3044\u304b\u3082\u3057\u308c\u307e\u305b\u3093\u3002\u6570\u65e5\u304a\u3044\u3066\u3082\u3046\u4e00\u5ea6\u3054\u78ba\u8a8d\u304f\u3060\u3055\u3044\u3002');
    } else {
      show('none', '\u5f53\u65e5\u53d7\u4ed8\u3067\u304a\u9810\u304b\u308a\u3057\u307e\u3059',
        '\u4e8b\u524d\u306e\u304a\u632f\u8fbc\u307f\u306f\u627f\u3063\u3066\u304a\u308a\u307e\u305b\u3093\u3002\u304a\u6c17\u6301\u3061\u3060\u3051\u3067\u5341\u5206\u3067\u3059\u3002');
    }
    stamp();
  }

  function load() {
    if (table) { return Promise.resolve(table); }
    return fetch(__DATA__, { cache: 'no-store' }).then(function (r) {
      if (!r.ok) { throw new Error('status ' + r.status); }
      return r.json();
    }).then(function (j) {
      asof = j.asof || '';
      table = j.entries || {};
      return table;
    });
  }

  function run() {
    var name = norm(input.value);
    if (!name) {
      show('none', '\u304a\u540d\u524d\u3092\u5165\u308c\u3066\u304f\u3060\u3055\u3044', '');
      return;
    }
    btn.disabled = true;
    load().then(function (t) {
      return hash(name).then(function (h) { render(t[h]); });
    }).catch(function () {
      show('none', '\u3046\u307e\u304f\u8aad\u307f\u8fbc\u3081\u307e\u305b\u3093\u3067\u3057\u305f',
        '\u6642\u9593\u3092\u304a\u3044\u3066\u304a\u8a66\u3057\u304f\u3060\u3055\u3044\u3002LINE\u306e\u30c8\u30fc\u30af\u3078\u304a\u540d\u524d\u3092\u304a\u9001\u308a\u3044\u305f\u3060\u3044\u3066\u3082\u7d50\u69cb\u3067\u3059\u3002');
    }).then(function () { btn.disabled = false; });
  }

  btn.addEventListener('click', run);
  input.addEventListener('keydown', function (e) { if (e.key === 'Enter') { run(); } });
})();
</script>"""

LOOKUP_JS = (LOOKUP_JS
             .replace('__DATA__', "'" + BASE + "payment.json'")
             .replace('__SALT__', js_str(SALT))
             .replace('__OLD__', js_str(OLD_KANJI))
             .replace('__NEW__', js_str(NEW_KANJI))
             .replace('__SUF__', ', '.join(js_str(s) for s in HONORIFICS)))


def head(title, desc):
    """各ページ共通の <head>。検索には出さない。"""
    return """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>%s｜増田・加藤 結婚式</title>
<meta name="description" content="%s">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;600&family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&display=swap" rel="stylesheet">
<style>%s</style>
</head>
<body>""" % (title, desc, CSS)


def header(title):
    return """
<header>
  <p class="en">Wedding Information</p>
  <h1>%s</h1>
  <p class="meta">2026年11月22日（日）　伊勢山ヒルズ</p>
</header>
""" % title


def more_links(current):
    """ほかの案内ページへの行き先。今いるページは出さない。"""
    items = ''.join(
        '    <li><a href="%s%s/">%s</a></li>\n' % (BASE, key, short)
        for key, short, _ in NAV if key != current)
    return """
  <nav class="more">
    <p>ほかのご案内</p>
    <ul>
%s    </ul>
  </nav>
""" % items


def footer():
    return """
<footer>
  <p class="names">Kazuya <span style="color:var(--gold)">&amp;</span> Sayaka</p>
  <p>当日、皆さまにお会いできるのを楽しみにしています。</p>
  <p style="margin-top:.5rem">ご不明な点はLINEのトークにお送りください</p>
</footer>
</body>
</html>
"""


def build_page(key, title, body):
    html = head(title, '%s｜増田和也・加藤さや香 結婚式のご案内' % title)
    html += header(title)
    html += '<div class="wrap">\n<main>\n%s\n</main>\n%s</div>\n' % (body, more_links(key))
    if key == 'gift':
        html += COPY_JS + '\n' + LOOKUP_JS + '\n'
    return html + footer()


def build_index():
    cards = ''.join(
        '    <li><a href="%s%s/">%s</a></li>\n' % (BASE, key, long) for key, _, long in NAV)
    body = """<p class="lead">ご覧になりたいものをお選びください。</p>
  <nav class="more" style="margin-top:0;border-top:0;padding-top:0">
    <ul>
%s    </ul>
  </nav>""" % cards
    html = head('当日のご案内', '増田和也・加藤さや香 結婚式 当日のご案内')
    html += header('当日のご案内')
    html += '<div class="wrap">\n<main>\n%s\n</main>\n</div>\n' % body
    return html + footer()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(text)
    return len(text)


def main():
    written = []
    for key, _, title in NAV:
        body = PAGES[key].replace('GIFT_URL', BASE + 'gift/')
        body = body.replace('ALBUM_URL', ALBUM)
        size = write(os.path.join(HERE, key, 'index.html'), build_page(key, title, body))
        written.append(('line/%s/index.html' % key, size))
    written.append(('line/index.html', write(os.path.join(HERE, 'index.html'), build_index())))
    for name, size in written:
        print('  %-26s %5.1f KB' % (name, size / 1024))
    print('%d ページを書き出しました。' % len(written))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('ERROR:', exc, file=sys.stderr)
        sys.exit(1)
