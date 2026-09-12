# Auditor Agéntico de Tickets Diarios (HubSpot CRM + Gemini)

Trabajo Final individual de la materia "Programación de y con Agentes de IA" — MBA UCEMA 2026 2T.  
**Alumno:** Walter Peron  

## Qué construí
Un sistema agéntico local que se conecta a la API de HubSpot CRM para extraer los tickets de soporte ingresados en una fecha dada, ejecuta un diagnóstico operativo mediante Gemini con un contrato estricto de 6 piezas, clasifica las fricciones del día (errores de firma de recetas, trabas de onboarding, dudas de usabilidad) y genera un reporte estructurado para el equipo de Customer Success con métricas de tokens y supervisión humana L0–L4.

## Cómo se lo pedí
1. "Diseñá un System Prompt con las seis piezas de contrato (rol, objetivo, contexto, restricciones de privacidad y grounding, few-shot y formato de salida JSON) para que actúe como Auditor Senior de Customer Support de una plataforma médica (RCTA)."
2. "Armá un User Prompt que reciba la fecha y el payload JSON crudo extraído de HubSpot CRM mediante el endpoint de búsqueda de tickets, exigiendo que no invente datos ni agregue texto fuera del JSON."
3. "Creá un backend en Python con Flask que consulte la API de HubSpot por rango horario, mida tokens reales y costos de Gemini Flash, y mantenga un historial local en cache para advertir si una fecha ya fue auditada antes de volver a correrla."
4. "Construí una interfaz web en un dashboard interactivo que permita seleccionar la fecha, visualizar el estado del día (Saludable/Alerta/Crítico), renderizar las recomendaciones operativas y exportar las corridas oficiales directamente a la carpeta `corridas/`."

## Qué funciona
* **Conector real de HubSpot:** Consulta tickets mediante la API v3 (`/crm/v3/objects/tickets/search`) filtrando por fecha (`createdate`) y extrayendo campos de asunto, descripción, prioridad y estado.
* **Contrato agéntico estructurado:** Gemini procesa el lote devolviendo siempre un objeto JSON válido con diagnóstico, distribución por categoría, Top 3 de fricciones y alertas inmediatas.
* **Control de re-ejecuciones y cache:** Si una fecha ya fue procesada, la interfaz muestra un modal de advertencia para evitar costos de inferencia innecesarios, permitiendo recargar el reporte almacenado o forzar una re-ejecución.
* **Medición de tokens y costos:** Cada ejecución registra tokens de entrada y salida reales y calcula el costo monetario en USD.
* **Tres corridas reales registradas:** Guardadas en `corridas/corrida_1.md`, `corridas/corrida_2.md` y `corridas/corrida_3.md` con entradas completas de tickets, salidas y niveles de supervisión definidos.
* **Documentación completa de gobierno y economía:** En `DECISIONES.md` se detallan las iteraciones de prompt, el análisis económico proyectado a escala y el marco de gobierno L0–L4 con firma responsable.

## Qué falta o qué falló
* **Falla de formato inicial:** En la primera versión del System Prompt, el modelo incluía introducciones conversacionales ("A continuación presento el reporte...") que rompían el parseo automático de JSON en Python con un error `JSONDecodeError`. Se solucionó forzando `responseMimeType: application/json` y agregando una prohibición estricta de saludos en el prompt.
* **Ambigüedad en acciones recomendadas:** Las primeras salidas sugerían recomendaciones genéricas ("capacitar al personal"). Se corrigió incorporando un ejemplo Few-Shot y limitando las sugerencias a un máximo de 20 palabras en modo imperativo técnico.
* **Qué falta para producción:** Actualmente la selección de fechas se realiza manualmente desde la webapp; para una operación desatendida completa, se podría configurar un cron diario (programador de tareas a las 20:00 hs) que envíe automáticamente el informe a un canal de Slack o correo electrónico del equipo de soporte.

## Qué aprendí
Entendí que para que un agente pase de ser un experimento interesante a un sistema de valor en el trabajo real, la clave no está en tener el modelo más grande, sino en la precisión del contrato y en la calidad del conector de datos. Un modelo liviano como Gemini Flash, con el contexto justo y una regla de grounding estricta, resuelve la tarea de forma más rápida, consistente y 50 veces más económica que un modelo frontier. También comprendí que definir quién firma y qué revisa una persona (L2) es indispensable para confiar operativamente en la IA en salud.
