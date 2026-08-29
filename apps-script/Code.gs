// 結婚式招待状フォーム用 Google Apps Script
// 使い方は同フォルダの deploy-instructions.txt を参照してください。

const SHEET_NAME = '回答一覧';
const PHOTO_FOLDER_NAME = '結婚式_ゲスト写真';

const HEADERS = [
  'タイムスタンプ', 'お名前', 'ふりがな', 'メールアドレス', '電話番号',
  '結婚式参加可否', 'アレルギー', 'お支払い方法', 'メッセージ', '写真リンク',
  '二次会参加可否', '招待状の種類'
];

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const sheet = getOrCreateSheet();

    const photoLinks = savePhotos(data.name, data.photos);

    sheet.appendRow([
      new Date(),
      data.name || '',
      data.nameKana || '',
      data.email || '',
      data.tel || '',
      data.attendance || '',
      data.allergy || '',
      data.giftMethod || '',
      data.message || '',
      photoLinks,
      data.partyAttendance || '',
      data.variant || ''
    ]);

    return jsonResponse({ result: 'success' });
  } catch (err) {
    return jsonResponse({ result: 'error', message: err.message });
  }
}

function getOrCreateSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
  }
  ensureHeaders(sheet);
  return sheet;
}

// 見出し行が古い（列が足りない・名称が違う）場合だけ書き直す。
// 既存の回答データには手を触れない。
function ensureHeaders(sheet) {
  const width = Math.max(sheet.getLastColumn(), HEADERS.length);
  const current = sheet.getRange(1, 1, 1, width).getValues()[0];
  const same = HEADERS.every(function (h, i) { return current[i] === h; });
  if (same) return;

  sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
  sheet.setFrozenRows(1);
}

function savePhotos(name, photos) {
  if (!photos || photos.length === 0) return '';

  const folder = getOrCreateFolder(PHOTO_FOLDER_NAME);
  const guestFolder = folder.createFolder(`${name || '無記名'}_${new Date().getTime()}`);
  const links = [];

  photos.forEach(photo => {
    const blob = Utilities.newBlob(
      Utilities.base64Decode(photo.data),
      photo.type,
      photo.name
    );
    const file = guestFolder.createFile(blob);
    file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    links.push(file.getUrl());
  });

  return links.join('\n');
}

function getOrCreateFolder(name) {
  const folders = DriveApp.getFoldersByName(name);
  if (folders.hasNext()) return folders.next();
  return DriveApp.createFolder(name);
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
