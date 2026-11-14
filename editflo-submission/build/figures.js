// Figures for the EditFlo report. Every count comes from the coding in Appendix A.
const $ = (id) => document.getElementById(id);
const ul = (a) => `<ul>${a.map((x) => `<li>${x}</li>`).join('')}</ul>`;

// ---------- Lean Canvas ----------
function canvas(d, changed = [], caption = '') {
  const blk = (cls, key, title, body, extra = '') => {
    const c = changed.includes(key);
    return `<div class="cb ${cls} ${c ? 'chg' : ''} ${key === 'uvp' ? 'uvp' : ''}"><h5>${title}${c ? '<span class="chgtag">CHANGED</span>' : ''}</h5>${body}${extra}</div>`;
  };
  return `<div class="canvas">
    ${blk('c-prob', 'prob', 'Problem', ul(d.prob), d.alt ? `<div class="sub"><b>Existing alternatives:</b> ${d.alt}</div>` : '')}
    ${blk('c-sol', 'sol', 'Solution', ul(d.sol))}
    ${blk('c-met', 'met', 'Key metrics', ul(d.met))}
    ${blk('c-uvp', 'uvp', 'Unique value proposition', `<p style="font-size:8.6pt;line-height:1.38;font-weight:600;color:#1E1B22;margin:0 0 2mm">${d.uvp}</p>`, d.uvpSub ? `<div class="sub">${d.uvpSub}</div>` : '')}
    ${blk('c-adv', 'adv', 'Unfair advantage', ul(d.adv))}
    ${blk('c-chan', 'chan', 'Channels', ul(d.chan))}
    ${blk('c-seg', 'seg', 'Customer segments', ul(d.seg), d.early ? `<div class="sub"><b>Early adopters:</b> ${d.early}</div>` : '')}
    ${blk('c-cost', 'cost', 'Cost structure', ul(d.cost))}
    ${blk('c-rev', 'rev', 'Revenue streams', ul(d.rev))}
  </div>${caption ? `<figcaption>${caption}</figcaption>` : ''}`;
}
$('lc1').innerHTML = canvas({
  prob: ['Lack of editing skills', 'Fear of poor-quality, unprofessional output', 'Time and effort to learn and edit'],
  alt: 'tutorials, mobile editing apps, templates, freelance editors, not publishing.',
  sol: ['Ready-to-use OpenFilm editing workflows', 'MCP integration with AI assistants', 'Guidance for repetitive tasks', 'Optional setup help'],
  met: ['Successful installs', 'First edit completed', 'Time per video', 'Videos published, repeat use', 'Demo-to-purchase conversion'],
  uvp: 'Make video creation approachable by reducing the technical knowledge, time and effort needed for basic editing.',
  uvpSub: '“Create more. Edit less. Start publishing.”',
  adv: ['Specialised OpenFilm and MCP workflow knowledge', 'Not yet defensible'],
  chan: ['YouTube and Instagram demos', 'Creator and Reddit communities', 'Direct outreach, referrals'],
  seg: ['Aspiring YouTubers', 'Beginner short-form creators', 'Working professionals building a presence', 'Entrepreneurs and personal brands'],
  early: 'people with ideas or footage who keep delaying publishing because of editing.',
  cost: ['Workflow development and maintenance', 'Software and infrastructure', 'Integration testing', 'Onboarding, support, marketing'],
  rev: ['One-time workflow packages', 'Installation and configuration fees', 'Premium packs, optional support', 'Willingness to pay: unvalidated'],
}, [], '<b>Figure 1.1 · Lean Canvas 1.</b> The initial idea, before any customer interviews. All blocks are assumptions.');

$('lc2').innerHTML = canvas({
  prob: ['Production causes mental fatigue', 'Editing and footage selection consume time', 'Perfectionism delays completion', 'Equipment and budget limit some creators'],
  alt: 'manual editing, freelance editors, general AI tools.',
  sol: ['OpenFilm workflows with MCP/AI-assistant integration', 'Help with footage selection, organisation, trimming and timeline', 'Possible storyboard and planning support', 'Optional setup'],
  met: ['Time saved per video', 'Reduction in manual editing steps', 'Successful installs, repeat use', 'Willingness to pay'],
  uvp: 'Help creators turn ideas and raw footage into coherent videos with less repetitive editing and planning effort.',
  adv: ['Specialised OpenFilm workflow and integration knowledge', 'Not yet defensible'],
  chan: ['YouTube and Instagram demos', 'Creator communities', 'Direct outreach', 'Practical workflow demos'],
  seg: ['Aspiring and short-form creators', 'Educational creators', 'Experienced editors', 'Full-time creators, personal brands'],
  early: 'not yet chosen. The first round widened the segment.',
  cost: ['Workflow development and maintenance', 'AI/API usage, software', 'Integration testing, onboarding, support', 'Marketing'],
  rev: ['One-time workflow packages', 'Installation and configuration', 'Premium packs, optional support', 'Willingness to pay: unvalidated'],
}, ['prob', 'sol', 'met', 'uvp', 'seg', 'cost'], '<b>Figure 2.3 · Lean Canvas 2.</b> Problem and segments widened beyond beginners; the solution added footage selection and planning; metrics shifted to time saved.');

$('lc3').innerHTML = canvas({
  prob: ['Repetitive trimming and cutting', 'Manual footage, asset and overlay organisation', 'Key sections, instructions and style must be respected', 'Unpredictable AI costs'],
  alt: 'manual editing, freelancers, general AI tools, editing-software features.',
  sol: ['Downloadable workflow repository + web library', 'Instruction-led trimming and organisation', 'Protected sections, style per project', 'Optional B-roll; review at every stage'],
  met: ['Setup success', 'Editing time vs usual process', 'Corrections per edit', 'Protected sections kept', 'Paid conversions, repeat use'],
  uvp: 'An instruction-led editing workflow that removes repetitive editing work while keeping the creator in control of the final video.',
  uvpSub: 'Not an editor, not a chatbot: a reusable workflow layer between the creator, their AI assistant and their editor.',
  adv: ['Task-specific workflow know-how', 'Learnings accumulated from pilots', 'Not yet defensible'],
  chan: ['Creator and editor communities', 'Before-and-after demos', 'Direct outreach to regular creators', 'Pilot referrals'],
  seg: ['Regular creators of recurring formats: educational, personal-brand, sponsored', 'Experienced freelance editors', 'Beginners: later'],
  early: 'creators who already edit and publish on a schedule (strongest fit: D).',
  cost: ['Workflow development and maintenance', 'Compatibility testing, documentation', 'Web library hosting, support, marketing', 'Customers pay their own AI and software'],
  rev: ['Pricing test: ₹3,000 one-time vs ₹500/month', 'Optional installation and configuration', 'Optional technical support'],
}, ['prob', 'sol', 'met', 'uvp', 'adv', 'chan', 'seg', 'cost', 'rev'], '<b>Figure 3.6 · Lean Canvas 3.</b> Focused on repetitive editing execution for regular creators, with creator control built into the solution and predictable pricing to test.');

// ---------- Participant × theme matrix (round 1) ----------
const P5 = ['A', 'B', 'C', 'D', 'E'];
const R1 = [
  ['Time, effort or mental fatigue', 'ABCDE'],
  ['Finding, selecting or organising footage', 'ABCD'],
  ['Quality pressure or perfectionism', 'BCDE'],
  ['Wants help that follows creative direction', 'BCD'],
  ['Equipment or cost constraints', 'ABC'],
  ['Wants planning or pre-production help', 'CD'],
  ['Has used AI editing tools', 'B'],
  ['Has paid for editing help', 'A'],
];
$('mx1').innerHTML = `<table class="mx"><tr><th>Theme raised in the first round</th>${P5.map((p) => `<th style="width:11mm">${p}</th>`).join('')}<th style="width:16mm">Count</th></tr>
  ${R1.map(([t, s]) => `<tr><td>${t}</td>${P5.map((p) => `<td><span class="dot ${s.includes(p) ? '' : 'o'}"></span></td>`).join('')}<td class="cnt">${s.length} of 5</td></tr>`).join('')}</table>
  <figcaption><b>Figure 2.1 · Participant × theme matrix, first round.</b> A filled dot means the participant’s summary explicitly describes the theme (coding rules and sources in Appendix A). Themes overlap. Counts describe this sample only and are not percentages of the creator market.</figcaption>`;

// ---------- Theme comparison A,B,D across rounds ----------
const CMP = [
  ['Repetitive editing execution (trimming, cutting, B-roll)', 'AB', 'ABD'],
  ['Finding, selecting or organising footage', 'ABD', 'AB'],
  ['Follow creative direction and intent', 'BD', 'ABD'],
  ['Visual style adapts per project', '', 'BD'],
  ['Cost or processing efficiency', 'AB', 'BD'],
  ['Planning, ideation or SEO help', 'D', ''],
];
const dots = (s) => ['A', 'B', 'D'].map((p) => `<span class="dot ${s.includes(p) ? '' : 'o'}" title="${p}"></span>`).join(' ');
$('cmp').innerHTML = `<table class="mx"><tr><th>Theme (participants A, B, D only)</th><th style="width:34mm">First round<br><span style="font-weight:400">A · B · D</span></th><th style="width:34mm">Follow-ups<br><span style="font-weight:400">A · B · D</span></th><th style="width:22mm">Direction</th></tr>
  ${CMP.map(([t, a, b]) => `<tr><td>${t}</td><td>${dots(a)}</td><td>${dots(b)}</td><td>${b.length > a.length ? '<span class="st sup">Stronger</span>' : b.length < a.length ? '<span class="st low">Weaker</span>' : '<span class="st inc">Same</span>'}</td></tr>`).join('')}</table>
  <figcaption><b>Figure 3.1 · Theme comparison for the same three participants.</b> Each row shows whether A, B and D raised the theme in each round (dots in order A, B, D). Repetitive execution counts B’s first-round trimming and A’s removal of pauses and filler words. Footage selection drops in the follow-ups because D shifted to B-roll insertion. “Stronger” or “weaker” compares these three people only.</figcaption>`;

// ---------- Creator workflow pain map ----------
const ST = [
  ['Plan', 'C D', '', 'storyboard, ideas, SEO'],
  ['Record', 'C', '', 'multiple angles'],
  ['Review takes', 'D', '', 'unsuccessful takes'],
  ['Select footage', 'A B C D', 'A B', 'find usable clips'],
  ['Trim and cut', 'A B', 'A B D', 'pauses, filler, length'],
  ['Arrange timeline', 'A B', 'B', 'order, objective'],
  ['B-roll, assets, overlays', 'A D', 'B D', 'templates, music, B-roll'],
  ['Sound', 'A D', '', 'music, sound quality'],
  ['Publish', 'D', '', 'final output'],
];
$('flow').innerHTML = `<div class="flow"><div class="focusbar">EditFlo focus · stages 4–7 (B-roll optional)</div>
  ${ST.map(([t, r1, r2, w], i) => {
    const focus = i >= 3 && i <= 6;
    const ids = [...new Set((r1 + ' ' + r2).split(' ').filter(Boolean))];
    return `<div class="stage ${focus ? 'focus' : ''}" style="grid-row:2"><div class="t">${i + 1}. ${t}</div><div class="ps">${ids.map((p) => `<span class="${r2.includes(p) ? 'r2' : ''}">${p}</span>`).join('')}</div><div class="what">${w}</div></div>`;
  }).join('')}</div>
  <figcaption><b>Figure 3.2 · Pain points along the creator’s workflow.</b> Letters show which participants described difficulty at each stage; purple letters were confirmed or raised again in the follow-ups. The shaded stages, where the follow-ups concentrated, are EditFlo’s focus. Planning, recording and sound remain outside the core product.</figcaption>`;

// ---------- Hypothesis evolution ----------
const hc = (id, txt, st, lab) => `<div class="hc"><span class="st ${st}">${lab}</span><b>${id}</b> ${txt}</div>`;
$('hypflow').innerHTML = `<div class="hyp-flow">
  <div class="hyp-col"><h5>Report 1 · Initial</h5>
    ${hc('H1', 'Beginners lack editing skills', 'part', 'Partial')}${hc('H2', 'Beginners fear unprofessional output', 'part', 'Partial')}${hc('H3', 'Editing takes too much time and effort', 'sup', 'Supported')}${hc('H4', 'Difficulty stops consistent publishing', 'part', 'Partial')}${hc('H5', 'Beginners want AI editing tools', 'inc', 'Inconclusive')}${hc('H6', 'Some will pay for workflows or setup', 'inc', 'Inconclusive')}
    <p class="small" style="margin-top:2mm">Assessed in Report 2</p></div>
  <div class="hyp-col"><h5>Report 2 · Generated</h5>
    ${hc('H7', 'Value footage selection and organisation', 'part', 'Partial')}${hc('H8', 'Want an assistant that follows creative direction', 'sup', 'Supported')}${hc('H9', 'Pre-production help reduces effort', 'low', 'Lower priority')}${hc('H10', 'Experienced creators value AI editing help', 'sup', 'Supported')}${hc('H11', 'SEO and research alongside editing', 'inc', 'Inconclusive')}
    <p class="small" style="margin-top:2mm">Assessed in Report 3</p></div>
  <div class="hyp-col"><h5>Report 3 · Generated for the pilot</h5>
    ${hc('H12', 'Predictable pricing preferred to usage-based pricing', 'new', 'To test')}${hc('H13', 'Instruction-led trimming with protected sections is accepted with limited corrections', 'new', 'To test')}${hc('H14', 'Regular creators of recurring formats are the best early segment', 'new', 'To test')}
    <p class="small" style="margin-top:2mm">Tested by the pilot in Report 4</p></div>
</div><figcaption><b>Figure 3.3 · Hypothesis evolution.</b> Each round assessed the previous hypotheses and generated the next set. The questions moved from skills and confidence, to control and execution, to price, reliability and segment.</figcaption>`;

// ---------- Feature priorities ----------
const it = (t, e) => `<div class="it">${t}<em>${e}</em></div>`;
$('prio').innerHTML = `<div class="prio">
  <div class="col core"><h5>Core</h5><div class="why">Raised in the follow-ups; central to editing execution</div>
    ${it('Trimming and cutting', 'A, B, D')}${it('Footage organisation', 'A, B · A–D in round 1')}${it('Protected sections', 'A, D')}${it('Review and correction', 'A, B, D')}${it('Style per project', 'B, D')}</div>
  <div class="col"><h5>Optional</h5><div class="why">Valuable for some projects only</div>
    ${it('B-roll insertion', 'B, D · not A')}${it('Asset and overlay handling', 'B')}</div>
  <div class="col"><h5>Later</h5><div class="why">Raised in round 1, not confirmed</div>
    ${it('Storyboarding and shot planning', 'C · lower for B')}${it('Sound quality', 'D')}</div>
  <div class="col"><h5>Not now</h5><div class="why">Outside an editing-focused product</div>
    ${it('Ideation and SEO', 'D in round 1 · B uses ChatGPT')}</div>
</div><figcaption><b>Figure 3.5 · Feature-priority matrix.</b> Priority reflects how directly each feature was raised in the follow-ups and how central it is to repetitive editing execution. It is a qualitative judgement, not a scored ranking.</figcaption>`;

// ---------- Deck slides ----------
const N = 13, img = (i) => `<img class="slide" src="deck/slide-${String(i).padStart(2, '0')}.jpg" alt="Slide ${i}">`;
$('slidesA').innerHTML = img(1);
let rest = '';
for (let i = 2; i <= N; i += 2) rest += `<section class="page-break"><div class="slides2">${img(i)}${i + 1 <= N ? img(i + 1) : ''}</div></section>`;
$('slidesRest').innerHTML = rest;

// keep every table on one page: wrap in a block that Chromium will not fragment
document.querySelectorAll('table').forEach((t)=>{const w=document.createElement('div');w.className='tw';t.parentNode.insertBefore(w,t);w.appendChild(t);});
