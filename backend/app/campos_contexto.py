"""Controles permitidos: el modelo elige IDs, nunca genera formularios arbitrarios."""
from app.schemas import CampoNecesario

CATALOGO = {
    'carrera': ('Carrera', 120, []),
    'curso': ('Nivel / curso', 80, ['Primer nivel','Segundo nivel','Tercer nivel','Cuarto nivel','Quinto nivel','Sexto nivel','Séptimo nivel','Octavo nivel','Noveno nivel','Décimo nivel','Egresado/a']),
    'modalidad': ('Modalidad de estudios', 120, ['Presencial','En línea','Semipresencial','A distancia']),
    'periodo': ('Período académico', 80, []),
    'jornada': ('Jornada', 80, ['Matutina','Vespertina','Nocturna','Fin de semana']),
    'tema': ('Tema de consulta', 80, ['Titulación','Matrícula','Prácticas preprofesionales','Vinculación','Homologación','Certificados','Normativa académica']),
    'objetivo': ('¿Qué ayuda necesitas?', 120, ['Entender el proceso','Preparar preguntas para Secretaría','Organizar mis próximos pasos','Identificar información que me falta','Explicar términos académicos']),
    'sede': ('Sede / extensión', 120, []),
    'modalidad_titulacion': ('Modalidad de titulación', 120, ['Examen complexivo','Trabajo de integración curricular','Otra modalidad (precisar en la consulta)']),
}

def campos_pendientes(ids, contexto):
    return [CampoNecesario(campo=campo, etiqueta=CATALOGO[campo][0],
                          max_length=CATALOGO[campo][1], tipo='select' if CATALOGO[campo][2] else 'texto',
                          opciones=CATALOGO[campo][2])
            for campo in dict.fromkeys(ids) if campo in CATALOGO and not contexto.get(campo, '').strip()]
