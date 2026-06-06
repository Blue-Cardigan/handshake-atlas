"use strict";

const FAMILY_COLORS = {
  Constant: "#6b7280",
  Alternating: "#c084fc",
  Barker: "#fbbf24",
  Unbordered: "#38bdf8",
  "Self-similar": "#4ade80",
  Generic: "#475569",
};

const METRIC_LABELS = {
  min_automaton_states: "Automaton size",
  merit_factor: "Merit factor",
  linear_complexity: "Linear complexity",
  lz76: "LZ76",
  invade_alld: "Invade-AllD fixation",
  mimic_fixation: "Mimic fixation (unconditional)",
  mimic_fixation_grim: "Mimic fixation (grim)",
};

let ATLAS = null;
let SELECTED = null;

const $ = (id) => document.getElementById(id);
const tooltip = Object.assign(document.createElement("div"), { className: "tooltip" });
document.body.appendChild(tooltip);

init();

async function init() {
  let data;
  try {
    const res = await fetch("./data/atlas.json");
    data = await res.json();
  } catch (e) {
    $("table").innerHTML =
      '<p style="color:#e06a6a;padding:20px">Could not load <code>data/atlas.json</code>. ' +
      "Serve this folder over HTTP (e.g. <code>python3 -m http.server</code>) rather than " +
      "opening the file directly.</p>";
    return;
  }
  ATLAS = data;
  $("meta").textContent =
    `${data.meta.n_handshakes} handshakes · structural ≤ k=${data.meta.struct_max} · ` +
    `evolutionary ≤ k=${data.meta.evo_max} · N=${data.meta.evolution.population}, ` +
    `${data.meta.evolution.rounds} rounds`;

  const famSel = $("familyFilter");
  for (const name of Object.keys(data.meta.families)) {
    const o = document.createElement("option");
    o.value = name;
    o.textContent = `${name} (${data.meta.families[name].count})`;
    famSel.appendChild(o);
  }

  ["metric", "familyFilter", "barkerOnly", "unborderedOnly"].forEach((id) =>
    $(id).addEventListener("change", render)
  );
  $("search").addEventListener("input", render);
  render();
}

function metricRange(metric) {
  let lo = Infinity,
    hi = -Infinity;
  for (const h of ATLAS.handshakes) {
    const v = h[metric];
    if (v == null) continue;
    if (v < lo) lo = v;
    if (v > hi) hi = v;
  }
  return [lo, hi];
}

function lerpColor(t) {
  // dark teal -> accent green
  const a = [35, 51, 51],
    b = [111, 227, 196];
  const c = a.map((x, i) => Math.round(x + (b[i] - x) * t));
  return `rgb(${c[0]},${c[1]},${c[2]})`;
}

function cellColor(h, metric) {
  if (metric === "family") return FAMILY_COLORS[h.family] || "#475569";
  const v = h[metric];
  if (v == null) return "#222838";
  const [lo, hi] = metricRange(metric);
  const t = hi > lo ? (v - lo) / (hi - lo) : 0.5;
  return lerpColor(t);
}

function passesFilters(h) {
  const fam = $("familyFilter").value;
  if (fam && h.family !== fam) return false;
  if ($("barkerOnly").checked && !h.is_barker) return false;
  if ($("unborderedOnly").checked && !h.is_unbordered) return false;
  const q = $("search").value.trim().toUpperCase();
  if (q && !h.label.startsWith(q)) return false;
  return true;
}

function render() {
  const metric = $("metric").value;
  renderLegend(metric);

  const byLength = new Map();
  for (const h of ATLAS.handshakes) {
    if (!byLength.has(h.length)) byLength.set(h.length, []);
    byLength.get(h.length).push(h);
  }

  const table = $("table");
  table.innerHTML = "";
  let visible = 0;

  for (const k of [...byLength.keys()].sort((a, b) => a - b)) {
    const row = document.createElement("div");
    row.className = "row";
    const label = document.createElement("div");
    label.className = "row-label mono";
    label.textContent = `k=${k}`;
    const cells = document.createElement("div");
    cells.className = "row-cells";

    for (const h of byLength.get(k)) {
      const cell = document.createElement("div");
      cell.className = "cell";
      cell.style.background = cellColor(h, metric);
      const ok = passesFilters(h);
      if (!ok) cell.classList.add("dim");
      else visible++;
      if (SELECTED && SELECTED.label === h.label) cell.classList.add("selected");
      cell.addEventListener("mouseenter", (e) => showTip(e, h, metric));
      cell.addEventListener("mousemove", moveTip);
      cell.addEventListener("mouseleave", hideTip);
      cell.addEventListener("click", () => selectHandshake(h));
      cells.appendChild(cell);
    }
    row.appendChild(label);
    row.appendChild(cells);
    table.appendChild(row);
  }
  $("count").textContent = `${visible} shown`;
}

function renderLegend(metric) {
  const legend = $("legend");
  legend.innerHTML = "";
  if (metric === "family") {
    for (const [name, color] of Object.entries(FAMILY_COLORS)) {
      const chip = document.createElement("span");
      chip.className = "chip";
      chip.innerHTML = `<span class="swatch" style="background:${color}"></span>${name}`;
      legend.appendChild(chip);
    }
  } else {
    const [lo, hi] = metricRange(metric);
    legend.innerHTML =
      `<span class="chip mono">${fmt(lo)}</span>` +
      `<span class="grad"></span>` +
      `<span class="chip mono">${fmt(hi)}</span>` +
      `<span class="chip">${METRIC_LABELS[metric] || metric}` +
      (metric === "merit_factor" || metric.includes("invade") || metric.includes("mimic")
        ? " · grey = not computed (k &gt; evo-max)"
        : "") +
      `</span>`;
  }
}

function fmt(v) {
  if (v == null) return "—";
  if (Number.isInteger(v)) return String(v);
  return v.toFixed(3);
}

function showTip(e, h, metric) {
  const extra = metric !== "family" && h[metric] != null ? ` · ${fmt(h[metric])}` : "";
  tooltip.textContent = `${h.label} · ${h.family}${extra}`;
  tooltip.style.opacity = "1";
  moveTip(e);
}
function moveTip(e) {
  tooltip.style.left = e.clientX + 14 + "px";
  tooltip.style.top = e.clientY + 14 + "px";
}
function hideTip() {
  tooltip.style.opacity = "0";
}

function selectHandshake(h) {
  SELECTED = h;
  render();
  const d = $("detail");
  d.classList.remove("hidden");
  const fam = ATLAS.meta.families[h.family];
  const bits = [...h.label]
    .map((c) => `<div class="bit ${c}">${c}</div>`)
    .join("");
  const famColor = FAMILY_COLORS[h.family] || "#475569";

  const evo = h.self_payoff != null;
  const evoRows = evo
    ? `<h3>Evolutionary (N=${ATLAS.meta.evolution.population})</h3><dl>
        ${row("Self payoff", fmt(h.self_payoff))}
        ${row("Payoff vs AllD", fmt(h.payoff_vs_alld))}
        ${row("Invade AllD", fmt(h.invade_alld))}
        ${boolRow("Invades defectors", h.invade_alld_favoured)}
      </dl>
      <h3>Mimic-resistance by regime <span style="color:var(--muted);text-transform:none;letter-spacing:0">(fixation; resistant if &lt; ${fmt(ATLAS.meta.evolution ? 1 / ATLAS.meta.evolution.population : 0)})</span></h3>
      <dl>
        ${regimeRow("Unconditional (coop)", h.mimic_fixation, h.mimic_resistant)}
        ${regimeRow("Grim", h.mimic_fixation_grim, h.mimic_resistant_grim)}
        ${regimeRow("Tit-for-tat", h.mimic_fixation_tft, h.mimic_resistant_tft)}
      </dl>`
    : `<h3>Evolutionary</h3><p class="desc">Not computed for k=${h.length} (beyond evo-max=${ATLAS.meta.evo_max}).</p>`;

  d.innerHTML = `
    <button class="close" aria-label="close">&times;</button>
    <h2>${h.label}</h2>
    <div class="pattern">${bits}</div>
    <span class="famtag" style="background:${famColor}">${h.family}</span>
    <p class="desc">${fam ? fam.description : ""}</p>
    <h3>Watch it play</h3>
    <div class="play-controls">
      <select id="play-opp">
        <option value="self">vs a copy of itself</option>
        <option value="AllD">vs AllD (defectors)</option>
        <option value="mimic">vs a mimic</option>
      </select>
      <select id="play-regime" title="post-recognition regime">
        <option value="coop">coop</option>
        <option value="grim">grim</option>
        <option value="tft">tft</option>
      </select>
      <button id="play-toggle" class="play-btn">&#9654; play</button>
      <button id="play-reset" class="play-btn" title="reset">&#8634;</button>
    </div>
    <div id="play-board" class="play-board"></div>
    <p id="play-caption" class="play-caption"></p>
    <p id="play-regime-desc" class="regime-desc"></p>
    <h3>Autocorrelation</h3>
    <dl>
      ${row("Peak sidelobe", h.peak_sidelobe)}
      ${row("Merit factor", fmt(h.merit_factor))}
      ${boolRow("Barker code", h.is_barker)}
    </dl>
    ${sidelobeSpark(h.sidelobes)}
    <h3>Self-overlap</h3>
    <dl>
      ${row("Longest border", h.longest_border)}
      ${row("Shortest period", h.shortest_period)}
      ${boolRow("Unbordered", h.is_unbordered)}
    </dl>
    <h3>Complexity</h3>
    <dl>
      ${row("LZ76", h.lz76)}
      ${row("Linear complexity", h.linear_complexity)}
      ${row("Distinct factors", h.distinct_factors)}
      ${row("Bit entropy", fmt(h.bit_entropy))}
      ${row("Min automaton states", h.min_automaton_states)}
      ${row("Raw automaton states", h.raw_automaton_states)}
    </dl>
    ${evoRows}
  `;
  d.querySelector(".close").addEventListener("click", () => {
    d.classList.add("hidden");
    SELECTED = null;
    stopPlay();
    render();
  });
  initPlay(h);
}

// --- per-handshake play animation -----------------------------------------
let PLAY = { timer: null };

function stopPlay() {
  if (PLAY.timer) clearInterval(PLAY.timer);
  PLAY.timer = null;
}

function initPlay(h) {
  stopPlay();
  const prefix = labelToPrefix(h.label);
  const rounds = Math.max(8, h.length + 6);
  const board = $("play-board");
  const caption = $("play-caption");
  const oppSel = $("play-opp");
  const regSel = $("play-regime");
  const toggle = $("play-toggle");

  const state = { frame: 0, match: null };

  function rebuild() {
    stopPlay();
    toggle.innerHTML = "&#9654; play";
    state.frame = 0;
    state.match = buildMatch(prefix, oppSel.value, regSel.value, rounds);
    $("play-regime-desc").innerHTML =
      `<b>${regSel.value}</b> &mdash; ${REGIME_DESC[regSel.value]}`;
    draw();
  }
  function draw() {
    renderPlay(board, state.match, state.frame);
    caption.textContent = playCaption(state.match, state.frame);
  }
  function step() {
    if (state.frame < state.match.rounds.length) {
      state.frame++;
      draw();
    } else {
      stopPlay();
      toggle.innerHTML = "&#9654; play";
    }
  }

  oppSel.addEventListener("change", rebuild);
  regSel.addEventListener("change", rebuild);
  $("play-reset").addEventListener("click", rebuild);
  toggle.addEventListener("click", () => {
    if (PLAY.timer) {
      stopPlay();
      toggle.innerHTML = "&#9654; play";
      return;
    }
    if (state.frame >= state.match.rounds.length) state.frame = 0;
    toggle.innerHTML = "&#10073;&#10073; pause";
    PLAY.timer = setInterval(step, 650);
  });

  rebuild();
}

function renderPlay(board, match, frame) {
  const n = match.rounds.length;
  const k = match.k;
  let nums = "";
  let them = "";
  let me = "";
  for (let i = 0; i < n; i++) {
    const shown = i < frame;
    const rd = match.rounds[i];
    const pfx = i < k ? " pfx" : "";
    nums += `<div class="pc-num${pfx}">${i + 1}</div>`;
    them += playCell(shown ? rd.them : null, pfx);
    me += playCell(shown ? rd.me : null, pfx);
  }
  const score = frame > 0 ? match.rounds[frame - 1].scoreMe : 0;
  const per = frame > 0 ? (score / frame).toFixed(2) : "0.00";
  board.innerHTML =
    `<div class="pc-row pc-head"><div class="pc-label">round</div>${nums}</div>` +
    `<div class="pc-row"><div class="pc-label">them</div>${them}</div>` +
    `<div class="pc-row"><div class="pc-label">you</div>${me}</div>` +
    `<div class="pc-foot">first ${k} = prefix · payoff to you ` +
    `<b>${score}</b> (${per}/round)</div>`;
}

function playCell(move, pfx) {
  if (move === null) return `<div class="pc-cell empty${pfx}"></div>`;
  return `<div class="pc-cell ${move}${pfx}">${move}</div>`;
}

function playCaption(match, frame) {
  const k = match.k;
  if (frame === 0) return "Press play. The first " + k + " rounds are the handshake prefix.";
  if (frame <= k) return `Playing the recognition prefix (round ${frame} of ${k}).`;
  // past the prefix
  const opp = match.opponent;
  const reg = match.regime;
  if (opp === "self") return "Both echoed the prefix — mutual recognition, cooperating forever (R=3 each).";
  if (opp === "AllD") {
    return match.recognised
      ? "AllD happens to match the all-defect prefix → mis-recognised as kin; you cooperate into exploitation."
      : "AllD never echoed a cooperative bit → not recognised; you defect forever (the prefix's cooperative bits were the probe cost).";
  }
  // mimic
  if (reg === "coop")
    return "The mimic forged the prefix, was recognised, and now defects — coop keeps cooperating, so it is exploited (S=0).";
  return "The mimic defects after the handshake; the vigilant regime punishes → mutual defection (P=1). Forgery yields nothing.";
}

function row(k, v) {
  return `<dt>${k}</dt><dd>${v}</dd>`;
}
function boolRow(k, v) {
  if (v == null) return row(k, "—");
  return `<dt>${k}</dt><dd class="${v ? "yes" : "no"}">${v ? "yes" : "no"}</dd>`;
}
function regimeRow(k, fix, resistant) {
  if (fix == null) return row(k, "—");
  const cls = resistant ? "yes" : "no";
  const mark = resistant ? " ✓resists" : " ✗bled";
  return `<dt>${k}</dt><dd class="${cls}">${fmt(fix)}${mark}</dd>`;
}
function sidelobeSpark(sidelobes) {
  if (!sidelobes || !sidelobes.length) return "";
  const max = Math.max(1, ...sidelobes.map((x) => Math.abs(x)));
  const bars = sidelobes
    .map((c) => {
      const hgt = (Math.abs(c) / max) * 100;
      return `<div class="bar ${c < 0 ? "neg" : ""}" style="height:${hgt}%"></div>`;
    })
    .join("");
  return `<div class="spark" title="aperiodic autocorrelation sidelobes">${bars}</div>`;
}
