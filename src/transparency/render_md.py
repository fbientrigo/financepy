from typing import Dict, Any
from .specs import METRIC_SPECS

class MarkdownRenderer:
    @staticmethod
    def render_transparency_section(manifest: Dict[str, Any], relative_manifest_path: str = None) -> str:
        """
        Generates a Markdown section summary for transparency.
        """
        if not manifest:
            return ""

        lines = []
        lines.append("## 🔍 Transparencia del Cálculo")
        lines.append("")
        
        # Meta
        meta = manifest.get('meta', {})
        inputs = manifest.get('inputs', {})
        params = manifest.get('parameters', {})
        
        lines.append(f"**Fecha de Corrida**: {meta.get('run_date')} | **Tickers**: {inputs.get('tickers_count')}")
        
        if relative_manifest_path:
             lines.append(f"> [Ver Manifest JSON Completo]({relative_manifest_path})")
        
        lines.append("")
        lines.append("### Parámetros Efectivos")
        
        # Table of key params
        lines.append("| Métrica | Parámetros Clave |")
        lines.append("|---|---|")
        
        # Extract params based on specs
        for key, spec in METRIC_SPECS.items():
            param_str = []
            for p_key in spec.get('params', []):
                # Handle nested keys e.g. ewma_vol.span
                parts = p_key.split('.')
                val = params
                found = True
                for part in parts:
                    if isinstance(val, dict) and part in val:
                        val = val[part]
                    else:
                        found = False
                        break
                if found:
                    param_str.append(f"{parts[-1]}={val}")
            
            if param_str:
                lines.append(f"| **{spec['name']}** | {', '.join(param_str)} |")
                
        lines.append("")
        return "\n".join(lines)
