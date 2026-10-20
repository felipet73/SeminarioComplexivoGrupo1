"""Descarga manual repetible de PDFs con URLs oficiales directas.

No indica vigencia jurídica; su revisión sigue siendo humana.
"""
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw"
SOURCES = {
    "uniandes-reforma-practicas-2023.pdf": "https://www.uniandes.edu.ec/wp-content/uploads/2024/08/REFORMA-2023-REGLAMENTO-DE-PRACTICAS.pdf",
    "uniandes-procedimiento-practicas-online-2024.pdf": "https://www.uniandes.edu.ec/wp-content/uploads/2024/08/V2-PROCEDIMIENTO-PRACTICAS-ON-LINE-2024.pdf",
}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    for name, url in SOURCES.items():
        try:
            data = urlopen(Request(url, headers={"User-Agent": "AcademicResearch/1.0"}), timeout=20).read()
            if not data.startswith(b"%PDF"):
                raise ValueError("Response is not PDF")
            (OUT/name).write_bytes(data)
            records.append({"file": name, "url": url, "status": "downloaded_unverified", "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        except Exception as exc:
            records.append({"file": name, "url": url, "status": "download_failed", "error": str(exc)})
    (OUT/"manifest.json").write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding="utf-8")
    for item in records: print(item["file"], item["status"])

if __name__ == "__main__": main()
