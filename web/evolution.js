"use strict";
// Spatial evolutionary simulation: handshakes EMERGE from selection rather than being
// prescribed. Each cell holds an agent with a heritable genotype (recognition prefix +
// whether it is a mimic). Agents play the gated IPD against their neighbours (reusing the
// play.js engine), the best-scoring neighbour's genotype is imitated, and mutation flips
// prefix bits or toggles the mimic trait. Watch cooperating same-prefix clusters form,
// mimics invade, vigilant regimes punish them, and recognition prefixes turn over.

const COLS = 84;
const ROWS = 52;
const ROUNDS = 12; // rounds per pairwise encounter
// Moore neighbourhood offsets.
const NB = [
  [-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1],
];

// strat id = prefixIndex * 2 + (isMimic ? 1 : 0)
function prefixOf(strat, k) {
  const idx = strat >> 1;
  const p = [];
  for (let i = 0; i < k; i++) p.push((idx >> (k - 1 - i)) & 1 ? "C" : "D");
  return p;
}
const isMimic = (strat) => (strat & 1) === 1;

function playerFor(strat, k, regime) {
  const prefix = prefixOf(strat, k);
  return isMimic(strat) ? mimicPlayer(prefix) : gatedPlayer(prefix, regime);
}

// Memoised payoff-to-A table over all strategies for the current (k, regime).
function buildMatchups(k, regime) {
  const nStrat = (1 << k) * 2;
  const table = [];
  const players = [];
  for (let s = 0; s < nStrat; s++) players.push(playerFor(s, k, regime));
  for (let a = 0; a < nStrat; a++) {
    table.push(new Float32Array(nStrat));
    for (let b = 0; b < nStrat; b++) {
      const log = simulate(players[a], players[b], ROUNDS);
      table[a][b] = log[ROUNDS - 1].scoreMe / ROUNDS;
    }
  }
  return table;
}

// hue from prefix index so same-prefix clusters share a colour; mimics drawn darker + dot.
function cellColor(strat, k) {
  const nPrefix = 1 << k;
  const hue = Math.round(((strat >> 1) / nPrefix) * 360);
  return isMimic(strat)
    ? `hsl(${hue},70%,30%)`
    : `hsl(${hue},68%,56%)`;
}

class World {
  constructor(k, regime, mutation) {
    this.k = k;
    this.regime = regime;
    this.mutation = mutation;
    this.nStrat = (1 << k) * 2;
    this.table = buildMatchups(k, regime);
    this.grid = new Int16Array(COLS * ROWS);
    this.gen = 0;
    this.history = [];
    this.rngState = 0x9e3779b9;
    this.seedRandom();
  }
  rand() {
    // xorshift32, deterministic
    let x = this.rngState | 0;
    x ^= x << 13; x ^= x >>> 17; x ^= x << 5;
    this.rngState = x | 0;
    return ((x >>> 0) % 100000) / 100000;
  }
  seedRandom() {
    // mostly handshakers with random prefixes, a few mimics
    for (let i = 0; i < this.grid.length; i++) {
      const prefixIdx = Math.floor(this.rand() * (1 << this.k));
      const mim = this.rand() < 0.05 ? 1 : 0;
      this.grid[i] = prefixIdx * 2 + mim;
    }
  }
  idx(c, r) {
    return ((r + ROWS) % ROWS) * COLS + ((c + COLS) % COLS);
  }
  fitnessAt(i) {
    const c = i % COLS;
    const r = (i / COLS) | 0;
    const self = this.grid[i];
    let f = 0;
    for (const [dc, dr] of NB) f += this.table[self][this.grid[this.idx(c + dc, r + dr)]];
    return f;
  }
  mutate(strat) {
    if (this.rand() >= this.mutation) return strat;
    if (this.rand() < 0.5) {
      // flip a random prefix bit
      const bit = Math.floor(this.rand() * this.k);
      const prefixIdx = (strat >> 1) ^ (1 << bit);
      return prefixIdx * 2 + (strat & 1);
    }
    return strat ^ 1; // toggle mimic trait
  }
  step() {
    const fit = new Float32Array(this.grid.length);
    for (let i = 0; i < this.grid.length; i++) fit[i] = this.fitnessAt(i);
    const next = new Int16Array(this.grid.length);
    for (let i = 0; i < this.grid.length; i++) {
      const c = i % COLS;
      const r = (i / COLS) | 0;
      let bestStrat = this.grid[i];
      let bestFit = fit[i];
      for (const [dc, dr] of NB) {
        const j = this.idx(c + dc, r + dr);
        if (fit[j] > bestFit) {
          bestFit = fit[j];
          bestStrat = this.grid[j];
        }
      }
      next[i] = this.mutate(bestStrat);
    }
    this.grid = next;
    this.gen++;
    this.recordStats(fit);
  }
  recordStats(fit) {
    let mimics = 0;
    let payoff = 0;
    const prefixes = new Set();
    for (let i = 0; i < this.grid.length; i++) {
      const s = this.grid[i];
      if (isMimic(s)) mimics++;
      else prefixes.add(s >> 1);
      payoff += fit[i];
    }
    const n = this.grid.length;
    this.history.push({
      mimicFreq: mimics / n,
      meanPayoff: payoff / n / NB.length, // per-encounter, 0..~3
      diversity: prefixes.size,
    });
    if (this.history.length > 240) this.history.shift();
  }
}

// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

let WORLD = null;
let TIMER = null;
const $ = (id) => document.getElementById(id);

function gridCanvas() {
  return $("ev-grid");
}
function drawGrid() {
  const cv = gridCanvas();
  const ctx = cv.getContext("2d");
  const px = cv.width / COLS;
  const py = cv.height / ROWS;
  for (let i = 0; i < WORLD.grid.length; i++) {
    const c = i % COLS;
    const r = (i / COLS) | 0;
    const s = WORLD.grid[i];
    ctx.fillStyle = cellColor(s, WORLD.k);
    ctx.fillRect(c * px, r * py, px, py);
    if (isMimic(s)) {
      ctx.fillStyle = "rgba(0,0,0,0.78)";
      ctx.fillRect(c * px + px * 0.34, r * py + py * 0.34, px * 0.32, py * 0.32);
    }
  }
}

function drawChart() {
  const cv = $("ev-chart");
  const ctx = cv.getContext("2d");
  const W = cv.width;
  const H = cv.height;
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = "#141824";
  ctx.fillRect(0, 0, W, H);
  const hist = WORLD.history;
  if (hist.length < 2) return;
  const n = hist.length;
  const x = (i) => (i / (n - 1)) * W;
  const maxDiv = Math.max(2, ...hist.map((h) => h.diversity));
  const line = (key, color, scale) => {
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.6;
    ctx.beginPath();
    hist.forEach((h, i) => {
      const y = H - scale(h) * H;
      i ? ctx.lineTo(x(i), y) : ctx.moveTo(x(i), y);
    });
    ctx.stroke();
  };
  line("meanPayoff", "#4ade80", (h) => Math.min(1, h.meanPayoff / 3));
  line("mimicFreq", "#e06a6a", (h) => h.mimicFreq);
  line("diversity", "#38bdf8", (h) => h.diversity / maxDiv);
}

function drawStats() {
  const h = WORLD.history[WORLD.history.length - 1];
  if (!h) return;
  $("ev-stats").innerHTML =
    `gen <b>${WORLD.gen}</b> &middot; ` +
    `mean payoff <b style="color:var(--good)">${h.meanPayoff.toFixed(2)}</b> &middot; ` +
    `mimics <b style="color:var(--bad)">${Math.round(h.mimicFreq * 100)}%</b> &middot; ` +
    `live prefixes <b style="color:#38bdf8">${h.diversity}</b>`;
}

function render() {
  drawGrid();
  drawChart();
  drawStats();
}

function rebuild() {
  stop();
  WORLD = new World(
    parseInt($("ev-k").value, 10),
    $("ev-regime").value,
    parseFloat($("ev-mut").value)
  );
  render();
}
function stop() {
  if (TIMER) clearInterval(TIMER);
  TIMER = null;
  $("ev-play").innerHTML = "&#9654; play";
}
function play() {
  if (TIMER) {
    stop();
    return;
  }
  $("ev-play").innerHTML = "&#10073;&#10073; pause";
  const delay = () => 220 - parseInt($("ev-speed").value, 10);
  const tick = () => {
    WORLD.step();
    render();
  };
  TIMER = setInterval(tick, Math.max(16, delay()));
}

function init() {
  ["ev-k", "ev-regime", "ev-mut"].forEach((id) =>
    $(id).addEventListener("change", rebuild)
  );
  $("ev-mut").addEventListener("input", () => {
    $("ev-mut-val").textContent = parseFloat($("ev-mut").value).toFixed(3);
    if (WORLD) WORLD.mutation = parseFloat($("ev-mut").value);
  });
  $("ev-play").addEventListener("click", play);
  $("ev-step").addEventListener("click", () => {
    stop();
    WORLD.step();
    render();
  });
  $("ev-reset").addEventListener("click", rebuild);
  rebuild();
}

init();
