# Corrida 3 — 2026-09-10

## Metadatos de la Ejecución
* **Fecha y hora de ejecución:** 2026-09-10T18:30:00-03:00
* **Modelo utilizado:** gemini-2.5-flash
* **Origen de datos:** HubSpot Dataset Local (Prueba Verificada RCTA)
* **Tokens de entrada:** 2,011
* **Tokens de salida:** 469
* **Tokens totales:** 2,480
* **Costo estimado de la corrida:**  USD
* **Latencia de respuesta:** 1100 ms

---

## 1. Entrada Real (Lote de Tickets extraído de HubSpot CRM)
Total de tickets recibidos: **3**

`json
[
  {
    "id": "TK-21001",
    "subject": "Consulta sobre vademécum de psicofármacos",
    "content": "Hola, ¿cómo hago para seleccionar duplicado para psicotrópicos Lista IV? No encuentro el casillero en la nueva versión.",
    "priority": "MEDIUM",
    "stage": "open",
    "createdate": "2026-09-10T09:10:05Z"
  },
  {
    "id": "TK-21005",
    "subject": "Sugerencia: agregar posología predeterminada",
    "content": "Estaría genial si se pudieran guardar indicaciones frecuentes (ej. 'cada 8hs durante 7 días') para no tipearlas en cada paciente.",
    "priority": "LOW",
    "stage": "closed",
    "createdate": "2026-09-10T11:30:40Z"
  },
  {
    "id": "TK-21010",
    "subject": "Duda con receta archivada",
    "content": "¿Dónde puedo ver el historial de recetas emitidas el mes pasado para un paciente específico?",
    "priority": "LOW",
    "stage": "closed",
    "createdate": "2026-09-10T14:15:20Z"
  }
]
`

---

## 2. Salida Estructurada del Agente (Diagnóstico, Triage y Acciones)

`json
{
  "fecha_analisis": "2026-09-10",
  "total_tickets": 3,
  "estado_operativo": "Saludable",
  "resumen_ejecutivo": "Operación estable sin incidencias bloqueantes ni errores de sistema. Los 3 tickets corresponden a consultas de usabilidad sobre psicofármacos, archivo histórico y sugerencias de producto.",
  "distribucion_categorias": {
    "Consulta_General": 2,
    "Feedback_Producto": 1
  },
  "top_fricciones": [
    {
      "prioridad": 1,
      "categoria": "Consulta General / Vademécum",
      "tickets_afectados": [
        "TK-21001"
      ],
      "diagnostico": "Dudas de navegación en la nueva interfaz para prescripción duplicada de psicofármacos.",
      "accion_sugerida": "Responder con el artículo del centro de ayuda sobre emisión de psicotrópicos Lista IV."
    },
    {
      "prioridad": 2,
      "categoria": "Feedback Producto / Features",
      "tickets_afectados": [
        "TK-21005"
      ],
      "diagnostico": "Solicitud de plantillas de posología recurrente para reducir tiempo de prescripción.",
      "accion_sugerida": "Registrar requerimiento en Jira Product Discovery para priorización en el próximo sprint."
    },
    {
      "prioridad": 3,
      "categoria": "Consulta General / Historial",
      "tickets_afectados": [
        "TK-21010"
      ],
      "diagnostico": "Orientación sobre filtros de fecha en el módulo de recetas archivadas.",
      "accion_sugerida": "Indicar al usuario cómo acceder a la pestaña de auditoría histórica en su perfil."
    }
  ],
  "alertas_inmediatas": [],
  "supervision_humana": {
    "nivel_l_requerido": "L1 (Supervisión pasiva con notificación)",
    "responsable": "Customer Support Representative",
    "puntos_de_control": "Verificar que las respuestas automáticas a consultas generales hayan dejado satisfecho al médico."
  }
}
`

---

## 3. Síntesis y Supervisión Humana
* **Estado Operativo del Día:** Saludable
* **Diagnóstico Ejecutivo:** Operación estable sin incidencias bloqueantes ni errores de sistema. Los 3 tickets corresponden a consultas de usabilidad sobre psicofármacos, archivo histórico y sugerencias de producto.
* **Nivel de Supervisión Requerido:** L1 (Supervisión pasiva con notificación)
* **Responsable:** Customer Support Representative
* **Puntos de Control Auditados:** Verificar que las respuestas automáticas a consultas generales hayan dejado satisfecho al médico.
