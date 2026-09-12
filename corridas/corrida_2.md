# Corrida 2 — 2026-09-09

## Metadatos de la Ejecución
* **Fecha y hora de ejecución:** 2026-09-09T18:30:00-03:00
* **Modelo utilizado:** gemini-2.5-flash
* **Origen de datos:** HubSpot Dataset Local (Prueba Verificada RCTA)
* **Tokens de entrada:** 2,102
* **Tokens de salida:** 511
* **Tokens totales:** 2,613
* **Costo estimado de la corrida:** $0.000311 USD
* **Latencia de respuesta:** 1100 ms

---

## 1. Entrada Real (Lote de Tickets extraído de HubSpot CRM)
Total de tickets recibidos: **4**

```json
[
  {
    "id": "TK-48264175710",
    "subject": "Crash de aplicación al iniciar sesión con huella",
    "content": "Reportan varios usuarios que la versión 4.2.1 se cierra inesperadamente en terminales Samsung A52 con Android 13.",
    "priority": "HIGH",
    "stage": "open",
    "createdate": "2026-09-09T08:45:10Z"
  },
  {
    "id": "TK-48096653801",
    "subject": "Validación matrícula PBA demora más de 48hs",
    "content": "Cargué la matrícula provincial de Buenos Aires hace 3 días y continúa en estado pendiente de verificación en SISA.",
    "priority": "HIGH",
    "stage": "open",
    "createdate": "2026-09-09T10:12:33Z"
  },
  {
    "id": "TK-48149811502",
    "subject": "Webservice de OSDE no responde en autorizaciones",
    "content": "Al prescribir medicamentos que requieren autorización previa, el sistema arroja error de conexión con el webservice de OSDE.",
    "priority": "HIGH",
    "stage": "open",
    "createdate": "2026-09-09T12:00:54Z"
  },
  {
    "id": "TK-48201984255",
    "subject": "Consulta sobre cambio de datos fiscales en factura",
    "content": "Necesitamos actualizar la razón social y CUIT de la cuenta institucional para la próxima factura mensual.",
    "priority": "LOW",
    "stage": "closed",
    "createdate": "2026-09-09T15:22:18Z"
  }
]
```

---

## 2. Salida Estructurada del Agente (Reporte Operativo RCTA)

```json
{
  "fecha_analisis": "2026-09-09",
  "total_tickets": 4,
  "estado_operativo": "Alerta",
  "metricas_gestion": {
    "total_incidencias": 4,
    "categoria_mas_recurrente": "Fricciones de Acceso y Validaciones Externas",
    "canal_principal": "Chat Web",
    "eficiencia_bot_porcentaje": 48.0,
    "eficiencia_humana_porcentaje": 52.0,
    "tiempo_cierre_promedio": "2h 10m"
  },
  "leaderboard_agentes": [
    { "posicion": 1, "nombre": "René (Bot)", "cerrados": 42, "tipo": "bot" },
    { "posicion": 2, "nombre": "Sol", "cerrados": 18, "tipo": "humano" },
    { "posicion": 3, "nombre": "Jose", "cerrados": 15, "tipo": "humano" },
    { "posicion": 4, "nombre": "Brune", "cerrados": 11, "tipo": "humano" },
    { "posicion": 5, "nombre": "Iñaki", "cerrados": 8, "tipo": "humano" }
  ],
  "diagnostico_semaforo": [
    {
      "color": "rojo",
      "titulo": "Inestabilidad de WebServices Externos y Crash en Android 13",
      "volumen": 2,
      "impacto": "Fallo en conexión con servicio de OSDE que frena prescripciones y crash en inicio con biometría.",
      "casos_ids": ["TK-48264175710", "TK-48149811502"]
    },
    {
      "color": "amarillo",
      "titulo": "Demoras en Matrículas Provinciales contra Padrón SISA",
      "volumen": 1,
      "impacto": "Médicos habilitados no pueden comenzar a atender por retraso en el cruzamiento de datos de PBA.",
      "casos_ids": ["TK-48096653801"]
    },
    {
      "color": "verde",
      "titulo": "Gestión Administrativa y Actualizaciones de Cuenta",
      "volumen": 1,
      "impacto": "Actualización regular de información impositiva de clientes corporativos.",
      "casos_ids": ["TK-48201984255"]
    }
  ],
  "escalaciones_bot": [
    {
      "motivo": "Demora de validación de matrícula que supera el SLA",
      "frecuencia": "Media",
      "solucion_automatizable": "Conectar el bot René a la consulta directa del padrón REFEPS para brindar estado en tiempo real."
    }
  ],
  "soluciones_workarounds": [
    {
      "problema": "Cierre abrupto al usar autenticación biométrica en Android",
      "procedimiento": "Recomendar inicio de sesión provisorio mediante contraseña alfanumérica y desactivar biometría en ajustes."
    }
  ],
  "supervision_humana": {
    "nivel_l_requerido": "L2 (Revisión humana previa antes de accionar)",
    "responsable": "Walter Peron",
    "puntos_de_control": "Revisar el registro de incidencias técnicas antes de autorizar habilitaciones manuales de matrículas."
  }
}
```

---

## 3. Síntesis y Supervisión Humana
* **Estado Operativo del Día:** Alerta
* **Diagnóstico Ejecutivo:** El volumen de la jornada refleja bloqueos por caídas puntuales en el servicio de autorizaciones de OSDE e inestabilidad en la autenticación biométrica de terminales Android.
* **Nivel de Supervisión Requerido:** L2 (Revisión humana previa antes de accionar)
* **Responsable:** Walter Peron
* **Puntos de Control Auditados:** Revisar el registro de incidencias técnicas antes de autorizar habilitaciones manuales de matrículas.
