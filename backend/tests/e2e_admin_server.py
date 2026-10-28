"""Servidor SOLO para pruebas E2E: datos temporales y LLM doble, nunca proveedores reales."""
import shutil
import json
import tempfile
from pathlib import Path
from app.services import admin_store as store
from app.services import metrics
from app.services.llm import ResultadoLLM
from app.config import Settings
from app import admin_auth, admin_routes
from app.main import app

temp=Path(tempfile.mkdtemp(prefix='uniandes-admin-e2e-'))
original=store.PROMPT_DIR
store.DATA_DIR=temp/'data'
store.PROMPT_DIR=temp/'prompts'
store.PROMPT_DIR.mkdir()
for file in original.glob('system_v[123].md'):
    shutil.copy2(file,store.PROMPT_DIR/file.name)
metrics.LOG_PATH=temp/'metrics.jsonl'
config=Settings(_env_file=None,admin_password='only-e2e-password',gemini_api_key='fake-only-e2e',openai_api_key=None)
admin_auth.get_settings=lambda:config
admin_routes.get_settings=lambda:config

class FakeLLM:
    def generar_texto(self,prompt,question,model,**kwargs):
        text='Comparación simulada: V3 ofrece mayor claridad; validar con referencia humana.' if 'Eres evaluador' in prompt else json.dumps({'respuesta':'Respuesta simulada: consulta tu modalidad de titulación con Secretaría.','estado':'abstencion','fragmentos':[],'campos_necesarios':[]})
        if 'Eres evaluador' not in prompt and 'aclaración' in question and not kwargs.get('contexto',{}).get('carrera'):
            text=json.dumps({'respuesta':'Necesito tu carrera para esta aclaración.','estado':'aclaracion','fragmentos':[],'campos_necesarios':['carrera']})
        return ResultadoLLM(text,'doble-e2e',False,.2,20,30,50)
app.dependency_overrides[admin_routes.admin_llm]=lambda:FakeLLM()

if __name__=='__main__':
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=9019)
