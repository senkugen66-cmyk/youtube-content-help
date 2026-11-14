// EditFlo — Report 4 incubation pitch deck (editable .pptx).
// Build: node deck.js  → ../final/25120989_EditFlo_Pitch_Deck.pptx
const pptxgen = require('pptxgenjs');
const path = require('path');
const { applyTheme } = require('/root/.claude/skills/synced/83cad3c6-7d84-42a1-9149-dbd1dbf3471c_ed21984b-d392-4e6b-a600-057053d147ca/pptx/scripts/apply_theme.js');

const THEME = {
  name: 'EditFlo',
  headFontFace: 'Inter', bodyFontFace: 'Inter',
  colors: { dk1: '1E1B22', lt1: 'FFFFFF', dk2: '3B3640', lt2: 'FAF8F4',
    accent1: '7B2CBF', accent2: 'C8A2E8', accent3: 'F4ECFB', accent4: '76707C', accent5: '2F8F5B', accent6: 'D18A1E',
    hlink: '7B2CBF', folHlink: '6A22A8' },
};
const K = { p: '7B2CBF', l: 'C8A2E8', tint: 'F4ECFB', bg: 'FAF8F4', ink: '1E1B22', ink2: '3B3640', mut: '76707C', faint: 'A8A2AE', line: 'E2DCD3', white: 'FFFFFF', sunk: 'F1EDE7' };
const IMG = (f) => path.join(__dirname, 'img', f);
const FOOT = 'EditFlo  ·  Incubation pitch  ·  25120989';

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE'; // 13.333 x 7.5 in
pres.title = 'EditFlo — Incubation Pitch';
pres.author = '25120989';
pres.theme = { headFontFace: 'Inter', bodyFontFace: 'Inter' };

pres.defineSlideMaster({
  title: 'EF_DARK',
  background: { color: K.p },
  objects: [
    { placeholder: { options: { name: 'title', type: 'title', x: 0.75, y: 2.35, w: 9.5, h: 1.4, fontSize: 60, bold: true, color: K.white, valign: 'top', align: 'left', margin: 0 }, text: '' } },
  ],
});
pres.defineSlideMaster({
  title: 'EF_CONTENT',
  background: { color: K.bg },
  margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 0.42, w: 12.1, h: 0.75, fontSize: 30, bold: true, color: K.ink, valign: 'top', align: 'left', margin: 0 }, text: '' } },
    { text: { text: FOOT, options: { x: 0.6, y: 7.02, w: 7, h: 0.28, fontSize: 10, color: K.mut, margin: 0 } } },
  ],
  slideNumber: { x: 12.25, y: 7.02, w: 0.5, h: 0.28, fontSize: 10, color: K.mut, align: 'right' },
});

// ---------- helpers (fresh option objects every call) ----------
const shadow = () => ({ type: 'outer', color: '3C1E5A', opacity: 0.12, blur: 8, offset: 2, angle: 90 });
function card(s, x, y, w, h, { fill = K.white, line = 'ECE7E0', name } = {}) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1, fill: { color: fill }, line: { color: line, width: 0.75 }, shadow: shadow(), objectName: name });
}
function txt(s, text, o) { s.addText(text, Object.assign({ isTextBox: true, margin: 0, color: K.ink, fontSize: 14, valign: 'top', fontFace: 'Inter' }, o)); }
function kicker(s, text, x, y, w = 6, color = K.p) { txt(s, text.toUpperCase(), { x, y, w, h: 0.3, fontSize: 11, bold: true, color, charSpacing: 2 }); }
function chip(s, text, x, y, { fill = K.tint, color = K.p, w } = {}) {
  const ww = w || Math.max(0.9, 0.11 * text.length + 0.35);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: ww, h: 0.32, rectRadius: 0.08, fill: { color: fill }, line: { color: fill, width: 0.5 } });
  txt(s, text, { x, y, w: ww, h: 0.32, fontSize: 11, bold: true, color, align: 'center', valign: 'middle' });
  return ww;
}
function iconCircle(s, x, y, label, { fill = K.p, color = K.white, d = 0.55 } = {}) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill, width: 0.5 } });
  txt(s, label, { x, y, w: d, h: d, fontSize: 14, bold: true, color, align: 'center', valign: 'middle' });
}
function content(title, section, notes) {
  const s = pres.addSlide({ masterName: 'EF_CONTENT', sectionTitle: section });
  s.addText(title, { placeholder: 'title' });
  if (notes) s.addNotes(notes);
  return s;
}

// ================= SLIDES =================
pres.addSection({ title: 'Opening' });
// 1 — Title
{
  const s = pres.addSlide({ masterName: 'EF_DARK', sectionTitle: 'Opening' });
  s.addImage({ path: IMG('mark-white.png'), x: 0.75, y: 1.15, w: 0.9, h: 0.9 });
  s.addText('EditFlo', { placeholder: 'title' });
  txt(s, 'Create more. Edit less. Start publishing.', { x: 0.75, y: 3.65, w: 9, h: 0.5, fontSize: 24, color: K.white });
  txt(s, 'Reusable editing workflows that a creator’s AI assistant runs in their editor — with the creator approving every result.', { x: 0.75, y: 4.35, w: 8.2, h: 0.9, fontSize: 16, color: 'E9DCF6' });
  txt(s, 'INCUBATION PITCH  ·  REPORT 4  ·  ROLL NO. 25120989', { x: 0.75, y: 6.55, w: 9, h: 0.3, fontSize: 11, bold: true, color: 'E9DCF6', charSpacing: 2 });
  s.addNotes('EditFlo helps regular creators spend less time on repetitive editing. This deck summarises the problem, what customer discovery taught us, the product, the business model and the incubation support requested.');
}

pres.addSection({ title: 'Problem and customer' });
// 2 — Problem
{
  const s = content('Editing execution, not editing knowledge, is the bottleneck', 'Problem and customer',
    'All figures are self-reported by individual interview participants. They illustrate the problem; they are not market averages.');
  txt(s, 'Creators can have the idea, the footage and the skills — and still lose hours to the same repetitive steps: reviewing takes, finding usable clips, trimming pauses and arranging the timeline.', { x: 0.6, y: 1.45, w: 5.4, h: 1.6, fontSize: 17, color: K.ink2 });
  txt(s, 'The burden is mental as well as practical: all five first-round participants described time pressure, effort or fatigue.', { x: 0.6, y: 3.25, w: 5.4, h: 1.0, fontSize: 14, color: K.mut });
  const stats = [
    ['1–1.5 h', 'to edit a single short video', 'Participant A'],
    ['~30 min', 'of work per finished minute of short-form video', 'Participant B'],
    ['~₹1,500', 'paid per post for an editor, then found it too costly', 'Participant A'],
  ];
  stats.forEach(([big, label, who], i) => {
    const y = 1.45 + i * 1.72;
    card(s, 6.6, y, 6.1, 1.5);
    txt(s, big, { x: 6.9, y: y + 0.28, w: 2.3, h: 0.9, fontSize: 36, bold: true, color: K.p, valign: 'middle' });
    txt(s, label, { x: 9.3, y: y + 0.32, w: 3.2, h: 0.6, fontSize: 14, color: K.ink });
    txt(s, who + ' · self-reported', { x: 9.3, y: y + 0.95, w: 3.2, h: 0.3, fontSize: 11, color: K.mut });
  });
}
// 3 — Customer
{
  const s = content('Who EditFlo serves first', 'Problem and customer',
    'The target moved from beginners (Report 1) to regular creators (Reports 2–3). The strongest observed fit is Participant D; B and A partly fit. This beachhead still needs validation in the pilot.');
  card(s, 0.6, 1.45, 7.2, 4.95, { fill: K.p, line: K.p });
  kicker(s, 'Beachhead segment', 0.95, 1.8, 6, 'E9DCF6');
  txt(s, 'Regular creators of recurring, structured videos', { x: 0.95, y: 2.2, w: 6.5, h: 1.2, fontSize: 26, bold: true, color: K.white });
  txt(s, 'Educational, personal-brand and sponsored talking-head content, published on a schedule.', { x: 0.95, y: 3.45, w: 6.4, h: 0.8, fontSize: 15, color: 'E9DCF6' });
  const pts = ['They already know how to edit', 'They repeat similar edits every video', 'They must protect key sections and brand instructions'];
  pts.forEach((t, i) => { iconCircle(s, 0.95, 4.42 + i * 0.6, '✓', { fill: K.white, color: K.p, d: 0.38 }); txt(s, t, { x: 1.5, y: 4.45 + i * 0.6, w: 6, h: 0.35, fontSize: 14, color: K.white }); });
  card(s, 8.15, 1.45, 4.55, 2.35);
  kicker(s, 'Why them first', 8.45, 1.75, 4);
  txt(s, 'Recurring formats make a workflow reusable — the same structure is edited again and again.', { x: 8.45, y: 2.15, w: 4.0, h: 1.4, fontSize: 14, color: K.ink2 });
  card(s, 8.15, 4.05, 4.55, 2.35, { fill: K.sunk, line: K.sunk });
  kicker(s, 'Not first', 8.45, 4.35, 4, K.mut);
  txt(s, 'Complete beginners — our Report 1 assumption. Their need is learning to edit, which is a different product.', { x: 8.45, y: 4.75, w: 4.0, h: 1.4, fontSize: 14, color: K.ink2 });
}
// 4 — Discovery insights
{
  const s = content('What customer discovery changed', 'Problem and customer',
    'Five exploratory conversations (A–E), then three follow-ups with A, B and D. Qualitative and small — patterns to test, not proof of market demand.');
  txt(s, '5 first-round conversations  ·  3 follow-ups with A, B and D  ·  qualitative, not a survey', { x: 0.6, y: 1.3, w: 12, h: 0.35, fontSize: 13, color: K.mut });
  const tiles = [
    ['Execution over ideation', 'All three follow-ups prioritised trimming, cutting and organising over planning or SEO.', 'A · B · D'],
    ['Control must be configurable', 'B wants full control, A is comfortable with substantial help, D wants instructions followed and correctable.', 'A · B · D'],
    ['Protect what matters', 'Key explanations and specified sections must never be cut just to shorten a video.', 'A · D'],
    ['Style changes per project', 'Visual treatment must adapt to each video’s concept and style.', 'B · D'],
    ['B-roll is optional', 'Valued by B and D; A prefers to source footage himself.', 'B · D (not A)'],
    ['Cost must be predictable', 'Token-based or unnecessary processing costs are a barrier to adoption.', 'B · D'],
  ];
  tiles.forEach(([h, b, who], i) => {
    const x = 0.6 + (i % 3) * 4.1, y = 1.85 + Math.floor(i / 3) * 2.5;
    card(s, x, y, 3.85, 2.25);
    txt(s, h, { x: x + 0.3, y: y + 0.28, w: 3.3, h: 0.4, fontSize: 16, bold: true });
    txt(s, b, { x: x + 0.3, y: y + 0.75, w: 3.3, h: 1.0, fontSize: 13, color: K.ink2 });
    txt(s, who, { x: x + 0.3, y: y + 1.78, w: 3.3, h: 0.3, fontSize: 11, bold: true, color: K.p });
  });
}

pres.addSection({ title: 'Solution' });
// 5 — Solution
{
  const s = content('EditFlo: reusable editing workflows you stay in control of', 'Solution',
    'Product form (hybrid): a downloadable workflow repository the creator sets up with their own AI assistant, plus a lightweight web library to browse and configure workflows.');
  txt(s, 'A workflow is a reusable set of editing instructions — for example “YouTube long-form” — that a compatible AI assistant follows inside the creator’s editing software. The creator sets the objective, style and protected sections, then reviews the result.', { x: 0.6, y: 1.4, w: 12.1, h: 1.0, fontSize: 16, color: K.ink2 });
  const parts = [
    ['1', 'Workflow repository', 'Downloadable, reusable editing workflows the creator sets up once with their AI assistant.'],
    ['2', 'Web library', 'Browse, save and configure workflows: style, protected sections, optional B-roll.'],
    ['3', 'Creator review', 'Every AI-assisted step produces a proposal. Nothing is final until the creator approves.'],
  ];
  parts.forEach(([n, h, b], i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 2.75, 3.85, 2.45);
    iconCircle(s, x + 0.3, 3.05, n);
    txt(s, h, { x: x + 0.3, y: 3.8, w: 3.3, h: 0.4, fontSize: 17, bold: true });
    txt(s, b, { x: x + 0.3, y: 4.25, w: 3.3, h: 0.9, fontSize: 13, color: K.ink2 });
  });
  kicker(s, 'What EditFlo is not', 0.6, 5.6, 6, K.mut);
  ['Not a video editor', 'Not a chatbot', 'Not a project-management tool', 'Not a replacement for the creator'].reduce((x, t) => x + chip(s, t, x, 5.98, { fill: K.sunk, color: K.ink2 }) + 0.15, 0.6);
}
// 6 — How it works
{
  const s = content('How it works', 'Solution',
    'MCP (Model Context Protocol) is an open standard that lets an AI assistant connect to external tools. EditFlo uses it to pass workflow instructions to a compatible assistant, which applies them in the editing environment. OpenFilm is the editing environment EditFlo is designed around; other editors are a later concept.');
  const nodes = [
    ['EditFlo', 'Stores and organises the reusable workflow', 'In prototype', K.p],
    ['MCP', 'Open standard that connects the workflow to tools', 'In prototype', K.p],
    ['AI assistant', 'The creator’s own MCP-compatible assistant follows the instructions', 'Exploring', 'A77CC9'],
    ['OpenFilm', 'The editing environment where the edit is applied', 'Concept', K.mut],
    ['Creator review', 'Accept, adjust or undo every change', 'By design', K.ink],
  ];
  const w = 2.25, gap = 0.21;
  nodes.forEach(([h, b, st, c], i) => {
    const x = 0.6 + i * (w + gap), y = 1.75;
    card(s, x, y, w, 2.9, { fill: i === 0 ? K.p : K.white, line: i === 0 ? K.p : 'ECE7E0' });
    txt(s, '0' + (i + 1), { x: x + 0.25, y: y + 0.25, w: 1, h: 0.3, fontSize: 11, bold: true, color: i === 0 ? 'E9DCF6' : K.faint });
    txt(s, h, { x: x + 0.25, y: y + 0.6, w: w - 0.4, h: 0.45, fontSize: 18, bold: true, color: i === 0 ? K.white : K.ink });
    txt(s, b, { x: x + 0.25, y: y + 1.1, w: w - 0.4, h: 1.1, fontSize: 12.5, color: i === 0 ? 'EFE4F8' : K.ink2 });
    chip(s, st, x + 0.25, y + 2.35, { fill: i === 0 ? K.white : K.tint, color: i === 0 ? K.p : c, w: w - 0.5 });
    if (i < 4) s.addShape(pres.shapes.LINE, { x: x + w + 0.02, y: y + 1.45, w: gap - 0.04, h: 0, line: { color: K.p, width: 1.75, endArrowType: 'triangle' } });
  });
  card(s, 0.6, 5.0, 12.1, 1.55, { fill: K.tint, line: K.tint });
  txt(s, 'In plain terms', { x: 0.9, y: 5.22, w: 3, h: 0.3, fontSize: 13, bold: true, color: K.p });
  txt(s, 'EditFlo is the recipe, the AI assistant is the cook, OpenFilm is the kitchen — and the creator tastes the result before it is served. Statuses are the founder’s own assessment: only the workflow library and MCP connection exist as a partial prototype.', { x: 0.9, y: 5.55, w: 11.5, h: 0.9, fontSize: 13.5, color: K.ink2 });
}
// 7 — Product: dashboard
{
  const s = content('The product: start from a workflow, not a blank timeline', 'Solution',
    'Conceptual prototype screen (design, not deployed software). The dashboard makes finding a reusable workflow the primary action.');
  s.addImage({ path: IMG('01-dashboard.png'), x: 0.6, y: 1.4, w: 7.6, h: 5.404, rounding: false });
  const pts = [['Search by editing task', 'Creators look for the job they repeat — “remove pauses”, “organise raw footage”.'], ['Reusable workflows', 'Long-form, short-form, podcast and general workflows as starting points.'], ['How it works, in three steps', 'Choose a workflow, connect your tools, review and approve.']];
  pts.forEach(([h, b], i) => { const y = 1.5 + i * 1.6; iconCircle(s, 8.6, y, String(i + 1), { d: 0.45 }); txt(s, h, { x: 9.25, y, w: 3.45, h: 0.35, fontSize: 15, bold: true }); txt(s, b, { x: 9.25, y: y + 0.4, w: 3.45, h: 0.9, fontSize: 12.5, color: K.ink2 }); });
  chip(s, 'Conceptual prototype', 8.6, 6.35, { w: 2.4 });
}
// 8 — Product: control
{
  const s = content('The creator stays in control at every stage', 'Solution',
    'Workflow detail screen (conceptual). Only stage 04 is AI-assisted; every stage has an explicit review point. Style and optional B-roll reflect follow-up findings from B and D.');
  s.addImage({ path: IMG('02-workflow-detail.png'), x: 0.6, y: 1.4, w: 7.6, h: 5.404 });
  const pts = [['One AI-assisted stage', 'The assistant proposes a rough cut; it never finalises one.'], ['Protected sections', '“Always keep” moments are never cut — from A and D.'], ['Style per project, optional B-roll', 'From B and D; B-roll is off by default because A did not want it.'], ['Review before finalising', 'Locked on for every export.']];
  pts.forEach(([h, b], i) => { const y = 1.45 + i * 1.22; iconCircle(s, 8.6, y, '✓', { d: 0.42 }); txt(s, h, { x: 9.2, y, w: 3.5, h: 0.35, fontSize: 14.5, bold: true }); txt(s, b, { x: 9.2, y: y + 0.38, w: 3.5, h: 0.7, fontSize: 12.5, color: K.ink2 }); });
}
// 9 — Differentiation
{
  const s = content('Why not existing alternatives?', 'Solution',
    'Differentiation is a hypothesis until side-by-side pilot tests compare setup effort, editing time, corrections and creator satisfaction.');
  const H = (t) => ({ text: t, options: { bold: true, color: K.white, fill: { color: K.ink }, fontSize: 12, fontFace: 'Inter', margin: [6, 8, 6, 8] } });
  const C = (t, o = {}) => ({ text: t, options: Object.assign({ fontSize: 12.5, color: K.ink2, fontFace: 'Inter', margin: [6, 8, 6, 8], valign: 'middle' }, o) });
  const rows = [
    [H('Alternative'), H('What it offers'), H('Where it falls short for this customer'), H('EditFlo’s intended difference')],
    [C('Manual editing', { bold: true, color: K.ink }), C('Full control'), C('Same repetitive steps every video'), C('Reusable instructions for the repetitive steps; creative decisions stay with the creator')],
    [C('Freelance editor', { bold: true, color: K.ink }), C('Human judgement'), C('Cost per post, availability, briefing each time (A paid ~₹1,500/post)'), C('Repeatable workflow for recurring formats; not a replacement for bespoke editing')],
    [C('General-purpose AI tools', { bold: true, color: K.ink }), C('Broad assistance'), C('Inconsistent output and token costs (B); no editing structure'), C('Creator-defined workflow stages, protected sections and review checkpoints')],
    [C('Editing applications', { bold: true, color: K.ink }), C('The editing environment'), C('Tools, not a repeatable process'), C('Works with the editor rather than replacing it')],
  ];
  s.addTable(rows, { x: 0.6, y: 1.45, w: 12.1, colW: [2.2, 2.2, 3.7, 4.0], border: { type: 'solid', color: 'E2DCD3', pt: 0.75 }, fill: { color: K.white }, rowH: [0.45, 0.85, 0.85, 0.85, 0.85] });
  card(s, 0.6, 5.65, 12.1, 0.95, { fill: K.tint, line: K.tint });
  txt(s, 'Still to test: how EditFlo compares with built-in automation in mainstream editing tools on the same tasks (pause removal, trimming, footage selection).', { x: 0.9, y: 5.83, w: 11.5, h: 0.6, fontSize: 13.5, color: K.ink2, valign: 'middle' });
}

pres.addSection({ title: 'Business' });
// 10 — Business model & pricing
{
  const s = content('Business model and pricing test', 'Business',
    'Both price points are hypotheses. Customers pay separately for their own AI assistant and editing software. The ₹1,500-per-post figure is one participant’s experience, used as a reference point only.');
  const opts = [['Option A', '₹3,000', 'one-time', 'Workflow repository + web library access. For creators who prefer a single payment.'], ['Option B', '₹500', 'per month', 'Lower-commitment way to start. Tests whether creators prefer to try before committing.']];
  opts.forEach(([k, p, per, d], i) => {
    const x = 0.6 + i * 3.95;
    card(s, x, 1.45, 3.7, 3.25);
    kicker(s, k, x + 0.3, 1.75, 3);
    txt(s, p, { x: x + 0.3, y: 2.1, w: 3.2, h: 0.85, fontSize: 40, bold: true, color: K.ink });
    txt(s, per, { x: x + 0.3, y: 2.95, w: 3.2, h: 0.35, fontSize: 14, color: K.mut });
    txt(s, d, { x: x + 0.3, y: 3.45, w: 3.15, h: 1.1, fontSize: 12.5, color: K.ink2 });
  });
  card(s, 8.5, 1.45, 4.2, 3.25, { fill: K.sunk, line: K.sunk });
  kicker(s, 'Optional add-ons', 8.8, 1.75, 3.6, K.ink2);
  ['Installation and configuration', 'Technical support'].forEach((t, i) => { txt(s, '+  ' + t, { x: 8.8, y: 2.2 + i * 0.45, w: 3.7, h: 0.35, fontSize: 14 }); });
  kicker(s, 'Customer also needs', 8.8, 3.25, 3.6, K.ink2);
  txt(s, 'A compatible AI assistant and editing software, paid for separately.', { x: 8.8, y: 3.62, w: 3.7, h: 0.8, fontSize: 12.5, color: K.ink2 });
  card(s, 0.6, 5.0, 12.1, 1.6, { fill: K.white });
  txt(s, 'Why predictable pricing', { x: 0.9, y: 5.22, w: 4, h: 0.3, fontSize: 13, bold: true, color: K.p });
  txt(s, 'B and D both rejected unpredictable, token-based costs. A flat price makes EditFlo’s cost easy to judge. Still unvalidated: which option creators choose, what the one-time price includes (updates, support period), and the total cost once AI usage is added.', { x: 0.9, y: 5.55, w: 11.5, h: 0.95, fontSize: 13, color: K.ink2 });
}
// 11 — Validation plan
{
  const s = content('Validation plan: prove it saves time before scaling', 'Business',
    'No traction, revenue or time-saving figures are claimed. These are the measures the pilot will produce.');
  const steps = [['1', 'Pilot', 'Regular creators run EditFlo on their own raw footage, instructions and protected sections.'], ['2', 'Measure', 'Setup time, editing time vs their usual process, corrections needed, protected sections kept, satisfaction.'], ['3', 'Test pricing', 'Compare ₹500/month and ₹3,000 one-time using a purchase or deposit signal, not stated interest.'], ['4', 'Decide', 'Continue, narrow or change the workflow based on accepted edits and paid conversions.']];
  steps.forEach(([n, h, b], i) => {
    const x = 0.6 + i * 3.075;
    card(s, x, 1.55, 2.85, 3.3);
    iconCircle(s, x + 0.3, 1.85, n);
    txt(s, h, { x: x + 0.3, y: 2.6, w: 2.3, h: 0.4, fontSize: 18, bold: true });
    txt(s, b, { x: x + 0.3, y: 3.05, w: 2.3, h: 1.7, fontSize: 12.5, color: K.ink2 });
    if (i < 3) s.addShape(pres.shapes.LINE, { x: x + 2.87, y: 3.2, w: 0.19, h: 0, line: { color: K.p, width: 1.75, endArrowType: 'triangle' } });
  });
  card(s, 0.6, 5.15, 12.1, 1.45, { fill: K.tint, line: K.tint });
  txt(s, 'Before scaling', { x: 0.9, y: 5.37, w: 4, h: 0.3, fontSize: 13, bold: true, color: K.p });
  txt(s, 'Document supported software and AI-assistant requirements, test workflow reliability across real projects, define update and support commitments, and collect permission-based demonstrations.', { x: 0.9, y: 5.7, w: 11.5, h: 0.8, fontSize: 13, color: K.ink2 });
}
// 12 — Risks
{
  const s = content('Key risks and how we will address them', 'Business',
    'Risks identified from the interviews and the product architecture.');
  const R = [
    ['Technical reliability', 'AI-assisted trimming may cut the wrong sections.', 'Protected sections, review checkpoints, pilot on real footage first.'],
    ['Platform dependence', 'Changes to AI assistants, MCP support or OpenFilm.', 'Document supported versions; keep workflows tool-agnostic where possible.'],
    ['AI usage cost', 'Customers pay their own token costs — a concern raised by B and D.', 'Avoid unnecessary generations; show expected usage per workflow.'],
    ['Copyability', 'Workflow files can be shared once bought.', 'Value in updates, the web library, setup and support — not files alone.'],
    ['Segment uncertainty', 'The beachhead rests mainly on one participant (D).', 'Recruit pilot creators from this segment and test before expanding.'],
  ];
  const H = (t) => ({ text: t, options: { bold: true, color: K.white, fill: { color: K.ink }, fontSize: 12, fontFace: 'Inter', margin: [6, 8, 6, 8] } });
  const C = (t, o = {}) => ({ text: t, options: Object.assign({ fontSize: 12.5, color: K.ink2, fontFace: 'Inter', margin: [6, 8, 6, 8], valign: 'middle' }, o) });
  s.addTable([[H('Risk'), H('Why it matters'), H('Mitigation')], ...R.map(([a, b, c]) => [C(a, { bold: true, color: K.ink }), C(b), C(c)])], { x: 0.6, y: 1.45, w: 12.1, colW: [2.6, 4.6, 4.9], border: { type: 'solid', color: 'E2DCD3', pt: 0.75 }, fill: { color: K.white }, rowH: [0.45, 0.85, 0.85, 0.85, 0.85, 0.85] });
}

pres.addSection({ title: 'The ask' });
// 13 — Ask
{
  const s = pres.addSlide({ masterName: 'EF_DARK', sectionTitle: 'The ask' });
  txt(s, 'INCUBATION SUPPORT REQUESTED', { x: 0.75, y: 0.75, w: 9, h: 0.3, fontSize: 12, bold: true, color: 'E9DCF6', charSpacing: 2 });
  txt(s, 'Help us run a credible pilot', { x: 0.75, y: 1.15, w: 11, h: 0.9, fontSize: 40, bold: true, color: K.white });
  const asks = [['Technical mentorship', 'MCP and editing-environment integration, reliability testing.'], ['Access to pilot creators', 'Introductions to regular creators of recurring formats.'], ['AI usage credits', 'To run pilot edits without passing token costs to participants.'], ['Business guidance', 'Pricing, licensing of workflows and go-to-market.']];
  asks.forEach(([h, b], i) => {
    const x = 0.75 + (i % 2) * 6.0, y = 2.4 + Math.floor(i / 2) * 1.75;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 5.7, h: 1.5, rectRadius: 0.1, fill: { color: '8E45CC' }, line: { color: '9A57D3', width: 0.75 } });
    txt(s, h, { x: x + 0.3, y: y + 0.25, w: 5.1, h: 0.4, fontSize: 18, bold: true, color: K.white });
    txt(s, b, { x: x + 0.3, y: y + 0.72, w: 5.1, h: 0.6, fontSize: 13.5, color: 'EFE4F8' });
  });
  txt(s, 'Create more. Edit less. Start publishing.', { x: 0.75, y: 6.15, w: 8, h: 0.45, fontSize: 20, bold: true, color: K.white });
  txt(s, 'Video pitch: youtube.com/watch?v=SlrPQ5JF8vY', { x: 0.75, y: 6.65, w: 8, h: 0.3, fontSize: 12, color: 'E9DCF6', hyperlink: { url: 'https://www.youtube.com/watch?v=SlrPQ5JF8vY' } });
  s.addImage({ path: IMG('mark-white.png'), x: 11.75, y: 6.1, w: 0.8, h: 0.8 });
  s.addNotes('Close: the immediate goal is a structured pilot with regular creators that measures time saved and tests both price options.');
}

(async () => {
  const out = path.join(__dirname, '..', 'final', '25120989_EditFlo_Pitch_Deck.pptx');
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log('wrote', out);
})();
