let currentActiveData = null;
let currentActiveDate = "";

document.addEventListener("DOMContentLoaded", () => {
  loadHistory();
});

function setQuickDate(d) {
  document.getElementById("date-input").value = d;
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

  // 1. Métricas
  const estado = payload.estado_operativo || "N/A";
  const valEstado = document.getElementById("val-estado");
  valEstado.innerHTML = `<span class="status-badge status-${estado}">${estado}</span>`;
  document.getElementById("sub-estado").innerText = res.from_cache ? "Recuperado de histórico" : "Ejecutado en vivo";

  document.getElementById("val-tickets").innerText = tickets.length;
  document.getElementById("sub-source").innerText = `Origen: ${res.source || 'HubSpot'}`;

  const inTok = metrics.input_tokens || 0;
  const outTok = metrics.output_tokens || 0;
  document.getElementById("val-tokens").innerText = (inTok + outTok).toLocaleString();
  document.getElementById("sub-tokens").innerText = `In: ${inTok.toLocaleString()} · Out: ${outTok.toLocaleString()}`;

  const cost = metrics.estimated_cost_usd || 0;
  document.getElementById("val-costo").innerText = `$${cost.toFixed(6)}`;
  document.getElementById("sub-model").innerText = `Modelo: ${audit.model || 'Gemini Flash'}`;

  // 2. Resumen ejecutivo
  document.getElementById("txt-resumen").innerText = payload.resumen_ejecutivo || "Sin resumen disponible.";

  // 3. Top Fricciones
  const friccionesList = document.getElementById("fricciones-list");
  const fricciones = payload.top_fricciones || [];
  if (fricciones.length === 0) {
    friccionesList.innerHTML = `<p style="color: var(--text-muted); font-size: 13px;">No se identificaron fricciones críticas en este lote.</p>`;
  } else {
    friccionesList.innerHTML = fricciones.map((f, idx) => `
      <div class="friccion-item prio-${f.prioridad || (idx+1)}">
        <div class="friccion-head">
          <span class="friccion-title">${f.prioridad ? '#' + f.prioridad + ' · ' : ''}${f.categoria || 'Incidencia'}</span>
          <span class="friccion-tickets">${(f.tickets_afectados || []).join(", ")}</span>
        </div>
        <p class="friccion-diag">${f.diagnostico || ''}</p>
        <div class="friccion-action">👉 <strong>Acción sugerida:</strong> ${f.accion_sugerida || ''}</div>
      </div>
    `).join("");
  }

  // 4. Categorías
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

  // 5. Alertas
  const alertList = document.getElementById("alertas-list");
  const alertas = payload.alertas_inmediatas || [];
  if (alertas.length === 0) {
    alertList.innerHTML = `<p style="color: var(--text-muted); font-size: 13px;">No hay alertas inmediatas.</p>`;
  } else {
    alertList.innerHTML = alertas.map(a => `<div class="alert-tag">🚨 ${a}</div>`).join("");
  }

  // 6. Supervisión Humana
  const sup = payload.supervision_humana || {};
  document.getElementById("txt-sup-nivel").innerText = sup.nivel_l_requerido || "L2";
  document.getElementById("txt-sup-resp").innerText = sup.responsable || "Customer Support Lead";
  document.getElementById("txt-sup-ctrl").innerText = sup.puntos_de_control || "Auditoría de tickets críticos";

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
  document.getElementById("date-input").value = dateStr;
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
