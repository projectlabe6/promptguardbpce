const btnAnalyze = document.getElementById("btn-analyze");
const inputText = document.getElementById("input-text");
const results = document.getElementById("results");
const badgeDecision = document.getElementById("badge-decision");
const riskScore = document.getElementById("risk-score");
const maskedText = document.getElementById("masked-text");
const entitiesBody = document.getElementById("entities-body");
const noEntities = document.getElementById("no-entities");
const entitiesTable = document.getElementById("entities-table");

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
  } catch (err) {
    alert("Erreur lors de l'analyse.");
  } finally {
    btnAnalyze.textContent = "Analyser";
    btnAnalyze.disabled = false;
  }
});

function renderResults(data) {
  results.hidden = false;

  // Badge décision
  badgeDecision.textContent = data.decision;
  badgeDecision.className = "badge " + data.decision;

  // Score
  riskScore.textContent = data.risk_score.toFixed(2) + "%";

  // Texte masqué avec mise en évidence des placeholders
  maskedText.innerHTML = highlightPlaceholders(escapeHtml(data.sanitized_text));

  // Tableau entités
  entitiesBody.innerHTML = "";
  if (data.entities.length === 0) {
    entitiesTable.hidden = true;
    noEntities.hidden = false;
  } else {
    entitiesTable.hidden = false;
    noEntities.hidden = true;
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

function highlightPlaceholders(text) {
  return text.replace(
    /\[([A-Z_]+)\]/g,
    '<span class="placeholder">[$1]</span>'
  );
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
