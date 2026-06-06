"use strict";
// Sequential-Bayesian "silent stages" simulation (the recognition layer the atlas omits).
// Mirrors handshake_atlas.courtship; seeded RNG so a given seed is reproducible.

const TYPES = ["interested", "mimic", "indifferent"];
const TYPE_COLOR = { interested: "#4ade80", mimic: "#fbbf24", indifferent: "#6b7280" };
const THETA_LO = 0.1;
const THETA_HI = 0.9;
const MAX_STEPS = 20;

function mulberry32(a) {
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const clip = (p) => Math.min(0.99, Math.max(0.01, p));

function reciprocationProb(type, x) {
  if (type === "interested") return clip(0.8 + 0.15 * x);
  if (type === "mimic") return clip(0.9 - 0.85 * x);
  return clip(0.15 - 0.05 * x); // indifferent
}
function observedProb(type, x, reliability) {
  return reliability * reciprocationProb(type, x) + (1 - reliability) * 0.5;
}
function binEntropy(p) {
  if (p <= 0 || p >= 1) return 0;
  return -(p * Math.log2(p) + (1 - p) * Math.log2(1 - p));
}
function infoGain(posterior, x, reliability, hyps) {
  const probs = hyps.map((t) => observedProb(t, x, reliability));
  const pRecip = posterior.reduce((s, w, i) => s + w * probs[i], 0);
  const hMarg = binEntropy(pRecip);
  const hCond = posterior.reduce((s, w, i) => s + w * binEntropy(probs[i]), 0);
  return hMarg - hCond;
}

function chooseProbe(policy, step, posterior, reliability, hyps) {
  if (policy.kind === "fixed") return policy.level;
  if (policy.kind === "ramp") return Math.min(1, step / policy.rampLen);
  // info_greedy with cost penalty
  let best = 0;
  let bestScore = -Infinity;
  for (let i = 0; i <= 10; i++) {
    const x = i / 10;
    const s = infoGain(posterior, x, reliability, hyps) - policy.costWeight * x;
    if (s > bestScore) {
      bestScore = s;
      best = x;
    }
  }
  return best;
}

function softmax(logw) {
  const m = Math.max(...logw);
  const e = logw.map((v) => Math.exp(v - m));
  const z = e.reduce((a, b) => a + b, 0);
  return e.map((v) => v / z);
}

// One encounter as a state machine driven by stepOnce().
function newRun(opts) {
  const hyps = opts.naive ? ["interested", "indifferent"] : TYPES.slice();
  return {
    opts,
    hyps,
    rng: mulberry32(opts.seed >>> 0),
    logpost: hyps.map(() => Math.log(1 / hyps.length)),
    step: 0,
    history: [],
    decision: null,
    posterior: hyps.map(() => 1 / hyps.length),
    pInterested: 1 / hyps.length,
  };
}

function stepOnce(run) {
  if (run.decision || run.step >= MAX_STEPS) {
    if (!run.decision) run.decision = "timeout (withdraw)";
    return run;
  }
  const { opts, hyps } = run;
  const posterior = softmax(run.logpost);
  const x = chooseProbe(opts.policy, run.step, posterior, opts.reliability, hyps);
  const pTrue = observedProb(opts.trueType, x, opts.reliability);
  const r = run.rng() < pTrue ? 1 : 0;

  for (let i = 0; i < hyps.length; i++) {
    const pt = observedProb(hyps[i], x, opts.reliability);
    run.logpost[i] += Math.log(r ? pt : 1 - pt);
  }
  run.posterior = softmax(run.logpost);
  run.pInterested = run.posterior[hyps.indexOf("interested")];
  run.step += 1;
  run.history.push({ x, r, p: run.pInterested });

  if (run.pInterested >= THETA_HI) run.decision = "APPROACH";
  else if (run.pInterested <= THETA_LO) run.decision = "WITHDRAW";
  else if (run.step >= MAX_STEPS) run.decision = "timeout (withdraw)";
  return run;
}

// ---------------------------------------------------------------------------
// UI
// ---------------------------------------------------------------------------

const $ = (id) => document.getElementById(id);
let RUN = null;
let TIMER = null;

function readOpts() {
  return {
    trueType: $("c-type").value,
    policy: parsePolicy($("c-policy").value),
    naive: $("c-model").value === "naive",
    reliability: parseFloat($("c-rel").value),
    seed: parseInt($("c-seed").value, 10) || 1,
  };
}
function parsePolicy(v) {
  if (v === "fixed") return { kind: "fixed", level: 0.15 };
  if (v === "ramp") return { kind: "ramp", rampLen: 8 };
  return { kind: "info_greedy", costWeight: 0.2 };
}

function reset() {
  stop();
  RUN = newRun(readOpts());
  draw();
}
function stop() {
  if (TIMER) clearInterval(TIMER);
  TIMER = null;
  $("c-play").innerHTML = "&#9654; play";
}
function play() {
  if (TIMER) {
    stop();
    return;
  }
  if (RUN.decision) reset();
  $("c-play").innerHTML = "&#10073;&#10073; pause";
  TIMER = setInterval(() => {
    stepOnce(RUN);
    draw();
    if (RUN.decision) stop();
  }, 750);
}

function bar(label, value, color, suffix) {
  const pct = Math.round(value * 100);
  return (
    `<div class="cbar"><span class="cbar-lab">${label}</span>` +
    `<span class="cbar-track"><span class="cbar-fill" style="width:${pct}%;background:${color}"></span></span>` +
    `<span class="cbar-val">${suffix || pct + "%"}</span></div>`
  );
}

function draw() {
  const run = RUN;
  const last = run.history[run.history.length - 1];

  // posterior bars over entertained hypotheses
  const post = run.hyps
    .map((t, i) => bar(t, run.posterior[i], TYPE_COLOR[t]))
    .join("");

  // probe + reciprocation for the latest step
  let probeHtml = '<p class="c-muted">Press play to begin probing.</p>';
  if (last) {
    const recip = last.r
      ? '<span class="recip yes">reciprocated &#10003;</span>'
      : '<span class="recip no">no response &#10007;</span>';
    probeHtml =
      `<div class="cbar"><span class="cbar-lab">probe</span>` +
      `<span class="cbar-track"><span class="cbar-fill" style="width:${Math.round(
        last.x * 100
      )}%;background:var(--accent)"></span></span>` +
      `<span class="cbar-val">${last.x.toFixed(1)}</span></div>` +
      `<p class="c-step">step ${run.step}: ${recip} ` +
      `<span class="c-muted">(probe intensity ${last.x.toFixed(1)})</span></p>`;
  }

  // belief track with thresholds
  const p = run.pInterested;
  const track =
    `<div class="belief">` +
    `<div class="belief-fill" style="width:${Math.round(p * 100)}%"></div>` +
    `<div class="thr lo" style="left:${THETA_LO * 100}%"></div>` +
    `<div class="thr hi" style="left:${THETA_HI * 100}%"></div>` +
    `<div class="belief-marker" style="left:${Math.min(99, p * 100)}%"></div>` +
    `</div>` +
    `<div class="belief-labels"><span>withdraw &le;${THETA_LO}</span>` +
    `<span>P(interested) = ${p.toFixed(2)}</span><span>approach &ge;${THETA_HI}</span></div>`;

  // history strip
  const strip = run.history
    .map(
      (h) =>
        `<div class="hcell ${h.r ? "yes" : "no"}" title="probe ${h.x.toFixed(
          1
        )}, ${h.r ? "reciprocated" : "no response"}" ` +
        `style="height:${10 + Math.round(h.x * 30)}px"></div>`
    )
    .join("");

  let banner = "";
  if (run.decision) {
    const cls = run.decision === "APPROACH" ? "approach" : "withdraw";
    banner = `<div class="decision ${cls}">${run.decision} after ${run.step} steps · partner was <b>${run.opts.trueType}</b></div>`;
  }

  $("c-stage").innerHTML =
    probeHtml +
    `<h3>Belief that the partner is interested</h3>${track}` +
    `<h3>Posterior over partner types ${
      run.opts.naive ? "(naive: no mimic hypothesis)" : ""
    }</h3>${post}` +
    `<h3>History</h3><div class="hstrip">${strip || '<span class="c-muted">—</span>'}</div>` +
    banner;
}

function init() {
  ["c-type", "c-policy", "c-model", "c-seed"].forEach((id) =>
    $(id).addEventListener("change", reset)
  );
  $("c-rel").addEventListener("input", () => {
    $("c-rel-val").textContent = parseFloat($("c-rel").value).toFixed(2);
    reset();
  });
  $("c-play").addEventListener("click", play);
  $("c-step").addEventListener("click", () => {
    stop();
    if (RUN.decision) reset();
    stepOnce(RUN);
    draw();
  });
  $("c-reset").addEventListener("click", reset);
  reset();
}

init();
