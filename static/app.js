document.addEventListener("DOMContentLoaded", () => {

  const btnAnalyze      = document.getElementById("btn-analyze");
  const inputText       = document.getElementById("input-text");
  const resultsArea     = document.getElementById("results-area");
  const emptyState      = document.getElementById("emptyState");
  const maskedText      = document.getElementById("masked-text");
  const entitiesContainer = document.getElementById("entities-container");
  const entityCountEl   = document.getElementById("entityCount");

  const verdictIconWrap = document.getElementById("verdictIconWrap");
  const verdictSvg      = document.getElementById("verdictSvg");
  const verdictTitle    = document.getElementById("verdictTitle");
  const verdictDesc     = document.getElementById("verdictDesc");
  const verdictPill     = document.getElementById("verdictPill");
  const verdictPillText = document.getElementById("verdictPillText");

  const btnAnalyzeFile  = document.getElementById("btn-analyze-file");
  const inputFile       = document.getElementById("input-file");

  const btnEvaluate     = document.getElementById("btn-evaluate");
  const inputDataset    = document.getElementById("input-dataset");
  const evalResults     = document.getElementById("eval-results");
  const evalTotal       = document.getElementById("eval-total");
  const evalPrecision   = document.getElementById("eval-precision");
  const evalRecall      = document.getElementById("eval-recall");
  const evalF1          = document.getElementById("eval-f1");
  const evalCases       = document.getElementById("eval-cases");

  const btnSettings     = document.getElementById("btn-settings");
  const modalOverlay    = document.getElementById("modal-overlay");
  const btnCloseModal   = document.getElementById("btn-close-modal");
  const btnCancelModal  = document.getElementById("btn-cancel-modal");
  const btnSaveWeights  = document.getElementById("btn-save-weights");
  const weightsList     = document.getElementById("weights-list");

  const copyBtn         = document.getElementById("copyBtn");
  const charCount       = document.getElementById("charCount");


  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");

  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      tabBtns.forEach((b) => b.classList.remove("active"));
      tabPanels.forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      const panel = document.getElementById("panel-" + btn.dataset.tab);
      if (panel) panel.classList.add("active");
    });
  });


  if (inputText && charCount) {
    inputText.addEventListener("input", () => {
      charCount.textContent = inputText.value.length.toLocaleString("fr-FR");
    });
  }


  if (copyBtn && maskedText) {
    copyBtn.addEventListener("click", () => {
      navigator.clipboard.writeText(maskedText.textContent).then(() => {
        copyBtn.innerHTML = '<i class="fas fa-check"></i> Copié !';
        setTimeout(() => {
          copyBtn.innerHTML = '<i class="far fa-copy"></i> Copier';
        }, 1500);
      });
    });
  }


  function setupUploadZone(zoneId, inputId, btnId) {
    const zone = document.getElementById(zoneId);
    const input = document.getElementById(inputId);
    const btn = btnId ? document.getElementById(btnId) : null;
    if (!zone || !input) return;

    const originalHTML = zone.innerHTML;

    ["dragover", "dragenter"].forEach((evt) => {
      zone.addEventListener(evt, (e) => { e.preventDefault(); zone.classList.add("dragover"); });
    });
    ["dragleave", "drop"].forEach((evt) => {
      zone.addEventListener(evt, () => { zone.classList.remove("dragover"); });
    });

    zone.addEventListener("drop", (e) => {
      e.preventDefault();
      if (e.dataTransfer.files.length) {
        input.files = e.dataTransfer.files;
        input.dispatchEvent(new Event("change"));
      }
    });

    input.addEventListener("change", () => {
      if (input.files && input.files.length > 0) {
        const file = input.files[0];
        zone.classList.add("has-file");
        const sizeKo = (file.size / 1024).toFixed(0);
        zone.innerHTML = `
          <div class="file-selected">
            <i class="fas fa-file-check"></i>
            <span class="file-name">${escapeHtml(file.name)}</span>
            <span class="file-size">(${sizeKo} Ko)</span>
            <button class="file-remove" title="Retirer"><i class="fas fa-xmark"></i></button>
          </div>`;
        if (btn) btn.disabled = false;

        zone.querySelector(".file-remove")?.addEventListener("click", (ev) => {
          ev.stopPropagation(); ev.preventDefault();
          input.value = "";
          zone.classList.remove("has-file");
          zone.innerHTML = originalHTML;
          if (!zone.querySelector('input[type="file"]')) {
            zone.insertAdjacentElement("afterbegin", input);
          }
          if (btn) btn.disabled = true;
        });
      }
    });
  }

  setupUploadZone("fileDropZone", "input-file", "btn-analyze-file");
  setupUploadZone("evalDropZone", "input-dataset", "btn-evaluate");


  const VERDICT_CONFIG = {
    BLOCK: {
      iconClass: "v-block",
      title: "Texte bloqué",
      desc: "Ce texte contient des données sensibles et ne peut pas être envoyé tel quel.",
      svg: `<circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/>`,
    },
    MASK: {
      iconClass: "v-mask",
      title: "Texte masqué",
      desc: "Certaines données sensibles ont été masquées. Vérifiez le texte désensibilisé.",
      svg: `<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/><line x1="1" y1="1" x2="23" y2="23"/>`,
    },
    ALLOW: {
      iconClass: "v-allow",
      title: "Texte autorisé",
      desc: "Aucune donnée sensible critique détectée. Ce texte peut être transmis.",
      svg: `<circle cx="12" cy="12" r="10"/><polyline points="8 12 11 15 16 9"/>`,
    },
  };

  const KNOWN_TYPES = [
    "BANK_CARD", "IBAN", "EMAIL", "I-PER", "PERSON",
    "I-LOC", "LOCATION", "MED_PATIENT", "PHONE", "DATE"
  ];

  function badgeClass(type) {
    return KNOWN_TYPES.includes(type) ? `eb-${type}` : "eb-default";
  }

  function sourceClass(src) {
    return src === "rules" ? "src-rules" : "src-ml";
  }


  function renderResults(data) {
    resultsArea.style.display = "flex";
    if (emptyState) emptyState.style.display = "none";

    const config = VERDICT_CONFIG[data.decision];
    if (config) {
      verdictIconWrap.className = "verdict-icon-wrap " + config.iconClass;
      verdictSvg.innerHTML = config.svg;
      verdictTitle.textContent = config.title;
      verdictDesc.textContent = config.desc;
    }

    const score = data.risk_score;
    let pillClass, label;
    if (score < 0.3)      { pillClass = "sp-success"; label = "Risque faible"; }
    else if (score < 0.7) { pillClass = "sp-warning"; label = "Risque modéré"; }
    else                  { pillClass = "sp-danger";  label = "Risque élevé"; }

    verdictPill.className = "score-pill " + pillClass;
    verdictPillText.textContent = `Score : ${score.toFixed(2)} — ${label}`;

    maskedText.innerHTML = highlightPlaceholders(escapeHtml(data.sanitized_text));

    const entities = data.entities || [];
    entityCountEl.textContent = entities.length > 0
      ? `${entities.length} trouvée${entities.length > 1 ? "s" : ""}`
      : "";

    if (entities.length === 0) {
      entitiesContainer.innerHTML = '<p class="muted">Aucune entité sensible détectée.</p>';
    } else {
      let rows = "";
      entities.forEach((e) => {
        rows += `
          <div class="entity-row">
            <div class="entity-type-col">
              <span class="entity-badge ${badgeClass(e.type)}">${escapeHtml(e.type)}</span>
            </div>
            <div class="entity-value-col">${escapeHtml(e.value)}</div>
            <div class="entity-conf-col">${(e.confidence * 100).toFixed(0)}%</div>
            <div class="entity-source-col">
              <span class="source-tag ${sourceClass(e.source)}">${escapeHtml(e.source)}</span>
            </div>
          </div>`;
      });
      entitiesContainer.innerHTML = `<div class="entity-list">${rows}</div>`;
    }
  }


  btnAnalyze.addEventListener("click", async () => {
    const text = inputText.value.trim();
    if (!text) return;

    setLoading(btnAnalyze, true);

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
      setLoading(btnAnalyze, false);
    }
  });


  btnAnalyzeFile.addEventListener("click", async () => {
    const file = inputFile.files[0];
    if (!file) return;

    setLoading(btnAnalyzeFile, true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("/sanitize-file", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      tabBtns.forEach((b) => b.classList.remove("active"));
      tabPanels.forEach((p) => p.classList.remove("active"));
      document.querySelector('[data-tab="text"]')?.classList.add("active");
      document.getElementById("panel-text")?.classList.add("active");

      renderResults(data);
    } catch {
      alert("Erreur lors de l'analyse du fichier.");
    } finally {
      setLoading(btnAnalyzeFile, false);
    }
  });


  btnEvaluate.addEventListener("click", async () => {
    const file = inputDataset.files[0];
    if (!file) { alert("Sélectionnez un fichier JSON."); return; }

    setLoading(btnEvaluate, true);

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
      setLoading(btnEvaluate, false);
    }
  });

  function renderEvalResults(data) {
    evalResults.style.display = "block";

    evalTotal.textContent     = data.total_cases;
    evalPrecision.textContent = (data.global_precision * 100).toFixed(1) + "%";
    evalRecall.textContent    = (data.global_recall * 100).toFixed(1) + "%";
    evalF1.textContent        = (data.global_f1 * 100).toFixed(1) + "%";

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
            <span class="eval-badge ${c.decision}">${c.decision}</span>
            <span>Score : ${c.risk_score.toFixed(1)}%</span>
            <span>F1 : <strong>${(c.f1 * 100).toFixed(1)}%</strong></span>
            <span class="eval-stat-tp"><i class="fas fa-check"></i> ${c.true_positives}</span>
            <span class="eval-stat-fp"><i class="fas fa-xmark"></i> ${c.false_positives}</span>
            <span class="eval-stat-fn"><i class="far fa-circle"></i> ${c.false_negatives}</span>
          </div>
        </div>
        <div class="eval-case-text">${escapeHtml(c.text)}</div>
        <div class="eval-entities">
          <div class="eval-col">
            <h3>Entités détectées</h3>
            <div>${c.detected_entities.map((e) => {
              const correct = expected.includes(e.value.toLowerCase());
              return `<span class="eval-tag ${correct ? "tp" : "fp"}">${escapeHtml(e.type)} : ${escapeHtml(e.value)}</span>`;
            }).join("") || '<span class="muted">Aucune</span>'}</div>
          </div>
          <div class="eval-col">
            <h3>Entités attendues</h3>
            <div>${c.expected_entities.map((e) => {
              const found = detected.includes(e.value.toLowerCase());
              return `<span class="eval-tag ${found ? "tp" : "fn"}">${escapeHtml(e.type)} : ${escapeHtml(e.value)}</span>`;
            }).join("") || '<span class="muted">Aucune attendue</span>'}</div>
          </div>
        </div>`;
      evalCases.appendChild(card);
    });
  }


  btnSettings.addEventListener("click", async () => {
    try {
      const weights = await fetch("/config/weights").then((r) => r.json());
      renderWeights(weights);
    } catch {
      // If endpoint doesn't exist yet, show empty
      weightsList.innerHTML = '<p class="muted">Impossible de charger les poids.</p>';
    }
    modalOverlay.hidden = false;
  });

  btnCloseModal.addEventListener("click",  () => { modalOverlay.hidden = true; });
  btnCancelModal.addEventListener("click", () => { modalOverlay.hidden = true; });

  modalOverlay.addEventListener("click", (e) => {
    if (e.target === modalOverlay) modalOverlay.hidden = true;
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") modalOverlay.hidden = true;
  });

  function renderWeights(weights) {
    weightsList.innerHTML = "";
    Object.entries(weights).forEach(([type, value]) => {
      const row = document.createElement("div");
      row.className = "weight-row";
      row.innerHTML = `
        <label>${escapeHtml(type)}</label>
        <input type="number" min="0" max="1" step="0.05"
               data-type="${escapeHtml(type)}" value="${value}" />`;
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


  function setLoading(button, loading) {
    if (!button) return;
    if (loading) {
      button._originalHTML = button.innerHTML;
      const icon = button.querySelector("i");
      if (icon) icon.className = "fas fa-spinner";
      button.classList.add("loading");
      button.disabled = true;
    } else {
      if (button._originalHTML) button.innerHTML = button._originalHTML;
      button.classList.remove("loading");
      button.disabled = false;
    }
  }

  function highlightPlaceholders(text) {
    return text.replace(/(&lt;[A-Z_]+&gt;)/g, '<span class="placeholder">$1</span>');
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

});