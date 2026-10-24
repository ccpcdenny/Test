// 台灣十六張麻將台數表（常見規則，可依各地習慣調整）
const YAKU = [
  {id:'menqing', n:'門清', t:1},
  {id:'zimo', n:'自摸', t:1, auto:true},
  {id:'mqzm', n:'門清自摸', t:3, note:'取代門清+自摸'},
  {id:'zf', n:'三元牌刻', t:1, multi:3},
  {id:'wind', n:'圈/門風刻', t:1, multi:2},
  {id:'flower', n:'花牌', t:1, multi:8},
  {id:'flowerset', n:'花槓(一組)', t:2, multi:2},
  {id:'haidi', n:'海底撈月', t:1},
  {id:'gangshang', n:'槓上開花', t:1},
  {id:'qianggang', n:'搶槓', t:1},
  {id:'duting', n:'獨聽/單吊', t:1},
  {id:'pinghu', n:'平胡', t:2},
  {id:'quanqiu', n:'全求人', t:2},
  {id:'sanan', n:'三暗刻', t:2},
  {id:'hunyise', n:'混一色', t:4},
  {id:'pengpeng', n:'碰碰胡', t:4},
  {id:'xiaosanyuan', n:'小三元', t:4},
  {id:'sian', n:'四暗刻', t:5},
  {id:'qingyise', n:'清一色', t:8},
  {id:'dasanyuan', n:'大三元', t:8},
  {id:'xiaosixi', n:'小四喜', t:8},
  {id:'wuan', n:'五暗刻', t:8},
  {id:'ziyise', n:'字一色', t:16},
  {id:'dasixi', n:'大四喜', t:16},
  {id:'tianhu', n:'天胡', t:16},
  {id:'dihu', n:'地胡', t:16},
];

const $ = s => document.querySelector(s);
const load = (k, d) => { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } };
const save = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} };

let S = load('mj', {names:['東家','南家','西家','北家'], base:100, perTai:20, scores:[0,0,0,0], history:[]});
let pick = {}; let winType = 'zimo'; let streak = 0;
const persist = () => save('mj', S);

function fillSelects() {
  for (const id of ['winner','loser','dealer']) {
    const el = $('#'+id), v = el.value;
    el.innerHTML = S.names.map((n,i)=>`<option value="${i}">${n}</option>`).join('');
    if (v) el.value = v;
  }
  if ($('#loser').value === $('#winner').value) $('#loser').value = (+$('#winner').value + 1) % 4;
}

function renderYaku() {
  $('#yaku').innerHTML = YAKU.filter(y=>!y.auto).map(y => {
    const c = pick[y.id] || 0;
    const ctl = y.multi ? `<span class="cnt"><button data-m="-1">−</button>${c}<button data-m="1">＋</button></span>` : `<small>${y.t}台</small>`;
    return `<div class="chip ${c?'on':''}" data-id="${y.id}"><span>${y.n}${y.multi?`<small> ${y.t}台</small>`:''}</span>${ctl}</div>`;
  }).join('');
}

function calc() {
  let tai = 0; const names = [];
  for (const y of YAKU) {
    const c = y.id==='zimo' ? (winType==='zimo' && !pick.mqzm ? 1 : 0) : (pick[y.id]||0);
    if (y.id==='menqing' && pick.mqzm) continue;
    if (c) { tai += y.t*c; names.push(y.n + (c>1?`×${c}`:'')); }
  }
  const W = +$('#winner').value, D = +$('#dealer').value, L = +$('#loser').value;
  const dealerTai = 1 + 2*streak;
  const payers = winType==='zimo' ? [0,1,2,3].filter(i=>i!==W) : [L];
  const pays = payers.map(p => {
    const t = tai + ((W===D || p===D) ? dealerTai : 0);
    return {p, t, amt: S.base + t*S.perTai};
  });
  return {tai, names, pays, W};
}

function update() {
  $('#loserRow').hidden = winType !== 'ron';
  const r = calc();
  $('#taiTotal').textContent = r.tai;
  $('#payDetail').innerHTML = r.pays.map(x=>`${S.names[x.p]} 付 ${x.amt}（${x.t}台）`).join('<br>')
    + `<br><b style="font-size:1rem">${S.names[r.W]} 共收 ${r.pays.reduce((a,x)=>a+x.amt,0)}</b>`;
}

function renderBoard() {
  $('#scores').innerHTML = S.names.map((n,i)=>`<div class="score"><span>${n}</span><span class="${S.scores[i]>=0?'pos':'neg'}">${S.scores[i]>0?'+':''}${S.scores[i]}</span></div>`).join('');
  $('#history').innerHTML = S.history.map(h=>`<li>${h.text}</li>`).reverse().join('') || '<li>尚無紀錄</li>';
}

function renderSettings() {
  $('#base').value = S.base; $('#perTai').value = S.perTai;
  $('#names').innerHTML = S.names.map((n,i)=>`<div class="row"><label>玩家${i+1}</label><input data-i="${i}" value="${n}"></div>`).join('');
}

// events
document.querySelectorAll('.tabs button').forEach(b => b.onclick = () => {
  document.querySelectorAll('.tabs button,.tab').forEach(e=>e.classList.remove('active'));
  b.classList.add('active'); $('#'+b.dataset.tab).classList.add('active');
  renderBoard();
});
$('#winType').onclick = e => {
  const b = e.target.closest('button'); if (!b) return;
  winType = b.dataset.v;
  $('#winType').querySelectorAll('button').forEach(x=>x.classList.toggle('active', x===b));
  if (winType==='ron') pick.mqzm = 0;
  renderYaku(); update();
};
$('.stepper').onclick = e => { const d = +e.target.dataset.d; if (d) { streak = Math.max(0, streak+d); $('#streak').textContent = streak; update(); } };
$('#yaku').onclick = e => {
  const chip = e.target.closest('.chip'); if (!chip) return;
  const y = YAKU.find(y=>y.id===chip.dataset.id);
  const m = +e.target.dataset.m;
  if (y.multi) pick[y.id] = Math.min(y.multi, Math.max(0, (pick[y.id]||0) + (m || 1)));
  else pick[y.id] = pick[y.id] ? 0 : 1;
  if (y.id==='mqzm' && pick.mqzm) { pick.menqing = 0; winType='zimo'; $('#winType').querySelectorAll('button').forEach(x=>x.classList.toggle('active', x.dataset.v==='zimo')); }
  if (y.id==='menqing' && pick.menqing) pick.mqzm = 0;
  renderYaku(); update();
};
['winner','loser','dealer'].forEach(id => $('#'+id).onchange = () => { fillSelects(); update(); });
$('#commit').onclick = () => {
  const r = calc();
  if (winType==='ron' && r.pays[0].p===r.W) return alert('放槍者不能是胡牌者');
  const delta = [0,0,0,0];
  r.pays.forEach(x => { delta[x.p] -= x.amt; delta[r.W] += x.amt; });
  S.scores = S.scores.map((s,i)=>s+delta[i]);
  S.history.push({delta, text:`${S.names[r.W]} ${winType==='zimo'?'自摸':'胡 '+S.names[r.pays[0].p]} ${r.tai}台［${r.names.join('、')||'無台'}］+${delta[r.W]}`});
  persist();
  // 莊家胡則連莊，否則下莊
  const D = +$('#dealer').value;
  if (r.W === D) streak++; else { streak = 0; $('#dealer').value = (D+1)%4; }
  $('#streak').textContent = streak;
  pick = {}; renderYaku(); update();
  alert('已記錄！');
};
$('#undo').onclick = () => { const h = S.history.pop(); if (!h) return; S.scores = S.scores.map((s,i)=>s-h.delta[i]); persist(); renderBoard(); };
$('#reset').onclick = () => { if (confirm('確定清除所有分數？')) { S.scores=[0,0,0,0]; S.history=[]; persist(); renderBoard(); } };
$('#base').oninput = e => { S.base = +e.target.value||0; persist(); update(); };
$('#perTai').oninput = e => { S.perTai = +e.target.value||0; persist(); update(); };
$('#names').oninput = e => { S.names[e.target.dataset.i] = e.target.value || `玩家${+e.target.dataset.i+1}`; persist(); fillSelects(); update(); };

fillSelects(); renderYaku(); renderSettings(); update();
if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(()=>{});
