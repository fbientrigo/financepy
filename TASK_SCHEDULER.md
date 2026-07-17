# FinancePy - Windows Task Scheduler Setup

## 🎯 Objetivo

Configurar una **tarea programada diaria a las 13:00 (1 PM)** que ejecute el pipeline de FinancePy sin necesidad de conda ni ventanas de terminal visibles.

## ✅ Requisitos Previos

1. ✓ `.venv` creado localmente en el proyecto
2. ✓ Dependencias instaladas en `.venv`
3. ✓ `run_pipeline.bat` presente en la raíz del proyecto
4. ✓ Carpeta `logs` para almacenar resultados

## 🔧 Configuración de Windows Task Scheduler

### Paso 1: Abrir Task Scheduler

```
1. Presiona Win + R
2. Escribe: taskschd.msc
3. Presiona Enter
```

O navega a: `Control Panel → Administrative Tools → Task Scheduler`

### Paso 2: Crear Nueva Tarea

1. En el panel izquierdo, haz clic en **Task Scheduler Library**
2. En el panel derecho, haz clic en **Create Task...**

### Paso 3: Configurar General

- **Name:** `FinancePy Daily Pipeline`
- **Description:** `Ejecuta el pipeline diario de análisis financiero a las 1 PM`
- **Location:** `\FinancePy` (o crear carpeta nueva)
- **Run whether user is logged in or not:** ☑ Checkear
- **Run with highest privileges:** ☐ Dejar sin checkear (o checkear si es necesario)

### Paso 4: Configurar Trigger (Activador)

1. Haz clic en la pestaña **Triggers**
2. Haz clic en **New...**

Configura así:
```
Begin the task:        At a scheduled time
Daily:                 ☑ Check
Start:                 13:00:00 (ajusta a tu hora preferida)
Repeat task every:     1 days
For a duration of:     [dejar vacío para indefinido]
Stop task if it runs:  30 minutes (o tu preferencia)
```

3. Haz clic en **OK**

### Paso 5: Configurar Action (Acción)

1. Haz clic en la pestaña **Actions**
2. Haz clic en **New...**

Configura así:
```
Action:             Start a program
Program/script:     C:\Users\Asus\Documents\code\financepy\run_pipeline.bat

(o simplemente: run_pipeline.bat si configuraste el path correctamente)

Add arguments:      [dejar vacío]
Start in:           C:\Users\Asus\Documents\code\financepy
```

3. Haz clic en **OK**

### Paso 6: Configurar Conditions (Condiciones - Opcional)

1. Haz clic en la pestaña **Conditions**

Recomendaciones:
```
Network:
  ☑ Start the task only if the following network connection is available
  ☑ Select "Any connection"

Power:
  ☑ Wake the computer to run this task (si la PC está en sleep)
  ☐ Start the task only if the computer is on AC power
```

3. Haz clic en **OK**

### Paso 7: Configurar Settings (Configuraciones)

1. Haz clic en la pestaña **Settings**

Recomendaciones:
```
☑ Allow task to be run on demand
☑ Run task as soon as possible after a scheduled start is missed
☑ If the task fails, restart every:    1 minute
   Attempt to restart up to:           3 times
☐ Stop the task if it runs longer than:   (dejar sin checkear o 1 hour)
```

2. Haz clic en **OK**

### Paso 8: Guardar y Probar

1. Se solicitará contraseña. Ingresa y confirma
2. Ahora la tarea está creada

**Para probar inmediatamente:**
1. En Task Scheduler, localiza la tarea creada
2. Haz clic derecho → **Run**
3. Verifica que se ejecute correctamente

## 📋 Verificación

### Después de ejecutar:

1. Revisa el log: `logs/pipeline_YYYY-MM-DD.log`

Ejemplo:
```
========================================
Pipeline Run: 2026-03-30 13:00:01
========================================
[INFO    ] [financepy.pipeline:run_pipeline:32] Running pipeline for 2026-03-30...
[INFO    ] [financepy.data:_update_ticker:39] [MSFT] Cache up to 2026-03-29...
[INFO    ] [financepy.report:save:220] Report saved to reports/2026-03-30_summary.md
[SUCCESS] Pipeline completed at 13:05:32
```

2. Revisa el reporte: `reports/YYYY-MM-DD_summary.md`

### Verificar en Task Scheduler:

1. Abre Task Scheduler
2. Localiza `FinancePy Daily Pipeline`
3. Haz clic en ella
4. En el panel inferior, verifica:
   - **Status:** `Running` o `Ready`
   - **Last Run Time:** muestra la última ejecución
   - **Last Run Result:** debe ser `(0x0)` (éxito)

## 🔄 Editar Tarea Existente

1. En Task Scheduler, haz clic derecho en la tarea
2. Selecciona **Edit**
3. Modifica los parámetros
4. Haz clic en **OK**

## ⏰ Cambiar Hora de Ejecución

1. Haz clic derecho en la tarea → **Edit**
2. Ve a la pestaña **Triggers**
3. Haz clic en el trigger existente → **Edit**
4. Cambia la hora en **Start:** a tu preferencia (ej: 14:00 para las 2 PM)
5. Haz clic en **OK** → **OK** → **OK**

## 🗑️ Eliminar Tarea

1. En Task Scheduler, haz clic derecho en la tarea
2. Selecciona **Delete**
3. Confirma

## 📊 Monitoreo y Logs

### Ver logs de ejecuciones pasadas:

```bash
# Listar todos los logs
dir logs\*.log

# Ver último log
type logs\pipeline_*.log
```

### Historial en Task Scheduler:

1. Selecciona la tarea
2. Haz clic en la pestaña **History**
3. Verás todas las ejecuciones pasadas

## 🚨 Troubleshooting

### Problema: Tarea no se ejecuta

**Causa:** Path incorrecto o archivo no encontrado

**Solución:**
1. Verifica que `run_pipeline.bat` existe en la raíz del proyecto
2. Verifica el "Start in" path: `C:\Users\Asus\Documents\code\financepy`
3. Prueba ejecutando manualmente: click derecho → **Run**

### Problema: Error 0x1

**Causa:** Script falló

**Solución:**
1. Revisa el log en `logs/pipeline_YYYY-MM-DD.log`
2. Ejecuta manualmente: `.venv\Scripts\python.exe run_daily.py --log-level DEBUG`
3. Corrije el error

### Problema: "Access Denied"

**Causa:** Permisos insuficientes

**Solución:**
1. En la tarea, ve a **Edit** → **General**
2. Checkea **Run with highest privileges**
3. Haz clic en **OK**

### Problema: ".venv no encontrado"

**Causa:** Script ejecutado en path diferente

**Solución:**
1. En **Actions**, verifica que **Start in:** sea correcta
2. Debe ser: `C:\Users\Asus\Documents\code\financepy`

## 💡 Tips

1. **Logging:** Los logs se guardan en `logs/` con timestamp
2. **Reintentos:** Si falla, Windows reintentará según config (máx 3 veces)
3. **Notificaciones:** Puedes configurar acciones adicionales si falla (ver evento en Event Viewer)
4. **Timezone:** Task Scheduler usa la zona horaria del sistema

## 📝 Script de Prueba Rápida

Para verificar que todo funciona antes de programar:

```bash
# Desde PowerShell en el proyecto
.\.venv\Scripts\python.exe run_daily.py --date 2026-03-30 --log-level DEBUG

# Verifica log
Get-Content logs\pipeline_2026-03-30.log
```

---

**Próxima ejecución:** Cada día a las 13:00 (1 PM) de forma automática
**Logs:** `logs/pipeline_YYYY-MM-DD.log`
**Reportes:** `reports/YYYY-MM-DD_summary.md`

¡Listo! 🎉
