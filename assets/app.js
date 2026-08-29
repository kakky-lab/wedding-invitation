/* ═══════════════════════════════════════════════
   増田和也・加藤さや香 Web招待状
   3バージョン（全体 / 一次会のみ / 二次会のみ）共通スクリプト
   ═══════════════════════════════════════════════ */

// ▼ Google Apps Script の「ウェブアプリのURL」
const GAS_URL = 'https://script.google.com/macros/s/AKfycbyG_6thziPz6ZB0Knip9EoKhBGsWNcRMkOV5ousddjXpEXR-KiPSXqEQky9-oz9YUWMJQ/exec';

const MAX_PHOTOS = 20;
const MAX_DIMENSION = 1600;   // 送信前にこのサイズへ縮小して負荷を軽減

const VARIANT = document.body.dataset.variant || 'both';   // both | ceremony | party

/* ── バージョンに応じて 使わない項目を無効化する ──
   非表示のままだと未入力の必須項目でフォームが送信できなくなるため
   disabled にして FormData からも外す */
(function applyVariant(){
  document.querySelectorAll('[data-v]').forEach(el => {
    const belongsTo = el.dataset.v;
    const hidden = (VARIANT === 'ceremony' && belongsTo === 'party')
                || (VARIANT === 'party'    && belongsTo === 'ceremony');
    if (!hidden) return;
    el.querySelectorAll('input, textarea, select').forEach(f => {
      f.disabled = true;
      f.required = false;
    });
  });
  // 二次会のみの回では 二次会の出欠を必須にする
  if (VARIANT === 'party') {
    document.querySelectorAll('input[name="partyAttendance"]').forEach(r => { r.required = true; });
    const badge = document.querySelector('#party-attendance-badge');
    if (badge) { badge.textContent = '必須'; badge.className = 'required'; }
  }
})();

/* ── オープニング：封筒 → 便箋 → 招待状 ── */
(function initOpening(){
  const opening  = document.getElementById('opening');
  const envelope = document.getElementById('envelope');
  if (!opening || !envelope) return;

  const inner  = opening.querySelector('.opening-inner');
  const letter = document.getElementById('letter');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let opened = false;

  function viewportH(){
    return (window.visualViewport && window.visualViewport.height)
        || document.documentElement.clientHeight
        || window.innerHeight || 0;
  }

  // 便箋を上へ（lift）／封筒を下へ（drop）動かす量を画面の高さから求める。
  // 便箋を少しだけ封筒に挿したまま 全体が画面中央に収まるようにしている。
  function measureTravel(){
    const vh = viewportH();
    if (!vh) return;
    const box = inner.getBoundingClientRect();
    const H = box.height, Lh = letter.offsetHeight;
    if (!H || !Lh) return;

    const base = H * 0.06;                    // .letter の bottom:6%
    const overlap = Math.min(40, H * 0.18);   // 封筒に残す差し込み分

    const sum  = H - base - overlap;                  // lift + drop
    const diff = vh - 2 * box.bottom + base + Lh;     // drop - lift
    let lift = Math.max(0, (sum - diff) / 2);
    const drop = Math.max(0, (sum + diff) / 2);

    const maxLift = Math.max(0, (box.bottom - base) - Lh - 8);
    lift = Math.min(lift, maxLift);
    const lift2 = Math.min(maxLift, Math.max(lift, (box.bottom - base) - Lh / 2 - vh / 2));

    letter.style.setProperty('--lift',  lift  + 'px');
    letter.style.setProperty('--lift2', lift2 + 'px');
    inner.style.setProperty('--drop',   drop  + 'px');
  }
  measureTravel();
  window.addEventListener('resize', () => { if (!opened) measureTravel(); });

  function reveal(){
    opening.classList.add('done');
    document.body.classList.remove('letter-locked');
    document.body.classList.add('revealed');
    runFadeIn();
    setTimeout(() => { opening.style.display = 'none'; }, 1000);
  }

  function open(){
    if (opened) return;
    opened = true;
    if (reduced) { reveal(); return; }
    measureTravel();
    opening.classList.add('opened');                              // フタが開き 便箋が出てくる
    setTimeout(() => opening.classList.add('unfolding'), 1650);   // 便箋が開く
    setTimeout(reveal, 2450);                                     // 招待状へ
  }

  envelope.addEventListener('click', open);
  opening.addEventListener('click', open);   // 封筒の外をタップしても開く
})();

/* ── スクロールに応じたフェードイン ── */
function runFadeIn(){
  document.querySelectorAll('.fade-in').forEach(el => {
    if (el.getBoundingClientRect().top < window.innerHeight * 0.9) el.classList.add('visible');
  });
}
window.addEventListener('scroll', runFadeIn, { passive: true });
runFadeIn();

/* ── 写真ギャラリー（横スクロール＋左右ボタン） ── */
(function initGallery(){
  const track = document.getElementById('g-track');
  if (!track) return;
  const prev = document.querySelector('.g-nav.prev');
  const next = document.querySelector('.g-nav.next');
  const dots = document.getElementById('g-dots');
  const slides = Array.from(track.children);

  slides.forEach((_, i) => {
    const b = document.createElement('button');
    b.className = 'g-dot' + (i === 0 ? ' active' : '');
    b.type = 'button';
    b.setAttribute('aria-label', `${i + 1}枚目の写真へ`);
    b.addEventListener('click', () => scrollToSlide(i));
    dots.appendChild(b);
  });

  function scrollToSlide(i){
    const s = slides[i];
    if (!s) return;
    // スライドが中央に来る位置までスクロールする
    track.scrollTo({ left: s.offsetLeft - (track.clientWidth - s.clientWidth) / 2, behavior: 'smooth' });
  }

  function currentIndex(){
    const center = track.scrollLeft + track.clientWidth / 2;
    let best = 0, bestDist = Infinity;
    slides.forEach((s, i) => {
      const d = Math.abs(s.offsetLeft + s.clientWidth / 2 - center);
      if (d < bestDist) { bestDist = d; best = i; }
    });
    return best;
  }

  function sync(){
    const i = currentIndex();
    dots.querySelectorAll('.g-dot').forEach((d, n) => d.classList.toggle('active', n === i));
    prev.disabled = track.scrollLeft <= 2;
    next.disabled = track.scrollLeft >= track.scrollWidth - track.clientWidth - 2;
  }

  prev.addEventListener('click', () => scrollToSlide(Math.max(0, currentIndex() - 1)));
  next.addEventListener('click', () => scrollToSlide(Math.min(slides.length - 1, currentIndex() + 1)));
  track.addEventListener('scroll', () => { clearTimeout(track._t); track._t = setTimeout(sync, 90); }, { passive: true });
  window.addEventListener('resize', sync);
  sync();
})();

/* ── お支払い方法：事前振込を選んだら振込先を表示 ── */
document.querySelectorAll('input[name="giftMethod"]').forEach(r => {
  r.addEventListener('change', () => {
    const card = document.getElementById('bank-card');
    if (card) card.classList.toggle('show', r.value === '事前振込' && r.checked);
  });
});

/* ── 思い出の写真 ── */
const photoInput  = document.getElementById('photo-input');
const fileCount   = document.getElementById('file-count');
const filePreview = document.getElementById('file-preview');
let selectedFiles = [];

if (photoInput) {
  photoInput.addEventListener('change', () => {
    const incoming = Array.from(photoInput.files);
    if (selectedFiles.length + incoming.length > MAX_PHOTOS) {
      alert('お一人様の上限は20枚までです。');
      photoInput.value = '';
      return;
    }
    selectedFiles = selectedFiles.concat(incoming);
    photoInput.value = '';
    renderPreview();
  });
}

function renderPreview(){
  fileCount.textContent = selectedFiles.length > 0 ? `${selectedFiles.length} / ${MAX_PHOTOS} 枚選択中` : '';
  filePreview.innerHTML = '';
  selectedFiles.forEach(file => {
    const img = document.createElement('img');
    img.src = URL.createObjectURL(file);
    filePreview.appendChild(img);
  });
}

// 画像を縮小してBase64化（送信データ量を抑えるため）
function resizeAndEncode(file){
  return new Promise((resolve, reject) => {
    const img = new Image();
    const reader = new FileReader();
    reader.onload = e => { img.src = e.target.result; };
    reader.onerror = reject;
    img.onload = () => {
      let { width, height } = img;
      if (width > MAX_DIMENSION || height > MAX_DIMENSION) {
        const scale = MAX_DIMENSION / Math.max(width, height);
        width = Math.round(width * scale);
        height = Math.round(height * scale);
      }
      const canvas = document.createElement('canvas');
      canvas.width = width; canvas.height = height;
      canvas.getContext('2d').drawImage(img, 0, 0, width, height);
      resolve({ name: file.name, type: 'image/jpeg', data: canvas.toDataURL('image/jpeg', 0.82).split(',')[1] });
    };
    img.onerror = reject;
    reader.readAsDataURL(file);
  });
}

/* ── 送信 ── */
(function initForm(){
  const form = document.getElementById('rsvp-form');
  if (!form) return;
  const submitBtn = document.getElementById('submit-btn');
  const errorMsg  = document.getElementById('error-msg');

  const VARIANT_LABEL = { both: '全体版', ceremony: '一次会のみ', party: '二次会のみ' };

  form.addEventListener('submit', async e => {
    e.preventDefault();
    errorMsg.style.display = 'none';
    submitBtn.disabled = true;
    submitBtn.textContent = '送信中…';

    try {
      const fd = new FormData(form);
      const photos = await Promise.all(selectedFiles.map(resizeAndEncode));

      const res = await fetch(GAS_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
        body: JSON.stringify({
          name:            fd.get('name') || '',
          nameKana:        fd.get('nameKana') || '',
          email:           fd.get('email') || '',
          tel:             fd.get('tel') || '',
          attendance:      fd.get('attendance') || '',
          allergy:         fd.get('allergy') || '',
          giftMethod:      fd.get('giftMethod') || '',
          message:         fd.get('message') || '',
          partyAttendance: fd.get('partyAttendance') || '',
          variant:         VARIANT_LABEL[VARIANT] || VARIANT,
          photos
        })
      });
      const result = await res.json();
      if (result.result !== 'success') throw new Error(result.message || 'unknown error');

      form.style.display = 'none';
      const thanks = document.getElementById('thanks');
      thanks.style.display = 'block';
      thanks.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } catch (err) {
      errorMsg.style.display = 'block';
      submitBtn.disabled = false;
      submitBtn.textContent = '回答を送信する';
    }
  });
})();
