"use strict";
// Shared iterated-prisoner's-dilemma play engine for the per-handshake animation.
// Encoding: atlas labels use G/B (Good/Bad); here we map to C (cooperate) / D (defect).

const PAYOFF = { CC: 3, CD: 0, DC: 5, DD: 1 }; // (me, them) -> me's payoff (R,S,T,P)

function payoff(me, them) {
  return PAYOFF[me + them];
}

function labelToPrefix(label) {
  return [...label].map((c) => (c === "G" ? "C" : "D"));
}

// A gated handshake strategy: play the prefix, then if the opponent echoed it exactly,
// run the post-recognition regime, else defect forever.
function gatedPlayer(prefix, regime) {
  const k = prefix.length;
  return (opp) => {
    const r = opp.length;
    if (r < k) return prefix[r];
    for (let i = 0; i < k; i++) if (opp[i] !== prefix[i]) return "D";
    const post = opp.slice(k);
    if (regime === "grim") return post.includes("D") ? "D" : "C";
    if (regime === "tft") return post.length ? post[post.length - 1] : "C";
    return "C"; // coop
  };
}

const allDPlayer = () => () => "D";

// A mimic: echo the prefix to be recognised, then defect forever.
function mimicPlayer(prefix) {
  const k = prefix.length;
  return (opp) => (opp.length < k ? prefix[opp.length] : "D");
}

function simulate(playerA, playerB, rounds) {
  const histA = [];
  const histB = [];
  const out = [];
  let scoreA = 0;
  let scoreB = 0;
  for (let t = 0; t < rounds; t++) {
    const a = playerA(histB);
    const b = playerB(histA);
    scoreA += payoff(a, b);
    scoreB += payoff(b, a);
    histA.push(a);
    histB.push(b);
    out.push({ me: a, them: b, scoreMe: scoreA, scoreThem: scoreB });
  }
  return out;
}

// Build a match for a handshake against one of {self, AllD, mimic} under a regime.
// Returns {rounds: [...], k, recognised, opponent, regime}.
function buildMatch(prefix, opponent, regime, rounds) {
  const me = gatedPlayer(prefix, regime);
  let them;
  if (opponent === "self") them = gatedPlayer(prefix, regime);
  else if (opponent === "AllD") them = allDPlayer();
  else them = mimicPlayer(prefix);
  const log = simulate(me, them, rounds);
  const k = prefix.length;
  // recognition verdict: did the opponent's first k moves equal the prefix?
  let recognised = true;
  for (let i = 0; i < k; i++) {
    if (!log[i] || log[i].them !== prefix[i]) recognised = false;
  }
  return { rounds: log, k, recognised, opponent, regime };
}
