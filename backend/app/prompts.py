from pathlib import Path
PROMPTS = Path(__file__).resolve().parent / "prompts"
def cargar_prompt(version: str = "system_v3") -> str: return (PROMPTS / f"{version}.md").read_text(encoding="utf-8")
