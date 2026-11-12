// 結婚式 公式LINE の応答を担当する Webhook。
// 設置手順は line-setup/手順.md を参照。
// 席の情報は「席次表2」シートを毎回読むので、席次表を直せば返答も自動で変わる。

var CFG = {
  SEAT_SHEET: '席次表2',
  REGISTRY_SHEET: 'LINE登録者',
  ALIAS_SHEET: 'LINE別名',
  UNMATCHED_SHEET: 'LINE未照合',
  HUB_URL: 'https://kakky-lab.github.io/wedding-invitation/line/',
  ALBUM_URL: ''  // Google フォト共有アルバムのURL。未設定なら写真案内は出さない。
};

// 席次表2 のブロック: [卓, [[席コード列, 名前列], ...], 先頭行]
var BLOCKS = [
  ['A', [[2, 3], [4, 5]], 3],
  ['B', [[7, 8], [9, 10]], 3],
  ['C', [[17, 18], [19, 20]], 3],
  ['D', [[22, 23], [24, 25]], 3],
  ['E', [[7, 8], [9, 10]], 10],
  ['F', [[12, 13], [14, 15]], 10],
  ['G', [[17, 18], [19, 20]], 10],
  ['H', [[7, 8], [9, 10]], 17],
  ['J', [[17, 18], [19, 20]], 17]
];

function token_() {
  var t = PropertiesService.getScriptProperties().getProperty('CHANNEL_ACCESS_TOKEN');
  if (!t) throw new Error('CHANNEL_ACCESS_TOKEN がスクリプトプロパティに未設定です');
  return t;
}

/** 照合用の正規化。空白・敬称・括弧内を落とし、旧字を新字に寄せる。 */
function norm_(s) {
  var v = String(s == null ? '' : s);
  v = v.replace(/[（(][^）)]*[）)]/g, '');
  v = v.replace(/[\s　]+/g, '');
  v = v.replace(/(様|さま|さん|君|くん|ちゃん|氏)$/, '');
  var old = '髙﨑濱邊邉瀨齋藤栁冨', neu = '高崎浜辺辺瀬斎藤柳富';
  for (var i = 0; i < old.length; i++) v = v.split(old.charAt(i)).join(neu.charAt(i));
  return v;
}

function sheet_(name) {
  var sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(name);
  if (!sh) throw new Error('シートが見つかりません: ' + name);
  return sh;
}

/** 席次表2 を読んで {正規化名: {卓, 席, 正式名}} を返す。 */
function seatIndex_() {
  var sh = sheet_(CFG.SEAT_SHEET);
  // 列を増減されても落ちないように、実際のシートの大きさに合わせて読む
  var rows = Math.min(25, sh.getMaxRows()), cols = Math.min(29, sh.getMaxColumns());
  var grid = sh.getRange(1, 1, rows, cols).getValues();
  var at = function (r, c) {
    return (r <= rows && c <= cols) ? String(grid[r - 1][c - 1] || '').trim() : '';
  };
  var index = {};
  for (var b = 0; b < BLOCKS.length; b++) {
    var table = BLOCKS[b][0], pairs = BLOCKS[b][1], top = BLOCKS[b][2];
    for (var r = top; r < top + 5; r++) {
      for (var p = 0; p < pairs.length; p++) {
        var name = at(r, pairs[p][1]);
        if (name) index[norm_(name)] = { table: table, code: at(r, pairs[p][0]), name: name };
      }
    }
  }
  return index;
}

/** 別名シート（A列=別名 / B列=席次表2の正式名）を読む。 */
function aliasMap_() {
  var map = {};
  var sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CFG.ALIAS_SHEET);
  if (!sh || sh.getLastRow() < 2) return map;
  var rows = sh.getRange(2, 1, sh.getLastRow() - 1, 2).getValues();
  for (var i = 0; i < rows.length; i++) {
    if (rows[i][0] && rows[i][1]) map[norm_(rows[i][0])] = norm_(rows[i][1]);
  }
  return map;
}

/** 名前から席を引く。別名も辿る。見つからなければ null。 */
function lookupSeat_(text) {
  var key = norm_(text);
  if (!key) return null;
  var seats = seatIndex_();
  if (seats[key]) return seats[key];
  var alias = aliasMap_()[key];
  return alias && seats[alias] ? seats[alias] : null;
}

function seatMessage_(seat) {
  // 二次会はご案内していない方がいるため、ここでは触れない。
  return [
    seat.name + ' 様のお席をご案内します。',
    '',
    '🪑 ' + seat.table + ' 卓（席番号 ' + seat.code + '）',
    '受付でお名前をお伝えいただくと、係の者がご案内します。',
    '',
    '当日の流れ・会場までの行き方はこちら',
    CFG.HUB_URL
  ].join('\n');
}

/** 登録者シートに userId と名前を記録する（同じ userId は上書き）。 */
function register_(userId, seat) {
  var sh = sheet_(CFG.REGISTRY_SHEET);
  var last = sh.getLastRow();
  var ids = last >= 2 ? sh.getRange(2, 2, last - 1, 1).getValues() : [];
  var row = 0;
  for (var i = 0; i < ids.length; i++) if (ids[i][0] === userId) row = i + 2;
  var values = [[new Date(), userId, seat.name, seat.table, seat.code, '', '']];
  if (row) {
    sh.getRange(row, 1, 1, 5).setValues([[new Date(), userId, seat.name, seat.table, seat.code]]);
  } else {
    sh.getRange(last + 1, 1, 1, 7).setValues(values);
  }
}

/** 照合できなかった発言を記録して、増田さんが後から拾えるようにする。 */
function logUnmatched_(userId, text) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(CFG.UNMATCHED_SHEET);
  if (!sh) {
    sh = ss.insertSheet(CFG.UNMATCHED_SHEET);
    sh.getRange(1, 1, 1, 4).setValues([['日時', 'userId', '送られてきた文字', '対応メモ']]);
    sh.setFrozenRows(1);
  }
  sh.appendRow([new Date(), userId, text, '']);
}

function checkin_(userId) {
  var sh = sheet_(CFG.REGISTRY_SHEET);
  var last = sh.getLastRow();
  if (last < 2) return;
  var ids = sh.getRange(2, 2, last - 1, 1).getValues();
  for (var i = 0; i < ids.length; i++) {
    if (ids[i][0] === userId) { sh.getRange(i + 2, 6).setValue(new Date()); return; }
  }
}

var MENU = [
  '次のことばを送っていただくと、すぐにお返事します。',
  '',
  '「席」… ご自分のお席',
  '「流れ」… 当日のスケジュール',
  '「行き方」… 駅から会場までの案内',
  '「写真」… 写真・動画の共有アルバム',
  '「振込」… ご祝儀の事前お振込について',
  '「質問」… 服装・持ち物などのよくある質問',
  '「受付」… 当日の到着のお知らせ'
].join('\n');

function routeText_(userId, text) {
  var t = String(text || '').trim();
  if (/^(席|せき|席次|座席|どこ)/.test(t)) return seatOrAsk_(userId);
  if (/^(流れ|ながれ|スケジュール|時間|予定)/.test(t)) return '当日の流れはこちらにまとめています。\n' + CFG.HUB_URL + '#schedule';
  if (/^(行き方|アクセス|地図|会場|場所|道)/.test(t)) return '駅から会場までの行き方です。\n' + CFG.HUB_URL + '#access';
  if (/^(写真|しゃしん|動画|アルバム)/.test(t)) {
    return CFG.ALBUM_URL
      ? '写真・動画はこちらの共有アルバムへどうぞ。\n' + CFG.ALBUM_URL
      : '共有アルバムは準備中です。当日までにこちらでご案内します。';
  }
  if (/^(振込|振り込み|ふりこみ|お祝い|祝儀|ご祝儀|口座)/.test(t)) {
    return [
      'ご祝儀は当日の受付でも、事前のお振込でもお受けしています。',
      '',
      '事前のお振込は 11月16日（月）中 までにお願いいたします。',
      'みずほ銀行 本郷支店（075）',
      '普通 4179333',
      'マスダ サヤカ',
      '',
      'お振込みいただいた方は、当日受付でお名前をお伝えいただくだけで結構です。',
      'お気持ちだけで十分ですので、ご無理のないようにお願いいたします。',
      '',
      CFG.HUB_URL + '#gift'
    ].join('\n');
  }
  if (/^(質問|よくある質問|服装|持ち物|ヘアセット)/.test(t)) {
    return 'よくあるご質問をまとめています。\n' + CFG.HUB_URL + '#faq';
  }
  if (/^(受付|チェックイン|着きました|到着)/.test(t)) {
    checkin_(userId);
    return '貴重な1日をありがとうございます。\nたくさん飲んで、食べて、最後まで楽しんでいってください！';
  }
  if (/^(メニュー|ヘルプ|使い方)/.test(t)) return MENU;

  var seat = lookupSeat_(t);
  if (seat) { register_(userId, seat); return seatMessage_(seat); }
  logUnmatched_(userId, t);
  return [
    'ありがとうございます。恐れ入りますが、お名前が見つけられませんでした。',
    '姓と名を続けて（例：増田和也）お送りいただけますでしょうか。',
    '旧姓でご登録の場合もありますので、うまくいかないときはそのままお待ちください。新郎新婦が確認いたします。',
    '',
    MENU
  ].join('\n');
}

/** 登録済みなら席を返し、未登録なら名前を尋ねる。 */
function seatOrAsk_(userId) {
  var sh = sheet_(CFG.REGISTRY_SHEET);
  var last = sh.getLastRow();
  if (last >= 2) {
    var rows = sh.getRange(2, 2, last - 1, 2).getValues();
    for (var i = 0; i < rows.length; i++) {
      if (rows[i][0] === userId) {
        var seat = lookupSeat_(rows[i][1]);
        if (seat) return seatMessage_(seat);
      }
    }
  }
  return 'お席をご案内するために、お名前（フルネーム）をお送りください。\n例：増田和也';
}

var WELCOME = [
  'ご登録ありがとうございます。増田和也・加藤さや香です。',
  '',
  '2026年11月22日（日）、横浜 伊勢山ヒルズでお待ちしています。',
  'このアカウントから、当日のお席・スケジュール・会場までの行き方をご案内します。',
  '',
  'さっそくですが、お名前（フルネーム）をこのトークにお送りください。',
  'ご自分のお席をすぐにお返しします。',
  '',
  '例：増田和也'
].join('\n');

function reply_(replyToken, text) {
  var payload = { replyToken: replyToken, messages: [{ type: 'text', text: String(text).slice(0, 4900) }] };
  UrlFetchApp.fetch('https://api.line.me/v2/bot/message/reply', {
    method: 'post', contentType: 'application/json',
    headers: { Authorization: 'Bearer ' + token_() },
    payload: JSON.stringify(payload), muteHttpExceptions: true
  });
}

function handleEvent_(ev) {
  var userId = ev.source && ev.source.userId ? ev.source.userId : '';
  if (ev.type === 'follow') return reply_(ev.replyToken, WELCOME);
  if (ev.type === 'message' && ev.message && ev.message.type === 'text') {
    return reply_(ev.replyToken, routeText_(userId, ev.message.text));
  }
  if (ev.type === 'message' && ev.replyToken) {
    return reply_(ev.replyToken, 'ありがとうございます。文字でお送りいただけると、お席などをご案内できます。\n\n' + MENU);
  }
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
    var body = JSON.parse(e.postData.contents);
    var events = body.events || [];
    for (var i = 0; i < events.length; i++) {
      try {
        handleEvent_(events[i]);
      } catch (inner) {
        Logger.log('event error: ' + inner.message);
      }
    }
  } catch (err) {
    Logger.log('doPost error: ' + err.message);
  } finally {
    try { lock.releaseLock(); } catch (ignore) { /* 解放できなくても応答は返す */ }
  }
  return ContentService.createTextOutput(JSON.stringify({ ok: true }))
    .setMimeType(ContentService.MimeType.JSON);
}

function doGet() {
  return ContentService.createTextOutput('ok');
}

/** 設置確認用。エディタから実行して席が引けるか試す。 */
function test_lookup() {
  var seat = lookupSeat_('志佐陽');
  Logger.log(seat ? seatMessage_(seat) : '見つかりません');
}
