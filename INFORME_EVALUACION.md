# Corrección — gualeee/proyecto-final-agentes-peron

## Puntaje por dimensión

| Dimensión | Nivel asignado | Puntos | Evidencia citada |
|---|---|---|---|
| Sistema completo y funcionando | Excelente | 30/30 | `prompts/system_prompt.md`, `app/hubspot_client.py` (API `POST /crm/v3/objects/tickets/search`), `corridas/corrida_1.md` y `DECISIONES.md` (marco L0–L4). |
| Proceso documentado | Excelente | 25/25 | `DECISIONES.md` (3 iteraciones con errores textuales de JSON y Few-Shot, más la falla real de timeout/fallback de red). |
| Formato y reproducibilidad | Excelente | 15/15 | `README.md`, `DECISIONES.md`, `prompts/` (system y user prompt) y `corridas/` (`corrida_1.md`, `corrida_2.md`, `corrida_3.md` con fecha y datos completos). |
| Análisis económico | Excelente | 15/15 | `DECISIONES.md` (tabla de tokens/costos de corridas 1, 2 y 3: $0.000325, $0.000311 y $0.000292 USD), proyección anual ($0.1128 USD/año) y justificación de Gemini Flash. |
| Gobierno y riesgo | Excelente | 15/15 | `DECISIONES.md` (permiso de lectura `tickets:read`, matriz de riesgos, mitigaciones, niveles L0–L4 y firma explicita de Walter Peron). |

## Puntaje total: 100/100

## Justificación por dimensión

**Sistema completo y funcionando:** El objetivo está definido claramente en `prompts/system_prompt.md` y los prompts incluyen contrato, restricciones y esquema JSON puro. Se utiliza un conector real con la API v3 de HubSpot (`app/hubspot_client.py`) verificado en las ejecuciones, las 3 corridas devuelven la salida estructurada oficial de 5 secciones y se formalizó la supervisión L0–L4 asignando firma profesional a Walter Peron.

**Proceso documentado:** En `DECISIONES.md` se detallan 3 iteraciones técnicas con fallas textuales de parseo (`JSONDecodeError`) y sugerencias genéricas iniciales. Además, reconoce de forma transparente la falla real de timeouts durante la integración con HubSpot y cómo se implementó un mecanismo de fallback técnico para evitar colapsos.

**Formato y reproducibilidad:** El repositorio mantiene de forma impecable la estructura solicitada (`README.md`, `prompts/system_prompt.md`, `prompts/user_prompt.md`, `DECISIONES.md` y la carpeta `corridas/`). Se aportan 3 corridas completas y fechadas (08/09, 09/09 y 10/09) con entradas crudas en JSON, respuestas estructuradas y métricas de inferencia.

**Análisis económico:** `DECISIONES.md` calcula el costo exacto por inferencia según tokens consumidos en cada corrida real (ej. Corrida 1: 2.210 in / 530 out = $0.000325 USD), elabora la proyección a escala anual ($0.1128 USD al año para auditorías diarias) y justifica la elección de Gemini 2.5 Flash aplicando estrictamente el principio del modelo más chico eficiente frente a opciones frontier.

**Gobierno y riesgo:** Se especifican las lecturas exclusivas sobre HubSpot CRM (`tickets:read`) e invalidez de permisos de escritura, junto con el tratamiento de PII. Se detallan 4 modos de falla técnicos (caídas de API, alucinaciones, prompt injection) con sus mitigaciones, la supervisión en nivel L2 y la firma de responsabilidad de Walter Peron.

## Señales de alerta

## Sugerencia concreta de mejora

Incorporar una rutina de validación sintáctica de esquemas (por ejemplo mediante `pydantic` o `jsonschema` en `app/gemini_agent.py`) antes de enviar la respuesta al dashboard, garantizando que si Gemini omite alguna clave esperada de las 5 secciones requeridas, el sistema fuerce un reintento automático (retry) en lugar de depender únicamente del formateo del cliente web.