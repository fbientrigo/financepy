# Minimal Production Setup - FinancePy

## 🎯 Objetivo Completado

Se ha generado un **environment mínimo de producción** con logging centralizado en lugar de print statements.

## 📦 Archivos Creados

### 1. **environment-minimal.yml** (Conda environment)
```bash
conda env create -f environment-minimal.yml
conda activate financepy
```
**Contenido:**
- Python 3.10
- pandas >= 2.2.0 (data manipulation)
- numpy >= 2.0 (numerical computing)
- scipy >= 1.11 (scientific computing)
- pyyaml >= 6.0 (config parsing)
- plotly >= 5.17 (visualizations)
- streamlit >= 1.28 (dashboard)
- yfinance >= 0.2.32 (via pip)

**Size:** ~500MB (mínimo productivo)

### 2. **requirements-minimal.txt** (Pip alternative)
```bash
pip install -r requirements-minimal.txt
```
Alternativa a conda para usuarios con pip.

### 3. **src/logger_config.py** (Centralizado logging)
Módulo de logging productivo con:
- ✓ Loggers por módulo (namespace logging)
- ✓ Formato: `[LEVEL] [module:function:line] message`
- ✓ Console handler (stdout)
- ✓ Optional file handler
- ✓ Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## 🔄 Cambios en Código

### Reemplazos print() → logging

| Archivo | Prints | Estado |
|---------|--------|--------|
| src/data.py | 3 | ✓ Reemplazados |
| src/store.py | 2 | ✓ Reemplazados |
| src/report.py | 1 | ✓ Reemplazados |
| src/indicators/hurst_dfa.py | 8 | ✓ Reemplazados |
| run_daily.py | 9 | ✓ Reemplazados |
| **Total** | **23** | ✓ **Completo** |

Scripts (CLI tools) mantienen print() para output de usuario - son intencionales.

## 🚀 Uso

### Activar environment
```bash
# Conda
conda activate financepy

# O con Python path completo (Windows)
C:\ProgramData\miniconda3\envs\financepy\python.exe
```

### Ejecutar con logging
```bash
# Nivel INFO (default)
python run_daily.py --date 2025-12-30

# Nivel DEBUG (verbose)
python run_daily.py --date 2025-12-30 --log-level DEBUG

# Nivel WARNING (quiet)
python run_daily.py --date 2025-12-30 --log-level WARNING
```

### Output de Logging
```
[INFO    ] [financepy.pipeline:run_pipeline:32] Running pipeline for 2025-12-30...
[INFO    ] [financepy.data:_update_ticker:39] [MSFT] Cache up to 2025-12-29 covers target 2025-12-30. Skipping fetch.
[WARNING ] [financepy.data:_update_ticker:77] No data found for INVALID_TICKER in range 2025-12-20 - 2025-12-30
[INFO    ] [financepy.report:save:220] Report saved to reports/2025-12-30_summary.md
```

## 📊 Comparativa: Print vs Logging

### Antes (print)
```python
print(f"[{ticker}] Cache up to {last_date} covers target {target_date}. Skipping fetch.")
print(f"Warning: No data found for {ticker}...")
```
❌ Sin nivel de severidad
❌ No se puede filtrar por módulo
❌ No se puede redirigir a archivo
❌ No tiene metadatos (línea, función)

### Después (logging)
```python
logger.info(f"[{ticker}] Cache up to {last_date} covers target {target_date}. Skipping fetch.")
logger.warning(f"No data found for {ticker}...")
```
✓ Con nivel de severidad (INFO, WARNING, ERROR, etc)
✓ Se puede filtrar por módulo/nivel
✓ Se redirige a consola y opcionalmente a archivo
✓ Incluye contexto: módulo, función, línea

## 🔍 Verificación

```bash
# Test de logging
conda activate financepy
cd C:\Users\Asus\Documents\code\financepy
python -c "from src.logger_config import setup_logging, get_logger; setup_logging('DEBUG'); logger = get_logger('test'); logger.info('✓ Working')"

# Output esperado:
# [INFO    ] [test:<module>:1] ✓ Working
```

## 📝 Notas Técnicas

### Logger Configuration (`src/logger_config.py`)
- **Namespace:** `logging.getLogger("financepy")` y derivados
- **Format:** `[%(levelname)-8s] [%(name)s:%(funcName)s:%(lineno)d] %(message)s`
- **Handler Console:** stderr → stdout
- **Optional File Handler:** con encoding UTF-8

### Integración en run_daily.py
```python
from src.logger_config import setup_logging, get_logger

# En main()
setup_logging(log_level=args.log_level)  # Configura logging global

# En módulos
logger = get_logger(__name__)  # Obtiene logger por módulo
logger.info("message")
```

### Niveles de Log (Usar apropiadamente)
- **DEBUG** - Detalles técnicos (algoritmo internals, variables)
- **INFO** - Eventos importantes (iniciación, fin de proceso)
- **WARNING** - Algo anómalo (datos faltantes, fallback usado)
- **ERROR** - Fallo en operación (excepción capturada)
- **CRITICAL** - Fallo severo (sistema no puede continuar)

## ✅ Checklist

- [x] Crear environment-minimal.yml con solo producción
- [x] Crear requirements-minimal.txt (pip alternative)
- [x] Implementar src/logger_config.py centralizado
- [x] Reemplazar todos los prints en src/
- [x] Reemplazar prints en run_daily.py
- [x] Agregar --log-level arg en run_daily.py
- [x] Verificar que logging funciona
- [x] Documentar uso y configuración

## 🎓 Próximas Mejoras (Opcionales)

1. **Scripts logging:** Usar logger también en scripts/qa.py, scripts/portfolio.py, etc
2. **File logging:** Agregar rotated file handler en src/logger_config.py
3. **Structured logging:** Considerar JSON logging para análisis
4. **Performance metrics:** Log de tiempos de ejecución (decorador)

---

**Resumen:** Environment mínimo (500MB) creado con logging productivo. 23 print statements reemplazados. Listo para producción. 🚀
