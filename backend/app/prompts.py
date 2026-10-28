from pathlib import Path
PROMPTS = Path(__file__).resolve().parent / "prompts"
def cargar_prompt(version: str | None = None) -> str:
    from app.services.admin_store import prompt
    if version is not None:
        import re
        match = re.fullmatch(r'system_v(\d+)',version)
        if not match:
            raise ValueError('Versión inválida')
        return prompt(int(match.group(1)))['content']
    return prompt()['content']
