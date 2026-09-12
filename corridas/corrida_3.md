# Corrida 3 — 2026-09-09

## Metadatos de la Ejecución
* **Fecha y hora de ejecución:** 2026-09-09T18:30:00-03:00
* **Modelo utilizado:** `gemini-2.5-flash (Simulado - Modo Local)`
* **Origen de datos:** HubSpot Dataset Local (Prueba Verificada RCTA)
* **Tokens de entrada:** 2102
* **Tokens de salida:** 511
* **Tokens totales:** 2613
* **Costo estimado de la corrida:** $0.000311 USD
* **Latencia de respuesta:** 1100 ms

---

## 1. Entrada Real (Lote de Tickets extraído de HubSpot CRM)
Total de tickets recibidos: **4**

```json
[
  {
    "id": "TK-20901",
    "subject": "Demora en validación de matrícula provincial",
    "content": "Cargué mis fotos de matrícula de PBA hace 72 horas y sigo en estado 'En revisión'. Tengo pacientes esperando prescripción hoy mismo.",
    "priority": "HIGH",
    "stage": "open",
    "createdate": "2026-09-09T08:45:10Z"
  },
  {
    "id": "TK-20904",
    "subject": "No puedo subir foto del DNI",
    "content": "La app me rechaza la foto del reverso del DNI diciendo 'formato no soportado', pero es un JPG estándar sacado con el celular.",
    "priority": "MEDIUM",
    "stage": "open",
    "createdate": "2026-09-09T10:12:33Z"
  },
  {
    "id": "TK-20908",
    "subject": "Médico nuevo no puede configurar membrete",
    "content": "Intento subir el logo del sanatorio para que salga en el encabezado de la receta y queda cortado.",
    "priority": "LOW",
    "stage": "in_progress",
    "createdate": "2026-09-09T12:00:54Z"
  },
  {
    "id": "TK-20912",
    "subject": "Validación matrícula bloqueada",
    "content": "Mi matrícula nacional vence en 2028 pero el validador automático me dice 'Matrícula no encontrada en SISA'.",
    "priority": "HIGH",
    "stage": "open",
    "createdate": "2026-09-09T15:22:18Z"
  }
]
```

---

## 2. Salida Estructurada del Agente (Diagnóstico, Triage y Acciones)

```json
{
  "fecha_analisis": "2026-09-09",
  "total_tickets": 4,
  "estado_operativo": "Alerta",
  "resumen_ejecutivo": "El 75% de los tickets ingresados corresponden a fricciones en el embudo de onboarding de nuevos profesionales. Se detectan cuellos de botella en la validación contra SISA y rechazos de formato en la carga de documentación.",
  "distribucion_categorias": {
    "Friccion_Onboarding": 3,
    "Soporte_Tecnico_UI": 1
  },
  "top_fricciones": [
    {
      "prioridad": 1,
      "categoria": "Fricción Onboarding / Validación Matrícula",
      "tickets_afectados": [
        "TK-20901",
        "TK-20912"
      ],
      "diagnostico": "Demora que supera el SLA de 48hs y fallo de sincronización con padrón SISA nacional.",
      "accion_sugerida": "Realizar validación manual de matrículas PBA en el registro del colegio médico."
    },
    {
      "prioridad": 2,
      "categoria": "Fricción Onboarding / Documentación",
      "tickets_afectados": [
        "TK-20904"
      ],
      "diagnostico": "Parser de imágenes rechaza archivos JPG estándar tomados con cámaras de smartphones modernos.",
      "accion_sugerida": "Ajustar validación de mime-type en formulario de carga para aceptar formatos JPG y HEIC."
    },
    {
      "prioridad": 3,
      "categoria": "Soporte Técnico UI",
      "tickets_afectados": [
        "TK-20908"
      ],
      "diagnostico": "Problema de maquetado en recorte de membrete para recetas institucionales.",
      "accion_sugerida": "Enviar guía de dimensiones recomendadas y reportar bug de recorte a diseño UI."
    }
  ],
  "alertas_inmediatas": [
    "Médicos con pacientes agendados frenados en etapa de onboarding (TK-20901, TK-20912)."
  ],
  "supervision_humana": {
    "nivel_l_requerido": "L2 (Revisión humana previa antes de accionar)",
    "responsable": "Customer Support Lead",
    "puntos_de_control": "Revisar antecedentes de matrículas en el portal provincial antes de otorgar aprobación excepcional."
  }
}
```

---

## 3. Síntesis y Supervisión Humana
* **Estado Operativo del Día:** `Alerta`
* **Diagnóstico Ejecutivo:** El 75% de los tickets ingresados corresponden a fricciones en el embudo de onboarding de nuevos profesionales. Se detectan cuellos de botella en la validación contra SISA y rechazos de formato en la carga de documentación.
* **Nivel de Supervisión Requerido:** `L2 (Revisión humana previa antes de accionar)`
* **Responsable:** Customer Support Lead
* **Puntos de Control Auditados:** Revisar antecedentes de matrículas en el portal provincial antes de otorgar aprobación excepcional.
