// Renders the overview page from data/summary.json.
// All text from data files is inserted as text, never as HTML.

const ML = {
  Kasaragod: 'കാസർകോട്', Kannur: 'കണ്ണൂർ', Wayanad: 'വയനാട്', Kozhikode: 'കോഴിക്കോട്',
  Malappuram: 'മലപ്പുറം', Palakkad: 'പാലക്കാട്', Thrissur: 'തൃശ്ശൂർ', Ernakulam: 'എറണാകുളം',
  Idukki: 'ഇടുക്കി', Kottayam: 'കോട്ടയം', Alappuzha: 'ആലപ്പുഴ', Pathanamthitta: 'പത്തനംതിട്ട',
  Kollam: 'കൊല്ലം', Thiruvananthapuram: 'തിരുവനന്തപുരം'
};

function el(tag, attrs, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined) continue;
    if (k === 'class') node.className = v;
    else if (k === 'style') node.style.cssText = v;
    else node.setAttribute(k, v);
  }
  for (const c of children.flat()) {
    if (c === null || c === undefined || c === false) continue;
    node.append(c instanceof Node ? c : String(c));
  }
  return node;
}

const inr = new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 });
const inr1 = new Intl.NumberFormat('en-IN', { maximumFractionDigits: 1 });

function crore(v, long) {
  if (v === null || v === undefined || Number.isNaN(v)) return '—';
  const f = v < 100 ? inr1 : inr;
  return '₹' + f.format(v) + (long ? ' crore' : ' cr');
}
function pct(v) {
  if (v === null || v === undefined || Number.isNaN(v)) return '—';
  return inr1.format(v) + '%';
}
function link(name, url) {
  return url ? el('a', { href: url }, name) : name;
}
function dateText(iso) {
  if (!iso) return 'unknown date';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' });
}

function card(title, big, caption, sourceNodes) {
  return el('article', { class: 'card' },
    el('h3', {}, title),
    el('p', { class: 'big' }, big),
    el('p', {}, caption),
    el('p', { class: 'source' }, 'Source: ', sourceNodes));
}

function renderKeyCards(s) {
  const box = document.getElementById('key-cards');
  const f = s.state_figures || {};
  for (const key of ['budget_estimate', 'actual_spending']) {
    const x = f[key];
    if (!x) continue;
    box.append(card(x.label, crore(x.value_cr, true), x.caption,
      [link(x.source_name, x.source_url), x.source_note ? ' · ' + x.source_note : '']));
  }
  const k = s.kiifb;
  if (k && k.total_approved_cr != null) {
    box.append(card('KIIFB infrastructure projects', crore(k.total_approved_cr, true),
      `approved for ${inr.format(k.project_count)} projects · ${crore(k.total_released_cr, true)} released`,
      [link('KIIFB project list', k.source_url), ' · collected ', dateText(k.collected_at)]));
  }
  const p = s.lsgd_plan;
  if (p && p.total) {
    box.append(card('Local government plans', pct(p.total.pct) + ' spent',
      `of this year's ${crore(p.total.budget_cr, true)} plan budget`,
      [link('LSGD Plan Dashboard', p.source_url), p.as_on ? ' · ' + p.as_on : '']));
  }
}

function renderPipeline(s) {
  const k = s.kiifb;
  const list = document.getElementById('pipeline');
  const note = document.getElementById('pipeline-note');
  if (!k || !k.pipeline) {
    list.append(el('li', {}, el('span', { class: 'step-sub' }, 'KIIFB data has not been collected yet.')));
    return;
  }
  k.pipeline.forEach((step, i) => {
    list.append(el('li', {},
      el('span', { class: 'step-no' }, 'STEP ' + (i + 1)),
      el('span', { style: 'font-weight:600' }, step.label),
      el('span', { class: 'step-value' }, step.value),
      el('span', { class: 'step-sub' }, step.sub)));
  });
  note.append('KIIFB does not publish how far work has got on the ground. We save its project list every day, so changes over time can be tracked. ',
    k.released_note ? k.released_note + ' ' : '',
    k.headline_note ? k.headline_note + ' ' : '',
    link('Source: KIIFB project list', k.source_url));
}

function renderDistricts(s) {
  const body = document.getElementById('district-rows');
  const plan = (s.lsgd_plan && s.lsgd_plan.by_district) || {};
  const kiifb = (s.kiifb && s.kiifb.by_district) || {};
  for (const name of s.district_order || Object.keys(ML)) {
    const p = plan[name] || {};
    const k = kiifb[name] || {};
    const share = p.pct != null ? Math.max(0, Math.min(100, p.pct)) : null;
    body.append(el('tr', {},
      el('th', { scope: 'row' }, name, el('span', { class: 'ml', lang: 'ml' }, ML[name] || '')),
      el('td', { class: 'num' }, crore(p.budget_cr)),
      el('td', {}, el('div', { class: 'bar' },
        el('div', { class: 'track', role: 'img', 'aria-label': share == null ? 'No data' : pct(share) + ' spent' },
          share == null ? null : el('div', { class: 'fill', style: `width:${share}%` })),
        el('span', { class: 'pct' }, pct(p.pct)))),
      el('td', { class: 'num' }, k.count != null ? inr.format(k.count) : '—'),
      el('td', { class: 'num' }, crore(k.approved_cr)),
      el('td', { class: 'num' }, crore(k.released_cr))));
  }
  const src = document.getElementById('district-sources');
  const multi = s.kiifb && s.kiifb.multi_district;
  src.append('Sources: ',
    link('LSGD Plan Dashboard', s.lsgd_plan && s.lsgd_plan.source_url),
    s.lsgd_plan && s.lsgd_plan.as_on ? ` (${s.lsgd_plan.as_on})` : '',
    ', ', link('KIIFB project list', s.kiifb && s.kiifb.source_url), '. ',
    multi ? `KIIFB columns count projects listed under one district only. Another ${inr.format(multi.count)} projects (${crore(multi.approved_cr, true)}) cover several districts or none.` : '');
}

function renderFlags(s) {
  const box = document.getElementById('flags');
  const groups = (s.kiifb && s.kiifb.flag_groups) || [];
  if (!groups.length) {
    box.append(el('p', { class: 'empty' }, 'No projects are flagged yet. Flags need at least one day of KIIFB data.'));
    return;
  }
  for (const g of groups) {
    box.append(el('div', { class: 'item' },
      el('span', { class: 'chip' }, g.rule),
      el('p', { class: 'meta' }, `${inr.format(g.count)} projects. ${g.items.length < g.count ? 'The largest are shown.' : ''}`)));
    for (const f of g.items) {
      box.append(el('article', { class: 'item sub' },
        el('h3', {}, f.name),
        el('p', { class: 'meta' }, [f.district, f.agency, crore(f.approved_cr) + ' approved', crore(f.released_cr) + ' released'].filter(Boolean).join(' · '))));
    }
  }
}

function renderAudits(s) {
  const box = document.getElementById('audit-list');
  for (const a of s.audits || []) {
    box.append(el('article', { class: 'item' },
      el('h3', {}, a.title),
      el('p', {}, a.finding),
      el('p', { class: 'meta' }, 'Source: ', link(a.source_name, a.source_url), a.source_note ? ', ' + a.source_note : '')));
  }
}

function renderOutcomes(s) {
  const box = document.getElementById('outcomes');
  for (const o of s.outcomes || []) {
    box.append(el('div', { class: 'card' },
      el('p', { class: 'big' }, o.value),
      el('p', {}, o.label),
      el('p', { class: 'source' }, 'Source: ', link(o.source_name, o.source_url))));
  }
}

async function main() {
  const updated = document.getElementById('updated');
  try {
    const res = await fetch('data/summary.json', { cache: 'no-store' });
    if (!res.ok) throw new Error(res.status);
    const s = await res.json();
    updated.textContent = 'Last updated ' + dateText(s.generated_at) + ' · Data collected daily';
    renderKeyCards(s);
    renderPipeline(s);
    renderDistricts(s);
    renderFlags(s);
    renderAudits(s);
    renderOutcomes(s);
  } catch (e) {
    updated.textContent = 'The data could not be loaded. Please try again later.';
  }
}
main();
