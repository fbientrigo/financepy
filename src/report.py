import pandas as pd
import datetime
from typing import List, Optional
from .logger_config import get_logger

logger = get_logger(__name__)

class Reporter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir


    def generate_from_snapshot(
        self,
        snapshot_df: pd.DataFrame,
        errors: List[str] = None,
        holdings_df: Optional[pd.DataFrame] = None,
    ) -> str:
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
            ticker = row.get('Ticker', 'UNKNOWN')
            
            try:
                close_val = float(row.get('Close'))
                close = f"{close_val:.2f}"
            except (TypeError, ValueError):
                close = "N/A"
            
            # Colorize returns
            ret = row.get('ret_1d')
            try:
                ret_val = float(ret)
                ret_str = f"{ret_val*100:+.2f}%"
            except (TypeError, ValueError):
                ret_str = "N/A"
                
            vol = row.get('vol_ewma', row.get('vol_20d'))
            try:
                vol_str = f"{float(vol)*100:.0f}%" # Compact
            except (TypeError, ValueError):
                vol_str = "N/A"
            
            hurst = row.get('hurst_dfa')
            try:
                hurst_str = f"{float(hurst):.2f}"
            except (TypeError, ValueError):
                hurst_str = "N/A"
            
            regime = row.get('regime_label', 'N/A')
            risk_off = "YES" if row.get('risk_off_flag', False) else "-"
            
            # Global stat collection
            if global_lambda == "N/A" and 'market_lambda1_norm' in row:
                global_lambda = row['market_lambda1_norm']
                global_lambda_pctl = row.get('market_lambda1_pctl', 0)
            
            market_regime_counts[regime] = market_regime_counts.get(regime, 0) + 1

            z = row.get('zscore')
            try:
                z_str = f"{float(z):.2f}"
            except (TypeError, ValueError):
                z_str = "N/A"
            
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
            sig_val = row.get('signal', 'NONE')
            
            # Show if current signal OR recent points OR reasons exist
            if reasons or sig_val != 'NONE' or recent:
                report_lines.append(f"### {row.get('Ticker', 'UNKNOWN')}")
                
                if sig_val != 'NONE':
                    report_lines.append(f"- **Current Signal**: {sig_val} ({row.get('confidence', 0.0):.2f})")
                
                if reasons:
                    report_lines.append(f"- **Reasons**:")
                    for r in reasons:
                        report_lines.append(f"  - {r}")
                
                if recent:
                    report_lines.append(f"- **Recent Tipping Points (Last 30d)**:")
                    for r in recent:
                        report_lines.append(f"  - {r}")
                
                report_lines.append("")
                
        # --- PORTFOLIO SECTION (only when holdings are provided) ---
        if holdings_df is not None and not holdings_df.empty:
            report_lines.append(self._render_portfolio_section(snapshot_df, holdings_df))

        return "\n".join(report_lines)

    def _render_portfolio_section(
        self,
        snapshot_df: pd.DataFrame,
        holdings_df: pd.DataFrame,
    ) -> str:
        """
        Render the '## 💼 Mi Portafolio' Markdown section.

        Cross-joins holdings_df (ticker, usd_amount) with snapshot_df
        (Ticker, Close, signal, confidence) and emits one row per held asset
        with an operational alert when a signal is active.
        """
        lines = ["", "## 💼 Mi Portafolio", ""]

        total_usd = holdings_df["usd_amount"].sum()
        lines.append(f"**Valor Total Estimado:** ${total_usd:,.2f} USD")
        lines.append("")

        # Left-join: start from MY holdings, pull in indicators when available
        if not snapshot_df.empty and "Ticker" in snapshot_df.columns:
            needed_cols = [c for c in ["Ticker", "Close", "signal", "confidence"] if c in snapshot_df.columns]
            merged = holdings_df.merge(
                snapshot_df[needed_cols],
                left_on="ticker",
                right_on="Ticker",
                how="left",
            )
        else:
            merged = holdings_df.copy()
            merged["signal"] = "NONE"
            merged["confidence"] = 0.0

        lines.append("| Activo | Monto (USD) | Señal | Alerta Operativa |")
        lines.append("|---|---|---|---|")

        for _, row in merged.iterrows():
            sig = row.get("signal", "NONE") or "NONE"
            amt = row["usd_amount"]

            if sig == "BUY_ALERT":
                sig_icon = "🟢"
                alert = f"🟢 BUY_ALERT (Tienes ${amt:,.2f} USD)"
            elif sig == "SELL_ALERT":
                sig_icon = "🔴"
                alert = f"🔴 SELL_ALERT (Tienes ${amt:,.2f} USD)"
            else:
                sig_icon = "⚪"
                alert = "—"

            lines.append(f"| {row['ticker']} | ${amt:,.2f} | {sig_icon} | {alert} |")

        lines.append("")
        return "\n".join(lines)

    def save(self, content: str, date_str: str) -> str:
        filename = f"{self.output_dir}/{date_str}_summary.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Report saved to {filename}")
        return filename
