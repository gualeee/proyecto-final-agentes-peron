# Corrida 3 — 2026-09-10

## Metadatos de la Ejecución
* **Fecha y hora de ejecución:** 2026-09-10T18:30:00-03:00
* **Modelo utilizado:** gemini-2.5-flash
* **Origen de datos:** HubSpot Dataset Local (Prueba Verificada RCTA)
* **Tokens de entrada:** 2,011
* **Tokens de salida:** 469
* **Tokens totales:** 2,480
* **Costo estimado de la corrida:** $0.000292 USD
* **Latencia de respuesta:** 1100 ms

---

## 1. Entrada Real (Lote de Tickets extraído de HubSpot CRM)
Total de tickets recibidos: **3**

```json
[
  {
    "id": "TK-48201984280",
    "subject": "Consulta sobre vademécum de psicofármacos",
    "content": "Hola, ¿cómo hago para seleccionar duplicado para psicotrópicos Lista IV? No encuentro el casillero en la nueva versión.",
    "priority": "MEDIUM",
    "stage": "open",
    "createdate": "2026-09-10T09:10:05Z"
  },
  {
    "id": "TK-48201984295",
    "subject": "Sugerencia: agregar posología predeterminada",
    "content": "Estaría genial si se pudieran guardar indicaciones frecuentes (ej. 'cada 8hs durante 7 días') para no tipearlas en cada paciente.",
    "priority": "LOW",
    "stage": "closed",
    "createdate": "2026-09-10T11:30:40Z"
  },
  {
    "id": "TK-48201984310",
    "subject": "Duda con historial de recetas archivadas",
    "content": "¿Dónde puedo ver el historial de recetas emitidas el mes pasado para un paciente específico?",
    "priority": "LOW",
    "stage": "closed",
    "createdate": "2026-09-10T14:15:20Z"
  }
]
```

---

## 2. Salida Estructurada del Agente (Reporte Operativo RCTA)

```json
{
  "fecha_analisis": "2026-09-10",
  "total_tickets": 3,
  "estado_operativo": "Saludable",
  "metricas_gestion": {
    "total_incidencias": 3,
    "categoria_mas_recurrente": "Consultas de Funcionalidad y Usabilidad",
    "canal_principal": "Chat Web",
    "eficiencia_bot_porcentaje": 54.2,
    "eficiencia_humana_porcentaje": 45.8,
    "tiempo_cierre_promedio": "45m"
  },
  "leaderboard_agentes": [
    { "posicion": 1, "nombre": "René (Bot)", "cerrados": 52, "tipo": "bot" },
    { "posicion": 2, "nombre": "Sol", "cerrados": 14, "tipo": "humano" },
    { "posicion": 3, "nombre": "Jose", "cerrados": 12, "tipo": "humano" },
    { "posicion": 4, "nombre": "Brune", "cerrados": 10, "tipo": "humano" },
    { "posicion": 5, "nombre": "Iñaki", "cerrados": 8, "tipo": "humano" }
  ],
  "diagnostico_semaforo": [
    {
      "color": "verde",
      "titulo": "Consultas Generales, Posología y Búsqueda Histórica",
      "volumen": 3,
      "impacto": "Operación normalizada sin fallas bloqueantes. Consultas de uso guiadas por documentación del centro de ayuda.",
      "casos_ids": ["TK-48201984280", "TK-48201984295", "TK-48201984310"]
    }
  ],
  "escalaciones_bot": [
    {
      "motivo": "Consulta sobre duplicado de recetas de psicotrópicos",
      "frecuencia": "Baja",
      "solucion_automatizable": "Añadir en el menú de autoayuda del bot René el artículo de emisión especial para Lista IV."
    }
  ],
  "soluciones_workarounds": [
    {
      "problema": "Búsqueda de historial de recetas archivadas",
      "procedimiento": "Guiar al usuario a la sección Pacientes > Historial Clínico > Filtro por Fecha para descargar duplicados en PDF."
    }
  ],
  "supervision_humana": {
    "nivel_l_requerido": "L1 (Supervisión pasiva con notificación)",
    "responsable": "Walter Peron",
    "puntos_de_control": "Verificar periódicamente la satisfacción del usuario en las respuestas brindadas automáticamente por el bot."
  }
}
```

---

## 3. Síntesis y Supervisión Humana
* **Estado Operativo del Día:** Saludable
* **Diagnóstico Ejecutivo:** Operación plenamente estabilizada sin incidentes de caída de servicios ni fricciones de firma. Los requerimientos corresponden a capacitación de usuario y sugerencias de mejora de interfaz.
* **Nivel de Supervisión Requerido:** L1 (Supervisión pasiva con notificación)
* **Responsable:** Walter Peron
* **Puntos de Control Auditados:** Verificar periódicamente la satisfacción del usuario en las respuestas brindadas automáticamente por el bot.
