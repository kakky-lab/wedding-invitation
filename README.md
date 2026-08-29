# 増田和也・加藤さや香 Web招待状

## 3つのバージョン

| 招待する相手 | URL |
| --- | --- |
| 一次会と二次会の両方 | https://kakky-lab.github.io/wedding-invitation/ |
| 一次会（挙式・披露宴）のみ | https://kakky-lab.github.io/wedding-invitation/ceremony/ |
| 二次会のみ | https://kakky-lab.github.io/wedding-invitation/party/ |

回答はスプレッドシートの「招待状の種類」列に、どのバージョンから届いたかが記録されます。

## 直すとき

**`index.html` だけを編集**してから、次を実行すると3バージョンすべてに反映されます。

```
python3 build.py
```

`ceremony/` と `party/` の中身は build.py が自動生成するので、直接編集しないでください。
build.py は CSS/JS の参照URLに版番号も付け直します。これをやらないと、
一度サイトを開いたことがあるゲストのブラウザが古いファイルを使い続けてしまいます。

- 文章・写真の並び → `index.html`
- 見た目・配色 → `assets/style.css`
- 動き・送信処理 → `assets/app.js`
- 写真 → `images/`

## 会場写真を追加する

`index.html` の次の2か所に `<img>` を入れると表示されます（1〜2枚）。

- 式場：`<div class="venue-photos" id="venue-photos-ceremony">`
- 二次会：`<div class="venue-photos" id="venue-photos-party">`

例：
```html
<div class="venue-photos" id="venue-photos-ceremony">
  <img src="images/venue-1.jpg" alt="" loading="lazy">
  <img src="images/venue-2.jpg" alt="" loading="lazy">
</div>
```
1枚だけのときは `class="venue-photos single"` にすると横幅いっぱいで表示されます。
最後に `python3 build.py` を忘れずに。

## 入力の下書き

出欠フォームは入力のたびに内容をゲスト自身のブラウザへ保存しています。
ページを閉じても続きから入力でき、送信が完了すると自動で消えます。
（写真は容量が大きいため保存対象外です。90日経った下書きは破棄されます）

## 公開

`main` ブランチに push すると GitHub Pages へ自動で反映されます（1分ほど）。
