# Corrida 1 — 2026-09-08

## Metadatos de la Ejecución
* **Fecha y hora de ejecución:** 2026-09-08T18:30:00-03:00
* **Modelo utilizado:** gemini-2.5-flash
* **Origen de datos:** HubSpot Dataset Local (Prueba Verificada RCTA)
* **Tokens de entrada:** 2,210
* **Tokens de salida:** 530
* **Tokens totales:** 2,740
* **Costo estimado de la corrida:** $0.000325 USD
* **Latencia de respuesta:** 1350 ms

---

## 1. Entrada Real (Lote de Tickets extraído de HubSpot CRM)
Total de tickets recibidos: **5**

```json
[
  {
    "id": "TK-48264175697",
    "subject": "Firma digital trabada en paso 3 y timeout OSDE",
    "content": "Estimados, estoy en consultorio intentando emitir recetas para pacientes crónicos. Al poner la clave de firma digital el sistema queda con la rueda girando en paso 3 y luego tira timeout con OSDE. No emite nada.",
    "priority": "HIGH",
    "stage": "open",
    "createdate": "2026-09-08T09:15:22Z"
  },
  {
    "id": "TK-48180653917",
    "subject": "App crash al abrir crypto token en Moto G60s",
    "content": "La aplicación médica se cierra súbitamente al querer validar la receta con el mensaje 'IllegalBlockSizeException' en teléfonos Motorola Android 12.",
    "priority": "HIGH",
    "stage": "open",
    "createdate": "2026-09-08T10:30:11Z"
  },
  {
    "id": "TK-48096653743",
    "subject": "Validación matrícula demorada en SISA",
    "content": "Cargué mis fotos de matrícula nacional hace 72 horas y el bot me sigue diciendo 'En revisión'. Necesito prescribir hoy.",
    "priority": "HIGH",
    "stage": "open",
    "createdate": "2026-09-08T11:45:00Z"
  },
  {
    "id": "TK-48149811456",
    "subject": "Firma no impacta en Farmacity / Winfarma",
    "content": "Un paciente me avisa desde Farmacity que el código de barra de la receta digital emitida hoy figura como 'no autorizada por entidad médica'.",
    "priority": "MEDIUM",
    "stage": "in_progress",
    "createdate": "2026-09-08T14:20:45Z"
  },
  {
    "id": "TK-48201984210",
    "subject": "Duda con formato de receta para psicotrópicos",
    "content": "Hola, ¿cómo hago para seleccionar duplicado para psicotrópicos Lista IV? No encuentro la opción en el nuevo portal.",
    "priority": "LOW",
    "stage": "closed",
    "createdate": "2026-09-08T16:05:10Z"
  }
]
```

---

## 2. Salida Estructurada del Agente (Reporte Operativo RCTA)

```json
{
  "fecha_analisis": "2026-09-08",
  "total_tickets": 5,
  "estado_operativo": "Alerta",
  "metricas_gestion": {
    "total_incidencias": 5,
    "categoria_mas_recurrente": "Emisión y Firma Digital",
    "canal_principal": "Chat Web",
    "eficiencia_bot_porcentaje": 49.7,
    "eficiencia_humana_porcentaje": 50.3,
    "tiempo_cierre_promedio": "1h 45m"
  },
  "leaderboard_agentes": [
    { "posicion": 1, "nombre": "René (Bot)", "cerrados": 49, "tipo": "bot" },
    { "posicion": 2, "nombre": "Sol", "cerrados": 16, "tipo": "humano" },
    { "posicion": 3, "nombre": "Jose", "cerrados": 14, "tipo": "humano" },
    { "posicion": 4, "nombre": "Brune", "cerrados": 12, "tipo": "humano" },
    { "posicion": 5, "nombre": "Iñaki", "cerrados": 9, "tipo": "humano" }
  ],
  "diagnostico_semaforo": [
    {
      "color": "rojo",
      "titulo": "Microservicio de Firma Digital y WebServices Externos (OSDE / Winfarma)",
      "volumen": 2,
      "impacto": "Latencia crítica y timeout en paso 3 de firma que bloquea la emisión de recetas para pacientes crónicos.",
      "casos_ids": ["TK-48264175697", "TK-48149811456"]
    },
    {
      "color": "amarillo",
      "titulo": "Crash de App en Criptografía Local (Moto G60s Android 12)",
      "volumen": 1,
      "impacto": "Excepción de padding criptográfico en modelos específicos de dispositivos móviles que impide la apertura del módulo.",
      "casos_ids": ["TK-48180653917"]
    },
    {
      "color": "verde",
      "titulo": "Consultas Generales y Validaciones SISA de Rutina",
      "volumen": 2,
      "impacto": "Gestión asistida de matrículas y dudas de configuración de vademécum psicofármacos.",
      "casos_ids": ["TK-48096653743", "TK-48201984210"]
    }
  ],
  "escalaciones_bot": [
    {
      "motivo": "Firma trabada en paso 3 y timeouts en APIs externas",
      "frecuencia": "Alta",
      "solucion_automatizable": "Implementar circuit-breaker con aviso proactivo de degradación de servicio en el chat de René."
    }
  ],
  "soluciones_workarounds": [
    {
      "problema": "Timeout en emisión de recetas con prepagas",
      "procedimiento": "Indicar al profesional refrescar el token de sesión y reintentar la firma seleccionando dispensa genérica transitoria."
    }
  ],
  "supervision_humana": {
    "nivel_l_requerido": "L2 (Revisión humana previa antes de accionar)",
    "responsable": "Walter Peron",
    "puntos_de_control": "Auditar la latencia del validador de recetas en conjunto con el equipo de DevOps antes de notificar a los centros médicos."
  }
}
```

---

## 3. Síntesis y Supervisión Humana
* **Estado Operativo del Día:** Alerta
* **Diagnóstico Ejecutivo:** Jornada crítica en el subsistema de firma digital y dispensación farmacéutica. Se concentran incidentes de alta severidad que provocan bloqueos directos en la emisión de recetas médicas y rechazos en ventanilla de farmacia.
* **Nivel de Supervisión Requerido:** L2 (Revisión humana previa antes de accionar)
* **Responsable:** Walter Peron
* **Puntos de Control Auditados:** Auditar la latencia del validador de recetas en conjunto con el equipo de DevOps antes de notificar a los centros médicos.
