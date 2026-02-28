import pandas as pd
import datetime
from typing import List

class Reporter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def generate_report(self, date_str: str, 
                        features: pd.DataFrame, 
                        signals: pd.DataFrame, 
                        errors: List[str] = None):
        
        # Features and Signals are "long" dataframes with MultiIndex or just combined?
        # To make a summary table, we usually want the LAST row per ticker.
        # But wait, the pipeline likely processes HISTORY.
        # We need to slice for the specific 'date_str'.
        
        target_date = pd.to_datetime(date_str)
        
        # Helper to get row for date
        # Assuming features has index level 0 = Date, or just Date index and we filter
        # It's better if we passed a dictionary of {ticker: last_row_series} or a DF with Ticker column?
        # The store returns DF with index=Date.
        # When we process all, we probably have a dictionary of DFs or one big concated DF with 'Ticker' column?
        # Let's assume the 'run_daily' script assembles a snapshot DataFrame for the day.
        
        # Let's write the logic assuming we receive a "Summary DataFrame" for the day
        # columns: Ticker, Close, ret_1d, zscore, signal, state, reasons
        
        report_lines = []
        report_lines.append(f"# Daily Market Summary: {date_str}")
        report_lines.append(f"Generated at: {datetime.datetime.now()}")
        report_lines.append("")
        
        if errors:
            report_lines.append("## ⚠️ Warnings")
            for e in errors:
                report_lines.append(f"- {e}")
            report_lines.append("")
            
        report_lines.append("## Market Snapshot")
        
        # Table Header
        headers = ["Ticker", "Close", "1D Return", "Vol 20d", "Z-Score", "Signal", "State", "Confidence"]
        report_lines.append("| " + " | ".join(headers) + " |")
        report_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        
        # We expect 'features' and 'signals' to be DFs containing data for ALL processed tickers for THAT DATE.
        # Or we act on a merged DF.
        
        # Let's assume the caller passes a combined DF ready for display called 'snapshot'
        # But here I defined signature with features/signals.
        # Let's do the merge here.
        
        # We need to iterate over tickers present in the features index (if MultiIndex) 
        # OR if features is just a list of rows. 
        # Simpler: The caller 'run_daily.py' will loop over tickers, get the row for the date, 
        # collect them into a list, and pass that to reporter. 
        # Let's change signature to accept a list of dicts or a summary DF.
        pass

    def generate_from_snapshot(self, snapshot_df: pd.DataFrame, errors: List[str] = None) -> str:
        """
        snapshot_df columns expected: 
        Ticker, Close, ret_1d, vol_20d, zscore, signal, state, confidence, reasons
        """
        report_lines = []
        report_lines.append(f"# Daily Market Summary: {datetime.date.today()}") # Or passed date
        report_lines.append(f"**Timestamp**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        if errors:
            report_lines.append("### ⚠️ Data Collection Warnings")
            for e in errors:
                report_lines.append(f"> [!WARNING]")
                report_lines.append(f"> {e}")
            report_lines.append("")

        report_lines.append("## Watchlist")
        
        headers = ["Ticker", "Close", "Chg", "Vol", "Hurst", "Regime", "RiskOff", "Z-Score", "Signal"] # Compact headers
        report_lines.append("| " + " | ".join(headers) + " |")
        report_lines.append("|" + "|".join(["---"] * len(headers)) + "|")
        
        # Collect global stats from first row if available
        global_lambda = "N/A"
        global_lambda_pctl = "N/A"
        market_regime_counts = {}
        
        for _, row in snapshot_df.iterrows():
            ticker = row['Ticker']
            close = f"{row['Close']:.2f}"
            
            # Colorize returns
            ret = row['ret_1d']
            try:
                ret_val = float(ret)
                ret_str = f"{ret_val*100:+.2f}%"
            except:
                ret_str = "N/A"
                
            vol = row.get('vol_ewma', row.get('vol_20d', 0))
            vol_str = f"{vol*100:.0f}%" # Compact
            
            hurst = row.get('hurst_dfa', 0)
            hurst_str = f"{hurst:.2f}"
            
            regime = row.get('regime_label', 'N/A')
            risk_off = "YES" if row.get('risk_off_flag', False) else "-"
            
            # Global stat collection
            if global_lambda == "N/A" and 'market_lambda1_norm' in row:
                global_lambda = row['market_lambda1_norm']
                global_lambda_pctl = row.get('market_lambda1_pctl', 0)
            
            market_regime_counts[regime] = market_regime_counts.get(regime, 0) + 1

            z = row.get('zscore', 0)
            z_str = f"{z:.2f}"
            
            sig = row.get('signal', 'NONE')
            
            # Add emoji
            if sig == 'BUY_ALERT':
                sig = "🟢"
            elif sig == 'SELL_ALERT':
                sig = "🔴"
            else:
                sig = "⚪"
                
            line = f"| {ticker} | {close} | {ret_str} | {vol_str} | {hurst_str} | {regime} | {risk_off} | {z_str} | {sig} |"
            report_lines.append(line)
            
        # --- NEW SECTION: REGIME & SYSTEMIC RISK ---
        report_lines.append("")
        report_lines.append("## Régimen y Riesgo Sistémico")
        
        # Dominant Regime
        if market_regime_counts:
            dom_regime = max(market_regime_counts, key=market_regime_counts.get)
            dom_pct = market_regime_counts[dom_regime] / sum(market_regime_counts.values())
            report_lines.append(f"- **Régimen Predominante**: {dom_regime} ({dom_pct:.0%} de los activos)")
        
        # Systemic Risk
        if global_lambda != "N/A":
             val = float(global_lambda)
             pctl = float(global_lambda_pctl)
             report_lines.append(f"- **Market Mode (Lambda1)**: {val:.2f} (Percentil Histórico: {pctl:.0%})")
             
             interp = "Normal"
             if pctl > 0.90:
                 interp = "CRITICAL (Alta Correlación Sistémica - Risk Off probable)"
             elif pctl > 0.75:
                 interp = "Elevado (Precaución)"
                 
             report_lines.append(f"- **Interpretación**: {interp}")
        else:
             report_lines.append("- No se pudo calcular Lambda1 Global.")
             
        report_lines.append("")
            
        report_lines.append("")
        report_lines.append("## Detailed Risks & Signals")
        # List interesting ones
        for _, row in snapshot_df.iterrows():
            reasons = row.get('reasons', [])
            recent = row.get('recent_signals', [])
            
            # Show if current signal OR recent points OR reasons exist
            if reasons or row['signal'] != 'NONE' or recent:
                report_lines.append(f"### {row['Ticker']}")
                
                if row['signal'] != 'NONE':
                    report_lines.append(f"- **Current Signal**: {row['signal']} ({row.get('confidence',0):.2f})")
                
                if reasons:
                    report_lines.append(f"- **Reasons**:")
                    for r in reasons:
                        report_lines.append(f"  - {r}")
                
                if recent:
                    report_lines.append(f"- **Recent Tipping Points (Last 30d)**:")
                    for r in recent:
                        report_lines.append(f"  - {r}")
                
                report_lines.append("")
                
        return "\n".join(report_lines)
    
    def save(self, content: str, date_str: str) -> str:
        filename = f"{self.output_dir}/{date_str}_summary.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Report saved to {filename}")
        return filename
