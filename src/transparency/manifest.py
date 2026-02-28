import json
import datetime
from pathlib import Path
from typing import Dict, Any, List

class ManifestManager:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def collect_run_info(self, config: Dict[str, Any], 
                         tickers_processed: List[str], 
                         run_date: datetime.date,
                         errors: List[str] = None) -> Dict[str, Any]:
        """
        Collects runtime information for the manifest.
        """
        return {
            "meta": {
                "run_date": str(run_date),
                "timestamp": datetime.datetime.now().isoformat(),
                "version": "1.0"
            },
            "inputs": {
                "tickers_count": len(tickers_processed),
                "tickers": tickers_processed,
                "data_cache_path": config.get('paths', {}).get('data_cache', 'Unknown')
            },
            "parameters": config.get('parameters', {}),
            "quality": {
                "errors_count": len(errors) if errors else 0,
                "errors": errors if errors else []
            }
        }

    def save_manifest(self, manifest: Dict[str, Any], run_date: datetime.date) -> Path:
        """
        Saves the manifest to JSON.
        """
        filename = self.output_dir / f"{run_date}_manifest.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=4)
        return filename

    def load_manifest(self, run_date: datetime.date) -> Dict[str, Any]:
        """
        Loads a manifest for a specific date.
        """
        filename = self.output_dir / f"{run_date}_manifest.json"
        if not filename.exists():
            return {}
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
