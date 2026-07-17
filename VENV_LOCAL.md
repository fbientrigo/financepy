# FinancePy - Usando .venv Local (Sin Conda)

## 🎯 Ventajas de .venv Local

✓ **Sin overhead de Conda** - más rápido y ligero
✓ **Ejecutable directo** - ideal para scheduled tasks
✓ **Aislado del sistema** - sin conflictos de dependencias
✓ **Portátil** - todo en la carpeta del proyecto
✓ **Ideal para tasks programadas** - Windows Task Scheduler sin problemas

## 📦 Setup Inicial (Una sola vez)

### Ya hecho ✓

El .venv ya está creado e instalado con todas las dependencias:

```
.venv/                      # Virtual environment local
├── Scripts/
│   ├── python.exe         # Python executable
│   ├── pip.exe            # Pip package manager
│   └── ...
├── Lib/
│   └── site-packages/     # Paquetes instalados
└── ...
```

Paquetes instalados:
- pandas, numpy, scipy
- pyyaml, plotly, streamlit
- yfinance
- (y sus dependencias)

## 🚀 Uso Diario

### Opción 1: Directa desde PowerShell (para desarrollo)

```bash
# Ejecutar con python del .venv
.\.venv\Scripts\python.exe run_daily.py --log-level DEBUG

# Con fecha específica
.\.venv\Scripts\python.exe run_daily.py --date 2026-03-30 --log-level INFO

# Instalar paquete nuevo (si es necesario)
.\.venv\Scripts\pip.exe install nombre_paquete
```

### Opción 2: Usando el script batch (para scheduled tasks)

```bash
# Solo ejecutar el archivo batch
run_pipeline.bat

# Crea log automático en logs/pipeline_YYYY-MM-DD.log
```

### Opción 3: Scheduled Task (automático diario a las 1 PM)

Ver `TASK_SCHEDULER.md` para configuración completa.

## 📝 Verificación

### Verificar que .venv funciona

```bash
.\.venv\Scripts\python.exe -c "print('✓ .venv working')"
```

### Ver paquetes instalados

```bash
.\.venv\Scripts\pip.exe list
```

### Actualizar paquetes (opcional)

```bash
.\.venv\Scripts\pip.exe install --upgrade -r requirements-minimal.txt
```

## 📁 Estructura

```
financepy/
├── .venv/                    ← Virtual environment (local)
│   ├── Scripts/
│   │   ├── python.exe       ← Usar este python
│   │   └── pip.exe
│   └── Lib/site-packages/
├── run_daily.py              ← Main script
├── run_pipeline.bat          ← Para Windows Task Scheduler
├── run_pipeline.sh           ← Para cron (Linux/Mac)
├── requirements-minimal.txt  ← Dependencias
├── src/                      ← Código
├── logs/                     ← Logs de ejecución
├── reports/                  ← Reportes generados
└── data_cache/               ← Caché de datos
```

## 🔄 Workflow para Desarrollo

### Cuando necesitas cambiar código:

1. Edita el código en `src/`
2. Ejecuta para probar:
   ```bash
   .\.venv\Scripts\python.exe run_daily.py --log-level DEBUG
   ```
3. Verifica log en `logs/`
4. Cuando esté listo para producción, la scheduled task automáticamente lo ejecutará

### Cuando necesitas agregar una dependencia nueva:

1. Identifica el paquete: `pip search nombre` (o busca en PyPI)
2. Instálalo:
   ```bash
   .\.venv\Scripts\pip.exe install nombre_paquete
   ```
3. Si es necesario para todos, actualiza `requirements-minimal.txt`:
   ```
   nombre_paquete>=version
   ```

## 📊 Comparativa: .venv vs Conda

| Aspecto | .venv | Conda |
|---------|-------|-------|
| **Tamaño** | ~500MB | ~2GB |
| **Startup** | <100ms | 1-2s |
| **Scheduled tasks** | ✓ Directo | ✗ Overhead |
| **Overhead** | Mínimo | Significativo |
| **Portabilidad** | Buena | Buena |
| **Complejidad** | Simple | Compleja |

**Conclusión:** Para una tarea diaria a las 1 PM, .venv es la mejor opción.

## ⏰ Scheduled Task (Windows)

### Configuración rápida:

```
Program:     C:\Users\Asus\Documents\code\financepy\run_pipeline.bat
Start in:    C:\Users\Asus\Documents\code\financepy
Time:        13:00 (1 PM) diario
```

Ver `TASK_SCHEDULER.md` para detalles completos.

### Verificar ejecución:

1. Ver último log:
   ```bash
   Get-Content logs\pipeline_*.log -Tail 20
   ```

2. Ver reporte:
   ```bash
   Get-Content reports\YYYY-MM-DD_summary.md
   ```

## 🛠️ Troubleshooting

### ".venv no encontrado"

```bash
# Recrear .venv
python -m venv .venv --upgrade-deps

# Instalar dependencias
.\.venv\Scripts\pip.exe install -r requirements-minimal.txt
```

### "ModuleNotFoundError: No module named 'pandas'"

```bash
# Reinstalar dependencias
.\.venv\Scripts\pip.exe install -r requirements-minimal.txt --force-reinstall
```

### "Python no se encuentra"

```bash
# Verificar path
.\.venv\Scripts\python.exe --version

# Si no funciona, crear nuevo .venv:
python -m venv .venv --upgrade-deps
.\.venv\Scripts\pip.exe install -r requirements-minimal.txt
```

## 📋 Checklist para Producción

- [x] .venv creado
- [x] Dependencias instaladas
- [x] Logging configurado
- [x] run_pipeline.bat creado
- [ ] Windows Task Scheduler configurado (ver TASK_SCHEDULER.md)
- [ ] Primer test manual exitoso
- [ ] Logs verificados en `logs/`
- [ ] Reportes generados en `reports/`

## 🎓 Comandos Útiles

```bash
# Ver versión de Python
.\.venv\Scripts\python.exe --version

# Ver tamaño del .venv
du -sh .venv  # PowerShell: (Get-ChildItem .venv -Recurse | Measure-Object -Sum Length).Sum / 1MB

# Eliminar caché Python
Get-ChildItem -r -i "__pycache__" -d | Remove-Item -r -Force

# Actualizar pip
.\.venv\Scripts\python.exe -m pip install --upgrade pip

# Listar paquetes en formato requirements
.\.venv\Scripts\pip.exe freeze > requirements-current.txt

# Desactivar y eliminar .venv (si necesitas empezar de nuevo)
Remove-Item -Recurse -Force .venv
```

## 📞 Referencia Rápida

| Tarea | Comando |
|-------|---------|
| Ejecutar pipeline | `.\.venv\Scripts\python.exe run_daily.py` |
| Con debug | `.\.venv\Scripts\python.exe run_daily.py --log-level DEBUG` |
| Verificar instalación | `.\.venv\Scripts\python.exe -c "import pandas; print('✓')"` |
| Instalar paquete | `.\.venv\Scripts\pip.exe install nombre` |
| Ver logs | `Get-Content logs\pipeline_*.log -Tail 50` |
| Ver reporte | `Get-Content reports\*.md` |

---

**Status:** ✅ .venv listo para producción
**Próximo paso:** Configurar Windows Task Scheduler (ver TASK_SCHEDULER.md)
