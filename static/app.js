const btnAnalyze     = document.getElementById("btn-analyze");
const inputText      = document.getElementById("input-text");
const results        = document.getElementById("results");
const badgeDecision  = document.getElementById("badge-decision");
const riskScore      = document.getElementById("risk-score");
const executionTime  = document.getElementById("execution-time");
const maskedText     = document.getElementById("masked-text");
const entitiesBody   = document.getElementById("entities-body");
const noEntities     = document.getElementById("no-entities");
const entitiesTable  = document.getElementById("entities-table");
const btnSettings    = document.getElementById("btn-settings");
const modalOverlay   = document.getElementById("modal-overlay");
const btnCloseModal  = document.getElementById("btn-close-modal");
const btnCancelModal = document.getElementById("btn-cancel-modal");
const btnSaveWeights = document.getElementById("btn-save-weights");
const weightsList    = document.getElementById("weights-list");

const btnAnalyzeFile = document.getElementById("btn-analyze-file");
const inputFile = document.getElementById("input-file");

const btnEvaluate   = document.getElementById("btn-evaluate");
const inputDataset  = document.getElementById("input-dataset");
const evalResults   = document.getElementById("eval-results");
const evalTotal     = document.getElementById("eval-total");
const evalPrecision = document.getElementById("eval-precision");
const evalRecall    = document.getElementById("eval-recall");
const evalF1        = document.getElementById("eval-f1");
const evalBody      = document.getElementById("eval-body");

// Analyse
btnAnalyze.addEventListener("click", async () => {
  const text = inputText.value.trim();
  if (!text) return;

  btnAnalyze.textContent = "Analyse en cours...";
  btnAnalyze.disabled = true;

  try {
    const response = await fetch("/sanitize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await response.json();
    renderResults(data);
  } catch {
    alert("Erreur lors de l'analyse.");
  } finally {
    btnAnalyze.textContent = "Analyser";
    btnAnalyze.disabled = false;
  }
});

function renderResults(data) {
  results.hidden = false;

  badgeDecision.textContent = data.decision;
  badgeDecision.className   = "badge " + data.decision;
  riskScore.textContent     = data.risk_score.toFixed(2) + "%";
  executionTime.textContent = data.execution_time_ms != null ? data.execution_time_ms + " ms" : "—";

  maskedText.innerHTML = highlightPlaceholders(escapeHtml(data.sanitized_text));

  entitiesBody.innerHTML = "";
  if (data.entities.length === 0) {
    entitiesTable.hidden = true;
    noEntities.hidden    = false;
  } else {
    entitiesTable.hidden = false;
    noEntities.hidden    = true;
    data.entities.forEach((e) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td><strong>${escapeHtml(e.type)}</strong></td>
        <td><code>${escapeHtml(e.value)}</code></td>
        <td>${e.start} – ${e.end}</td>
        <td>${(e.confidence * 100).toFixed(0)}%</td>
        <td>${escapeHtml(e.source)}</td>
      `;
      entitiesBody.appendChild(row);
    });
  }
}

// Réglages
btnSettings.addEventListener("click", async () => {
  const weights = await fetch("/config/weights").then((r) => r.json());
  renderWeights(weights);
  modalOverlay.hidden = false;
});

btnCloseModal.addEventListener("click",  () => { modalOverlay.hidden = true; });
btnCancelModal.addEventListener("click", () => { modalOverlay.hidden = true; });

function renderWeights(weights) {
  weightsList.innerHTML = "";
  Object.entries(weights).forEach(([type, value]) => {
    const row = document.createElement("div");
    row.className = "weight-row";
    row.innerHTML = `
      <label>${escapeHtml(type)}</label>
      <input type="number" min="0" max="1" step="0.05"
             data-type="${escapeHtml(type)}" value="${value}" />
    `;
    weightsList.appendChild(row);
  });
}

btnSaveWeights.addEventListener("click", async () => {
  const inputs  = weightsList.querySelectorAll("input");
  const weights = {};
  inputs.forEach((input) => {
    weights[input.dataset.type] = parseFloat(input.value);
  });

  await fetch("/config/weights", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ weights }),
  });

  modalOverlay.hidden = true;
});

function highlightPlaceholders(text) {
  return text.replace(/\[([A-Z_]+)\]/g, '<span class="placeholder">[$1]</span>');
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}


btnAnalyzeFile.addEventListener("click", async () => {
  const file = inputFile.files[0];
  if (!file) {
    alert("Sélectionne un fichier.");
    return;
  }

  btnAnalyzeFile.textContent = "Analyse en cours...";
  btnAnalyzeFile.disabled = true;

  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("/sanitize-file", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    renderResults(data);
  } catch {
    alert("Erreur lors de l'analyse du fichier.");
  } finally {
    btnAnalyzeFile.textContent = "Analyser le fichier";
    btnAnalyzeFile.disabled = false;
  }
});
btnEvaluate.addEventListener("click", async () => {
  const file = inputDataset.files[0];
  if (!file) { alert("Sélectionne un fichier JSON."); return; }

  btnEvaluate.textContent = "Évaluation en cours...";
  btnEvaluate.disabled = true;

  try {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch("/evaluate", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    renderEvalResults(data);
  } catch {
    alert("Erreur lors de l'évaluation.");
  } finally {
    btnEvaluate.textContent = "Lancer l'évaluation";
    btnEvaluate.disabled = false;
  }
});

function renderEvalResults(data) {
  evalResults.hidden = false;

  evalTotal.textContent     = data.total_cases;
  evalPrecision.textContent = (data.global_precision * 100).toFixed(1) + "%";
  evalRecall.textContent    = (data.global_recall * 100).toFixed(1) + "%";
  evalF1.textContent        = (data.global_f1 * 100).toFixed(1) + "%";

  const evalCases = document.getElementById("eval-cases");
  evalCases.innerHTML = "";

  data.cases.forEach((c) => {
    const detected = c.detected_entities.map((e) => e.value.toLowerCase());
    const expected = c.expected_entities.map((e) => e.value.toLowerCase());

    const card = document.createElement("div");
    card.className = "eval-case";
    card.innerHTML = `
      <div class="eval-case-header">
        <span class="eval-case-id">${escapeHtml(c.id)}</span>
        <div class="eval-case-scores">
          <span><span class="badge ${c.decision}">${c.decision}</span></span>
          <span>Score : ${c.risk_score.toFixed(1)}%</span>
          <span>F1 : <strong>${(c.f1 * 100).toFixed(1)}%</strong></span>
          <span style="color:#065f46">✔ ${c.true_positives}</span>
          <span style="color:#991b1b">✘ ${c.false_positives}</span>
          <span style="color:#92400e">◯ ${c.false_negatives}</span>
        </div>
      </div>
      <div class="eval-case-text">${escapeHtml(c.text)}</div>
      <div class="eval-entities">
        <div class="eval-col">
          <h3>Entités détectées</h3>
          <div>${c.detected_entities.map((e) => {
            const correct = expected.includes(e.value.toLowerCase());
            return `<span class="eval-tag ${correct ? "tp" : "fp"}">${escapeHtml(e.type)} : ${escapeHtml(e.value)}</span>`;
          }).join("") || "<span style='color:#9ca3af;font-size:0.85rem'>Aucune</span>"}</div>
        </div>
        <div class="eval-col">
          <h3>Entités attendues</h3>
          <div>${c.expected_entities.map((e) => {
            const found = detected.includes(e.value.toLowerCase());
            return `<span class="eval-tag ${found ? "tp" : "fn"}">${escapeHtml(e.type)} : ${escapeHtml(e.value)}</span>`;
          }).join("") || "<span style='color:#9ca3af;font-size:0.85rem'>Aucune attendue</span>"}</div>
        </div>
      </div>
    `;
    evalCases.appendChild(card);
  });
}
