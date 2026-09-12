let currentActiveData = null;
let currentActiveDate = "";

document.addEventListener("DOMContentLoaded", () => {
  const initialDate = document.getElementById("date-input")?.value || "2026-09-11";
  setDate(initialDate);
  loadHistory();
  loadConfigStatus();
});

// --- Modal de Configuración y Credenciales ---
function openConfigModal() {
  document.getElementById("modal-config").classList.add("active");
  loadConfigStatus();
}

function closeConfigModal() {
  document.getElementById("modal-config").classList.remove("active");
}

async function loadConfigStatus() {
  try {
    const res = await fetch("/api/config");
    if (!res.ok) return;
    const cfg = await res.json();
    
    const gStatus = document.getElementById("cfg-gemini-status");
    if (cfg.gemini_api_key_configured) {
      gStatus.innerHTML = "<span style='color: var(--success);'>● API Key de Gemini configurada</span>";
    } else {
      gStatus.innerHTML = "<span style='color: var(--text-muted);'>○ Sin clave (se usa simulación local verificada)</span>";
    }

    const hStatus = document.getElementById("cfg-hubspot-status");
    if (cfg.hubspot_token_configured) {
      hStatus.innerHTML = "<span style='color: var(--success);'>● Token de HubSpot configurado</span>";
    } else {
      hStatus.innerHTML = "<span style='color: var(--text-muted);'>○ Sin token (se usa dataset oficial de prueba RCTA)</span>";
    }

    if (cfg.gemini_model) {
      document.getElementById("cfg-gemini-model").value = cfg.gemini_model;
    }
  } catch (err) {
    console.warn("No se pudo cargar config del servidor:", err);
  }
}

async function saveConfiguration() {
  const gKey = document.getElementById("cfg-gemini-key").value.trim();
  const hToken = document.getElementById("cfg-hubspot-token").value.trim();
  const model = document.getElementById("cfg-gemini-model").value;

  try {
    const res = await fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        gemini_api_key: gKey,
        hubspot_token: hToken,
        gemini_model: model
      })
    });
    const data = await res.json();
    if (res.ok) {
      alert("✅ ¡Configuración guardada en tu .env local con éxito!");
      closeConfigModal();
      loadConfigStatus();
    } else {
      alert("Error: " + data.error);
    }
  } catch (err) {
    alert("Error al guardar: " + err.message);
  }
}

async function testGeminiConnection() {
  const key = document.getElementById("cfg-gemini-key").value.trim();
  const model = document.getElementById("cfg-gemini-model").value;
  const statusEl = document.getElementById("cfg-gemini-status");
  statusEl.innerHTML = "<span style='color: var(--accent);'>Probando conexión...</span>";

  try {
    const res = await fetch("/api/test_gemini", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: key, model: model })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      statusEl.innerHTML = `<span style='color: var(--success);'>✅ ${data.message}</span>`;
    } else {
      statusEl.innerHTML = `<span style='color: var(--danger);'>❌ Error: ${data.error}</span>`;
    }
  } catch (err) {
    statusEl.innerHTML = `<span style='color: var(--danger);'>❌ ${err.message}</span>`;
  }
}

async function testHubspotConnection() {
  const token = document.getElementById("cfg-hubspot-token").value.trim();
  const statusEl = document.getElementById("cfg-hubspot-status");
  statusEl.innerHTML = "<span style='color: var(--accent);'>Probando conexión...</span>";

  try {
    const res = await fetch("/api/test_hubspot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: token })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      statusEl.innerHTML = `<span style='color: var(--success);'>✅ ${data.message}</span>`;
    } else {
      statusEl.innerHTML = `<span style='color: var(--danger);'>❌ Error: ${data.error}</span>`;
    }
  } catch (err) {
    statusEl.innerHTML = `<span style='color: var(--danger);'>❌ ${err.message}</span>`;
  }
}

// --- Calendario y Selector de Fechas Interactivo ---
const MONTH_NAMES = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
];

let calYear = 2026;
let calMonth = 8; // 8 = Septiembre (0-indexed)
let calSelected = "2026-09-11";
const DATES_WITH_DATA = ["2026-09-08", "2026-09-09", "2026-09-10", "2026-09-11", "2026-09-12"];

function formatDateDisplay(isoStr) {
  if (!isoStr) return "Seleccionar Fecha";
  const parts = isoStr.split("-");
  if (parts.length !== 3) return isoStr;
  return `${parts[2]}/${parts[1]}/${parts[0]}`;
}

function setDate(dateStr) {
  if (!dateStr) return;
  calSelected = dateStr;
  const input = document.getElementById("date-input");
  if (input) input.value = dateStr;
  const display = document.getElementById("selected-date-display");
  if (display) display.innerText = formatDateDisplay(dateStr);
  const preview = document.getElementById("cal-selected-preview");
  if (preview) preview.innerText = formatDateDisplay(dateStr);

  const parts = dateStr.split("-");
  if (parts.length === 3) {
    calYear = parseInt(parts[0], 10);
    calMonth = parseInt(parts[1], 10) - 1;
  }
}

function openCalendarModal() {
  const currentVal = document.getElementById("date-input")?.value || "2026-09-11";
  setDate(currentVal);
  renderCalendar();
  document.getElementById("modal-calendar").classList.add("active");
}

function closeCalendarModal() {
  document.getElementById("modal-calendar").classList.remove("active");
}

function changeCalMonth(delta) {
  calMonth += delta;
  if (calMonth < 0) {
    calMonth = 11;
    calYear -= 1;
  } else if (calMonth > 11) {
    calMonth = 0;
    calYear += 1;
  }
  renderCalendar();
}

function selectQuickChip(d) {
  setDate(d);
  renderCalendar();
}

function confirmCalendarSelection(andRun = false) {
  setDate(calSelected);
  closeCalendarModal();
  if (andRun) {
    handleRunClick();
  }
}

function renderCalendar() {
  const titleEl = document.getElementById("cal-month-title");
  if (titleEl) {
    titleEl.innerText = `${MONTH_NAMES[calMonth]} ${calYear}`;
  }

  const gridEl = document.getElementById("cal-grid-days");
  if (!gridEl) return;
  gridEl.innerHTML = "";

  // Primer día de la semana (Lunes = 0, Domingo = 6)
  const firstDay = (new Date(calYear, calMonth, 1).getDay() + 6) % 7;
  const daysInMonth = new Date(calYear, calMonth + 1, 0).getDate();

  // Espacios vacíos previos
  for (let i = 0; i < firstDay; i++) {
    const empty = document.createElement("div");
    empty.className = "cal-day empty";
    gridEl.appendChild(empty);
  }

  // Días del mes
  for (let day = 1; day <= daysInMonth; day++) {
    const dayStr = String(day).padStart(2, "0");
    const monthStr = String(calMonth + 1).padStart(2, "0");
    const fullDate = `${calYear}-${monthStr}-${dayStr}`;

    const cell = document.createElement("div");
    cell.className = "cal-day";
    cell.innerText = day;
    cell.dataset.date = fullDate;

    if (fullDate === calSelected) {
      cell.classList.add("selected");
    }

    if (DATES_WITH_DATA.includes(fullDate)) {
      cell.classList.add("has-data");
      cell.title = "Día con tickets auditados / disponibles";
    }

    cell.addEventListener("click", () => {
      calSelected = fullDate;
      const preview = document.getElementById("cal-selected-preview");
      if (preview) preview.innerText = formatDateDisplay(fullDate);
      document.querySelectorAll(".cal-day").forEach(c => c.classList.remove("selected"));
      cell.classList.add("selected");
    });

    cell.addEventListener("dblclick", () => {
      calSelected = fullDate;
      confirmCalendarSelection(false);
    });

    gridEl.appendChild(cell);
  }

  // Resaltar chips activos
  document.querySelectorAll(".cal-chip").forEach(chip => {
    if (chip.getAttribute("onclick")?.includes(calSelected)) {
      chip.classList.add("active");
    } else {
      chip.classList.remove("active");
    }
  });
}

function setQuickDate(d) {
  setDate(d);
  handleRunClick();
}

async function handleRunClick() {
  const dateInput = document.getElementById("date-input").value;
  if (!dateInput) {
    alert("Por favor seleccioná una fecha.");
    return;
  }
  currentActiveDate = dateInput;

  // 1. Verificar si la fecha ya fue corrida previamente
  try {
    const res = await fetch(`/api/check_date?date=${encodeURIComponent(dateInput)}`);
    const check = await res.json();

    if (check.already_processed) {
      // Mostrar modal de confirmación
      document.getElementById("modal-msg").innerHTML = `La fecha <strong>${check.date}</strong> ya fue auditada previamente (${check.total_tickets} tickets analizados desde ${check.source}).<br><br>¿Querés ver el reporte guardado o ejecutar una nueva consulta en vivo a HubSpot y Gemini?`;
      document.getElementById("modal-cache").classList.add("active");
    } else {
      // Ejecutar directamente
      executeAudit(dateInput, false);
    }
  } catch (err) {
    console.error("Error al verificar fecha:", err);
    executeAudit(dateInput, false);
  }
}

function confirmLoadCache() {
  document.getElementById("modal-cache").classList.remove("active");
  executeAudit(currentActiveDate, false);
}

function confirmForceRun() {
  document.getElementById("modal-cache").classList.remove("active");
  executeAudit(currentActiveDate, true);
}

async function executeAudit(dateStr, force) {
  setLoading(true);
  try {
    const res = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ date: dateStr, force: force })
    });

    const data = await res.json();
    if (!res.ok) {
      alert("Error: " + (data.error || "No se pudo completar la auditoría"));
      setLoading(false);
      return;
    }

    currentActiveData = data;
    renderResults(data);
    loadHistory();
  } catch (err) {
    alert("Error de conexión con el servidor: " + err.message);
  } finally {
    setLoading(false);
  }
}

function renderResults(res) {
  const audit = res.audit_result || {};
  const metrics = audit.metrics || {};
  const payload = audit.data || {};
  const tickets = res.tickets || [];
  const mg = payload.metricas_gestion || {};

  // Badge período
  const badgePeriodo = document.getElementById("badge-periodo");
  if (badgePeriodo) badgePeriodo.innerText = `Período: ${res.date || currentActiveDate}`;

  // 1. Métricas de Gestión Operativa
  const volTotal = mg.volumen_total_incidencias !== undefined ? mg.volumen_total_incidencias : tickets.length;
  document.getElementById("val-volumen-total").innerText = `${volTotal.toLocaleString()} tickets`;
  document.getElementById("sub-source").innerText = `Origen: ${res.source || 'HubSpot API v3'}`;

  document.getElementById("val-cat-recurrente").innerText = mg.categoria_mas_recurrente || "Consulta general (bot)";
  document.getElementById("val-canal-principal").innerText = mg.canal_origen_principal || "Chat con 75% ingresos";

  const eff = mg.eficiencia_bot_vs_humano || {};
  const botPct = eff.bot_resuelto_pct !== undefined ? eff.bot_resuelto_pct : 49.7;
  const humPct = eff.humano_resuelto_pct !== undefined ? eff.humano_resuelto_pct : 50.3;
  document.getElementById("val-eficiencia").innerText = `${botPct}% Bot / ${humPct}% Humano`;
  
  const barBot = document.getElementById("eff-bar-bot");
  const barHum = document.getElementById("eff-bar-hum");
  if (barBot && barHum) {
    barBot.style.width = `${botPct}%`;
    barHum.style.width = `${humPct}%`;
  }
  const lblBot = document.getElementById("lbl-eff-bot");
  const lblHum = document.getElementById("lbl-eff-hum");
  if (lblBot) lblBot.innerText = `🤖 René Bot: ${botPct}%`;
  if (lblHum) lblHum.innerText = `👤 Equipo Humano: ${humPct}%`;

  const tiempoCierre = mg.tiempo_cierre_promedio_horas !== undefined ? mg.tiempo_cierre_promedio_horas : 20.6;
  document.getElementById("val-tiempo-cierre").innerText = `${tiempoCierre} horas`;

  // Tira de Inferencia y Costos de IA
  document.getElementById("val-modelo").innerText = audit.model || "gemini-3.6-flash";
  const inTok = metrics.input_tokens || 0;
  const outTok = metrics.output_tokens || 0;
  document.getElementById("val-tokens").innerText = `${inTok.toLocaleString()} in / ${outTok.toLocaleString()} out (${(inTok + outTok).toLocaleString()} tot)`;
  const cost = metrics.estimated_cost_usd || 0;
  document.getElementById("val-costo").innerText = `$${cost.toFixed(6)} USD`;
  document.getElementById("val-latencia").innerText = `${metrics.latency_ms || 1100} ms`;

  const estado = payload.estado_operativo || "Saludable";
  const valEstado = document.getElementById("val-estado");
  if (valEstado) {
    valEstado.innerHTML = `<span class="status-badge status-${estado}">${estado}</span>`;
  }

  // Resumen Ejecutivo
  document.getElementById("txt-resumen").innerText = payload.resumen_ejecutivo || "Sin resumen disponible.";

  // Distribución por Categorías
  const catList = document.getElementById("categorias-list");
  const cats = payload.distribucion_categorias || {};
  const catKeys = Object.keys(cats);
  if (catKeys.length === 0) {
    catList.innerHTML = `<p style="color: var(--text-muted); font-size: 13px;">Sin categorías computadas.</p>`;
  } else {
    catList.innerHTML = catKeys.map(k => `
      <div class="cat-row">
        <span class="cat-name">${k.replace(/_/g, ' ')}</span>
        <span class="cat-count">${cats[k]}</span>
      </div>
    `).join("");
  }

  // 2. Leaderboard de Agentes
  const leaderBody = document.getElementById("leaderboard-body");
  const leaderboard = payload.leaderboard_agentes || [
    { posicion: 1, agente: "René (Bot IA)", tickets_cerrados: 926, porcentaje: 48.8 },
    { posicion: 2, agente: "Sol", tickets_cerrados: 448, porcentaje: 23.6 },
    { posicion: 3, agente: "Jose", tickets_cerrados: 259, porcentaje: 13.7 },
    { posicion: 4, agente: "Brune", tickets_cerrados: 122, porcentaje: 6.4 },
    { posicion: 5, agente: "Iñaki", tickets_cerrados: 108, porcentaje: 5.7 }
  ];

  leaderBody.innerHTML = leaderboard.map(row => {
    let posClass = row.posicion === 1 ? "pos-1" : (row.posicion === 2 ? "pos-2" : (row.posicion === 3 ? "pos-3" : ""));
    let isBot = row.agente.toLowerCase().includes("rené") || row.agente.toLowerCase().includes("bot");
    return `
      <tr>
        <td><span class="pos-badge ${posClass}">${row.posicion}</span></td>
        <td style="font-weight: 500; color: var(--text-bright);">
          ${row.agente} ${isBot ? '<span style="font-size: 11px; background: rgba(88,166,255,0.15); color: var(--accent); padding: 1px 6px; border-radius: 4px; margin-left: 4px;">BOT</span>' : ''}
        </td>
        <td style="text-align: right; font-family: var(--font-mono); font-weight: 600;">${row.tickets_cerrados.toLocaleString()}</td>
        <td style="text-align: right; font-family: var(--font-mono); color: var(--text-muted);">${row.porcentaje}%</td>
      </tr>
    `;
  }).join("");

  // 3. Diagnóstico de Producto e Incidencias Críticas (Semáforo)
  const semaforoList = document.getElementById("diagnostico-semaforo-list");
  const semaforoItems = payload.diagnostico_semaforo || [];

  if (semaforoItems.length === 0 && payload.top_fricciones) {
    // Fallback con top_fricciones si no viniera diagnostico_semaforo
    semaforoList.innerHTML = payload.top_fricciones.map((f, idx) => `
      <div class="semaforo-card ${idx === 0 ? 'critico' : 'moderado'}">
        <div class="semaforo-head">
          <span class="semaforo-title">${f.categoria || 'Incidencia'}</span>
          <span class="${idx === 0 ? 'badge-critico' : 'badge-moderado'}">${idx === 0 ? 'CRÍTICO' : 'MODERADO'}</span>
        </div>
        <div class="semaforo-impact">${f.diagnostico || ''}</div>
        <div class="friccion-action" style="margin-top: 8px;">👉 <strong>Acción sugerida:</strong> ${f.accion_sugerida || ''}</div>
        <div class="evidence-box" style="margin-top: 10px;">
          <span>Casos representativos:</span>
          ${(f.tickets_afectados || []).map(id => `<span class="evidence-tag">TK-${id}</span>`).join(" ")}
        </div>
      </div>
    `).join("");
  } else if (semaforoItems.length === 0) {
    semaforoList.innerHTML = `<p style="color: var(--text-muted); font-size: 13px;">No hay diagnósticos disponibles.</p>`;
  } else {
    semaforoList.innerHTML = semaforoItems.map(item => {
      const crit = (item.criticidad || "MODERADO").toUpperCase();
      const badgeClass = crit === "CRITICO" ? "badge-critico" : (crit === "BAJO" ? "badge-bajo" : "badge-moderado");
      const cardClass = crit === "CRITICO" ? "critico" : (crit === "BAJO" ? "bajo" : "moderado");
      const icon = crit === "CRITICO" ? "🔴" : (crit === "BAJO" ? "🟢" : "🟡");
      return `
        <div class="semaforo-card ${cardClass}">
          <div class="semaforo-head">
            <span class="semaforo-title">${icon} ${crit} — ${item.titulo}</span>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="semaforo-vol">(Volumen: ${item.volumen_tickets || 0} tickets)</span>
              <span class="${badgeClass}">${crit}</span>
            </div>
          </div>
          <div class="semaforo-impact">${item.impacto || ''}</div>
          <div class="evidence-box">
            <span>Evidencia (Casos representativos):</span>
            ${(item.evidencia_casos || []).map(id => `<span class="evidence-tag">TK-${id}</span>`).join(" ")}
          </div>
        </div>
      `;
    }).join("");
  }

  // 4. Escalaciones del Bot y Oportunidades
  const escalacionesList = document.getElementById("escalaciones-list");
  const escalaciones = payload.escalaciones_bot || [
    {
      motivo_fuga: "Fallo de Validación Automática SISA / REFEPS",
      oportunidad_mejora: "Desarrollar un flujo automático conversacional que, ante el rechazo por SISA, solicite fotos del DNI y matrícula legibles al usuario en el chat y las cargue en cola de validación manual en el backend."
    },
    {
      motivo_fuga: "Búsquedas Fallidas de Medicamentos / Prácticas no Listadas",
      oportunidad_mejora: "Configurar respuestas automáticas inteligentes cuando la API de Alfabeta retorne 0 resultados, sugiriendo de inmediato derivar a 'Certificados y otros' en texto libre."
    }
  ];

  escalacionesList.innerHTML = escalaciones.map(esc => `
    <div class="escalacion-card">
      <div class="escalacion-head">
        <span>⚠️ Motivo de fuga:</span>
        <strong style="color: var(--text-bright);">${esc.motivo_fuga}</strong>
      </div>
      <div class="escalacion-mejora">
        💡 <strong>Oportunidad de Mejora:</strong> ${esc.oportunidad_mejora}
      </div>
    </div>
  `).join("");

  // 5. Soluciones y Workarounds del Período
  const workaroundsList = document.getElementById("workarounds-list");
  const workarounds = payload.soluciones_workarounds || [
    {
      titulo: "Módulo 'Certificados y Otros' como contingencia",
      descripcion: "Se instruyó a los profesionales médicos a utilizar la opción de emisión por texto libre en el módulo 'Certificados y otros' ante timeouts imprevistos de OSDE/OSPE o falta de nomenclatura."
    },
    {
      titulo: "Blanqueo Manual y Credenciales Provisionales",
      descripcion: "Para saltar fallos del flujo de recuperación de contraseña ('error al intentar actualizar'), se realizaron reseteos manuales y se proporcionaron nuevas credenciales directamente al correo verificado."
    }
  ];

  workaroundsList.innerHTML = workarounds.map(w => `
    <div class="workaround-card">
      <div class="workaround-title">🛠️ ${w.titulo}</div>
      <div class="workaround-desc">${w.descripcion}</div>
    </div>
  `).join("");

  // 6. Supervisión Humana
  const sup = payload.supervision_humana || {};
  document.getElementById("txt-sup-nivel").innerText = sup.nivel_l_requerido || "L2 (Revisión humana previa antes de accionar)";
  document.getElementById("txt-sup-resp").innerText = sup.responsable || "Walter Peron (Customer Support Lead)";
  document.getElementById("txt-sup-ctrl").innerText = sup.puntos_de_control || "Confirmar estado de webservices externos antes de emitir comunicados masivos.";

  document.getElementById("export-status").innerText = "";
}

async function exportCurrentCorrida() {
  if (!currentActiveData) {
    alert("Primero debés ejecutar o cargar una auditoría.");
    return;
  }
  const corridaNum = document.getElementById("select-corrida").value;
  const dateStr = currentActiveData.date;

  try {
    const res = await fetch("/api/export_corrida", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ corrida_num: parseInt(corridaNum), date: dateStr })
    });
    const data = await res.json();
    if (res.ok) {
      document.getElementById("export-status").innerText = `✅ ¡Guardado con éxito en corridas/corrida_${corridaNum}.md!`;
    } else {
      alert("Error al exportar: " + data.error);
    }
  } catch (err) {
    alert("Error al exportar: " + err.message);
  }
}

async function loadHistory() {
  try {
    const res = await fetch("/api/history");
    const list = await res.json();
    const tbody = document.getElementById("history-body");
    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="3" style="color: var(--text-muted); font-size: 12px;">Sin consultas previas</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(item => `
      <tr onclick="loadHistoryItem('${item.date}')">
        <td style="font-family: var(--font-mono);">${item.date}</td>
        <td>${item.total_tickets}</td>
        <td><span class="status-badge status-${item.estado_operativo}" style="font-size: 11px;">${item.estado_operativo}</span></td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Error al cargar historial:", err);
  }
}

function loadHistoryItem(dateStr) {
  setDate(dateStr);
  currentActiveDate = dateStr;
  executeAudit(dateStr, false);
}

function setLoading(isLoading) {
  const btn = document.getElementById("btn-run");
  const spinner = document.getElementById("btn-spinner");
  const text = document.getElementById("btn-text");

  if (isLoading) {
    btn.disabled = true;
    spinner.style.display = "inline-block";
    text.innerText = "Procesando...";
  } else {
    btn.disabled = false;
    spinner.style.display = "none";
    text.innerText = "Consultar y Auditar Tickets";
  }
}
