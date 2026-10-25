from datetime import date
from typing import Literal
from pydantic import BaseModel, Field, model_validator

class Login(BaseModel):
    username: str = Field(min_length=1,max_length=80)
    password: str = Field(min_length=1,max_length=200)

class PromptInput(BaseModel):
    content: str = Field(min_length=20,max_length=40000)
    description: str = Field(min_length=3,max_length=300)
    expected_revision: int | None = Field(default=None,ge=1)

class DocMeta(BaseModel):
    title: str = Field(min_length=3,max_length=200)
    kind: Literal['normativa','informativo'] = 'informativo'
    source_url: str = Field(default='',max_length=1000)
    valid_from: date
    valid_to: date | None = None
    approved: bool = False
    enabled: bool = True
    notes: str = Field(default='',max_length=2000)

    @model_validator(mode='after')
    def valid_dates(self):
        if self.valid_to and self.valid_to < self.valid_from:
            raise ValueError('La fecha final no puede ser anterior al inicio de vigencia.')
        if self.source_url and not self.source_url.startswith(('https://','http://')):
            raise ValueError('La fuente debe ser una URL HTTP o HTTPS.')
        return self

class DocUpdate(DocMeta):
    expected_revision: int = Field(ge=1)

class RAGConfig(BaseModel):
    active_prompt: int = Field(ge=1,le=999)
    chunk_size: int = Field(default=1400,ge=300,le=4000)
    overlap: int = Field(default=160,ge=0,le=1000)
    top_k: int = Field(default=4,ge=1,le=10)
    strategy: Literal['lexical','hybrid'] = 'lexical'
    embedding_model: Literal['gemini-embedding-001'] = 'gemini-embedding-001'
    min_similarity: float = Field(default=.65,ge=0,le=1)
    revision: int = Field(ge=1)

    @model_validator(mode='after')
    def overlap_valid(self):
        if self.overlap >= self.chunk_size // 2:
            raise ValueError('El solapamiento debe ser menor a la mitad del fragmento.')
        return self

class Search(BaseModel):
    query: str = Field(min_length=3,max_length=2000)

class AnalysisCase(BaseModel):
    question: str = Field(min_length=3,max_length=2000)
    expected: str = Field(default='',max_length=2000)
    contexto: dict[Literal['carrera','curso','modalidad','periodo','jornada','tema','objetivo','sede','modalidad_titulacion'],str] = Field(default_factory=dict)

    @model_validator(mode='after')
    def validate_context(self):
        from app.schemas import ConsultaChat
        payload=ConsultaChat(pregunta=self.question,**self.contexto)
        self.contexto={k:v for k,v in payload.model_dump(exclude={'pregunta','modelo_preferido'},exclude_none=True).items()}
        return self

class AnalysisInput(BaseModel):
    versions: list[int] = Field(min_length=1,max_length=5)
    model: Literal['gemini','openai'] = 'gemini'
    cases: list[AnalysisCase] = Field(min_length=1,max_length=10)
    use_rag: bool = True

    @model_validator(mode='after')
    def unique_versions(self):
        if len(set(self.versions)) != len(self.versions):
            raise ValueError('No repitas versiones de prompt.')
        return self
