# FinancePy - Quick Start (Minimal Setup)

## 📦 Virtual Environment Local (.venv)

FinancePy ahora tiene un **.venv local mínimo** sin necesidad de Conda. **Ideal para scheduled tasks** como Windows Task Scheduler.

### Requisitos
- **Python**: 3.10+
- **.venv**: Ya incluido en el proyecto ✓
- **Espacio**: ~500MB

## 🚀 Instalación (Ya completada ✓)

### El .venv ya está listo

```bash
# Verificar que funciona
.\.venv\Scripts\python.exe -c "print('✓ Ready')"
```

Si necesitas recrearlo:
```bash
python -m venv .venv --upgrade-deps
.\.venv\Scripts\pip.exe install -r requirements-minimal.txt
```

## ▶️ Ejecutar Pipeline

### Opción 1: Directa (Para desarrollo)
```bash
# Hoy
.\.venv\Scripts\python.exe run_daily.py

# Fecha específica
.\.venv\Scripts\python.exe run_daily.py --date 2025-12-30

# Con logging detallado
.\.venv\Scripts\python.exe run_daily.py --log-level DEBUG
```

### Opción 2: Script Batch (Para Windows Task Scheduler)
```bash
run_pipeline.bat
```
- Crea log automático en `logs/pipeline_YYYY-MM-DD.log`
- Ideal para tarea programada diaria a las 1 PM

### Opción 3: Automated Daily (Scheduled Task)
Ver **TASK_SCHEDULER.md** para configurar Windows Task Scheduler.

## 📊 Output de Logging

```
[INFO    ] [financepy.pipeline:run_pipeline:32] Running pipeline for 2025-12-30...
[INFO    ] [financepy.data:_update_ticker:39] [MSFT] Cache up to 2025-12-29 covers target 2025-12-30. Skipping fetch.
[INFO    ] [financepy.data:_update_ticker:73] [NVDA] Fetching from 2025-10-31 to 2025-12-31 (Target: 2025-12-30)...
[WARNING ] [financepy.store:load:27] Failed to load cache for INVALID_TICKER: [Errno 2] No such file
[INFO    ] [financepy.report:save:220] Report saved to reports/2025-12-30_summary.md
```

## 🎮 Script Setup

```bash
# Ver opciones disponibles
python setup_check.py

# Espera:
# ✓ Python 3.10
# ✓ All dependencies installed
# ✓ Logging is working correctly
# ✓ All checks passed!
```

## 📁 Estructura de Output

| Ubicación | Contenido |
|-----------|-----------|
| `reports/YYYY-MM-DD_summary.md` | Reporte diario generado |
| `reports/manifests/` | Manifest JSON (metadata) |
| `data_cache/` | Datos descargados (Parquet comprimido) |
| `logs/pipeline_YYYY-MM-DD.log` | Log de ejecución |

## ⏰ Para Tarea Programada (Windows)

**Configuración rápida** en Windows Task Scheduler:

```
Program:     C:\Users\Asus\Documents\code\financepy\run_pipeline.bat
Schedule:    Daily at 13:00 (1 PM)
```

Ver **TASK_SCHEDULER.md** para guía paso a paso.

## 📋 Opciones de Log Level

```bash
# DEBUG - Máximo detalle
.\.venv\Scripts\python.exe run_daily.py --log-level DEBUG

# INFO - Normal (default)
.\.venv\Scripts\python.exe run_daily.py --log-level INFO

# WARNING - Solo alertas
.\.venv\Scripts\python.exe run_daily.py --log-level WARNING
```

## 📚 Documentación Completa

| Documento | Propósito |
|-----------|-----------|
| **VENV_LOCAL.md** | Usar .venv local sin Conda |
| **MINIMAL_SETUP.md** | Detalles técnicos de logging |
| **OPERATIONS.md** | Guía operacional |
| **TASK_SCHEDULER.md** | Configurar scheduled task |
| **SETUP_CHECKLIST.md** | Checklist de verificación |

## 🔗 Recursos

- **Reportes:** `reports/YYYY-MM-DD_summary.md`
- **Caché:** `data_cache/`
- **Config:** `configs/config.yaml`
- **Logs:** `logs/pipeline_*.log`
- **Tests:** `tests/`

## ⚡ Performance

| Métrica | Valor |
|---------|-------|
| .venv startup | <100ms |
| Full pipeline | 5-10 minutos |
| Memory (idle) | ~100MB |
| Memory (running) | ~500MB |

---

**¿Usar con Task Scheduler?** → Lee `TASK_SCHEDULER.md`
**¿Problemás?** → Ver `OPERATIONS.md`

**Listo para producción** ✅
