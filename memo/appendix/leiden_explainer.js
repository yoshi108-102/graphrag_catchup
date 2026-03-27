const svg = document.getElementById("graph");
const stepNameEl = document.getElementById("stepName");
const bestScoreEl = document.getElementById("bestScore");
const descEl = document.getElementById("description");
const scoreBody = document.getElementById("scoreBody");
const gammaInput = document.getElementById("gamma");
const gammaValueEl = document.getElementById("gammaValue");

const palette = ["#f08a5d", "#4aa3a1", "#d2a84c", "#8ea0b8"];

const nodes = [
  { id: "A", x: 120, y: 90 },
  { id: "B", x: 220, y: 75 },
  { id: "C", x: 180, y: 180 },
  { id: "D", x: 280, y: 170 },
  { id: "E", x: 370, y: 160 },
  { id: "F", x: 460, y: 190 },
  { id: "G", x: 430, y: 85 },
  { id: "H", x: 540, y: 105 },
];

const edges = [
  ["A", "B", 3], ["A", "C", 2], ["B", "C", 3], ["B", "D", 1], ["C", "D", 2],
  ["E", "F", 3], ["E", "G", 2], ["F", "G", 3], ["F", "H", 2], ["G", "H", 3],
  ["D", "E", 1], ["C", "F", 1],
];

const candidatePartitions = [
  {
    label: "P1: 1ノード1コミュニティ",
    groups: [["A"], ["B"], ["C"], ["D"], ["E"], ["F"], ["G"], ["H"]],
  },
  {
    label: "P2: 2分割",
    groups: [["A", "B", "C", "D"], ["E", "F", "G", "H"]],
  },
  {
    label: "P3: 3分割",
    groups: [["A", "B", "C"], ["D", "E"], ["F", "G", "H"]],
  },
  {
    label: "P4: 1つに統合",
    groups: [["A", "B", "C", "D", "E", "F", "G", "H"]],
  },
];

const stages = [
  {
    title: "初期化",
    partition: 0,
    text: (gamma) => `最初は各ノードを独立コミュニティとして置きます。Leiden法はLouvain法と同様に目的関数を上げますが、途中で「連結でないコミュニティ」が残らないように後段の精緻化を入れる点が重要です。現在のγ=${gamma.toFixed(2)}では、細かく分けるほどペナルティが軽くなりやすい状態です。`,
  },
  {
    title: "局所移動(Local Moving)",
    partition: 2,
    text: (gamma) => `ノードを近傍コミュニティへ移動させ、Qが上がる操作を反復します。この例では橋ノードD/E周辺が揺れます。Louvainはここで止まることがありますが、Leidenは次の「精緻化」でコミュニティ内部の質を確認します。γ=${gamma.toFixed(2)}。`,
  },
  {
    title: "精緻化(Refinement)",
    partition: 1,
    text: (gamma) => `各コミュニティの内部連結性をチェックし、必要なら分割し直します。この工程で「つながっていない塊」を除去できるため、Louvainより安定したコミュニティになります。特に大規模グラフで意味的に一貫したクラスタが得やすくなります。γ=${gamma.toFixed(2)}。`,
  },
  {
    title: "集約(Aggregation)",
    partition: 1,
    text: (gamma) => `精緻化後のコミュニティを超ノードとして新しいグラフを作り、再び局所移動へ戻ります。Leiden法はこのループで品質を改善しつつ、各コミュニティの連結性保証を保ちます。実務では反復終了条件を「Q改善が閾値未満」などで設定します。γ=${gamma.toFixed(2)}。`,
  },
  {
    title: "収束と解釈",
    partition: 1,
    text: (gamma) => `収束後はコミュニティを「トピック」「組織単位」「機能モジュール」などとして解釈します。γを上げると細分化、下げると統合寄りになるので、目的に応じて調整します。GraphRAGではこの粒度が検索文脈の単位に効きます。現在のγ=${gamma.toFixed(2)}。`,
  },
];

let stageIndex = 0;
let autoplayId = null;

function groupMap(groups) {
  const map = new Map();
  groups.forEach((g, idx) => g.forEach((n) => map.set(n, idx)));
  return map;
}

function cpmScore(groups, gamma) {
  const gMap = groupMap(groups);
  let score = 0;

  groups.forEach((g) => {
    const n = g.length;
    score -= gamma * ((n * (n - 1)) / 2);
  });

  edges.forEach(([u, v, w]) => {
    if (gMap.get(u) === gMap.get(v)) {
      score += w;
    }
  });

  return score;
}

function renderGraph(groups) {
  svg.innerHTML = "";
  const gMap = groupMap(groups);

  edges.forEach(([u, v, w]) => {
    const nu = nodes.find((n) => n.id === u);
    const nv = nodes.find((n) => n.id === v);
    const same = gMap.get(u) === gMap.get(v);

    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", nu.x);
    line.setAttribute("y1", nu.y);
    line.setAttribute("x2", nv.x);
    line.setAttribute("y2", nv.y);
    line.setAttribute("stroke", same ? "#2f4f58" : "#8ea0b8");
    line.setAttribute("stroke-opacity", same ? "0.9" : "0.35");
    line.setAttribute("stroke-width", String(1 + w * 0.6));
    svg.appendChild(line);
  });

  nodes.forEach((n) => {
    const cIdx = gMap.get(n.id) ?? 0;

    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", n.x);
    circle.setAttribute("cy", n.y);
    circle.setAttribute("r", "19");
    circle.setAttribute("fill", palette[cIdx % palette.length]);
    circle.setAttribute("stroke", "#1f2a2e");
    circle.setAttribute("stroke-width", "1.6");
    circle.style.transition = "fill 0.3s ease";
    svg.appendChild(circle);

    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.setAttribute("x", n.x);
    label.setAttribute("y", n.y + 5);
    label.setAttribute("text-anchor", "middle");
    label.setAttribute("font-size", "13");
    label.setAttribute("font-family", "BIZ UDPGothic, sans-serif");
    label.setAttribute("fill", "#132024");
    label.textContent = n.id;
    svg.appendChild(label);
  });
}

function renderScoreTable(gamma) {
  const scored = candidatePartitions.map((p) => ({
    ...p,
    score: cpmScore(p.groups, gamma),
  }));

  const best = scored.reduce((a, b) => (a.score >= b.score ? a : b));
  bestScoreEl.textContent = `${best.label} / Q=${best.score.toFixed(2)}`;

  scoreBody.innerHTML = "";
  scored.forEach((item) => {
    const tr = document.createElement("tr");
    if (item.label === best.label) {
      tr.classList.add("best");
    }

    const td1 = document.createElement("td");
    const td2 = document.createElement("td");
    const td3 = document.createElement("td");

    td1.textContent = item.label;
    td2.textContent = item.groups.map((g) => `[${g.join("")}]`).join(" ");
    td3.textContent = item.score.toFixed(2);

    tr.append(td1, td2, td3);
    scoreBody.appendChild(tr);
  });
}

function render() {
  const gamma = Number(gammaInput.value);
  const stage = stages[stageIndex];
  const partition = candidatePartitions[stage.partition].groups;

  gammaValueEl.textContent = gamma.toFixed(2);
  stepNameEl.textContent = `${stageIndex + 1}/${stages.length} ${stage.title}`;
  descEl.textContent = stage.text(gamma);

  renderGraph(partition);
  renderScoreTable(gamma);
}

function nextStage() {
  stageIndex = (stageIndex + 1) % stages.length;
  render();
}

document.getElementById("next").addEventListener("click", nextStage);

document.getElementById("prev").addEventListener("click", () => {
  stageIndex = (stageIndex - 1 + stages.length) % stages.length;
  render();
});

document.getElementById("reset").addEventListener("click", () => {
  stageIndex = 0;
  gammaInput.value = "1.0";
  stopAutoplay();
  render();
});

document.getElementById("play").addEventListener("click", () => {
  if (autoplayId) {
    stopAutoplay();
    return;
  }

  autoplayId = window.setInterval(nextStage, 1800);
  document.getElementById("play").textContent = "停止";
});

function stopAutoplay() {
  if (!autoplayId) {
    return;
  }
  window.clearInterval(autoplayId);
  autoplayId = null;
  document.getElementById("play").textContent = "自動再生";
}

gammaInput.addEventListener("input", render);

render();
