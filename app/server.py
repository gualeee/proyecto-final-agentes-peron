"""
Servidor Web Flask local para el Sistema Agéntico de Tickets (HubSpot + Gemini).
Permite seleccionar fechas, consultar HubSpot, procesar con Gemini,
gestionar historial de consultas y exportar corridas oficiales.
"""

import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
import sys
sys.path.insert(0, os.path.dirname(__file__))
from hubspot_client import get_tickets_for_date
from gemini_agent import run_ticket_audit

app = Flask(__name__, static_folder="static")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
CORRIDAS_DIR = os.path.join(BASE_DIR, "corridas")
CACHE_FILE = os.path.join(DATA_DIR, "cache_history.json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CORRIDAS_DIR, exist_ok=True)


def load_history() -> dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_history(history: dict):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)


@app.route("/api/check_date", methods=["GET"])
def check_date():
    """Verifica si una fecha ya fue auditada previamente"""
    date_str = request.args.get("date", "")
    if not date_str:
        return jsonify({"error": "Parámetro date es requerido"}), 400

    history = load_history()
    if date_str in history:
        item = history[date_str]
        return jsonify({
            "already_processed": True,
            "date": date_str,
            "last_execution": item.get("timestamp"),
            "source": item.get("source"),
            "total_tickets": item.get("total_tickets"),
            "saved_data": item.get("audit_result", {}).get("data", {})
        })

    return jsonify({"already_processed": False, "date": date_str})


@app.route("/api/run", methods=["POST"])
def run_audit():
    """Ejecuta la extracción de tickets en HubSpot y el análisis agéntico con Gemini"""
    payload = request.get_json() or {}
    date_str = payload.get("date", "")
    force = payload.get("force", False)

    if not date_str:
        return jsonify({"error": "Fecha requerida (AAAA-MM-DD)"}), 400

    history = load_history()

    # Si ya existe y no se forzó re-ejecución, devolver de cache
    if date_str in history and not force:
        cached = history[date_str]
        return jsonify({
            "from_cache": True,
            "date": date_str,
            "timestamp": cached.get("timestamp"),
            "source": cached.get("source"),
            "tickets": cached.get("tickets", []),
            "audit_result": cached.get("audit_result", {})
        })

    # 1. Extracción conector HubSpot / n8n / dataset
    try:
        tickets_resp = get_tickets_for_date(date_str)
        tickets = tickets_resp.get("tickets", [])
        source = tickets_resp.get("source", "Desconocido")
    except Exception as e:
        return jsonify({"error": f"Error al extraer tickets de HubSpot: {str(e)}"}), 500

    if not tickets:
        return jsonify({
            "success": False,
            "message": f"No se encontraron tickets en HubSpot para la fecha {date_str}."
        }), 404

    # 2. Análisis con Gemini Agent
    try:
        audit_result = run_ticket_audit(date_str, tickets)
    except Exception as e:
        return jsonify({"error": f"Error en la ejecución de Gemini: {str(e)}"}), 500

    # 3. Guardar en historial local
    execution_record = {
        "date": date_str,
        "timestamp": datetime.now().isoformat(),
        "source": source,
        "total_tickets": len(tickets),
        "tickets": tickets,
        "audit_result": audit_result
    }
    history[date_str] = execution_record
    save_history(history)

    return jsonify({
        "from_cache": False,
        "date": date_str,
        "timestamp": execution_record["timestamp"],
        "source": source,
        "tickets": tickets,
        "audit_result": audit_result
    })


@app.route("/api/history", methods=["GET"])
def get_history():
    """Devuelve la lista resumida del historial de corridas"""
    history = load_history()
    summary = []
    for d, item in history.items():
        summary.append({
            "date": d,
            "timestamp": item.get("timestamp"),
            "source": item.get("source"),
            "total_tickets": item.get("total_tickets"),
            "estado_operativo": item.get("audit_result", {}).get("data", {}).get("estado_operativo", "N/A"),
            "cost_usd": item.get("audit_result", {}).get("metrics", {}).get("estimated_cost_usd", 0)
        })
    # Ordenar por fecha descendente
    summary.sort(key=lambda x: x["date"], reverse=True)
    return jsonify(summary)


@app.route("/api/export_corrida", methods=["POST"])
def export_corrida():
    """Exporta el resultado de una corrida al formato estricto de corridas/corrida_X.md"""
    payload = request.get_json() or {}
    corrida_num = payload.get("corrida_num", 1)
    date_str = payload.get("date", "")

    history = load_history()
    record = history.get(date_str)
    if not record:
        return jsonify({"error": f"No hay datos guardados para la fecha {date_str}"}), 404

    tickets = record.get("tickets", [])
    audit_result = record.get("audit_result", {})
    metrics = audit_result.get("metrics", {})
    data = audit_result.get("data", {})
    timestamp = record.get("timestamp", datetime.now().isoformat())
    source = record.get("source", "HubSpot CRM")
    model = audit_result.get("model", "gemini-2.5-flash")

    # Armar archivo Markdown de corrida conforme a la consigna y rúbrica
    content = f"""# Corrida {corrida_num} — {date_str}

## Metadatos de la Ejecución
* **Fecha y hora de ejecución:** {timestamp}
* **Modelo utilizado:** `{model}`
* **Origen de datos:** {source}
* **Tokens de entrada:** {metrics.get('input_tokens', 0)}
* **Tokens de salida:** {metrics.get('output_tokens', 0)}
* **Tokens totales:** {metrics.get('total_tokens', 0)}
* **Costo estimado de la corrida:** ${metrics.get('estimated_cost_usd', 0):.6f} USD
* **Latencia de respuesta:** {metrics.get('latency_ms', 0)} ms

---

## 1. Entrada Real (Lote de Tickets extraído de HubSpot CRM)
Total de tickets recibidos: **{len(tickets)}**

```json
{json.dumps(tickets, indent=2, ensure_ascii=False)}
```

---

## 2. Salida Estructurada del Agente (Diagnóstico, Triage y Acciones)

```json
{json.dumps(data, indent=2, ensure_ascii=False)}
```

---

## 3. Síntesis y Supervisión Humana
* **Estado Operativo del Día:** `{data.get('estado_operativo', 'N/A')}`
* **Diagnóstico Ejecutivo:** {data.get('resumen_ejecutivo', 'N/A')}
* **Nivel de Supervisión Requerido:** `{data.get('supervision_humana', {}).get('nivel_l_requerido', 'L2')}`
* **Responsable:** {data.get('supervision_humana', {}).get('responsable', 'Customer Support Lead')}
* **Puntos de Control Auditados:** {data.get('supervision_humana', {}).get('puntos_de_control', 'Verificación manual de incidencias críticas.')}
"""

    file_path = os.path.join(CORRIDAS_DIR, f"corrida_{corrida_num}.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return jsonify({
        "success": True,
        "file_path": file_path,
        "corrida_num": corrida_num,
        "date": date_str
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Iniciando servidor web en http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
