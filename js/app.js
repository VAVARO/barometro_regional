/**
 * Barómetro Regional UAysén 2025 - Interactive Dashboard Engine
 */

let appData = null;
let charts = {};

// Active Filter State
const filterState = {
  comuna: "Todas",
  zona: "Todas",
  edad: "Todos",
  gse: "Todos"
};

document.addEventListener("DOMContentLoaded", () => {
  initApp();
});

async function initApp() {
  try {
    const response = await fetch("data/barometro_summary.json");
    appData = await response.json();
    console.log("Data loaded successfully:", appData);

    setupNavigation();
    setupFilters();
    setupExplorer();
    setupModals();
    updateDashboard();

  } catch (error) {
    console.error("Error loading dashboard data:", error);
  }
}

// ----------------------------------------------------
// Global Helper: getVariableLabel (Translate numeric codes to text)
// ----------------------------------------------------
function getVariableLabel(varName, code) {
  if (code === null || code === undefined || code === "") return "";

  // 1. Core Fallback Maps
  if (varName === "B1") {
    const mapB1 = { "1": "Progresando", "2": "Estancada", "3": "En decadencia" };
    if (mapB1[Math.round(Number(code))]) return mapB1[Math.round(Number(code))];
  }
  if (varName === "C1") {
    const mapC1 = { "1": "Se puede confiar en las personas", "2": "No se puede confiar en las personas" };
    if (mapC1[Math.round(Number(code))]) return mapC1[Math.round(Number(code))];
  }
  if (varName === "C2" || varName === "I5") {
    const mapYesNo = { "1": "Sí", "2": "No" };
    if (mapYesNo[Math.round(Number(code))]) return mapYesNo[Math.round(Number(code))];
  }
  if (varName === "C2_2_RECOD") {
    const mapC2_2 = {
      "1": "Voluntariado",
      "2": "Talleres y agrupaciones",
      "3": "Organizaciones sociales",
      "4": "Organizaciones políticas",
      "5": "Organizaciones gremiales",
      "444": "Otro"
    };
    if (mapC2_2[Math.round(Number(code))]) return mapC2_2[Math.round(Number(code))];
  }

  // Demographics filter strings
  if (["comuna", "zona", "edad", "gse", "sexo"].includes(varName)) {
    return String(code);
  }

  // 2. Lookup in appData.variables (Primary) or appData.metadata
  const varObj = (appData && appData.variables && appData.variables[varName]) 
              || (appData && appData.metadata && appData.metadata.variable_info && appData.metadata.variable_info[varName]);

  if (varObj) {
    const vMap = varObj.values || varObj.value_labels;
    if (vMap) {
      const numKey = Math.round(Number(code));
      if (vMap[code]) return vMap[code];
      if (vMap[String(code)]) return vMap[String(code)];
      if (!isNaN(numKey)) {
        if (vMap[numKey]) return vMap[numKey];
        if (vMap[String(numKey)]) return vMap[String(numKey)];
        if (vMap[numKey + ".0"]) return vMap[numKey + ".0"];
      }
    }
  }

  return String(code);
}

// ----------------------------------------------------
// Navigation & Tabs
// ----------------------------------------------------
function setupNavigation() {
  const tabs = document.querySelectorAll("#main-nav-tabs .nav-tab");
  const mobileLinks = document.querySelectorAll("#mobile-nav-links .mobile-nav-link");
  const panels = document.querySelectorAll(".tab-panel");

  function switchTab(tabId) {
    tabs.forEach(t => {
      if (t.dataset.tab === tabId) {
        t.classList.add("active");
        t.classList.remove("text-white/80");
      } else {
        t.classList.remove("active");
        t.classList.add("text-white/80");
      }
    });

    mobileLinks.forEach(m => {
      if (m.dataset.tab === tabId) {
        m.classList.add("bg-secondary-container/20", "text-secondary-container");
      } else {
        m.classList.remove("bg-secondary-container/20", "text-secondary-container");
      }
    });

    panels.forEach(p => {
      if (p.id === `tab-content-${tabId}`) {
        p.classList.remove("hidden");
      } else {
        p.classList.add("hidden");
      }
    });

    document.getElementById("mobile-drawer").classList.add("hidden");
    window.dispatchEvent(new Event("resize"));
  }

  tabs.forEach(tab => {
    tab.addEventListener("click", () => switchTab(tab.dataset.tab));
  });

  mobileLinks.forEach(link => {
    link.addEventListener("click", () => switchTab(link.dataset.tab));
  });

  const menuBtn = document.getElementById("mobile-menu-btn");
  const closeBtn = document.getElementById("close-drawer-btn");
  const drawer = document.getElementById("mobile-drawer");

  if (menuBtn && drawer) {
    menuBtn.addEventListener("click", () => drawer.classList.remove("hidden"));
  }
  if (closeBtn && drawer) {
    closeBtn.addEventListener("click", () => drawer.classList.add("hidden"));
  }
}

// ----------------------------------------------------
// Modals Manager (Metodología & Diccionario)
// ----------------------------------------------------
function setupModals() {
  const linkMetodologia = document.getElementById("link-metodologia");
  const linkDiccionario = document.getElementById("link-diccionario");

  const modalMetodologia = document.getElementById("modal-metodologia");
  const modalDiccionario = document.getElementById("modal-diccionario");

  const closeBtns = document.querySelectorAll(".close-modal-btn");
  const searchInput = document.getElementById("dict-search-input");

  function openModal(modal) {
    if (modal) {
      modal.classList.remove("hidden");
      document.body.style.overflow = "hidden";
    }
  }

  function closeModal(modal) {
    if (modal) {
      modal.classList.add("hidden");
      document.body.style.overflow = "";
    }
  }

  if (linkMetodologia) {
    linkMetodologia.addEventListener("click", () => openModal(modalMetodologia));
  }

  if (linkDiccionario) {
    linkDiccionario.addEventListener("click", () => {
      openModal(modalDiccionario);
      renderVariableDictionary();
    });
  }

  closeBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const modalId = btn.dataset.modal;
      if (modalId) {
        closeModal(document.getElementById(modalId));
      }
    });
  });

  [modalMetodologia, modalDiccionario].forEach(modal => {
    if (modal) {
      modal.addEventListener("click", (e) => {
        if (e.target === modal) closeModal(modal);
      });
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeModal(modalMetodologia);
      closeModal(modalDiccionario);
    }
  });

  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      renderVariableDictionary(e.target.value);
    });
  }
}

function renderVariableDictionary(filterText = "") {
  const tbody = document.getElementById("dict-table-body");
  if (!tbody || !appData) return;

  const varInfo = appData.variables || (appData.metadata && appData.metadata.variable_info);
  if (!varInfo) return;

  const query = filterText.toLowerCase().trim();
  tbody.innerHTML = "";

  let count = 0;

  for (const [code, info] of Object.entries(varInfo)) {
    const label = info.label || "";
    const vLabels = info.values || info.value_labels || {};

    const optionsArray = Object.entries(vLabels).map(([k, v]) => `${k}: ${v}`);
    const optionsStr = optionsArray.join(", ");

    const matchCode = code.toLowerCase().includes(query);
    const matchLabel = label.toLowerCase().includes(query);
    const matchOptions = optionsStr.toLowerCase().includes(query);

    if (query === "" || matchCode || matchLabel || matchOptions) {
      count++;
      const tr = document.createElement("tr");
      tr.className = "hover:bg-surface-container/50 transition-colors";

      const optBadges = optionsArray.length > 0
        ? optionsArray.slice(0, 6).map(o => `<span class="inline-block px-2 py-0.5 m-0.5 bg-surface-container rounded font-mono text-[11px] text-primary">${o}</span>`).join(" ") + (optionsArray.length > 6 ? ` <span class="text-outline text-[11px] italic">+${optionsArray.length - 6} más</span>` : "")
        : `<span class="text-outline italic">Variable numérica / abierta</span>`;

      tr.innerHTML = `
        <td class="p-3 font-bold font-mono text-secondary border-r border-outline-variant/20 bg-surface-container-low/40">${code}</td>
        <td class="p-3 font-semibold text-primary border-r border-outline-variant/20">${label}</td>
        <td class="p-3">${optBadges}</td>
      `;

      tbody.appendChild(tr);
    }
  }

  if (count === 0) {
    tbody.innerHTML = `<tr><td colspan="3" class="p-6 text-center text-outline italic">No se encontraron variables que coincidan con "${filterText}".</td></tr>`;
  }
}

// ----------------------------------------------------
// Filters & Active Chips
// ----------------------------------------------------
function setupFilters() {
  const comunaSel = document.getElementById("filter-comuna");
  const zonaSel = document.getElementById("filter-zona");
  const edadSel = document.getElementById("filter-edad");
  const gseSel = document.getElementById("filter-gse");
  const resetBtn = document.getElementById("reset-filters-btn");

  comunaSel.addEventListener("change", (e) => {
    filterState.comuna = e.target.value;
    updateDashboard();
  });

  zonaSel.addEventListener("change", (e) => {
    filterState.zona = e.target.value;
    updateDashboard();
  });

  edadSel.addEventListener("change", (e) => {
    filterState.edad = e.target.value;
    updateDashboard();
  });

  gseSel.addEventListener("change", (e) => {
    filterState.gse = e.target.value;
    updateDashboard();
  });

  resetBtn.addEventListener("click", () => {
    comunaSel.value = "Todas";
    zonaSel.value = "Todas";
    edadSel.value = "Todos";
    gseSel.value = "Todos";

    filterState.comuna = "Todas";
    filterState.zona = "Todas";
    filterState.edad = "Todos";
    filterState.gse = "Todos";

    updateDashboard();
  });
}

function updateActiveChips() {
  const container = document.getElementById("active-chips-list");
  container.innerHTML = "";

  const chips = [];
  if (filterState.comuna !== "Todas") chips.push(`Comuna: ${filterState.comuna}`);
  if (filterState.zona !== "Todas") chips.push(`Zona: ${filterState.zona}`);
  if (filterState.edad !== "Todos") chips.push(`Edad: ${filterState.edad}`);
  if (filterState.gse !== "Todos") chips.push(`GSE: ${filterState.gse}`);

  if (chips.length === 0) {
    container.innerHTML = `<span class="px-2.5 py-0.5 rounded-full bg-secondary-container/10 border border-secondary-container/30 text-secondary-container font-semibold">Toda la Región de Aysén</span>`;
  } else {
    chips.forEach(c => {
      const chip = document.createElement("span");
      chip.className = "px-2.5 py-0.5 rounded-full bg-primary-container/10 border border-primary-container/30 text-primary font-semibold flex items-center gap-1";
      chip.innerHTML = `${c}`;
      container.appendChild(chip);
    });
  }
}

// ----------------------------------------------------
// Micro-filtering & Stats Calculation Engine
// ----------------------------------------------------
function getFilteredRecords() {
  if (!appData || !appData.records) return [];

  return appData.records.filter(r => {
    // Filter Comuna
    if (filterState.comuna !== "Todas") {
      const comunaLabel = r.comuna || getVariableLabel("COMUNA", r.COMUNA);
      if (comunaLabel !== filterState.comuna) return false;
    }

    // Filter Zona (AREA: 1 = Urbano, 2 = Rural)
    if (filterState.zona !== "Todas") {
      const zonaLabel = r.zona || getVariableLabel("AREA", r.AREA);
      if (filterState.zona === "Urbana" && !zonaLabel.toLowerCase().includes("urb")) return false;
      if (filterState.zona === "Rural" && !zonaLabel.toLowerCase().includes("rur")) return false;
    }

    // Filter Edad (TRAMOS: 1 = 18-29, 2 = 30-44, 3 = 45-59, 4 = 60+)
    if (filterState.edad !== "Todos") {
      if (r.edad) {
        if (r.edad !== filterState.edad) return false;
      } else {
        const tramoVal = Math.round(Number(r.TRAMOS));
        if (filterState.edad === "18-29" && tramoVal !== 1) return false;
        if (filterState.edad === "30-44" && tramoVal !== 2) return false;
        if (filterState.edad === "45-59" && tramoVal !== 3) return false;
        if (filterState.edad === "60+" && tramoVal !== 4) return false;
      }
    }

    // Filter GSE
    if (filterState.gse !== "Todos") {
      const gseLabel = r.gse || getVariableLabel("GSE", r.GSE);
      if (gseLabel !== filterState.gse) return false;
    }

    return true;
  });
}

function calculateWeightedCounts(records, varName) {
  let totalW = 0;
  const counts = {};

  records.forEach(r => {
    const val = r[varName];
    if (val !== null && val !== undefined && val < 97) {
      const w = Number(r.weight || r.PONDERADOR) || 1.0;
      totalW += w;
      const key = String(val);
      if (!counts[key]) {
        counts[key] = { weighted_count: 0, unweighted_count: 0 };
      }
      counts[key].weighted_count += w;
      counts[key].unweighted_count += 1;
    }
  });

  const result = {};
  for (const [code, data] of Object.entries(counts)) {
    const lbl = getVariableLabel(varName, code);
    result[lbl] = {
      code: code,
      count: data.unweighted_count,
      weighted_count: data.weighted_count,
      percentage: totalW > 0 ? (data.weighted_count / totalW) * 100 : 0
    };
  }

  return result;
}

function calculateWeightedMean(records, varName) {
  let totalW = 0;
  let sumWX = 0;

  records.forEach(r => {
    const val = r[varName];
    if (val !== null && val !== undefined && val < 97) {
      const w = Number(r.weight || r.PONDERADOR) || 1.0;
      totalW += w;
      sumWX += val * w;
    }
  });

  return totalW > 0 ? sumWX / totalW : null;
}

// ----------------------------------------------------
// Dashboard Update Trigger
// ----------------------------------------------------
function updateDashboard() {
  const filtered = getFilteredRecords();
  const sampleSize = filtered.length;

  document.getElementById("kpi-sample-size").textContent = sampleSize;
  updateActiveChips();

  // 1. KPI Updates
  // Rumbo
  const rumboCounts = calculateWeightedCounts(filtered, "B1");
  const progPct = rumboCounts["Progresando"] ? rumboCounts["Progresando"].percentage.toFixed(1) : "0.0";
  document.getElementById("kpi-progreso-pct").textContent = `${progPct}%`;
  document.getElementById("kpi-progreso-bar").style.width = `${progPct}%`;

  // Top Problem
  const probCounts = calculateWeightedCounts(filtered, "B2_RECOD");
  let topProb = { name: "Seguridad", code: "1", pct: 0 };
  for (const [pName, pData] of Object.entries(probCounts)) {
    if (pData.percentage > topProb.pct) {
      topProb = { name: pName, code: pData.code, pct: pData.percentage };
    }
  }
  document.getElementById("kpi-problema-pct").textContent = `${topProb.pct.toFixed(1)}%`;
  document.getElementById("kpi-problema-name").textContent = topProb.name;

  // UAysén Identificación (I6: 0-100)
  const identMean = calculateWeightedMean(filtered, "I6");
  const identScore = identMean ? identMean.toFixed(1) : "--";
  document.getElementById("kpi-ident-score").textContent = identScore;
  document.getElementById("kpi-ident-bar").style.width = `${Math.min(100, Math.max(0, identMean || 0))}%`;

  // UAysén Nota (I8: 1-7)
  const notaMean = calculateWeightedMean(filtered, "I8");
  const notaScore = notaMean ? notaMean.toFixed(1) : "--";
  document.getElementById("kpi-nota-score").textContent = notaScore;
  document.getElementById("uaysen-nota-big").textContent = notaScore;

  // UAysén Conocimiento (I5: 1=Sí, 2=No)
  const conCounts = calculateWeightedCounts(filtered, "I5");
  const conSi = conCounts["Sí"] ? conCounts["Sí"].percentage.toFixed(1) : "0.0";
  const conNo = conCounts["No"] ? conCounts["No"].percentage.toFixed(1) : "0.0";
  document.getElementById("uaysen-conocimiento-si").textContent = `${conSi}%`;
  document.getElementById("uaysen-conocimiento-no").textContent = `${conNo}%`;

  // 2. Confianza Social Panel Updates (C1, C2, C2_2_RECOD)
  updateConfianzaPanel(filtered);

  // 3. Render General Charts
  renderRumboChart(rumboCounts);
  renderProblemasChart(probCounts);
  renderPertenenciaChart(filtered);
  renderServiciosChart(filtered);
  renderGobernanzaChart(filtered);
  renderInstitucionesChart(filtered);
  renderAmbientalChart(filtered);
  renderEconomiaChart(filtered);
  renderUAysenceAporteChart(filtered);

  // 4. Update Explorer
  renderExplorerTable();
}

// ----------------------------------------------------
// Confianza Social Panel Logic & Calculations
// ----------------------------------------------------
function updateConfianzaPanel(filteredRecords) {
  if (!filteredRecords) return;

  // 1. Calculate Weighted % for C1 (Confianza Interpersonal = Code 1)
  const c1ValidRecords = filteredRecords.filter(r => r.C1 !== null && r.C1 !== undefined && (Number(r.C1) === 1 || Number(r.C1) === 2));
  const c1TrustWeightedSum = c1ValidRecords
    .filter(r => Number(r.C1) === 1)
    .reduce((sum, r) => sum + (Number(r.weight || r.PONDERADOR) || 1.0), 0);
  const c1TotalWeightedSum = c1ValidRecords
    .reduce((sum, r) => sum + (Number(r.weight || r.PONDERADOR) || 1.0), 0);

  const trustPct = c1TotalWeightedSum > 0 ? (c1TrustWeightedSum / c1TotalWeightedSum) * 100 : 0;

  // 2. Calculate Weighted % for C2 (Participación Activa = Code 1)
  const c2ValidRecords = filteredRecords.filter(r => r.C2 !== null && r.C2 !== undefined && (Number(r.C2) === 1 || Number(r.C2) === 2));
  const c2YesWeightedSum = c2ValidRecords
    .filter(r => Number(r.C2) === 1)
    .reduce((sum, r) => sum + (Number(r.weight || r.PONDERADOR) || 1.0), 0);
  const c2TotalWeightedSum = c2ValidRecords
    .reduce((sum, r) => sum + (Number(r.weight || r.PONDERADOR) || 1.0), 0);

  const partPct = c2TotalWeightedSum > 0 ? (c2YesWeightedSum / c2TotalWeightedSum) * 100 : 0;

  // 3. Update Top Organization C2_2_RECOD
  const c22Counts = calculateWeightedCounts(filteredRecords, "C2_2_RECOD");
  let topOrg = { name: "Organizaciones sociales", pct: 0 };
  for (const [oName, oData] of Object.entries(c22Counts)) {
    if (oData.percentage > topOrg.pct) {
      topOrg = { name: oName, pct: oData.percentage };
    }
  }

  // 4. Update KPI Card DOM
  const elTrust = document.getElementById("kpi-confianza-pct");
  const elPart = document.getElementById("kpi-participacion-pct");
  const elTopOrg = document.getElementById("kpi-top-org");

  if (elTrust) elTrust.textContent = `${trustPct.toFixed(1)}%`;
  if (elPart) elPart.textContent = `${partPct.toFixed(1)}%`;
  if (elTopOrg) elTopOrg.textContent = topOrg.name;

  // 5. Update Doughnut Chart (chart-confianza-canvas)
  const noTrustWeightedSum = c1TotalWeightedSum - c1TrustWeightedSum;
  renderConfianzaChart(c1TrustWeightedSum, noTrustWeightedSum);

  // 6. Update Bar Chart (chart-participacion-canvas)
  renderParticipacionChart(c22Counts);
}

// ----------------------------------------------------
// Chart Renderers (Chart.js)
// ----------------------------------------------------
const BRAND_COLORS = {
  primary: "#0a2540",
  accent: "#00a3e0",
  secondary: "#41befd",
  muted: "#768dad",
  gray: "#e2e8f0",
  rose: "#f43f5e",
  emerald: "#10b981",
  amber: "#f59e0b"
};

function renderRumboChart(rumboCounts) {
  const ctx = document.getElementById("chart-rumbo-canvas");
  if (!ctx) return;

  const labels = ["Progresando", "Estancada", "En decadencia"];
  const data = labels.map(l => rumboCounts[l] ? rumboCounts[l].percentage.toFixed(1) : 0);

  if (charts.rumbo) charts.rumbo.destroy();

  charts.rumbo = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: [BRAND_COLORS.accent, BRAND_COLORS.muted, BRAND_COLORS.rose],
        borderWidth: 2,
        borderColor: "#ffffff"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          callbacks: {
            label: (item) => ` ${item.label}: ${item.raw}%`
          }
        }
      }
    }
  });
}

function renderConfianzaChart(trustWeightedSum, noTrustWeightedSum) {
  const ctx = document.getElementById("chart-confianza-canvas");
  if (!ctx) return;

  const total = trustWeightedSum + noTrustWeightedSum;
  const trustPct = total > 0 ? ((trustWeightedSum / total) * 100).toFixed(1) : 0;
  const noTrustPct = total > 0 ? ((noTrustWeightedSum / total) * 100).toFixed(1) : 0;

  const labels = ["Se puede confiar en las personas", "No se puede confiar en las personas"];
  const data = [trustPct, noTrustPct];

  if (charts.confianza) charts.confianza.destroy();

  charts.confianza = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: [BRAND_COLORS.accent, BRAND_COLORS.primary],
        borderWidth: 2,
        borderColor: "#ffffff"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          callbacks: {
            label: (item) => ` ${item.label}: ${item.raw}%`
          }
        }
      }
    }
  });
}

function renderParticipacionChart(c22Counts) {
  const ctx = document.getElementById("chart-participacion-canvas");
  if (!ctx) return;

  const sorted = Object.entries(c22Counts)
    .map(([k, v]) => ({ name: k, pct: v.percentage }))
    .sort((a, b) => b.pct - a.pct);

  const labels = sorted.map(s => s.name);
  const data = sorted.map(s => s.pct.toFixed(1));

  if (charts.participacion) charts.participacion.destroy();

  charts.participacion = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "% Participación",
        data: data,
        backgroundColor: BRAND_COLORS.emerald,
        borderRadius: 8
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { x: { ticks: { callback: v => `${v}%` } } }
    }
  });
}

function renderProblemasChart(probCounts) {
  const ctx = document.getElementById("chart-problemas-canvas");
  if (!ctx) return;

  const sorted = Object.entries(probCounts)
    .map(([k, v]) => ({ name: k, pct: v.percentage }))
    .sort((a, b) => b.pct - a.pct)
    .slice(0, 6);

  const labels = sorted.map(s => s.name);
  const data = sorted.map(s => s.pct.toFixed(1));

  if (charts.problemas) charts.problemas.destroy();

  charts.problemas = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "% Mención",
        data: data,
        backgroundColor: BRAND_COLORS.primary,
        borderRadius: 8
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: { ticks: { callback: v => `${v}%` } }
      }
    }
  });
}

function renderPertenenciaChart(filtered) {
  const ctx = document.getElementById("chart-pertenencia-canvas");
  if (!ctx) return;

  const pCounts = calculateWeightedCounts(filtered, "A1");

  const sorted = Object.entries(pCounts)
    .map(([k, v]) => ({ name: k, pct: v.percentage }))
    .sort((a, b) => b.pct - a.pct);

  const labels = sorted.map(s => s.name);
  const data = sorted.map(s => s.pct.toFixed(1));

  if (charts.pertenencia) charts.pertenencia.destroy();

  charts.pertenencia = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "% Pertenencia",
        data: data,
        backgroundColor: BRAND_COLORS.secondary,
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { ticks: { callback: v => `${v}%` } } }
    }
  });
}

function renderServiciosChart(filtered) {
  const ctx = document.getElementById("chart-servicios-canvas");
  if (!ctx) return;

  const items = [
    { col: "B3_A", label: "Salud pública" },
    { col: "B3_B", label: "Educación pública" },
    { col: "B3_C", label: "Transporte y conectividad" },
    { col: "B3_D", label: "Vivienda" },
    { col: "B3_E", label: "Seguridad y orden" }
  ];

  const labels = [];
  const means = [];

  items.forEach(it => {
    const m = calculateWeightedMean(filtered, it.col);
    if (m !== null) {
      labels.push(it.label);
      means.push(m.toFixed(2));
    }
  });

  if (charts.servicios) charts.servicios.destroy();

  charts.servicios = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Nota Promedio (1-7)",
        data: means,
        backgroundColor: BRAND_COLORS.primary,
        borderRadius: 8
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { x: { min: 1, max: 7 } }
    }
  });
}

function renderGobernanzaChart(filtered) {
  const ctx = document.getElementById("chart-gobernanza-canvas");
  if (!ctx || !filtered || filtered.length === 0) return;

  const cols = [
    { code: "G1_A", name: "Salud Pública" },
    { code: "G1_B", name: "Educación Básica/Media" },
    { code: "G1_E", name: "Protección Medioambiente" },
    { code: "G1_H", name: "Seguridad Pública" },
    { code: "G1_I", name: "Fomento Productivo" }
  ];

  const labels = cols.map(c => c.name);
  const nacPct = [];
  const regPct = [];

  cols.forEach(c => {
    let nacW = 0;
    let regW = 0;

    filtered.forEach(r => {
      const rawVal = r[c.code];
      if (rawVal !== null && rawVal !== undefined) {
        const val = Math.round(Number(rawVal));
        const w = Number(r.PONDERADOR || r.weight) || 1.0;

        if (val === 1) {
          nacW += w; // 1 = Autoridades Nacionales
        } else if (val === 2 || val === 3) {
          regW += w; // 2 = Autoridades Regionales, 3 = Autoridades Comunales
        }
      }
    });

    const total = nacW + regW;
    if (total > 0) {
      nacPct.push(Number(((nacW / total) * 100).toFixed(1)));
      regPct.push(Number(((regW / total) * 100).toFixed(1)));
    } else {
      nacPct.push(0);
      regPct.push(0);
    }
  });

  if (charts.gobernanza) charts.gobernanza.destroy();

  charts.gobernanza = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        { 
          label: "Decisión Regional/Comunal", 
          data: regPct, 
          backgroundColor: BRAND_COLORS.secondary || "#00A3E0" 
        },
        { 
          label: "Decisión Gobierno Nacional", 
          data: nacPct, 
          backgroundColor: BRAND_COLORS.primary || "#0A2540" 
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            label: (item) => ` ${item.dataset.label}: ${item.raw}%`
          }
        }
      },
      scales: {
        x: { stacked: true },
        y: { stacked: true, max: 100, ticks: { callback: v => `${v}%` } }
      }
    }
  });
}

function renderInstitucionesChart(filtered) {
  const ctx = document.getElementById("chart-instituciones-canvas");
  if (!ctx) return;

  const insts = [
    { col: "F4_A", label: "Gobierno Central" },
    { col: "F4_B", label: "Gobierno Regional" },
    { col: "F4_C", label: "Municipios" },
    { col: "F4_D", label: "Empresas Regionales" },
    { col: "F4_F", label: "Organizaciones Sociales" },
    { col: "F4_G", label: "Universidades" }
  ];

  const labels = [];
  const data = [];

  insts.forEach(i => {
    const m = calculateWeightedMean(filtered, i.col);
    if (m !== null) {
      labels.push(i.label);
      data.push(m.toFixed(2));
    }
  });

  if (charts.instituciones) charts.instituciones.destroy();

  charts.instituciones = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Evaluación Aporte (1-7)",
        data: data,
        backgroundColor: BRAND_COLORS.accent,
        borderRadius: 8
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { x: { min: 1, max: 7 } }
    }
  });
}

function renderAmbientalChart(filtered) {
  const ctx = document.getElementById("chart-ambiental-canvas");
  if (!ctx) return;

  const probs = [
    { col: "I4_A", label: "Humo leña" },
    { col: "I4_B", label: "Agua potable / APR" },
    { col: "I4_C", label: "Deterioro humedales" },
    { col: "I4_D", label: "Gestión basura" },
    { col: "I4_E", label: "Biodiversidad mar" },
    { col: "I4_F", label: "Bosque nativo" }
  ];

  const labels = [];
  const data = [];

  probs.forEach(p => {
    const m = calculateWeightedMean(filtered, p.col);
    if (m !== null) {
      labels.push(p.label);
      data.push(m.toFixed(2));
    }
  });

  if (charts.ambiental) charts.ambiental.destroy();

  charts.ambiental = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Urgencia (1-4)",
        data: data,
        backgroundColor: BRAND_COLORS.rose,
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { min: 1, max: 4 } }
    }
  });
}

function renderEconomiaChart(filtered) {
  const ctx = document.getElementById("chart-economia-canvas");
  if (!ctx) return;

  const secs = [
    { col: "I1_C", label: "Turismo" },
    { col: "I1_F", label: "Energías Renovables" },
    { col: "I1_A", label: "Agricultura" },
    { col: "I1_D", label: "Salmonicultura" },
    { col: "I1_H", label: "Pesca Artesanal" },
    { col: "I1_I", label: "Tecnología e Innovación" }
  ];

  const labels = [];
  const data = [];

  secs.forEach(s => {
    const m = calculateWeightedMean(filtered, s.col);
    if (m !== null) {
      labels.push(s.label);
      data.push(m.toFixed(2));
    }
  });

  if (charts.economia) charts.economia.destroy();

  charts.economia = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Importancia Futura (1-4)",
        data: data,
        backgroundColor: BRAND_COLORS.emerald,
        borderRadius: 8
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { x: { min: 1, max: 4 } }
    }
  });
}

function renderUAysenceAporteChart(filtered) {
  const ctx = document.getElementById("chart-uaysen-aporte-canvas");
  if (!ctx) return;

  const items = [
    { col: "I7_1", label: "Vínculos estables con territorios y comunidades" },
    { col: "I7_2", label: "Vínculos con actores regionales e internacionales" },
    { col: "I7_3", label: "Docencia e investigación enfocada en temas regionales" }
  ];

  const labels = [];
  const data = [];

  items.forEach(i => {
    const m = calculateWeightedMean(filtered, i.col);
    if (m !== null) {
      labels.push(i.label);
      data.push(m.toFixed(2));
    }
  });

  if (charts.uaysenAporte) charts.uaysenAporte.destroy();

  charts.uaysenAporte = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Evaluación Aporte (1-7)",
        data: data,
        backgroundColor: BRAND_COLORS.primary,
        borderRadius: 8
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { x: { min: 1, max: 7 } }
    }
  });
}

// ----------------------------------------------------
// Data Intelligence Explorer Crosstab Matrix Table
// ----------------------------------------------------
function setupExplorer() {
  const varX = document.getElementById("explorer-var-x");
  const varY = document.getElementById("explorer-var-y");
  const btnCsv = document.getElementById("export-csv-btn");

  if (varX && varY) {
    varX.addEventListener("change", renderExplorerTable);
    varY.addEventListener("change", renderExplorerTable);
  }

  if (btnCsv) {
    btnCsv.addEventListener("click", exportExplorerCSV);
  }
}

function renderExplorerTable() {
  const varX = document.getElementById("explorer-var-x").value;
  const varY = document.getElementById("explorer-var-y").value;
  const tbody = document.getElementById("explorer-table-body");
  const thead = document.getElementById("explorer-table-head");

  const filteredRecords = getFilteredRecords();
  if (!filteredRecords || filteredRecords.length === 0) {
    tbody.innerHTML = `<tr><td colspan="100%" class="p-4 text-center text-outline">No hay datos disponibles para la selección actual.</td></tr>`;
    return;
  }

  // Unique X Values (Rows)
  const xSet = new Set();
  filteredRecords.forEach(r => {
    if (r[varX] !== null && r[varX] !== undefined && r[varX] < 97) {
      xSet.add(r[varX]);
    }
  });
  const xValues = Array.from(xSet).sort((a, b) => Number(a) - Number(b));

  // Unique Y Values (Columns)
  const ySet = new Set();
  filteredRecords.forEach(r => {
    if (r[varY] !== null && r[varY] !== undefined && r[varY] !== "") {
      ySet.add(r[varY]);
    }
  });
  const yValues = Array.from(ySet).sort();

  // Column Totals
  const colTotals = {};
  let grandTotalWeight = 0;
  let grandTotalCount = 0;

  yValues.forEach(yVal => {
    colTotals[yVal] = { weight: 0, count: 0 };
  });

  filteredRecords.forEach(r => {
    const yVal = r[varY];
    if (ySet.has(yVal)) {
      const w = Number(r.weight || r.PONDERADOR) || 1.0;
      colTotals[yVal].weight += w;
      colTotals[yVal].count += 1;
      grandTotalWeight += w;
      grandTotalCount += 1;
    }
  });

  // Build Table Header
  let headHtml = `<tr class="bg-primary-container text-white text-xs uppercase tracking-wider">`;
  headHtml += `<th class="p-3 font-bold border-r border-white/10">Variable ${varX} \\ ${varY.toUpperCase()}</th>`;
  yValues.forEach(yVal => {
    const colLabel = getVariableLabel(varY, yVal);
    headHtml += `<th class="p-3 font-bold text-center border-r border-white/10">${colLabel}</th>`;
  });
  headHtml += `<th class="p-3 font-bold text-center">Total</th></tr>`;
  thead.innerHTML = headHtml;

  // Build Table Body Rows
  tbody.innerHTML = "";

  xValues.forEach(xVal => {
    const rowLabel = getVariableLabel(varX, xVal);
    let rowWeight = 0;
    let rowCount = 0;

    let rowHtml = `<tr class="hover:bg-surface-container/50 transition-colors">`;
    rowHtml += `<td class="p-3 font-semibold text-primary border-r border-outline-variant/20">${rowLabel}</td>`;

    yValues.forEach(yVal => {
      const groupRecords = filteredRecords.filter(r => String(r[varX]) === String(xVal) && String(r[varY]) === String(yVal));
      const cellCount = groupRecords.length;
      let cellWeight = 0;
      groupRecords.forEach(r => cellWeight += (Number(r.weight || r.PONDERADOR) || 1.0));

      rowWeight += cellWeight;
      rowCount += cellCount;

      const colWeight = colTotals[yVal].weight;
      const cellPct = colWeight > 0 ? (cellWeight / colWeight) * 100 : 0;

      rowHtml += `
        <td class="p-3 text-center border-r border-outline-variant/20">
          <div class="font-bold text-secondary text-sm">${cellPct.toFixed(1)}%</div>
          <div class="text-[11px] text-outline font-medium">N = ${cellCount}</div>
        </td>
      `;
    });

    const rowPct = grandTotalWeight > 0 ? (rowWeight / grandTotalWeight) * 100 : 0;
    rowHtml += `
      <td class="p-3 text-center bg-surface-container-low/50">
        <div class="font-extrabold text-primary text-sm">${rowPct.toFixed(1)}%</div>
        <div class="text-[11px] text-outline font-bold">N = ${rowCount}</div>
      </td>
    </tr>`;

    tbody.innerHTML += rowHtml;
  });

  // Summary Foot Row (Total)
  let footHtml = `<tr class="bg-surface-container-high/80 font-bold border-t-2 border-primary-container text-xs">`;
  footHtml += `<td class="p-3 uppercase text-primary border-r border-outline-variant/20">Total</td>`;

  yValues.forEach(yVal => {
    const cCount = colTotals[yVal].count;
    footHtml += `
      <td class="p-3 text-center border-r border-outline-variant/20">
        <div class="font-extrabold text-primary text-sm">100.0%</div>
        <div class="text-[11px] text-outline font-bold">N = ${cCount}</div>
      </td>
    `;
  });

  footHtml += `
    <td class="p-3 text-center bg-primary-container/10">
      <div class="font-extrabold text-primary text-sm">100.0%</div>
      <div class="text-[11px] text-primary font-bold">N = ${grandTotalCount}</div>
    </td>
  </tr>`;

  tbody.innerHTML += footHtml;
}

function exportExplorerCSV() {
  const varX = document.getElementById("explorer-var-x").value;
  const varY = document.getElementById("explorer-var-y").value;
  const filteredRecords = getFilteredRecords();
  if (!filteredRecords || filteredRecords.length === 0) return;

  const xSet = new Set();
  filteredRecords.forEach(r => {
    if (r[varX] !== null && r[varX] !== undefined && r[varX] < 97) xSet.add(r[varX]);
  });
  const xValues = Array.from(xSet).sort((a, b) => Number(a) - Number(b));

  const ySet = new Set();
  filteredRecords.forEach(r => {
    if (r[varY] !== null && r[varY] !== undefined && r[varY] !== "") ySet.add(r[varY]);
  });
  const yValues = Array.from(ySet).sort();

  const colTotals = {};
  yValues.forEach(yVal => { colTotals[yVal] = 0; });
  filteredRecords.forEach(r => {
    if (ySet.has(r[varY])) colTotals[r[varY]] += (Number(r.weight || r.PONDERADOR) || 1.0);
  });

  let csv = `"${varX} / ${varY.toUpperCase()}",`;
  yValues.forEach(yVal => {
    csv += `"${getVariableLabel(varY, yVal).replace(/"/g, '""')}",`;
  });
  csv += `"Total"\n`;

  xValues.forEach(xVal => {
    csv += `"${getVariableLabel(varX, xVal).replace(/"/g, '""')}",`;
    yValues.forEach(yVal => {
      const groupRecords = filteredRecords.filter(r => String(r[varX]) === String(xVal) && String(r[varY]) === String(yVal));
      let cellWeight = 0;
      groupRecords.forEach(r => cellWeight += (Number(r.weight || r.PONDERADOR) || 1.0));
      const colWeight = colTotals[yVal];
      const cellPct = colWeight > 0 ? (cellWeight / colWeight) * 100 : 0;
      csv += `${cellPct.toFixed(1)}%,`;
    });
    csv += `\n`;
  });

  const encodedUri = encodeURI("data:text/csv;charset=utf-8," + csv);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `barometro_crosstab_${varX}_vs_${varY}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
