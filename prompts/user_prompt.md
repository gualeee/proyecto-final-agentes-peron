# User Prompt: Inyección de Lote Diario de Tickets

## Tarea
Procesá el lote de tickets de soporte extraído de HubSpot CRM para la fecha solicitada. Aplicá las directivas de clasificación, diagnóstico de cuellos de botella y recomendaciones operativas estipuladas en el System Prompt. Devolvé únicamente el JSON estructurado solicitado.

## Parámetros de la Corrida
* **Fecha de consulta:** {{FECHA_CONSULTA}}
* **Total de tickets en el lote:** {{TOTAL_TICKETS}}
* **Origen de datos:** HubSpot CRM API (`POST /crm/v3/objects/tickets/search`)

## Lote de Tickets Recibidos (JSON crudo de HubSpot):
```json
{{TICKETS_PAYLOAD_JSON}}
```
