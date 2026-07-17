"""
scripts/rebalance.py
--------------------
Standalone script to calculate optimal portfolio weights and 
print rebalancing orders based on your current SQLite holdings.
"""

import argparse
import sys
from pathlib import Path

# Ensure absolute imports work from the root project directory
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.store import DataStore
from src.data import DataLoader
from src.optimization.strategies.mc_sharpe import MonteCarloSharpeOptimizer
from src.portfolio_manager import compute_rebalance_orders

def get_config_paths():
    """Fallback to standard paths if not injecting full config.yaml parsing"""
    base_dir = Path(__file__).resolve().parent.parent
    return {
        "data_cache": str(base_dir / "data_cache"),
        "portfolio_db": str(base_dir / "data_cache" / "portfolio.db")
    }

def print_orders_table(orders_df, current_total: float, target_total: float):
    print("\n" + "="*60)
    print(f"💰 RESUMEN DE REBALANCEO")
    print("="*60)
    print(f"Valor Actual del Portafolio : ${current_total:,.2f} USD")
    print(f"Valor Objetivo (Inversión)  : ${target_total:,.2f} USD")
    print(f"Diferencia (Efectivo a Mover) : ${(target_total - current_total):,.2f} USD\n")
    
    if orders_df.empty:
        print("No hay órdenes de rebalanceo.")
        return

    # Helper formatters
    orders_df['curr_p'] = (orders_df['current_usd'] / current_total * 100).fillna(0) if current_total else 0
    orders_df['target_p'] = orders_df['target_weight'] * 100
    
    print(f"{'Ticker':<10} | {'Actual %':<10} | {'Objetivo %':<10} | {'Actual USD':<12} | {'Objetivo USD':<12} | {'Orden (USD)':<12}")
    print("-" * 80)
    
    for _, row in orders_df.iterrows():
        t = row['ticker']
        cp = f"{row['curr_p']:.1f}%"
        tp = f"{row['target_p']:.1f}%"
        cu = f"${row['current_usd']:,.2f}"
        tu = f"${row['target_usd']:,.2f}"
        d  = row['delta_usd']
        
        # Colorize / Format delta
        if d > 1:
            delta_str = f"+${d:,.2f} (COMPRAR)"
        elif d < -1:
            delta_str = f"-${abs(d):,.2f} (VENDER)"
        else:
            delta_str = "MANTENER"
        
        # Print each row correctly
        print(f"{t:<10} | {cp:<10} | {tp:<10} | {cu:<12} | {tu:<12} | {delta_str}")
        
    print("="*80 + "\n")

    # Explicar qué significa Monte Carlo
    print("⚙️  Motor: Monte Carlo Mean-Variance (Sharpe Ratio)")
    print("⚠️  Nota: Los pesos óptimos pueden variar ligeramente en cada corrida debido a simulación estocástica.")


def main():
    parser = argparse.ArgumentParser(description="Calcula el rebalanceo óptimo del portafolio.")
    parser.add_argument(
        "--target-usd", 
        type=float, 
        default=None,
        help="Nuevo valor total del portafolio si deseas inyectar o retirar capital. Si se omite, se rebalancea el capital actual."
    )
    parser.add_argument(
        "--simulations", 
        type=int, 
        default=25000,
        help="Número de simulaciones de Monte Carlo para la optimización (default: 25000)"
    )
    parser.add_argument(
        "--risk-free", 
        type=float, 
        default=0.04,
        help="Tasa libre de riesgo para el Sharpe Ratio (default: 0.04)"
    )
    
    args = parser.parse_args()
    
    paths = get_config_paths()
    
    print(f"Iniciando optimización de portafolio...")
    print(f"- Simulaciones : {args.simulations:,}")
    print(f"- Risk-free rate: {args.risk_free:.1%}")
    
    # Initialize components
    store = DataStore(paths["data_cache"])
    loader = DataLoader(store)
    optimizer = MonteCarloSharpeOptimizer(
        num_simulations=args.simulations, 
        risk_free_rate=args.risk_free
    )
    
    try:
        # compute
        orders_df = compute_rebalance_orders(
            db_path=paths["portfolio_db"],
            data_loader=loader,
            optimizer=optimizer,
            target_total_usd=args.target_usd
        )
        
        if orders_df.empty:
            print("❌ No se pudo calcular el rebalanceo (¿portafolio vacío o sin datos históricos?).")
            return
            
        # Get totals for display
        current_total = orders_df["current_usd"].sum()
        target_total = args.target_usd if args.target_usd is not None else current_total
        
        print_orders_table(orders_df, current_total=current_total, target_total=target_total)
        
    except ValueError as e:
        print(f"❌ Error de Validación: {e}")
    except Exception as e:
        print(f"❌ Error crítico durante la optimización: {e}")

if __name__ == "__main__":
    main()
