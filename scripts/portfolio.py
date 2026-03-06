import argparse
import sqlite3
import datetime
import sys
import yfinance as yf
import pandas as pd
from pathlib import Path

# Configuración de BD con ruta absoluta basada en la ubicación del script
# Asumiendo que el script está en financepy/scripts/portfolio.py
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data_cache" / "portfolio.db"

def init_db():
    """Inicializa la tabla si no existe."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ticker TEXT NOT NULL,
            usd_amount REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_holding(ticker: str, amount: float):
    """Inserta el registro en la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO holdings (ticker, usd_amount) VALUES (?, ?)", 
        (ticker.upper(), amount)
    )
    conn.commit()
    conn.close()
    print(f"✅ Registrado: {amount} USD en {ticker.upper()} ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})")

def is_valid_ticker(ticker: str) -> bool:
    """Valida rápidamente si el ticker existe usando yfinance."""
    print(f"Buscando '{ticker}' en el mercado...", end="\r")
    stock = yf.Ticker(ticker)
    try:
        # Si tiene info o precio actual, es válido
        info = stock.fast_info
        if 'lastPrice' in info or len(info) > 0:
            return True
    except Exception:
        pass
    return False

def show_portfolio():
    """Muestra el estado actual del portafolio en una tabla formateada."""
    if not DB_PATH.exists():
        print("❌ No se encontró la base de datos. Agrega activos primero.")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        # Obtenemos solo el registro más reciente por cada ticker y ordenamos por monto
        query = """
            SELECT ticker, usd_amount, MAX(timestamp) as last_updated
            FROM holdings
            GROUP BY ticker
            ORDER BY usd_amount DESC
        """
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            print("El portafolio está vacío.")
        else:
            total_usd = df['usd_amount'].sum()
            
            # Formatear para visualización
            df['usd_amount'] = df['usd_amount'].apply(lambda x: f"${x:,.2f}")
            df.rename(columns={
                'ticker': 'Activo', 
                'usd_amount': 'Monto (USD)', 
                'last_updated': 'Última Actualización'
            }, inplace=True)
            
            print("\n" + "="*45)
            print("🏦 ESTADO ACTUAL DEL PORTAFOLIO")
            print("="*45)
            print(df.to_string(index=False))
            print("-" * 45)
            print(f"💰 VALOR TOTAL ESTIMADO: ${total_usd:,.2f} USD")
            print("="*45 + "\n")
            
    except Exception as e:
        print(f"❌ Error al leer la base de datos: {e}")
    finally:
        conn.close()

def interactive_mode():
    """Bucle interactivo para registrar activos."""
    print("=== Gestor de Portafolio Interactivo ===")
    print("Escribe 'salir' o 'exit' para terminar.\n")
    
    while True:
        try:
            raw_input = input("🔎 Símbolo (ej. QQQ, MSFT): ").strip().upper()
            if raw_input in ['SALIR', 'EXIT', 'QUIT']:
                print("Saliendo...")
                break
            if not raw_input:
                continue
                
            # Validación simple
            if not is_valid_ticker(raw_input):
                print(f"⚠️  No se encontró información clara para '{raw_input}'.")
                confirm = input("¿Deseas agregarlo de todas formas? (s/N): ").lower()
                if confirm != 's':
                    continue
            
            # Pedir monto
            while True:
                amount_str = input(f"💰 Monto actual en USD para {raw_input}: ")
                try:
                    amount = float(amount_str)
                    if amount < 0:
                        print("El monto no puede ser negativo.")
                        continue
                    break
                except ValueError:
                    print("Por favor, ingresa un número válido (ej. 150.50).")
            
            # Guardar
            add_holding(raw_input, amount)
            print("-" * 40)
            
        except KeyboardInterrupt:
            print("\nOperación cancelada. Saliendo...")
            break

def main():
    # Inicializar DB antes de cualquier acción
    init_db()
    
    parser = argparse.ArgumentParser(description="Gestor de Portafolio CLI")
    parser.add_argument("--interactive", action="store_true", help="Inicia el modo interactivo (loop)")
    parser.add_argument("--show", action="store_true", help="Muestra el estado actual del portafolio")
    parser.add_argument("-stock", type=str, help="Símbolo de la acción a registrar (ej. QUBT)")
    parser.add_argument("-quant", type=float, help="Monto total en USD de la acción")
    
    args = parser.parse_args()
    
    # Modo Mostrar
    if args.show:
        show_portfolio()
        sys.exit(0)
        
    # Modo Directo (One-liner)
    if args.stock and args.quant is not None:
        add_holding(args.stock, args.quant)
        sys.exit(0)
        
    # Validar mala combinación de argumentos
    if (args.stock and args.quant is None) or (args.quant is not None and not args.stock):
        print("❌ Error: Para el modo directo debes proveer ambos argumentos: -stock y -quant")
        parser.print_help()
        sys.exit(1)
        
    # Modo Interactivo
    if args.interactive:
        interactive_mode()
    elif not args.show:
        # Si no se pasa nada, mostrar ayuda
        parser.print_help()

if __name__ == "__main__":
    main()