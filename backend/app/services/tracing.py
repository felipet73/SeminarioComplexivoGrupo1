"""Trazas explicativas con datos observados; no son razonamiento interno del modelo."""
def step(id, title, description, status='completed', **details):
    return {'id':id,'title':title,'description':description,'status':status,'details':details}
