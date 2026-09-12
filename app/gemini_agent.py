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
    model = model or os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
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

        # Estimación de tokens para modo simulación (1 token ~ 3.5 caracteres en español)
        approx_in_tokens = int((len(system_prompt_text) + len(user_prompt_text)) / 3.5)
        approx_out_tokens = 540
        cost = calculate_cost(approx_in_tokens, approx_out_tokens)

        # Calcular leaderboard determinístico según el lote
        agente_counts = {}
        canal_counts = {}
        bot_count = 0
        duraciones = []

        for t in tickets:
            ag = t.get("agente", "Otro / Sin Asignar")
            agente_counts[ag] = agente_counts.get(ag, 0) + 1
            can = t.get("origen", "Chat")
            canal_counts[can] = canal_counts.get(can, 0) + 1
            if "René" in ag or t.get("tipo_resolucion") == "Bot / IA":
                bot_count += 1
            if t.get("time_to_close_hs"):
                duraciones.append(float(t["time_to_close_hs"]))

        tot = max(len(tickets), 1)
        sorted_agentes = sorted(agente_counts.items(), key=lambda x: x[1], reverse=True)
        leaderboard = [
            {
                "posicion": idx + 1,
                "agente": ag,
                "tickets_cerrados": cnt,
                "porcentaje": round((cnt / tot) * 100, 1)
            }
            for idx, (ag, cnt) in enumerate(sorted_agentes)
        ]

        bot_pct = round((bot_count / tot) * 100, 1)
        hum_pct = round(100.0 - bot_pct, 1)
        canal_top = max(canal_counts.items(), key=lambda x: x[1])[0] if canal_counts else "Chat"
        canal_top_cnt = canal_counts.get(canal_top, 0)
        avg_close = round(sum(duraciones) / len(duraciones), 1) if duraciones else 1.2

        simulated_data = {
            "fecha_analisis": date_str,
            "total_tickets": len(tickets),
            "estado_operativo": "Crítico" if any(t.get("priority") == "HIGH" and "firma" in t.get("subject", "").lower() for t in tickets) else ("Alerta" if any(t.get("priority") == "HIGH" for t in tickets) else "Saludable"),
            "resumen_ejecutivo": f"Para el período {date_str} se procesaron {len(tickets)} incidencias en RCTA. La resolución automática de René Bot alcanzó el {bot_pct}%, derivando al equipo humano los casos de mayor complejidad técnica y validaciones federadas.",
            "metricas_gestion": {
                "volumen_total_incidencias": len(tickets),
                "categoria_mas_recurrente": "Emisión / Firma de Recetas (60% casos)" if any("firma" in t.get("subject", "").lower() for t in tickets) else "Consulta General / Soporte",
                "canal_origen_principal": f"{canal_top} con {canal_top_cnt} ingresos ({round((canal_top_cnt/tot)*100, 1)}%)",
                "eficiencia_bot_vs_humano": {
                    "bot_resuelto_pct": bot_pct,
                    "humano_resuelto_pct": hum_pct
                },
                "tiempo_cierre_promedio_horas": avg_close
            },
            "leaderboard_agentes": leaderboard or [
                {"posicion": 1, "agente": "René (Bot IA)", "tickets_cerrados": bot_count, "porcentaje": bot_pct},
                {"posicion": 2, "agente": "Equipo Humano", "tickets_cerrados": tot - bot_count, "porcentaje": hum_pct}
            ],
            "diagnostico_semaforo": [
                {
                    "criticidad": "CRITICO",
                    "titulo": "Caída de Servicio e Inestabilidad en Microservicio de Firma Digital",
                    "volumen_tickets": sum(1 for t in tickets if "firma" in t.get("subject", "").lower() or "504" in t.get("subject", "").lower()),
                    "impacto": "Bloqueo de la emisión y firma de recetas médicas en paso 3. Latencias críticas en webservices externos y validadores farmacéuticos.",
                    "evidencia_casos": [t["id"] for t in tickets if "firma" in t.get("subject", "").lower() or "504" in t.get("subject", "").lower()][:4] or [tickets[0]["id"]] if tickets else []
                },
                {
                    "criticidad": "MODERADO",
                    "titulo": "Fricción en Onboarding y Validación de Matrículas (SISA / REFEPS)",
                    "volumen_tickets": sum(1 for t in tickets if "matrícula" in t.get("subject", "").lower() or "dni" in t.get("subject", "").lower()),
                    "impacto": "Demoras superiores al SLA de 48hs por desfase en la base de datos nacional de prestadores y rechazo de fotos de DNI en formato JPG.",
                    "evidencia_casos": [t["id"] for t in tickets if "matrícula" in t.get("subject", "").lower() or "dni" in t.get("subject", "").lower()][:4]
                },
                {
                    "criticidad": "BAJO",
                    "titulo": "Consultas Operativas de Autogestión y Soporte de Cuenta",
                    "volumen_tickets": sum(1 for t in tickets if "factura" in t.get("subject", "").lower() or "consulta" in t.get("subject", "").lower() or t.get("priority") == "LOW"),
                    "impacto": "Consultas informativas sobre actualización de CUIT, reseteo de claves y navegación en el recetario.",
                    "evidencia_casos": [t["id"] for t in tickets if "factura" in t.get("subject", "").lower() or "consulta" in t.get("subject", "").lower()][:4]
                }
            ],
            "escalaciones_bot": [
                {
                    "motivo_fuga": "Fallo de Validación Automática SISA / REFEPS",
                    "oportunidad_mejora": "Desarrollar un flujo conversacional que solicite foto legible de credencial y DNI para encolar validación en segundo plano sin transferir en frío al humano."
                },
                {
                    "motivo_fuga": "Búsquedas Fallidas de Medicamentos / Prácticas no Listadas",
                    "oportunidad_mejora": "Configurar respuesta automática inteligente cuando la API de Alfabeta retorne 0 resultados, derivando al módulo de texto libre 'Certificados y otros'."
                }
            ],
            "soluciones_workarounds": [
                {
                    "titulo": "Módulo 'Certificados y Otros' como contingencia",
                    "descripcion": "Se instruyó a los profesionales médicos a utilizar prescripción en texto libre ante timeouts de webservices de OSDE/OSPE."
                },
                {
                    "titulo": "Blanqueo Manual y Credenciales Provisionales",
                    "descripcion": "Reseteo directo de cuentas y envío de claves temporales para sortear errores del flujo web de recuperación."
                }
            ],
            "distribucion_categorias": {
                "Emision_Firma_Recetas": sum(1 for t in tickets if "firma" in t.get("subject", "").lower() or "504" in t.get("subject", "")),
                "Friccion_Onboarding": sum(1 for t in tickets if "matrícula" in t.get("subject", "").lower() or "dni" in t.get("subject", "").lower()),
                "Consulta_General": sum(1 for t in tickets if "consulta" in t.get("subject", "").lower() or "factura" in t.get("subject", "").lower())
            },
            "supervision_humana": {
                "nivel_l_requerido": "L2 (Revisión humana previa antes de accionar)",
                "responsable": "Customer Support Lead (Walter Peron)",
                "puntos_de_control": "Confirmar estado de nodos de firma digital con DevOps antes de emitir notificación masiva a prestadores."
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
