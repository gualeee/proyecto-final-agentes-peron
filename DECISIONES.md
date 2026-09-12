# DECISIONES.md — Bitácora de Construcción, Gobierno y Análisis Económico

**Proyecto:** Auditor Agéntico de Tickets Diarios (HubSpot + Gemini)  
**Autor:** Walter Peron  
**Materia:** Programación de y con Agentes de IA — MBA UCEMA 2026 2T  

---

## 1. Historia del Proceso e Iteraciones Técnicas

El objetivo fue construir un sistema que permita a un equipo de Customer Success y Operaciones auditar el volumen diario de tickets en HubSpot CRM, categorizar fricciones operativas y emitir recomendaciones de acción sin intervención manual en la extracción, pero con control humano antes de ejecutar cualquier cambio.

### Iteración 1 · El problema de la salida verborrágica y el parsing JSON
* **Qué se probó:** En la primera versión del System Prompt se le pedía al modelo analizar los tickets y devolver un informe ejecutivo junto con un JSON de categorías.
* **Qué falló textualmente:** El modelo devolvía texto explicativo antes y después del bloque JSON, incluyendo frases conversacionales:
  > *"A continuación presento el análisis de los tickets del día. Observo que hubo varias fallas en firma digital..."*
  
  Al intentar procesar la respuesta con `json.loads(response.text)`, el backend arrojaba:
  `json.decoder.JSONDecodeError: Extra data: line 1 column 1 (char 0)`
* **Qué se cambió:** 
  1. Se agregó una restricción explícita en el contrato (`prompts/system_prompt.md`): *"PROHIBICIÓN ESTRICTA: Tu única salida debe ser el JSON parseable. No incluyas saludos, introducciones ni explicaciones fuera del bloque JSON."*
  2. Se configuró en la API de Gemini el parámetro de salida forzada `responseMimeType: "application/json"`.
  3. Se incorporó en `app/gemini_agent.py` una rutina de limpieza de bloques markdown (````json ... ````) como defensa en profundidad.

### Iteración 2 · Acciones recomendadas abstractas y diagnósticos genéricos
* **Qué se probó:** Con el formato JSON estabilizado, se evaluó la calidad operativa de las sugerencias en `top_fricciones`.
* **Qué falló:** El agente tendía a sugerir recomendaciones genéricas e inviables en el día a día, como:
  > *"Mejorar la capacitación del personal de soporte técnico y realizar reuniones con los médicos para explicarles el sistema."*
  
  Esto violaba el principio de acción operativa inmediata y no resolvía el cuello de botella técnico del día (ej. caída de servicio o rechazos de matrícula).
* **Qué se cambió:**
  1. Se ajustó la regla de `accion_sugerida` en el System Prompt: *"Cada sugerencia de acción debe ser hiper-específica, de máximo 20 palabras y redactada en modo imperativo orientada a la acción técnica u operativa inmediata."*
  2. Se incorporó un ejemplo Few-Shot representativo en el prompt para guiar el tono y nivel de detalle requerido.
  3. A partir de esta modificación, el agente devolvió acciones concretas como: *"Reiniciar nodos del microservicio de firma y monitorear latencia de respuestas con infraestructura."*

### Iteración 3 · Alineación con el Reporte Oficial Corporativo de Operaciones y Soporte (RCTA)
* **Qué se probó:** Presentar los resultados en una lista plana de tickets categorizados con recomendaciones generales.
* **Qué falló:** La estructura no reflejaba la metodología real con la que la gerencia y el equipo de operaciones analizan la performance del servicio (donde conviven un bot autónomo "René" y un equipo humano de agentes). Faltaban métricas de eficiencia comparativa, ranking de resolución (Leaderboard), categorización estricta por semáforo de criticidad (🔴/🟡/🟢) y diagnóstico de los motivos de fuga (escalaciones del bot) con sus respectivos workarounds documentados.
* **Qué se cambió:**
  1. Se rediseñó el contrato JSON (`prompts/system_prompt.md`) y el modelo de datos para estructurar el output en 5 pilares operativos oficiales:
     - **Métricas de Gestión Operativa:** Total incidencias, categoría más recurrente, canal principal, split de eficiencia Bot René vs. Humanos y tiempo promedio de cierre.
     - **Leaderboard de Agentes:** Ranking de tickets cerrados con medallas y desglose por tipo (bot vs humano).
     - **Diagnóstico de Producto e Incidencias Críticas (Semáforo):** Agrupación por Rojo (Crítico), Amarillo (Moderado) y Verde (Bajo) con impacto y tags de IDs de HubSpot.
     - **Análisis de Escalaciones del Bot y Oportunidades de Mejora:** Identificación de motivos de fuga de René Bot y soluciones automatizables en el flujo.
     - **Soluciones y Workarounds del Período:** Procedimientos de contingencia documentados para destrabar la operación.
  2. Se rediseñó completamente la interfaz en `dashboard_directo.html` y en `app/static/` para visualizar estas 5 secciones con diseño ejecutivo, tarjetas de semáforo con bordes distintivos, barra visual de distribución bot/humano y badges de evidencia.
  3. Se alimentaron los datasets verificados con los datos reales del reporte semanal de RCTA (tickets `48264175697`, `48180653917`, etc.).

### Falla real reconocida con honestidad
Durante las pruebas de integración con la API de búsqueda de HubSpot (`/crm/v3/objects/tickets/search`), se observó que cuando una fecha no contenía tickets o cuando la red corporativa bloqueaba las llamadas salientes hacia `api.hubapi.com`, la aplicación web quedaba colgada esperando el timeout del socket sin darle feedback al usuario. 
Para resolverlo honestamente, se implementó un timeout estricto de 15 segundos en `requests`, un bloque `try/except` que captura errores de red y un mecanismo de fallback que ofrece datos verificados de prueba para que el sistema nunca colapse en silencio.

---

## 2. Análisis Económico de Inferencia

### Métricas de las Corridas Reales del Repositorio
Se utilizó como motor `gemini-2.5-flash`. Los costos oficiales de Google AI Studio son:
* **Entrada:** \$0.075 USD por cada 1.000.000 de tokens (\$0.000000075 / token).
* **Salida:** \$0.30 USD por cada 1.000.000 de tokens (\$0.00000030 / token).

| Corrida | Fecha | Tickets | Tokens Entrada | Tokens Salida | Tokens Totales | Costo Unitario (USD) |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **Corrida 1** | 2026-09-08 | 5 | 2.210 | 530 | 2.740 | **\$0.000325** |
| **Corrida 2** | 2026-09-09 | 4 | 2.102 | 511 | 2.613 | **\$0.000311** |
| **Corrida 3** | 2026-09-10 | 3 | 2.011 | 469 | 2.480 | **\$0.000292** |
| **Promedio** | — | **4** | **2.108** | **503** | **2.611** | **\$0.000309** |

### Proyección de Costos a Escala Operativa
Considerando una auditoría diaria automatizada al cierre de cada jornada operativa:
* **Costo diario (1 corrida/día):** \$0.000309 USD.
* **Costo semanal (7 corridas):** \$0.002163 USD.
* **Costo mensual (30 corridas):** \$0.009270 USD (menos de 1 centavo de dólar por mes).
* **Costo anual (365 corridas):** **\$0.1128 USD al año** (~11 centavos de dólar al año).

Incluso en un escenario de **alta intensidad** donde el agente se ejecute cada 2 horas (12 corridas diarias) para triage en tiempo real:
* **Costo mensual intensivo:** \$0.111 USD/mes.
* **Costo anual intensivo:** \$1.35 USD/año.

### Justificación de Elección de Modelo
Se seleccionó **Gemini 2.5 Flash** aplicando el criterio fundacional de la materia: *"el modelo más chico que hace bien la tarea"*.
* **Comparación con modelos Frontier (Claude 3.5 Sonnet / GPT-4o / Opus):** Un modelo de frontera cuesta entre \$3.00 y \$15.00 por millón de tokens de entrada (entre 40x y 200x más caro). Dado que la tarea del agente es de extracción, formateo estructurado y clasificación bajo una rúbrica explícita, los modelos frontier introducen sobrecosto y mayor latencia sin aportar una mejora perceptible en la calidad de categorización.
* Gemini Flash resuelve el análisis completo con latencias inferiores a 1.2 segundos y garantiza el cumplimiento del esquema JSON a una fracción microscópica de costo.

---

## 3. Gobierno, Riesgo y Supervisión Humana

### 1. Sistemas y Datos Tocados
* **HubSpot CRM:** Acceso al objeto `tickets` mediante token de App Privada.
* **Permisos otorgados:** Principio de mínimo privilegio: únicamente permiso de lectura (`tickets:read`). El agente **no tiene credenciales de escritura, modificación ni borrado** en el CRM.
* **Políticas de Privacidad y PII:** Los tickets médicos pueden contener nombres de pacientes o referencias clínicas. El System Prompt prohíbe explícitamente citar datos personales; el agente opera exclusivamente sobre el ID de ticket y la descripción funcional del problema.

### 2. Modos de Falla y Mitigaciones
| Riesgo / Falla Posible | Impacto | Mitigación Implementada |
|---|---|---|
| **Caída de API de HubSpot (429/500)** | Alto | Timeout de 15s y mensaje explicativo en UI sin cierre inesperado del servicio. |
| **Alucinación de tickets no existentes** | Crítico | Regla de Grounding Observable en System Prompt: prohibido inventar IDs o citas no respaldadas por el payload. |
| **Inyección de Prompt en Tickets** | Medio | Los datos del ticket se inyectan en el User Prompt delimitados por bloques JSON puros y tipados; el System Prompt fija reglas de prioridad inmutables. |
| **Falso positivo de estado 'Crítico'** | Medio | Revisión humana obligatoria antes de activar protocolos de emergencia. |

### 3. Niveles de Supervisión Humana (Marco L0–L4 de la materia)
* **Nivel L0 (Automatización Total):** Extracción de tickets desde HubSpot, cálculo de tokens y renderizado de métricas en el dashboard.
* **Nivel L1 (Notificación Informativa):** Publicación del informe en el historial y alerta de estado (`Saludable` / `Alerta`).
* **Nivel L2 (Supervisión Humana Previa - Nivel Operativo Principal):** El analista de Customer Support revisa el diagnóstico y el Top 3 de fricciones antes de tomar cualquier decisión de contacto con clientes o crear incidentes en Jira.
* **Nivel L3 / L4 (Aprobación Requerida / Ejecución Manual Asistida):** Ningún comunicado a médicos, cancelación masiva o reclamo a proveedores de firma digital puede ser disparado automáticamente por el agente. Requiere autorización humana explícita.

### 4. Responsabilidad y Firma Profesional
> *"La responsabilidad profesional por el output de un agente nunca se delega. El humano firma."*

* **Firmante Responsable:** **Walter Peron** (Customer Support Lead / Responsable de Operaciones).
* **Declaración:** Cada reporte generado es auditado por el firmante para verificar que los incidentes señalados tengan correspondencia con los registros del sistema antes de su comunicación a los equipos de desarrollo.
