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


@app.route("/api/config", methods=["GET", "POST"])
def manage_config():
    env_path = os.path.join(BASE_DIR, ".env")
    if request.method == "GET":
        # Devolver estado sin exponer claves completas
        g_key = os.getenv("GEMINI_API_KEY", "")
        h_token = os.getenv("HUBSPOT_ACCESS_TOKEN", "")
        n8n_url = os.getenv("N8N_WEBHOOK_URL", "")
        model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
        return jsonify({
            "gemini_api_key_configured": bool(g_key and g_key != "tu_api_key_gemini_aqui"),
            "hubspot_token_configured": bool(h_token and h_token != "tu_token_privado_hubspot_aqui"),
            "n8n_webhook_url": n8n_url if n8n_url != "http://localhost:5678/webhook/tickets" else "",
            "gemini_model": model
        })

    # Guardar en .env local
    data = request.get_json() or {}
    g_key = data.get("gemini_api_key", "").strip()
    h_token = data.get("hubspot_token", "").strip()
    n8n_url = data.get("n8n_url", "").strip()
    model = data.get("gemini_model", "gemini-3.6-flash").strip()

    # Actualizar os.environ en memoria
    if g_key:
        os.environ["GEMINI_API_KEY"] = g_key
    if h_token:
        os.environ["HUBSPOT_ACCESS_TOKEN"] = h_token
    if n8n_url:
        os.environ["N8N_WEBHOOK_URL"] = n8n_url
    if model:
        os.environ["GEMINI_MODEL"] = model

    # Escribir en .env (ignorado por git)
    env_content = f"""# Variables de Entorno Locales (NUNCA subir a GitHub)
GEMINI_API_KEY={os.environ.get('GEMINI_API_KEY', '')}
HUBSPOT_ACCESS_TOKEN={os.environ.get('HUBSPOT_ACCESS_TOKEN', '')}
N8N_WEBHOOK_URL={os.environ.get('N8N_WEBHOOK_URL', '')}
GEMINI_MODEL={os.environ.get('GEMINI_MODEL', 'gemini-3.6-flash')}
PORT={os.environ.get('PORT', 8000)}
"""
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(env_content)

    return jsonify({"success": True, "message": "Configuración guardada localmente en .env con éxito."})


@app.route("/api/test_gemini", methods=["POST"])
def test_gemini():
    import requests, time
    data = request.get_json() or {}
    key = data.get("api_key", "").strip() or os.getenv("GEMINI_API_KEY", "")
    model = data.get("model", "gemini-3.6-flash").strip()

    if not key or key == "tu_api_key_gemini_aqui":
        return jsonify({"success": False, "error": "No se ingresó ninguna clave de Gemini"}), 400

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": "Responde únicamente 'OK'"}]}]
    }

    t0 = time.time()
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        ms = int((time.time() - t0) * 1000)
        if r.status_code == 200:
            return jsonify({"success": True, "message": f"Conexión exitosa con {model} ({ms} ms)", "latency_ms": ms})
        else:
            return jsonify({"success": False, "error": f"Error {r.status_code}: {r.text}"}), r.status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/test_hubspot", methods=["POST"])
def test_hubspot():
    import requests, time
    data = request.get_json() or {}
    token = data.get("token", "").strip() or os.getenv("HUBSPOT_ACCESS_TOKEN", "")

    if not token or token == "tu_token_privado_hubspot_aqui":
        return jsonify({"success": False, "error": "No se ingresó token de HubSpot"}), 400

    url = "https://api.hubapi.com/crm/v3/objects/tickets?limit=1"
    headers = {"Authorization": f"Bearer {token}"}

    t0 = time.time()
    try:
        r = requests.get(url, headers=headers, timeout=10)
        ms = int((time.time() - t0) * 1000)
        if r.status_code == 200:
            res_data = r.json()
            return jsonify({
                "success": True,
                "message": f"Conexión exitosa con HubSpot API ({ms} ms)",
                "total_tickets": res_data.get("total", 1),
                "latency_ms": ms
            })
        else:
            return jsonify({"success": False, "error": f"Error HubSpot {r.status_code}: {r.text}"}), r.status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/test_n8n", methods=["POST"])
def test_n8n():
    import requests, time
    data = request.get_json() or {}
    webhook_url = data.get("url", "").strip() or os.getenv("N8N_WEBHOOK_URL", "")

    if not webhook_url:
        return jsonify({"success": False, "error": "No se ingresó URL de webhook de n8n"}), 400

    t0 = time.time()
    try:
        # Ping de prueba
        r = requests.get(webhook_url, params={"date": "2026-09-08", "test": "ping"}, timeout=10)
        ms = int((time.time() - t0) * 1000)
        return jsonify({
            "success": True,
            "status_code": r.status_code,
            "message": f"Webhook n8n respondió con código HTTP {r.status_code} ({ms} ms)"
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Error conectando a n8n: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Iniciando servidor web en http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
