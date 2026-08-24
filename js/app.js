/**
 * Barómetro Regional UAysén 2025 - Interactive Dashboard Engine (V2.0 Complete & Shielded)
 */

let appData = null;
let comparativaData = null;
let currentActiveTab = "resumen";
let charts = {};
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// Register and configure DataLabels globally
if (typeof ChartDataLabels !== "undefined") {
  Chart.register(ChartDataLabels);
}

// Reduce Chart.js animation duration for snappier feel (default is 1000ms)
if (typeof Chart !== "undefined" && Chart.defaults) {
  Chart.defaults.animation = prefersReducedMotion
    ? { duration: 0 }
    : { duration: 400, easing: "easeOutQuart" };
}

if (typeof Chart !== "undefined" && Chart.defaults) {
  Chart.defaults.set('plugins.datalabels', {
    color: (context) => {
      const bg = context.dataset.backgroundColor;
      // White text on dark primary colors, dark slate on bright/accent colors
      if (Array.isArray(bg)) {
        const currentBg = bg[context.dataIndex];
        return (currentBg === "#0a2540" || currentBg === "#0A2540") ? "#ffffff" : "#0f172a";
      }
      return (bg === "#0a2540" || bg === "#0A2540") ? "#ffffff" : "#0f172a";
    },
    anchor: 'end',
    align: 'start',
    offset: 4,
    font: {
      family: "'Inter', sans-serif",
      weight: 'bold',
      size: 11
    },
    formatter: (value, context) => {
      if (value === 0 || value === "0" || value === null || value === undefined) return "";

      const chart = context.chart;
      const canvasId = chart.canvas?.id || "";
      const xMax = chart.options.scales?.x?.max;
      const yMax = chart.options.scales?.y?.max;
      const xMin = chart.options.scales?.x?.min;
      const yMin = chart.options.scales?.y?.min;

      // Detect if chart uses a mean score scale (1-4, 1-7) rather than percentage (0-100%)
      const isScoreAxis = (xMax && xMax <= 10) || (yMax && yMax <= 10) || xMin === 1 || yMin === 1;
      
      // Explicit list of score/average canvas IDs
      const isScoreChart = [
        "chart-ambiental-canvas",
        "chart-economia-canvas",
        "chart-servicios-canvas",
        "chart-servicios-completo-canvas",
        "chart-instituciones-canvas",
        "chart-uaysen-aporte-canvas",
        "chart-comp-seguridad"
      ].includes(canvasId);

      // If it's a score scale, return as clean decimal number without '%'
      if (isScoreAxis || isScoreChart || context.dataset.isScore) {
        return Number(value).toFixed(2);
      }

      // Default for distribution charts: append '%'
      return `${value}%`;
    }
  });
}

// Active Filter State
const filterState = {
  comuna: "Todas",
  zona: "Todas",
  edad: "Todos",
  gse: "Todos"
};

function getActiveFilterDescription() {
  const parts = [];
  if (filterState.comuna !== "Todas") parts.push(`Comuna: ${filterState.comuna}`);
  if (filterState.zona !== "Todas") parts.push(`Zona: ${filterState.zona}`);
  if (filterState.edad !== "Todos") parts.push(`Edad: ${filterState.edad}`);
  if (filterState.gse !== "Todos") parts.push(`GSE: ${filterState.gse}`);
  
  return parts.length > 0 ? parts.join(" • ") : "Toda la Región de Aysén";
}

// ----------------------------------------------------
// Safe Element Helper
// ----------------------------------------------------
function safeGetCanvas(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) {
    console.warn(`[Dashboard Warning] Canvas element with ID "${canvasId}" was not found in index.html.`);
    return null;
  }
  return canvas;
}

function safeSetText(id, text) {
  const el = document.getElementById(id);
  if (el) {
    el.textContent = text;
  } else {
    console.warn(`[Dashboard Warning] Element with ID "${id}" was not found in index.html.`);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initApp();
});

async function initApp() {
  try {
    const response = await fetch("data/barometro_summary.json");
    appData = await response.json();
    console.log("Data loaded successfully:", appData);

    try {
      const compResp = await fetch("data/comparativa_interregional.json");
      comparativaData = await compResp.json();
      compData = comparativaData;
      console.log("Comparativa data loaded successfully:", comparativaData);
    } catch (errComp) {
      console.warn("Could not load comparativa_interregional.json:", errComp);
    }

    setupNavigation();
    setupFilters();
    setupExplorer();
    setupModals();
    setupComparativaSubNavigation();
    updateDashboard();
    setupChartCardActions();

  } catch (error) {
    console.error("Error loading dashboard data:", error);
  }
}

// ----------------------------------------------------
// Global Helper: getVariableLabel (Translate numeric codes to text)
// ----------------------------------------------------
function getVariableLabel(varName, code) {
  if (code === null || code === undefined || code === "") return "";

  const numKey = Math.round(Number(code));

  // Core Explicit Fallback Maps
  if (varName === "B1") {
    const mapB1 = { "1": "Progresando", "2": "Estancada", "3": "En decadencia" };
    if (mapB1[numKey]) return mapB1[numKey];
  }
  if (varName === "A2") {
    const mapA2 = { "1": "Sí, desea irse", "2": "No, prefiere quedarse" };
    if (mapA2[numKey]) return mapA2[numKey];
  }
  if (varName === "A3") {
    const mapA3 = {
      "1": "Misma comuna",
      "2": "Otra comuna en Aysén",
      "3": "Otra Región del país",
      "4": "Otro país"
    };
    if (mapA3[numKey]) return mapA3[numKey];
  }
  if (varName === "C1") {
    const mapC1 = { "1": "Se puede confiar en las personas", "2": "No se puede confiar en las personas" };
    if (mapC1[numKey]) return mapC1[numKey];
  }
  if (varName === "C2" || varName === "I5" || varName === "F3") {
    const mapYesNo = { "1": "Sí", "2": "No" };
    if (mapYesNo[numKey]) return mapYesNo[numKey];
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
    if (mapC2_2[numKey]) return mapC2_2[numKey];
  }
  if (varName === "E2") {
    const mapE2 = {
      "1": "TV Nacional",
      "2": "TV Local/Regional",
      "3": "Radios Nacionales",
      "4": "Radios Locales",
      "5": "Web Noticias Nacional",
      "6": "Web Noticias Regional",
      "7": "Redes Sociales"
    };
    if (mapE2[numKey]) return mapE2[numKey];
  }
  if (varName === "G2") {
    const mapG2 = {
      "1": "Aumentó Centralismo",
      "2": "Mayor Autonomía Regional"
    };
    if (mapG2[numKey]) return mapG2[numKey];
  }
  if (varName === "G3") {
    const mapG3 = {
      "1": "Impulso al desarrollo",
      "2": "Igual que antes",
      "3": "Más problemas"
    };
    if (mapG3[numKey]) return mapG3[numKey];
  }
  if (varName === "H1") {
    const mapH1 = {
      "1": "Democracia preferible",
      "2": "Gobierno autoritario",
      "3": "Da lo mismo el régimen"
    };
    if (mapH1[numKey]) return mapH1[numKey];
  }
  if (varName === "H2") {
    const mapH2 = {
      "1": "Izquierda",
      "2": "Centro Izquierda",
      "3": "Centro",
      "4": "Centro Derecha",
      "5": "Derecha",
      "97": "Ninguna"
    };
    if (mapH2[numKey]) return mapH2[numKey];
  }
  if (varName === "J1") {
    const mapJ1 = {
      "1": "No Estudió",
      "2": "Básica Incompleta",
      "3": "Básica Completa",
      "4": "Media Incompleta",
      "5": "Media Completa",
      "6": "IP/CFT Incompleto",
      "7": "IP/CFT Completo",
      "8": "Universitaria Incompleta",
      "9": "Universitaria Completa",
      "10": "Postgrado"
    };
    if (mapJ1[numKey]) return mapJ1[numKey];
  }
  if (varName === "GSE_4_Categorias") {
    const mapGSE4 = {
      "1": "ABC1",
      "2": "C2",
      "3": "C3",
      "4": "D+E"
    };
    if (mapGSE4[numKey]) return mapGSE4[numKey];
  }
  if (varName === "CIUO08_1N") {
    const mapCIUO = {
      "0": "Fuerzas Armadas",
      "1": "Directores y Gerentes",
      "2": "Profesionales y Científicos",
      "3": "Técnicos Nivel Medio",
      "4": "Apoyo Administrativo",
      "5": "Servicios y Comercio",
      "6": "Agropecuario y Pesca",
      "7": "Artesanos y Operarios",
      "8": "Operadores de Maquinaria",
      "9": "Ocupaciones Elementales"
    };
    if (mapCIUO[numKey]) return mapCIUO[numKey];
  }
  if (varName === "I51_COD") {
    const mapI51 = {
      "11": "Nuevas carreras",
      "12": "Buena calidad educación",
      "13": "Realizan investigaciones",
      "14": "Fomenta educación regional",
      "15": "Charlas y capacitaciones",
      "21": "Solo de nombre",
      "22": "Es universidad nueva",
      "23": "Sobre oferta de carreras",
      "24": "Conoce egresados/estudiantes",
      "31": "Problemas financieros",
      "32": "Mala administración",
      "33": "Quiebra",
      "34": "Falta mejorar calidad",
      "35": "Muy politizada",
      "36": "Despidos masivos",
      "444": "Otro"
    };
    if (mapI51[numKey]) return mapI51[numKey];
  }

  // Demographics filter strings
  if (["comuna", "zona", "edad", "gse", "sexo"].includes(varName)) {
    return String(code);
  }

  // Lookup in appData.variables (Primary) or appData.metadata
  const varObj = (appData && appData.variables && appData.variables[varName]) 
              || (appData && appData.metadata && appData.metadata.variable_info && appData.metadata.variable_info[varName]);

  if (varObj) {
    const vMap = varObj.values || varObj.value_labels;
    if (vMap) {
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
    currentActiveTab = tabId;

    // Toggle aria-selected on tab buttons
    tabs.forEach(t => {
      if (t.dataset.tab === tabId) {
        t.classList.add("active");
        t.setAttribute("aria-selected", "true");
      } else {
        t.classList.remove("active");
        t.setAttribute("aria-selected", "false");
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
        // Trigger opacity entrance transition
        p.classList.add("tab-panel-entering");
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            p.classList.remove("tab-panel-entering");
          });
        });
      } else {
        p.classList.add("hidden");
      }
    });

    // Toggle filter bar visibility for Comparativa
    const filterBar = document.getElementById("global-filter-bar");
    if (filterBar) {
      if (tabId === "comparativa") {
        filterBar.classList.add("hidden");
      } else {
        filterBar.classList.remove("hidden");
      }
    }

    document.getElementById("mobile-drawer")?.classList.remove("drawer-open");
    document.getElementById("mobile-menu-btn")?.setAttribute("aria-expanded", "false");

    // Resize and render active charts
    setTimeout(() => {
      window.dispatchEvent(new Event("resize"));
      if (tabId === "comparativa") {
        if (typeof updateComparativaPanel === "function") updateComparativaPanel();
      } else {
        if (typeof updateDashboard === "function") updateDashboard();
      }
      setupChartCardActions();
    }, 50);
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
    menuBtn.addEventListener("click", () => {
      drawer.classList.add("drawer-open");
      menuBtn.setAttribute("aria-expanded", "true");
    });
  }
  if (closeBtn && drawer) {
    closeBtn.addEventListener("click", () => {
      drawer.classList.remove("drawer-open");
      menuBtn?.setAttribute("aria-expanded", "false");
    });
  }

  setupNavScrollControls();
}

function setupNavScrollControls() {
  const nav = document.getElementById("main-nav-tabs");
  const btnLeft = document.getElementById("nav-scroll-left");
  const btnRight = document.getElementById("nav-scroll-right");

  if (!nav) return;

  function updateArrows() {
    if (!btnLeft || !btnRight) return;
    const maxScroll = nav.scrollWidth - nav.clientWidth;
    const canScrollLeft = nav.scrollLeft > 10;
    const canScrollRight = nav.scrollLeft < maxScroll - 10;

    btnLeft.classList.toggle("hidden", !canScrollLeft);
    btnRight.classList.toggle("hidden", !canScrollRight);
  }

  if (btnLeft) {
    btnLeft.addEventListener("click", (e) => {
      e.stopPropagation();
      nav.scrollBy({ left: -220, behavior: prefersReducedMotion ? "auto" : "smooth" });
    });
  }

  if (btnRight) {
    btnRight.addEventListener("click", (e) => {
      e.stopPropagation();
      nav.scrollBy({ left: 220, behavior: prefersReducedMotion ? "auto" : "smooth" });
    });
  }

  nav.addEventListener("scroll", updateArrows);
  window.addEventListener("resize", updateArrows);

  // Safe inner tab focus (does NOT shift window viewport)
  document.querySelectorAll(".nav-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      const tabLeft = tab.offsetLeft;
      const tabWidth = tab.offsetWidth;
      const navScroll = nav.scrollLeft;
      const navWidth = nav.clientWidth;

      const scrollBehavior = prefersReducedMotion ? "auto" : "smooth";
      if (tabLeft < navScroll + 40) {
        nav.scrollTo({ left: Math.max(0, tabLeft - 40), behavior: scrollBehavior });
      } else if (tabLeft + tabWidth > navScroll + navWidth - 40) {
        nav.scrollTo({ left: tabLeft + tabWidth - navWidth + 40, behavior: scrollBehavior });
      }

      setTimeout(updateArrows, 250);
    });
  });

  setTimeout(updateArrows, 150);
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
      // Use CSS transitions (modal-backdrop + modal-open classes)
      requestAnimationFrame(() => {
        modal.classList.add("modal-open");
      });
      document.body.style.overflow = "hidden";
    }
  }

  function closeModal(modal) {
    if (modal) {
      modal.classList.remove("modal-open");
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

  if (comunaSel) {
    comunaSel.addEventListener("change", (e) => {
      filterState.comuna = e.target.value;
      updateDashboard();
    });
  }

  if (zonaSel) {
    zonaSel.addEventListener("change", (e) => {
      filterState.zona = e.target.value;
      updateDashboard();
    });
  }

  if (edadSel) {
    edadSel.addEventListener("change", (e) => {
      filterState.edad = e.target.value;
      updateDashboard();
    });
  }

  if (gseSel) {
    gseSel.addEventListener("change", (e) => {
      filterState.gse = e.target.value;
      updateDashboard();
    });
  }

  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      if (comunaSel) comunaSel.value = "Todas";
      if (zonaSel) zonaSel.value = "Todas";
      if (edadSel) edadSel.value = "Todos";
      if (gseSel) gseSel.value = "Todos";

      filterState.comuna = "Todas";
      filterState.zona = "Todas";
      filterState.edad = "Todos";
      filterState.gse = "Todos";

      updateDashboard();
    });
  }
}

function updateActiveChips() {
  const container = document.getElementById("active-chips-list");
  if (!container) return;

  container.innerHTML = "";

  if (currentActiveTab === "comparativa") {
    container.innerHTML = `<span class="px-2.5 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-700 font-bold flex items-center gap-1"><span class="material-symbols-outlined text-sm">public</span> Ámbito: Comparativa Nacional / Interregional (7 Regiones)</span>`;
    return;
  }

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
    if (filterState.comuna !== "Todas") {
      const comunaLabel = r.comuna || getVariableLabel("COMUNA", r.COMUNA);
      if (comunaLabel !== filterState.comuna) return false;
    }

    if (filterState.zona !== "Todas") {
      const zonaLabel = r.zona || getVariableLabel("AREA", r.AREA);
      if (filterState.zona === "Urbana" && !zonaLabel.toLowerCase().includes("urb")) return false;
      if (filterState.zona === "Rural" && !zonaLabel.toLowerCase().includes("rur")) return false;
    }

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

function calculateConsolidatedWeightedCounts(records, col1, col2) {
  let totalW = 0;
  const counts = {};

  records.forEach(r => {
    const w = Number(r.weight || r.PONDERADOR) || 1.0;
    totalW += w;
    const val1 = r[col1];
    const val2 = r[col2];

    const added = new Set();
    [val1, val2].forEach(val => {
      if (val !== null && val !== undefined && val < 97) {
        const key = String(val);
        if (!added.has(key)) {
          added.add(key);
          if (!counts[key]) {
            counts[key] = { weighted_count: 0, unweighted_count: 0 };
          }
          counts[key].weighted_count += w;
          counts[key].unweighted_count += 1;
        }
      }
    });
  });

  const result = {};
  for (const [code, data] of Object.entries(counts)) {
    const lbl = getVariableLabel(col1, code);
    result[lbl] = {
      code: code,
      count: data.unweighted_count,
      weighted_count: data.weighted_count,
      percentage: totalW > 0 ? (data.weighted_count / totalW) * 100 : 0
    };
  }

  return result;
}

function calculateWeightedMean(records, varName, minVal = 0, maxVal = 97) {
  let totalW = 0;
  let sumWX = 0;

  records.forEach(r => {
    const val = r[varName];
    if (val !== null && val !== undefined && val >= minVal && val < maxVal) {
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

  safeSetText("kpi-sample-size", sampleSize);
  updateActiveChips();

  // 1. KPI Updates
  const rumboCounts = calculateWeightedCounts(filtered, "B1");
  const progPct = rumboCounts["Progresando"] ? rumboCounts["Progresando"].percentage.toFixed(1) : "0.0";
  safeSetText("kpi-progreso-pct", `${progPct}%`);
  const elProgBar = document.getElementById("kpi-progreso-bar");
  if (elProgBar) elProgBar.style.width = `${progPct}%`;

  // Top Problem (Consolidated M1 + M2)
  const probCounts = calculateConsolidatedWeightedCounts(filtered, "B2_RECOD", "B2_2_RECOD");
  let topProb = { name: "Seguridad", code: "1", pct: 0 };
  for (const [pName, pData] of Object.entries(probCounts)) {
    if (pData.percentage > topProb.pct) {
      topProb = { name: pName, code: pData.code, pct: pData.percentage };
    }
  }
  safeSetText("kpi-problema-pct", `${topProb.pct.toFixed(1)}%`);
  safeSetText("kpi-problema-name", topProb.name);

  const identMean = calculateWeightedMean(filtered, "I6");
  const identScore = identMean ? identMean.toFixed(1) : "--";
  safeSetText("kpi-ident-score", identScore);
  const elIdentBar = document.getElementById("kpi-ident-bar");
  if (elIdentBar) elIdentBar.style.width = `${Math.min(100, Math.max(0, identMean || 0))}%`;

  const notaMean = calculateWeightedMean(filtered, "I8");
  const notaScore = notaMean ? notaMean.toFixed(1) : "--";
  safeSetText("kpi-nota-score", notaScore);
  safeSetText("uaysen-nota-big", notaScore);

  const conCounts = calculateWeightedCounts(filtered, "I5");
  const conSi = conCounts["Sí"] ? conCounts["Sí"].percentage.toFixed(1) : "0.0";
  const conNo = conCounts["No"] ? conCounts["No"].percentage.toFixed(1) : "0.0";
  safeSetText("uaysen-conocimiento-si", `${conSi}%`);
  safeSetText("uaysen-conocimiento-no", `${conNo}%`);

  // 2. Confianza Social Panel Updates
  updateConfianzaPanel(filtered);

  // 3. Perfil Demográfico Panel Updates
  updateDemografiaPanel(filtered);

  // 4. Safe Chart Renderers Execution
  const chartRenderers = [
    () => renderRumboChart(rumboCounts),
    () => renderProblemasChart(probCounts),
    () => renderPertenenciaChart(filtered),
    () => renderServiciosChart(filtered),
    () => renderServiciosCompletoChart(filtered),
    () => renderMovilidadCharts(filtered),
    () => renderGobernanzaChart(filtered),
    () => renderInstitucionesChart(filtered),
    () => renderMediosCharts(filtered),
    () => renderCentralismoChart(filtered),
    () => renderGobernadoresChart(filtered),
    () => renderPoliticaCharts(filtered),
    () => renderAmbientalChart(filtered),
    () => renderAfectacionAmbientalChart(filtered),
    () => renderEconomiaChart(filtered),
    () => renderSalmonImpactosChart(filtered),
    () => renderTurismoMitosChart(filtered),
    () => renderUAysenceAporteChart(filtered),
    () => renderUAysenceCualitativoChart(filtered),
    () => { if (currentActiveTab === "comparativa") updateComparativaPanel(); }
  ];

  chartRenderers.forEach(fn => {
    try {
      fn();
    } catch (err) {
      console.error("[Dashboard Chart Error]:", err);
    }
  });

  // 5. Update Explorer
  renderExplorerTable();

  // 6. Update dynamic filter subtitles & attach chart card toolbar actions
  document.querySelectorAll(".chart-filter-context").forEach(el => {
    el.textContent = getActiveFilterDescription();
  });
  setupChartCardActions();
}

// ----------------------------------------------------
// Demografía Panel Logic
// ----------------------------------------------------
function updateDemografiaPanel(filteredRecords) {
  if (!filteredRecords) return;

  try {
    // 1. Ingreso Promedio Hogar (J7: > 10000 CLP)
    const incomeMean = calculateWeightedMean(filteredRecords, "J7", 10000, 99000000);
    if (incomeMean !== null) {
      const formattedIncome = "$" + Math.round(incomeMean).toLocaleString("es-CL") + " CLP";
      safeSetText("kpi-ingreso-promedio", formattedIncome);
    } else {
      safeSetText("kpi-ingreso-promedio", "--");
    }

    // 2. Educación Predominante J1
    const eduCounts = calculateWeightedCounts(filteredRecords, "J1");
    let topEdu = { name: "Media Completa", pct: 0 };
    for (const [eName, eData] of Object.entries(eduCounts)) {
      if (eData.percentage > topEdu.pct) {
        topEdu = { name: eName, pct: eData.percentage };
      }
    }
    safeSetText("kpi-top-educacion", topEdu.name);

    // 3. Matriz Ocupacional Top CIUO08_1N
    const ocCounts = calculateWeightedCounts(filteredRecords, "CIUO08_1N");
    let topOc = { name: "Servicios y Comercio", pct: 0 };
    for (const [oName, oData] of Object.entries(ocCounts)) {
      if (oData.percentage > topOc.pct) {
        topOc = { name: oName, pct: oData.percentage };
      }
    }
    safeSetText("kpi-top-ocupacion", topOc.name);

    // 4. Render Demographic Charts
    renderEducacionChart(eduCounts);
    renderGseChart(filteredRecords);
    renderOcupacionChart(ocCounts);

  } catch (err) {
    console.error("[Demografia Panel Error]:", err);
  }
}

// ----------------------------------------------------
// Confianza Social Panel Logic
// ----------------------------------------------------
function updateConfianzaPanel(filteredRecords) {
  if (!filteredRecords) return;

  try {
    const c1ValidRecords = filteredRecords.filter(r => r.C1 !== null && r.C1 !== undefined && (Number(r.C1) === 1 || Number(r.C1) === 2));
    const c1TrustWeightedSum = c1ValidRecords
      .filter(r => Number(r.C1) === 1)
      .reduce((sum, r) => sum + (Number(r.weight || r.PONDERADOR) || 1.0), 0);
    const c1TotalWeightedSum = c1ValidRecords
      .reduce((sum, r) => sum + (Number(r.weight || r.PONDERADOR) || 1.0), 0);

    const trustPct = c1TotalWeightedSum > 0 ? (c1TrustWeightedSum / c1TotalWeightedSum) * 100 : 0;

    const c2ValidRecords = filteredRecords.filter(r => r.C2 !== null && r.C2 !== undefined && (Number(r.C2) === 1 || Number(r.C2) === 2));
    const c2YesWeightedSum = c2ValidRecords
      .filter(r => Number(r.C2) === 1)
      .reduce((sum, r) => sum + (Number(r.weight || r.PONDERADOR) || 1.0), 0);
    const c2TotalWeightedSum = c2ValidRecords
      .reduce((sum, r) => sum + (Number(r.weight || r.PONDERADOR) || 1.0), 0);

    const partPct = c2TotalWeightedSum > 0 ? (c2YesWeightedSum / c2TotalWeightedSum) * 100 : 0;

    const c22Counts = calculateWeightedCounts(filteredRecords, "C2_2_RECOD");
    let topOrg = { name: "Organizaciones sociales", pct: 0 };
    for (const [oName, oData] of Object.entries(c22Counts)) {
      if (oData.percentage > topOrg.pct) {
        topOrg = { name: oName, pct: oData.percentage };
      }
    }

    safeSetText("kpi-confianza-pct", `${trustPct.toFixed(1)}%`);
    safeSetText("kpi-participacion-pct", `${partPct.toFixed(1)}%`);
    safeSetText("kpi-top-org", topOrg.name);

    const noTrustWeightedSum = c1TotalWeightedSum - c1TrustWeightedSum;
    renderConfianzaChart(c1TrustWeightedSum, noTrustWeightedSum);
    renderParticipacionChart(c22Counts);

  } catch (err) {
    console.error("[Confianza Panel Error]:", err);
  }
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
  amber: "#f59e0b",
  indigo: "#6366f1"
};

function renderEducacionChart(eduCounts) {
  const ctx = safeGetCanvas("chart-educacion-canvas");
  if (!ctx) return;

  const sorted = Object.entries(eduCounts)
    .map(([k, v]) => ({ name: k, pct: v.percentage }))
    .sort((a, b) => b.pct - a.pct);

  const labels = sorted.map(s => s.name);
  const data = sorted.map(s => s.pct.toFixed(1));

  if (charts.educacion) charts.educacion.destroy();

  charts.educacion = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "% Nivel Educacional",
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
      scales: { x: { ticks: { callback: v => `${v}%` } } }
    }
  });
}

function renderGseChart(filtered) {
  const ctx = safeGetCanvas("chart-gse-canvas");
  if (!ctx || !filtered || filtered.length === 0) return;

  // GSE_4_Categorias: 1 = ABC1, 2 = C2, 3 = C3, 4 = D+E
  let gse1W = 0, gse2W = 0, gse3W = 0, gse4W = 0;
  let totalW = 0;

  filtered.forEach(r => {
    const rawVal = r.GSE_4_Categorias || r.GSE;
    if (rawVal !== null && rawVal !== undefined) {
      const val = Math.round(Number(rawVal));
      const w = Number(r.PONDERADOR || r.weight) || 1.0;

      if (val === 1) gse1W += w;      // ABC1
      else if (val === 2) gse2W += w; // C2
      else if (val === 3) gse3W += w; // C3
      else if (val === 4 || val === 5 || val === 6 || val === 7) gse4W += w; // D+E
      
      if ([1,2,3,4,5,6,7].includes(val)) totalW += w;
    }
  });

  const labels = ["ABC1", "C2", "C3", "D+E"];
  const data = totalW > 0 ? [
    Number(((gse1W / totalW) * 100).toFixed(1)),
    Number(((gse2W / totalW) * 100).toFixed(1)),
    Number(((gse3W / totalW) * 100).toFixed(1)),
    Number(((gse4W / totalW) * 100).toFixed(1))
  ] : [15, 25, 35, 25];

  if (charts.gse) charts.gse.destroy();

  charts.gse = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: [
          BRAND_COLORS.accent || "#00A3E0",
          BRAND_COLORS.secondary || "#41BEFD",
          BRAND_COLORS.primary || "#0A2540",
          "#64748B"
        ],
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

function renderOcupacionChart(ocCounts) {
  const ctx = safeGetCanvas("chart-ocupacion-canvas");
  if (!ctx) return;

  const sorted = Object.entries(ocCounts)
    .map(([k, v]) => ({ name: k, pct: v.percentage }))
    .sort((a, b) => b.pct - a.pct);

  const labels = sorted.map(s => s.name);
  const data = sorted.map(s => s.pct.toFixed(1));

  if (charts.ocupacion) charts.ocupacion.destroy();

  charts.ocupacion = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "% Matriz Ocupacional",
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

function renderUAysenceCualitativoChart(filtered) {
  const ctx = safeGetCanvas("chart-uaysen-cualitativo-canvas");
  if (!ctx) return;

  const i51Counts = calculateWeightedCounts(filtered, "I51_COD");
  const sorted = Object.entries(i51Counts)
    .map(([k, v]) => ({ name: k, pct: v.percentage }))
    .sort((a, b) => b.pct - a.pct)
    .slice(0, 10);

  const labels = sorted.map(s => s.name);
  const data = sorted.map(s => s.pct.toFixed(1));

  if (charts.uaysenCualitativo) charts.uaysenCualitativo.destroy();

  charts.uaysenCualitativo = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "% Mención Espontánea",
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
      scales: { x: { ticks: { callback: v => `${v}%` } } }
    }
  });
}

function renderRumboChart(rumboCounts) {
  const ctx = safeGetCanvas("chart-rumbo-canvas");
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
        tooltip: { callbacks: { label: (item) => ` ${item.label}: ${item.raw}%` } }
      }
    }
  });
}

function renderConfianzaChart(trustWeightedSum, noTrustWeightedSum) {
  const ctx = safeGetCanvas("chart-confianza-canvas");
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
        tooltip: { callbacks: { label: (item) => ` ${item.label}: ${item.raw}%` } }
      }
    }
  });
}

function renderMovilidadCharts(filtered) {
  const ctxMov = safeGetCanvas("chart-movilidad-canvas");
  const ctxDes = safeGetCanvas("chart-destino-canvas");

  if (ctxMov) {
    const a2Counts = calculateWeightedCounts(filtered, "A2");
    const labels = ["No, prefiere quedarse", "Sí, desea irse"];
    const data = labels.map(l => a2Counts[l] ? a2Counts[l].percentage.toFixed(1) : 0);

    if (charts.movilidad) charts.movilidad.destroy();
    charts.movilidad = new Chart(ctxMov, {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: [BRAND_COLORS.emerald, BRAND_COLORS.rose],
          borderWidth: 2,
          borderColor: "#ffffff"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom" } }
      }
    });
  }

  if (ctxDes) {
    const a3Counts = calculateWeightedCounts(filtered, "A3");
    const sorted = Object.entries(a3Counts)
      .map(([k, v]) => ({ name: k, pct: v.percentage }))
      .sort((a, b) => b.pct - a.pct);

    const labels = sorted.map(s => s.name);
    const data = sorted.map(s => s.pct.toFixed(1));

    if (charts.destino) charts.destino.destroy();
    charts.destino = new Chart(ctxDes, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: "% Destino",
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
        scales: { x: { ticks: { callback: v => `${v}%` } } }
      }
    });
  }
}

function renderParticipacionChart(c22Counts) {
  const ctx = safeGetCanvas("chart-participacion-canvas");
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
  const ctx = safeGetCanvas("chart-problemas-canvas");
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
        label: "% Mención Consolidada (1° + 2°)",
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
      scales: { x: { ticks: { callback: v => `${v}%` } } }
    }
  });
}

function renderPertenenciaChart(filtered) {
  const ctx = safeGetCanvas("chart-pertenencia-canvas");
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
  const ctx = safeGetCanvas("chart-servicios-canvas");
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

function renderServiciosCompletoChart(filtered) {
  const ctx = safeGetCanvas("chart-servicios-completo-canvas");
  if (!ctx) return;

  const items = [
    { col: "B3_A", label: "Salud pública" },
    { col: "B3_B", label: "Educación pública" },
    { col: "B3_C", label: "Transporte y conectividad" },
    { col: "B3_D", label: "Vivienda" },
    { col: "B3_E", label: "Seguridad y orden" },
    { col: "B3_F", label: "Opciones de empleo" },
    { col: "B3_G", label: "Recreación y cultura" },
    { col: "B3_H", label: "Calidad del medioambiente" },
    { col: "B3_I", label: "Conexión a Internet" },
    { col: "B4_A", label: "Oportunidades de trabajo" },
    { col: "B4_B", label: "Recreación y cultura (B4)" },
    { col: "B4_C", label: "Posibilidad de buen sueldo" },
    { col: "B4_D", label: "Posibilidad de consumir" },
    { col: "B4_E", label: "Participación ciudadana" }
  ];

  const sorted = items.map(it => ({
    label: it.label,
    mean: calculateWeightedMean(filtered, it.col)
  }))
  .filter(i => i.mean !== null)
  .sort((a, b) => b.mean - a.mean);

  const labels = sorted.map(s => s.label);
  const means = sorted.map(s => s.mean.toFixed(2));

  if (charts.serviciosCompleto) charts.serviciosCompleto.destroy();

  charts.serviciosCompleto = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Nota Promedio (1 a 7)",
        data: means,
        backgroundColor: BRAND_COLORS.accent,
        borderRadius: 6
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
  const ctx = safeGetCanvas("chart-gobernanza-canvas");
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
          nacW += w;
        } else if (val === 2 || val === 3) {
          regW += w;
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
        { label: "Decisión Regional/Comunal", data: regPct, backgroundColor: BRAND_COLORS.secondary || "#00A3E0" },
        { label: "Decisión Gobierno Nacional", data: nacPct, backgroundColor: BRAND_COLORS.primary || "#0A2540" }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: { callbacks: { label: (item) => ` ${item.dataset.label}: ${item.raw}%` } },
        datalabels: {
          align: 'center',
          anchor: 'center',
          color: '#ffffff'
        }
      },
      scales: { x: { stacked: true }, y: { stacked: true, max: 100, ticks: { callback: v => `${v}%` } } }
    }
  });
}

function renderMediosCharts(filtered) {
  const ctxMain = safeGetCanvas("chart-medio-principal-canvas");

  if (ctxMain) {
    const e2Counts = calculateWeightedCounts(filtered, "E2");
    const sorted = Object.entries(e2Counts)
      .map(([k, v]) => ({ name: k, pct: v.percentage }))
      .sort((a, b) => b.pct - a.pct);

    const labels = sorted.map(s => s.name);
    const data = sorted.map(s => s.pct.toFixed(1));

    if (charts.medioPrincipal) charts.medioPrincipal.destroy();
    charts.medioPrincipal = new Chart(ctxMain, {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: [
            BRAND_COLORS.accent, BRAND_COLORS.primary, BRAND_COLORS.secondary,
            BRAND_COLORS.emerald, BRAND_COLORS.amber, BRAND_COLORS.rose, BRAND_COLORS.indigo
          ],
          borderWidth: 2,
          borderColor: "#ffffff"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom" } }
      }
    });
  }
}

// Pregunta G2: Centralismo vs Autonomía (Doughnut Chart)
function renderCentralismoChart(filtered) {
  const ctx = safeGetCanvas("chart-centralismo-canvas");
  if (!ctx || !filtered || filtered.length === 0) return;

  let centW = 0, autoW = 0, totalW = 0;

  filtered.forEach(r => {
    const val = Math.round(Number(r.G2));
    const w = Number(r.PONDERADOR || r.weight) || 1.0;
    if (val === 1) { centW += w; totalW += w; }      // 1 = Aumentó centralismo
    else if (val === 2) { autoW += w; totalW += w; } // 2 = Mayor autonomía
  });

  const centPct = totalW > 0 ? Number(((centW / totalW) * 100).toFixed(1)) : 0;
  const autoPct = totalW > 0 ? Number(((autoW / totalW) * 100).toFixed(1)) : 0;

  if (charts.centralismo) charts.centralismo.destroy();

  charts.centralismo = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Aumentó el centralismo", "Mayor autonomía regional"],
      datasets: [{
        data: [centPct, autoPct],
        backgroundColor: ["#F43F5E", "#10B981"],
        borderWidth: 2,
        borderColor: "#ffffff"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom", labels: { font: { size: 11 } } },
        tooltip: { callbacks: { label: (item) => ` ${item.label}: ${item.raw}%` } }
      }
    }
  });
}

// Pregunta G3: Impacto Gobernadores (Horizontal Bar Chart with Multiline Y-Labels)
function renderGobernadoresChart(filtered) {
  const ctx = safeGetCanvas("chart-gobernadores-canvas");
  if (!ctx || !filtered || filtered.length === 0) return;

  let igualW = 0, impulsoW = 0, problemasW = 0, totalW = 0;

  filtered.forEach(r => {
    const val = Math.round(Number(r.G3));
    const w = Number(r.PONDERADOR || r.weight) || 1.0;
    if (val === 1) { impulsoW += w; totalW += w; }      // 1 = Impulso
    else if (val === 2) { igualW += w; totalW += w; }   // 2 = Dejó igual
    else if (val === 3) { problemasW += w; totalW += w; } // 3 = Más problemas
  });

  // Array of arrays forces Chart.js to render multi-line Y-axis labels cleanly
  const labels = [
    ["Ha dejado las", "cosas igual"],
    ["Ha sido un", "impulso"],
    ["Ha traído más", "problemas"]
  ];

  const data = totalW > 0 ? [
    Number(((igualW / totalW) * 100).toFixed(1)),
    Number(((impulsoW / totalW) * 100).toFixed(1)),
    Number(((problemasW / totalW) * 100).toFixed(1))
  ] : [0, 0, 0];

  if (charts.gobernadores) charts.gobernadores.destroy();

  charts.gobernadores = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "% de respuesta",
        data: data,
        backgroundColor: ["#64748B", "#00A3E0", "#F59E0B"],
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      layout: {
        padding: {
          left: 5,
          right: 15,
          top: 5,
          bottom: 5
        }
      },
      plugins: { 
        legend: { display: false },
        tooltip: {
          callbacks: {
            // Join multiline label into single line string inside tooltip
            title: (items) => Array.isArray(items[0].label) ? items[0].label.join(" ") : items[0].label,
            label: (item) => ` ${item.raw}%`
          }
        }
      },
      scales: { 
        x: { max: 100, ticks: { callback: v => `${v}%` } },
        y: {
          ticks: {
            font: { size: 11, weight: "500" },
            color: "#475569"
          }
        }
      }
    }
  });
}

function renderPoliticaCharts(filtered) {
  const ctxDem = safeGetCanvas("chart-democracia-canvas");
  const ctxPol = safeGetCanvas("chart-posicion-politica-canvas");

  if (ctxDem) {
    const h1Counts = calculateWeightedCounts(filtered, "H1");
    const sorted = Object.entries(h1Counts).map(([k, v]) => ({ name: k, pct: v.percentage }));

    const labels = sorted.map(s => s.name);
    const data = sorted.map(s => s.pct.toFixed(1));

    if (charts.democracia) charts.democracia.destroy();
    charts.democracia = new Chart(ctxDem, {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: [BRAND_COLORS.emerald, BRAND_COLORS.rose, BRAND_COLORS.muted],
          borderWidth: 2,
          borderColor: "#ffffff"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom" } }
      }
    });
  }

  if (ctxPol) {
    const h2Counts = calculateWeightedCounts(filtered, "H2");
    const labels = ["Izquierda", "Centro Izquierda", "Centro", "Centro Derecha", "Derecha", "Ninguna"];
    const data = labels.map(l => h2Counts[l] ? h2Counts[l].percentage.toFixed(1) : 0);

    if (charts.politica) charts.politica.destroy();
    charts.politica = new Chart(ctxPol, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: "% Identificación Polítca",
          data: data,
          backgroundColor: BRAND_COLORS.primary,
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
}

function renderInstitucionesChart(filtered) {
  const ctx = safeGetCanvas("chart-instituciones-canvas");
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
  const ctx = safeGetCanvas("chart-ambiental-canvas");
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

function renderAfectacionAmbientalChart(filtered) {
  const ctx = safeGetCanvas("chart-afectacion-ambiental-canvas");
  if (!ctx) return;

  const items = [
    { col: "D1_A", label: "Centrales energéticas" },
    { col: "D1_B", label: "Faenas mineras" },
    { col: "D1_C", label: "Efectos pesca industrial" },
    { col: "D1_D", label: "Contaminación agua/aire" },
    { col: "D1_E", label: "Contaminación suelo" },
    { col: "D1_F", label: "Deterioro patrimonio natural" },
    { col: "D1_G", label: "Construcción autopistas" },
    { col: "D1_H", label: "Actividad salmonicultura" }
  ];

  const sorted = items.map(it => {
    let affectedW = 0;
    let totalW = 0;
    filtered.forEach(r => {
      const val = Math.round(Number(r[it.col]));
      if (val === 1 || val === 2) {
        const w = Number(r.PONDERADOR || r.weight) || 1.0;
        totalW += w;
        if (val === 1) affectedW += w;
      }
    });
    return {
      label: it.label,
      pct: totalW > 0 ? (affectedW / totalW) * 100 : 0
    };
  })
  .sort((a, b) => b.pct - a.pct);

  const labels = sorted.map(s => s.label);
  const data = sorted.map(s => s.pct.toFixed(1));

  if (charts.afectacionAmbiental) charts.afectacionAmbiental.destroy();

  charts.afectacionAmbiental = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "% Afectado",
        data: data,
        backgroundColor: BRAND_COLORS.rose,
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

function renderEconomiaChart(filtered) {
  const ctx = safeGetCanvas("chart-economia-canvas");
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

function renderSalmonImpactosChart(filtered) {
  const ctx = safeGetCanvas("chart-salmon-impactos-canvas");
  if (!ctx) return;

  const items = [
    { col: "I2_A", label: "Habría menos empleo" },
    { col: "I2_B", label: "Habría más recursos mar" },
    { col: "I2_C", label: "Progresaría menos econ." },
    { col: "I2_D", label: "Menos conflictos soc." },
    { col: "I2_E", label: "Menos conflictos amb." },
    { col: "I2_F", label: "Aumentaría la pobreza" }
  ];

  const labels = items.map(i => i.label);
  const agreePct = [];

  items.forEach(it => {
    let agreeW = 0;
    let totalW = 0;
    filtered.forEach(r => {
      const val = Math.round(Number(r[it.col]));
      if (val >= 1 && val <= 4) {
        const w = Number(r.PONDERADOR || r.weight) || 1.0;
        totalW += w;
        if (val === 3 || val === 4) agreeW += w;
      }
    });
    agreePct.push(totalW > 0 ? Number(((agreeW / totalW) * 100).toFixed(1)) : 0);
  });

  if (charts.salmonImpactos) charts.salmonImpactos.destroy();

  charts.salmonImpactos = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "% De Acuerdo / Muy De Acuerdo",
        data: agreePct,
        backgroundColor: BRAND_COLORS.primary,
        borderRadius: 8
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { x: { max: 100, ticks: { callback: v => `${v}%` } } }
    }
  });
}

function renderTurismoMitosChart(filtered) {
  const ctx = safeGetCanvas("chart-turismo-mitos-canvas");
  if (!ctx) return;

  const items = [
    { col: "I3_A", label: "Principal actividad futura" },
    { col: "I3_B", label: "Genera molestias habitantes" },
    { col: "I3_C", label: "Sustentable y respeta medioambiente" },
    { col: "I3_D", label: "Beneficios solo para algunos" }
  ];

  const labels = items.map(i => i.label);
  const agreePct = [];

  items.forEach(it => {
    let agreeW = 0;
    let totalW = 0;
    filtered.forEach(r => {
      const val = Math.round(Number(r[it.col]));
      if (val >= 1 && val <= 4) {
        const w = Number(r.PONDERADOR || r.weight) || 1.0;
        totalW += w;
        if (val === 3 || val === 4) agreeW += w;
      }
    });
    agreePct.push(totalW > 0 ? Number(((agreeW / totalW) * 100).toFixed(1)) : 0);
  });

  if (charts.turismoMitos) charts.turismoMitos.destroy();

  charts.turismoMitos = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "% De Acuerdo / Muy De Acuerdo",
        data: agreePct,
        backgroundColor: BRAND_COLORS.emerald,
        borderRadius: 8
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { x: { max: 100, ticks: { callback: v => `${v}%` } } }
    }
  });
}

function renderUAysenceAporteChart(filtered) {
  const ctx = safeGetCanvas("chart-uaysen-aporte-canvas");
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
  const elVarX = document.getElementById("explorer-var-x");
  const elVarY = document.getElementById("explorer-var-y");
  const tbody = document.getElementById("explorer-table-body");
  const thead = document.getElementById("explorer-table-head");

  if (!elVarX || !elVarY || !tbody || !thead) return;

  const varX = elVarX.value;
  const varY = elVarY.value;

  const filteredRecords = getFilteredRecords();
  if (!filteredRecords || filteredRecords.length === 0) {
    tbody.innerHTML = `<tr><td colspan="100%" class="p-4 text-center text-outline">No hay datos disponibles para la selección actual.</td></tr>`;
    return;
  }

  const xSet = new Set();
  filteredRecords.forEach(r => {
    if (r[varX] !== null && r[varX] !== undefined && r[varX] < 97) {
      xSet.add(r[varX]);
    }
  });
  const xValues = Array.from(xSet).sort((a, b) => Number(a) - Number(b));

  const ySet = new Set();
  filteredRecords.forEach(r => {
    if (r[varY] !== null && r[varY] !== undefined && r[varY] !== "") {
      ySet.add(r[varY]);
    }
  });
  const yValues = Array.from(ySet).sort();

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

  let headHtml = `<tr class="bg-primary-container text-white text-xs uppercase tracking-wider">`;
  headHtml += `<th class="p-3 font-bold border-r border-white/10">Variable ${varX} \\ ${varY.toUpperCase()}</th>`;
  yValues.forEach(yVal => {
    const colLabel = getVariableLabel(varY, yVal);
    headHtml += `<th class="p-3 font-bold text-center border-r border-white/10">${colLabel}</th>`;
  });
  headHtml += `<th class="p-3 font-bold text-center">Total</th></tr>`;
  thead.innerHTML = headHtml;

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
  const elVarX = document.getElementById("explorer-var-x");
  const elVarY = document.getElementById("explorer-var-y");
  if (!elVarX || !elVarY) return;

  const varX = elVarX.value;
  const varY = elVarY.value;
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

// ----------------------------------------------------
// Comparativa Interregional Panel & Charts Engine
// ----------------------------------------------------
let currentCompSubtab = "coyuntura";
let compData = null;

async function loadComparativaData() {
  if (compData) return;
  try {
    const res = await fetch("data/comparativa_interregional.json?v=" + Date.now());
    compData = await res.json();
  } catch (err) {
    console.error("Error loading comparativa_interregional.json:", err);
  }
}

function setupComparativaSubNavigation() {
  const subtabs = document.querySelectorAll(".comp-subtab");
  if (!subtabs || subtabs.length === 0) return;

  subtabs.forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.subtab;
      currentCompSubtab = target;

      subtabs.forEach(b => {
        if (b.dataset.subtab === target) {
          b.classList.add("active");
          b.classList.remove("text-outline", "hover:bg-white/60");
        } else {
          b.classList.remove("active");
          b.classList.add("text-outline", "hover:bg-white/60");
        }
      });

      document.querySelectorAll(".comp-subpanel").forEach(p => {
        if (p.id === `comp-subpanel-${target}`) {
          p.classList.remove("hidden");
          // Trigger opacity entrance
          p.classList.add("subpanel-entering");
          requestAnimationFrame(() => {
            requestAnimationFrame(() => {
              p.classList.remove("subpanel-entering");
            });
          });
        } else {
          p.classList.add("hidden");
        }
      });

      setTimeout(() => {
        window.dispatchEvent(new Event("resize"));
        renderActiveCompSubpanel();
        setupChartCardActions();
      }, 50);
    });
  });
}

async function updateComparativaPanel() {
  await loadComparativaData();
  if (!compData) return;
  renderActiveCompSubpanel();
  setupChartCardActions();
}

function renderActiveCompSubpanel() {
  if (!compData) return;

  // Generic Bar Chart Renderer (Aysén in #00A3E0, others in #94A3B8)
  function renderCompBar(canvasId, items, valKey, isGrade = false) {
    const ctx = safeGetCanvas(canvasId);
    if (!ctx || !items) return;

    const labels = items.map(i => i.region || i.institucion);
    const data = items.map(i => i[valKey]);
    const colors = items.map(i => i.is_target ? "#00A3E0" : "#94A3B8");

    if (charts[canvasId]) charts[canvasId].destroy();

    charts[canvasId] = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: colors,
          borderRadius: 6,
          isScore: isGrade
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            min: isGrade ? 1 : 0,
            max: isGrade ? 7 : undefined,
            ticks: { callback: v => isGrade ? v : `${v}%` }
          }
        }
      }
    });
  }

  // Generic Stacked Bar Renderer (100% distribution across categories)
  function renderCompStackedBar(canvasId, items, catKeys, catLabels, palette) {
    const ctx = safeGetCanvas(canvasId);
    if (!ctx || !items || items.length === 0) return;

    const labels = items.map(i => i.region);
    const datasets = catKeys.map((k, idx) => {
      const color = palette[idx % palette.length];
      return {
        label: catLabels[idx],
        data: items.map(i => Number(k === "region" && i.su_region !== undefined ? i.su_region : i[k]) || 0),
        backgroundColor: color,
        borderWidth: 1,
        borderColor: "#ffffff",
        borderRadius: 0,
        // Stacked specific datalabels configuration
        datalabels: {
          display: (context) => {
            const val = context.dataset.data[context.dataIndex];
            return val >= 6.0; // Hide labels on thin segments to avoid clutter/overflow
          },
          formatter: (val) => `${val}%`,
          color: (context) => {
            // Dynamic contrast helper
            const hex = color.replace("#", "");
            const r = parseInt(hex.substr(0, 2), 16);
            const g = parseInt(hex.substr(2, 2), 16);
            const b = parseInt(hex.substr(4, 2), 16);
            const yiq = (r * 299 + g * 587 + b * 114) / 1000;
            return yiq >= 150 ? "#0A2540" : "#FFFFFF";
          },
          anchor: "center",
          align: "center",
          font: {
            family: "'Inter', sans-serif",
            weight: "700",
            size: 10.5
          }
        }
      };
    });

    if (charts[canvasId]) charts[canvasId].destroy();

    charts[canvasId] = new Chart(ctx, {
      type: "bar",
      data: { labels: labels, datasets: datasets },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: { left: 5, right: 15, top: 5, bottom: 5 }
        },
        plugins: {
          legend: {
            position: "top",
            labels: {
              font: { family: "'Inter', sans-serif", size: 11, weight: "600" },
              boxWidth: 12,
              padding: 12
            }
          },
          tooltip: {
            callbacks: {
              label: (item) => ` ${item.dataset.label}: ${item.raw}%`
            }
          }
        },
        scales: {
          x: {
            stacked: true,
            max: 100,
            ticks: { callback: v => `${v}%` },
            grid: { color: "rgba(0,0,0,0.05)" }
          },
          y: {
            stacked: true,
            ticks: {
              font: { family: "'Inter', sans-serif", size: 11, weight: "600" },
              color: (c) => items[c.index]?.is_target ? "#00A3E0" : "#475569"
            },
            grid: { display: false }
          }
        }
      }
    });
  }

  // Render active subpanel charts dynamically
  if (currentCompSubtab === "coyuntura" && compData.coyuntura) {
    const c = compData.coyuntura;
    // 1. Rumbo Regional (Evaluative Semantic Tri-Color: Emerald / Amber / Coral)
    renderCompStackedBar(
      "chart-comp-rumbo",
      c.rumbo,
      ["progresando", "estancada", "decadencia"],
      ["Progresando", "Estancada", "En Decadencia"],
      ["#059669", "#D97706", "#E11D48"]
    );
    renderCompBar("chart-comp-migrar", c.disposicion_migrar, "pct");
    // 2. Destino de Migración (Step Sequential: Sky -> Turquoise -> Deep Navy)
    renderCompStackedBar(
      "chart-comp-destino",
      c.destino_migracion,
      ["otra_comuna", "otra_region", "extranjero"],
      ["Otra Comuna", "Otra Región", "Al Extranjero"],
      ["#38BDF8", "#00A3E0", "#0A2540"]
    );
    // 3. Espacio de Mayor Identificación (Territorial Hierarchy Scale)
    renderCompStackedBar(
      "chart-comp-identificacion",
      c.identificacion_territorial,
      ["barrio", "comuna", "region", "pais"],
      ["Barrio", "Comuna", "Región", "País"],
      ["#7DD3FC", "#00A3E0", "#0369A1", "#0A2540"]
    );
    // 4. Principal Problema Regional (Curated Editorial Palette)
    renderCompStackedBar(
      "chart-comp-problema",
      c.principal_problema,
      ["seguridad", "conectividad", "salud", "empleo", "vivienda"],
      ["Seguridad", "Conectividad", "Salud", "Empleo", "Vivienda"],
      ["#E11D48", "#0A2540", "#EA580C", "#00A3E0", "#64748B"]
    );
    renderCompBar("chart-comp-erd", c.conocimiento_erd, "pct");

  } else if (currentCompSubtab === "servicios" && compData.servicios) {
    const s = compData.servicios;
    renderCompBar("chart-comp-caminos", s.caminos, "nota", true);
    renderCompBar("chart-comp-seguridad", s.seguridad, "nota", true);
    renderCompBar("chart-comp-salud", s.salud, "nota", true);
    renderCompBar("chart-comp-internet", s.internet, "nota", true);
    renderCompBar("chart-comp-vivienda", s.vivienda, "nota", true);
    renderCompBar("chart-comp-transporte", s.transporte, "nota", true);
    renderCompBar("chart-comp-educacion", s.educacion, "nota", true);
    renderCompBar("chart-comp-agua", s.agua, "nota", true);
    renderCompBar("chart-comp-medioambiente", s.medioambiente, "nota", true);
    renderCompBar("chart-comp-empleo", s.empleo, "nota", true);
    renderCompBar("chart-comp-sueldos", s.sueldos, "nota", true);
    renderCompBar("chart-comp-recreacion", s.recreacion, "nota", true);

  } else if (currentCompSubtab === "descentralizacion" && compData.descentralizacion) {
    const d = compData.descentralizacion;
    renderCompBar("chart-comp-centralismo", d.centralismo, "pct");
    // 5. Impacto Gobernadores Regionales (Evaluative Palette)
    if (d.gobernadores) {
      renderCompStackedBar(
        "chart-comp-gobernadores",
        d.gobernadores,
        ["impulso", "igual", "problemas"],
        ["Ha sido un impulso", "Ha dejado igual", "Más problemas"],
        ["#00A3E0", "#64748B", "#E11D48"]
      );
    }
    renderCompBar("chart-comp-dec-obras", d.decision_obras, "pct");
    renderCompBar("chart-comp-dec-salud", d.decision_salud, "pct");
    renderCompBar("chart-comp-dec-educacion", d.decision_educacion, "pct");
    renderCompBar("chart-comp-dec-fomento", d.decision_fomento, "pct");
    renderCompBar("chart-comp-dec-ambiente", d.decision_medioambiente, "pct");
    renderCompBar("chart-comp-dec-agua", d.decision_agua, "pct");
    renderCompBar("chart-comp-dec-vivienda", d.decision_vivienda, "pct");
    renderCompBar("chart-comp-dec-inversion", d.decision_inversion, "pct");
    renderCompBar("chart-comp-dec-seguridad", d.decision_seguridad, "pct");
    renderCompBar("chart-comp-instituciones", d.aporte_institucional, "pct");

  } else if (currentCompSubtab === "cohesion" && compData.cohesion) {
    const k = compData.cohesion;
    renderCompBar("chart-comp-confianza", k.confianza, "pct");
    renderCompBar("chart-comp-participacion", k.participacion_comunitaria, "pct");
    renderCompBar("chart-comp-afec-aire", k.afectacion_aire, "pct");
    renderCompBar("chart-comp-afec-extractivismo", k.afectacion_extractivismo, "pct");
    renderCompBar("chart-comp-afec-basura", k.afectacion_basura, "pct");
    renderCompBar("chart-comp-afec-agua", k.afectacion_agua, "pct");
    renderCompBar("chart-comp-afec-clima", k.afectacion_clima, "pct");
    renderCompBar("chart-comp-democracia", k.adhesion_democracia, "pct");
    renderCompBar("chart-comp-uso-radios", k.uso_radios, "pct");
    renderCompBar("chart-comp-uso-tv", k.uso_tv, "pct");
    // 6. Medio Principal de Información (Ecología de Medios)
    if (k.medio_principal) {
      renderCompStackedBar(
        "chart-comp-medio-principal",
        k.medio_principal,
        ["redes_sociales", "tv_abierta", "radios_locales", "prensa_digital"],
        ["Redes Sociales", "TV Abierta", "Radios Locales", "Prensa Digital"],
        ["#00A3E0", "#0A2540", "#D97706", "#64748B"]
      );
    }
  }
}

// ----------------------------------------------------
// Export & Clipboard Engine with Context Stamping
// ----------------------------------------------------
async function exportChartWithContext(canvasId, action = "download", customTitle = "") {
  const sourceCanvas = document.getElementById(canvasId);
  if (!sourceCanvas) return;

  const isComparative = canvasId.includes("comp") || canvasId.startsWith("chart-comp");
  const card = sourceCanvas.closest(".bg-white") || sourceCanvas.parentElement;
  
  // Safe extraction: Clone title element and remove any button/toolbar children before reading text
  let titleText = customTitle;
  if (!titleText) {
    const rawTitleEl = card.querySelector("h4, h3, p.font-bold, p.text-lg");
    if (rawTitleEl) {
      const clone = rawTitleEl.cloneNode(true);
      clone.querySelectorAll(".chart-actions-toolbar, button, span.material-symbols-outlined").forEach(el => el.remove());
      titleText = clone.textContent.trim();
    } else {
      titleText = "Gráfico Barómetro";
    }
  }

  const subtitleEl = card.querySelector("p.text-xs.text-outline");
  const subtitleText = subtitleEl ? subtitleEl.textContent.trim() : "";
  
  const filterText = isComparative 
    ? "Ámbito: Benchmark Nacional / Interregional (7 Regiones)" 
    : `Filtros: ${getActiveFilterDescription()}`;
    
  const sampleText = isComparative 
    ? "Muestra Total: N = 3.813 encuestados (7 Regiones) | Barómetro Regional 2024" 
    : `Muestra actual: N = ${document.getElementById("kpi-sample-size")?.textContent || "465"} encuestados | Barómetro Regional UAysén 2025`;

  // Create High-Res Export Canvas
  const exportCanvas = document.createElement("canvas");
  const ctx = exportCanvas.getContext("2d");
  const padding = 30;
  const headerHeight = subtitleText ? 75 : 60;
  const footerHeight = 35;

  exportCanvas.width = sourceCanvas.width + padding * 2;
  exportCanvas.height = sourceCanvas.height + headerHeight + footerHeight + padding;

  // 1. Solid White Background
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, exportCanvas.width, exportCanvas.height);

  // 2. Header Title & Subtitle
  ctx.fillStyle = "#0a2540";
  ctx.font = "bold 15px 'Plus Jakarta Sans', sans-serif";
  ctx.fillText(titleText, padding, padding + 15);

  if (subtitleText) {
    ctx.fillStyle = "#475569";
    ctx.font = "italic 11px 'Inter', sans-serif";
    ctx.fillText(subtitleText, padding, padding + 33);
  }

  ctx.fillStyle = "#00a3e0";
  ctx.font = "600 11px 'Inter', sans-serif";
  ctx.fillText(filterText, padding, padding + (subtitleText ? 50 : 35));

  // 3. Draw Chart Image
  ctx.drawImage(sourceCanvas, padding, headerHeight + 15);

  // 4. Footer Watermark
  ctx.fillStyle = "#74777e";
  ctx.font = "11px 'Inter', sans-serif";
  ctx.fillText(sampleText, padding, exportCanvas.height - 15);

  // 5. Trigger Action
  if (action === "copy") {
    exportCanvas.toBlob(async (blob) => {
      try {
        await navigator.clipboard.write([new ClipboardItem({ "image/png": blob })]);
        showToast("¡Gráfico copiado al portapapeles!");
      } catch (err) {
        console.error("Error copying to clipboard:", err);
        downloadCanvas(exportCanvas, titleText);
      }
    });
  } else {
    downloadCanvas(exportCanvas, titleText);
  }
}

function downloadCanvas(canvas, filename) {
  const cleanName = filename.toLowerCase().replace(/[^a-z0-9]/gi, "_").substring(0, 35);
  const link = document.createElement("a");
  link.download = `barometro_${cleanName}.png`;
  link.href = canvas.toDataURL("image/png");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showToast("Descargando imagen del gráfico...");
}

// Toast notification helper
let _toastTimer = null;
function showToast(message) {
  let toast = document.getElementById("dashboard-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "dashboard-toast";
    toast.className = "fixed bottom-6 right-6 z-50 bg-primary-container text-white text-xs font-bold px-4 py-3 rounded-2xl shadow-2xl border border-white/20 flex items-center gap-2 translate-y-10 opacity-0 pointer-events-none";
    document.body.appendChild(toast);
  }
  // Clear any pending dismiss timer to prevent overlap bugs
  if (_toastTimer) clearTimeout(_toastTimer);
  // Remove exit class for fresh enter animation (300ms via CSS)
  toast.classList.remove("toast-exiting");
  toast.innerHTML = `<span class="material-symbols-outlined text-secondary-container text-base">check_circle</span> ${message}`;
  toast.classList.remove("translate-y-10", "opacity-0", "pointer-events-none");
  _toastTimer = setTimeout(() => {
    // Add exit class for faster dismiss (150ms via CSS)
    toast.classList.add("toast-exiting");
    toast.classList.add("translate-y-10", "opacity-0", "pointer-events-none");
    _toastTimer = null;
  }, 2500);
}

// ----------------------------------------------------
// Chart Card Action Buttons Injection
// ----------------------------------------------------
function setupChartCardActions() {
  document.querySelectorAll("canvas").forEach(canvas => {
    if (canvas.id.includes("explorer") || canvas.id.includes("toast")) return;
    const card = canvas.closest(".bg-white");
    if (!card || card.querySelector(".chart-actions-toolbar")) return;

    let header = card.querySelector(".chart-header-wrapper, .mb-3, .mb-4, .mb-6");
    if (!header) {
      const titles = card.querySelectorAll("h3, h4, p.text-lg, p.font-bold");
      if (titles.length > 0) {
        const wrapper = document.createElement("div");
        wrapper.className = "chart-header-wrapper mb-3 flex justify-between items-start gap-2";
        const titleContainer = document.createElement("div");
        titles.forEach(t => titleContainer.appendChild(t));
        wrapper.appendChild(titleContainer);
        card.insertBefore(wrapper, card.firstChild);
        header = wrapper;
      } else {
        header = card.firstElementChild;
      }
    }

    if (header) {
      header.classList.add("flex", "justify-between", "items-start", "gap-2");
      
      const toolbar = document.createElement("div");
      toolbar.className = "chart-actions-toolbar flex items-center gap-1 shrink-0 bg-surface p-1 rounded-xl border border-outline-variant/30";
      toolbar.innerHTML = `
        <button title="Copiar gráfico al portapapeles" class="btn-copy-chart p-1.5 rounded-lg hover:bg-surface-container text-outline hover:text-primary transition-colors flex items-center">
          <span class="material-symbols-outlined text-sm">content_copy</span>
        </button>
        <button title="Descargar como imagen PNG" class="btn-download-chart p-1.5 rounded-lg hover:bg-surface-container text-outline hover:text-primary transition-colors flex items-center">
          <span class="material-symbols-outlined text-sm">download</span>
        </button>
      `;

      toolbar.querySelector(".btn-copy-chart").addEventListener("click", () => exportChartWithContext(canvas.id, "copy"));
      toolbar.querySelector(".btn-download-chart").addEventListener("click", () => exportChartWithContext(canvas.id, "download"));
      header.appendChild(toolbar);
    }
  });
}



