"""
Módulo de ejecución agéntica con Google Gemini.
Aplica el contrato estricto de prompts/system_prompt.md y prompts/user_prompt.md.
Mide tokens reales (input/output), calcula el costo económico exacto y valida el JSON.
"""

import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# Precios oficiales de Gemini 2.5 / 1.5 Flash (por millón de tokens)
# Input: $0.075 / 1M ($0.000000075 por token)
# Output: $0.30 / 1M ($0.00000030 por token)
COST_PER_INPUT_TOKEN = 0.075 / 1_000_000
COST_PER_OUTPUT_TOKEN = 0.30 / 1_000_000

PROMPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "prompts"))


def load_prompt_templates():
    """Carga los templates del contrato agéntico desde prompts/"""
    sys_path = os.path.join(PROMPTS_DIR, "system_prompt.md")
    usr_path = os.path.join(PROMPTS_DIR, "user_prompt.md")

    with open(sys_path, "r", encoding="utf-8") as f:
        system_prompt = f.read()

    with open(usr_path, "r", encoding="utf-8") as f:
        user_prompt = f.read()

    return system_prompt, user_prompt


def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """Calcula el costo económico en USD de la inferencia"""
    return (input_tokens * COST_PER_INPUT_TOKEN) + (output_tokens * COST_PER_OUTPUT_TOKEN)


def run_ticket_audit(date_str: str, tickets: list, model: str = None) -> dict:
    """
    Ejecuta el agente evaluador de tickets con Gemini.
    Devuelve la respuesta estructurada, los tokens medidos y los costos.
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    system_prompt_text, user_prompt_template = load_prompt_templates()

    # Inyección en el User Prompt
    user_prompt_text = user_prompt_template.replace("{{FECHA_CONSULTA}}", date_str)
    user_prompt_text = user_prompt_text.replace("{{TOTAL_TICKETS}}", str(len(tickets)))
    user_prompt_text = user_prompt_text.replace("{{TICKETS_PAYLOAD_JSON}}", json.dumps(tickets, indent=2, ensure_ascii=False))

    start_time = time.time()

    # Si no hay API key configurada, generar respuesta de simulación realista basada en el lote
    if not api_key or api_key == "tu_api_key_gemini_aqui":
        print("[Gemini Agent] Sin API key configurada. Generando análisis simulado estructurado.")
        time.sleep(1.2)  # Simular latencia de red
        latency_ms = int((time.time() - start_time) * 1000)

        # Estimación aproximada de tokens para modo simulación (1 token ~ 3.5 caracteres en español)
        approx_in_tokens = int((len(system_prompt_text) + len(user_prompt_text)) / 3.5)
        approx_out_tokens = 380
        cost = calculate_cost(approx_in_tokens, approx_out_tokens)

        simulated_data = {
            "fecha_analisis": date_str,
            "total_tickets": len(tickets),
            "estado_operativo": "Alerta" if any(t.get("priority") == "HIGH" for t in tickets) else "Saludable",
            "resumen_ejecutivo": f"Para el día {date_str} se procesaron {len(tickets)} tickets. Se observa concentración de casos de soporte en emisión y validación de usuarios con necesidad de atención operativa.",
            "distribucion_categorias": {
                "Emision_Firma_Recetas": sum(1 for t in tickets if "firma" in t.get("subject", "").lower() or "504" in t.get("subject", "")),
                "Friccion_Onboarding": sum(1 for t in tickets if "matrícula" in t.get("subject", "").lower() or "dni" in t.get("subject", "").lower()),
                "Consulta_General": sum(1 for t in tickets if "consulta" in t.get("subject", "").lower() or "posología" in t.get("subject", "").lower())
            },
            "top_fricciones": [
                {
                    "prioridad": 1,
                    "categoria": "Operaciones / Triage",
                    "tickets_afectados": [t["id"] for t in tickets[:2]],
                    "diagnostico": "Tickets con prioridad alta que requieren resolución antes de comprometer el servicio al paciente.",
                    "accion_sugerida": "Contactar a los médicos afectados y reasignar a guardia técnica inmediata."
                }
            ],
            "alertas_inmediatas": [
                f"Ticket {tickets[0]['id']} requiere seguimiento prioritario por severidad declarada."
            ] if tickets else [],
            "supervision_humana": {
                "nivel_l_requerido": "L2 (Revisión humana previa antes de accionar)",
                "responsable": "Customer Support Lead",
                "puntos_de_control": "Auditar si la causa raíz reportada en los tickets críticos afecta a más usuarios concurrentes."
            }
        }

        return {
            "success": True,
            "data": simulated_data,
            "raw_text": json.dumps(simulated_data, indent=2, ensure_ascii=False),
            "model": f"{model} (Simulado - Modo Local)",
            "metrics": {
                "input_tokens": approx_in_tokens,
                "output_tokens": approx_out_tokens,
                "total_tokens": approx_in_tokens + approx_out_tokens,
                "estimated_cost_usd": round(cost, 6),
                "latency_ms": latency_ms
            },
            "system_prompt_used": system_prompt_text,
            "user_prompt_used": user_prompt_text
        }

    # Llamada real a Gemini API
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "system_instruction": {
            "parts": [{"text": system_prompt_text}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_prompt_text}]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,  # Temperatura baja para consistencia y rigor evaluativo
            "responseMimeType": "application/json"
        }
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    latency_ms = int((time.time() - start_time) * 1000)

    if resp.status_code != 200:
        raise RuntimeError(f"Error de Gemini API ({resp.status_code}): {resp.text}")

    resp_json = resp.json()

    # Extraer texto generado
    candidates = resp_json.get("candidates", [])
    if not candidates:
        raise RuntimeError(f"Gemini no devolvió candidatos: {resp_json}")

    raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")

    # Limpiar posibles delimitadores de markdown si existieran
    cleaned_text = raw_text.strip()
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:]
    elif cleaned_text.startswith("```"):
        cleaned_text = cleaned_text[3:]
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]
    cleaned_text = cleaned_text.strip()

    parsed_data = json.loads(cleaned_text)

    # Extraer métricas oficiales de tokens
    usage = resp_json.get("usageMetadata", {})
    input_tokens = usage.get("promptTokenCount", 0)
    output_tokens = usage.get("candidatesTokenCount", 0)
    total_tokens = usage.get("totalTokenCount", input_tokens + output_tokens)
    cost = calculate_cost(input_tokens, output_tokens)

    return {
        "success": True,
        "data": parsed_data,
        "raw_text": raw_text,
        "model": model,
        "metrics": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(cost, 6),
            "latency_ms": latency_ms
        },
        "system_prompt_used": system_prompt_text,
        "user_prompt_used": user_prompt_text
    }
