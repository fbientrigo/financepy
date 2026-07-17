# FinancePy Operación - Guía de Referencia Rápida

## 🎯 Verificación Inicial

```bash
# 1. Verificar setup
python setup_check.py

# Output esperado:
# ✓ Python 3.10
# ✓ All dependencies installed
# ✓ Logging is working correctly
# ✓ All checks passed! Ready to run pipeline.
```

## 🚀 Ejecución del Pipeline

### Configuración Básica
```bash
# Hoy (default)
python run_daily.py

# Fecha específica
python run_daily.py --date 2025-12-30

# Con logging detallado
python run_daily.py --date 2025-12-30 --log-level DEBUG
```

### Niveles de Logging
```bash
# DEBUG - Máximo detalle (para diagnóstico)
python run_daily.py --log-level DEBUG

# INFO - Información normal (default)
python run_daily.py  # o --log-level INFO

# WARNING - Solo anomalías y errores
python run_daily.py --log-level WARNING

# ERROR - Solo errores críticos
python run_daily.py --log-level ERROR

# CRITICAL - Solo fallos del sistema
python run_daily.py --log-level CRITICAL
```

## 📊 Interpretar Logs

### Formato Standard
```
[INFO    ] [financepy.data:_update_ticker:39] [MSFT] Cache up to 2025-12-29 covers target 2025-12-30. Skipping fetch.
         ^                ^        ^           ^
      LEVEL          MODULE   FUNCTION     MESSAGE
```

### Ejemplos de Logs

| Log | Significado | Acción |
|-----|-------------|--------|
| `[INFO] Running pipeline for 2025-12-30` | Pipeline iniciando | Normal - esperar |
| `[INFO] Cache up to X covers target Y. Skipping fetch.` | Data ya existe | Normal - optimización |
| `[INFO] Fetching from X to Y` | Descargando datos nuevos | Normal - en progreso |
| `[WARNING] No data found for TICKER in range X - Y` | Ticker sin datos en rango | Verificar ticker |
| `[WARNING] Failed to load cache for TICKER` | Cache corrupto | Se descargará de nuevo |
| `[ERROR] Error processing TICKER: ...` | Error en cálculos | Revisar configuración |
| `[INFO] Report saved to reports/YYYY-MM-DD_summary.md` | Pipeline completado | Éxito ✓ |

## 📁 Outputs

### Reportes
```
reports/
├── 2025-12-30_summary.md      # Reporte Markdown
├── 2025-12-29_summary.md
└── manifests/
    ├── 2025-12-30_manifest.json
    └── 2025-12-29_manifest.json
```

### Caché de Datos
```
data_cache/
├── MSFT.parquet               # Datos históricos comprimidos
├── NVDA.parquet
├── SPY.parquet
└── portfolio.db               # Base de datos de portafolio
```

## 🔍 Diagnóstico

### Problema: "No data found"
```bash
# Causa: Ticker no existe o sin datos en Yahoo Finance
# Solución:
1. Verificar ticker en configs/assets.txt
2. Probar manualmente con yfinance:
   python -c "import yfinance as yf; print(yf.download('TICKER', start='2025-12-01'))"
```

### Problema: "Failed to load cache"
```bash
# Causa: Archivo .parquet corrupto
# Solución:
1. Buscar archivo corrupto: ls data_cache/*.parquet
2. Eliminar: rm data_cache/TICKER.parquet
3. Ejecutar pipeline - se descargará nuevamente
```

### Problema: Pipeline lento
```bash
# Causa: Descargando demasiados datos
# Opciones:
1. Usar --log-level WARNING para menos output
2. Verificar que caché esté completo (INFO logs)
3. Reducir tickers en configs/config.yaml
```

### Problema: Logging no aparece
```bash
# Causa: Nivel de log demasiado alto
# Solución:
python run_daily.py --log-level DEBUG  # Ver todos
python run_daily.py --log-level INFO   # Normal
```

## 🛠️ Uso con Makefile

```bash
# Ver todas las opciones
make help

# Crear environment mínimo
make setup-env

# Instalar solo dependencias
make install-minimal

# Ejecutar tests
make test

# Limpiar caché
make clean

# Iniciar dashboard
make dashboard
```

## 📝 Agregar Logging a Nuevo Código

```python
# 1. Import al inicio del módulo
from src.logger_config import get_logger
logger = get_logger(__name__)

# 2. Usar en funciones
def mi_funcion():
    logger.debug(f"Debug: valores internos = {x}")
    logger.info("Inicio de procesamiento")
    
    try:
        resultado = hacer_algo()
        logger.info(f"✓ Resultado: {resultado}")
    except Exception as e:
        logger.error(f"Fallo: {e}")
    
    logger.warning("Nota: algo anómalo detectado")
```

## ✅ Checklists

### Verificación Pre-Operación
- [ ] `python setup_check.py` pasa todos los tests
- [ ] `configs/config.yaml` tiene tickers correctos
- [ ] Espacio en disco disponible (> 1GB recomendado)
- [ ] Network conexión (para descargar datos)

### Verificación Post-Pipeline
- [ ] Reporte generado en `reports/YYYY-MM-DD_summary.md`
- [ ] Manifest creado en `reports/manifests/`
- [ ] Log final: `[INFO] Report saved to...`
- [ ] No hay `[ERROR]` o `[CRITICAL]` logs sin explicación

### Troubleshooting
1. ¿Logs aparecen? Sí → Ejecutar con `--log-level INFO`
2. ¿Datos descargando? Sí → Esperar, normal
3. ¿Errores? Sí → Verificar con `--log-level DEBUG`
4. ¿Aún hay problema? → Ver sección "Diagnóstico"

## 🔗 Recursos

| Recurso | Ruta | Propósito |
|---------|------|----------|
| Configuración | `configs/config.yaml` | Parámetros del pipeline |
| Tickers | `configs/assets.txt` | Lista de símbolos |
| Setup | `setup_check.py` | Verificación inicial |
| Documentación | `QUICKSTART.md` | Guía rápida |
| Detalles | `MINIMAL_SETUP.md` | Configuración avanzada |

---

**Última actualización:** 2026-03-30
**Versión:** 0.1.0 (Minimal Production)
**Status:** ✓ Listo para Producción
