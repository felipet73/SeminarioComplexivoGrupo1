import { test, expect } from '@playwright/test';

test('chat: completa campos faltantes y reconsulta conservando pregunta y modelo',async({page})=>{
  const consultas:Record<string,string>[]=[];
  await page.route('**/api/chat/stream',async route=>{
    const datos=route.request().postDataJSON();
    consultas.push(datos);
    const respuesta={respuesta:consultas.length===1?'Para orientarte necesito tu carrera y nivel.':'Gracias. Confirma el trámite con Secretaría.',
      estado:consultas.length===1?'aclaracion':'abstencion',fuentes:[],requiere_revision_humana:true,modelo_utilizado:'doble',fallback_activado:false,tiempo_segundos:.1,
      campos_necesarios:consultas.length===1?[{campo:'carrera',etiqueta:'Carrera',tipo:'texto',opciones:[],max_length:120},{campo:'curso',etiqueta:'Nivel / curso',tipo:'select',opciones:['Primer nivel','Noveno nivel'],max_length:80}]:[]};
    await route.fulfill({status:200,contentType:'text/event-stream',headers:{'Access-Control-Allow-Origin':'*'},body:`event: done\ndata: ${JSON.stringify(respuesta)}\n\n`});
  });
  await page.goto('/');
  await page.getByLabel('Modelo',{exact:true}).selectOption('openai');
  await page.getByLabel('Tu consulta').fill('¿Cómo consulto mi modalidad de titulación?');
  await page.getByRole('button',{name:'Enviar consulta'}).click();
  const dialog=page.getByRole('dialog');
  await expect(dialog).toBeVisible();
  await dialog.getByRole('button',{name:'Salir sin consultar'}).click();
  await page.getByRole('button',{name:/Completar datos necesarios/}).click();
  await expect(dialog).toBeVisible();
  await expect(page.locator('.conversacion')).toContainText('Para orientarte necesito tu carrera y nivel.');
  await dialog.getByRole('button',{name:'Volver a consultar'}).click();
  expect(consultas).toHaveLength(1);
  await page.setViewportSize({width:390,height:844});
  await dialog.getByRole('textbox',{name:'Carrera',exact:true}).fill('Software');
  await dialog.getByRole('combobox',{name:'Nivel / curso',exact:true}).selectOption('Noveno nivel');
  await page.screenshot({path:'test-results/chat-campos-movil.png',fullPage:true});
  await dialog.getByRole('button',{name:'Volver a consultar'}).click();
  await expect(dialog).not.toBeVisible();
  await expect(page.locator('.conversacion')).toContainText('Gracias. Confirma el trámite con Secretaría.');
  expect(consultas).toHaveLength(2);
  expect(consultas[1]).toMatchObject({pregunta:consultas[0].pregunta,modelo_preferido:'openai',carrera:'Software',curso:'Noveno nivel'});
});

test('acceso admin acepta mayúsculas y barra final',async({page})=>{
  for(const route of ['/Admin','/ADMIN/','/admin/']){
    await page.goto(route);
    await expect(page.getByRole('button',{name:'Ingresar al administrador'})).toBeVisible();
  }
});

async function login(page:import('@playwright/test').Page){
  await page.goto('/admin');
  await expect(page.getByRole('alert')).toHaveCount(0);
  await page.getByLabel('Contraseña',{exact:true}).fill('only-e2e-password');
  await page.getByRole('button',{name:'Ingresar al administrador'}).click();
  await expect(page.getByRole('heading',{name:'Conocimiento con trazabilidad.'})).toBeVisible();
}

test('admin: login, prompts, fuentes, índice y análisis con métricas',async({page})=>{
  const initial=await page.request.get('/api/admin/bootstrap');
  expect(initial.status()).toBe(401);
  await login(page);
  await page.getByLabel('Descripción / qué permite esta versión').fill('Variante E2E con instrucciones académicas');
  await page.getByRole('button',{name:'Crear nueva versión con este contenido'}).click();
  await expect(page.getByRole('status')).toContainText('Nueva versión creada');
  await page.getByRole('button',{name:'Usar en el chat'}).click();
  await expect(page.getByRole('status')).toContainText('V4 se usará');
  await page.getByLabel('Título',{exact:true}).fill('Reglamento E2E');
  await page.getByLabel('Vigente desde').fill('2020-01-01');
  await page.getByLabel('O escribe información adicional para el bot').fill('Artículo 1. Titulación: consultar modalidad con Secretaría Académica.\nArtículo 2. Prácticas: contactar la coordinación de carrera.');
  await page.getByLabel(/He revisado su vigencia/).check();
  await page.getByRole('button',{name:'Agregar fuente',exact:true}).click();
  await expect(page.getByRole('status')).toContainText('Fuente guardada');
  await page.getByRole('button',{name:/02.*RAG/}).click();
  await page.getByRole('button',{name:'Dividir e indexar documento'}).click();
  await expect(page.getByRole('status')).toContainText('2 fragmentos indexados');
  await page.getByLabel('Consulta de prueba').fill('titulación');
  await page.getByRole('button',{name:'Buscar evidencia'}).click();
  await expect(page.locator('.chunk-result').first()).toContainText('Artículo 1');
  await page.getByRole('button',{name:/03.*Análisis/}).click();
  await page.getByLabel('Consulta',{exact:true}).fill('¿Cómo consulto mi modalidad de titulación?');
  await page.getByRole('button',{name:/Ejecutar 3 respuestas/}).click();
  await expect(page.getByRole('status')).toContainText('Estado: completed',{timeout:20000});
  await expect(page.locator('.simulation-answer')).toHaveCount(3);
  await expect(page.getByRole('heading',{name:'Análisis comparativo',exact:true})).toHaveCount(0);
  const simulationProcess=page.getByLabel('Proceso interno de la simulación',{exact:true});
  await simulationProcess.getByRole('button',{name:'Nodo 6: Guardar resultados',exact:true}).click();
  await expect(simulationProcess.getByRole('button',{name:'6 Guardar resultados',exact:true})).toHaveAttribute('aria-current','step');
  await expect(simulationProcess).toContainText('evaluaciones ia');
  await expect(page.locator('.analysis-stats').first()).toContainText('Total: 50');
  await page.screenshot({path:'test-results/admin-analisis.png',fullPage:true});
  await page.getByRole('button',{name:'Cargar los 10 casos propuestos del seminario'}).click();
  await expect(page.locator('.analysis-case')).toHaveCount(10);
  await page.getByRole('button',{name:'Cerrar sesión'}).click();
  await expect(page.getByRole('button',{name:'Ingresar al administrador'})).toBeVisible();
  expect((await page.request.get('/api/admin/bootstrap')).status()).toBe(401);
});

test('login y panel admin adaptables a móvil',async({page})=>{
  await page.setViewportSize({width:390,height:844});
  await page.goto('/admin');
  await page.screenshot({path:'test-results/admin-login-movil.png',fullPage:true});
  await login(page);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.screenshot({path:'test-results/admin-config-movil.png',fullPage:true});
});

test('admin: simulación tipo chat pide datos y compara de nuevo con el contexto',async({page})=>{
  await login(page);
  await page.getByRole('button',{name:/03.*Análisis/}).click();
  await expect(page.getByRole('button',{name:/Jailbreak/})).toBeVisible();
  await page.getByRole('button',{name:/Bono de transporte/}).click();
  await expect(page.getByRole('textbox',{name:'Consulta',exact:true})).toHaveValue('¿Cómo solicito el bono de transporte gratuito para estudiantes?');
  await page.getByRole('textbox',{name:'Consulta',exact:true}).fill('Consulta de titulación con aclaración');
  await page.getByRole('button',{name:/Ejecutar 3 respuestas/}).click();
  await expect(page.getByRole('status')).toContainText('Estado: completed',{timeout:20000});
  await expect(page.locator('.simulation-answer')).toHaveCount(3);
  await page.getByRole('button',{name:'Completar datos y repetir comparación'}).first().click();
  const dialog=page.getByRole('dialog');
  await dialog.getByRole('textbox',{name:'Carrera',exact:true}).fill('Software');
  await dialog.getByRole('button',{name:'Volver a consultar'}).click();
  await expect(dialog).not.toBeVisible();
  await expect(page.locator('.simulation-context')).toContainText('Software');
  await expect(page.getByRole('status')).toContainText('Estado: completed',{timeout:20000});
  await expect(page.locator('.simulation-answer')).toHaveCount(3);
  await expect(page.getByRole('button',{name:'Completar datos y repetir comparación'})).toHaveCount(0);
  await page.setViewportSize({width:390,height:844});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.screenshot({path:'test-results/admin-chat-movil.png',fullPage:true});
});

test('admin: nueva fuente limpia archivo, campos y errores; secciones contraíbles',async({page})=>{
  await login(page);
  const upload=await page.request.post('/api/admin/documents',{headers:{'X-Admin-Request':'1'},multipart:{metadata:JSON.stringify({title:'Fuente para edición',kind:'informativo',source_url:'',valid_from:'2020-01-01',approved:false,enabled:true,notes:''}),file:{name:'edicion.md',mimeType:'text/markdown',buffer:Buffer.from('Información de prueba para revisar la edición de fuentes.')}}});
  expect(upload.ok()).toBe(true);
  await page.reload();
  await expect(page.getByRole('heading',{name:'Conocimiento con trazabilidad.'})).toBeVisible();
  const formulario=page.locator('form.admin-form');
  await formulario.getByRole('textbox',{name:'Título',exact:true}).fill('Borrador sin guardar');
  await formulario.getByLabel('Vigente desde').fill('2020-01-01');
  await formulario.getByRole('button',{name:'Agregar fuente',exact:true}).click();
  await expect(formulario.getByRole('alert')).toBeVisible();
  await formulario.getByLabel('Archivo PDF, DOCX, TXT, MD o CSV').setInputFiles({name:'borrador.md',mimeType:'text/markdown',buffer:Buffer.from('Información de prueba que no se debe guardar.')});
  await formulario.getByLabel('Observaciones de gestión (privadas)').fill('Nota de prueba');
  await page.getByRole('button',{name:'Contraer Agregar una fuente',exact:true}).click();
  await page.getByRole('button',{name:'Nueva fuente',exact:true}).click();
  await expect(formulario.getByRole('textbox',{name:'Título',exact:true})).toHaveValue('');
  await expect(formulario.getByRole('textbox',{name:'Título',exact:true})).toBeFocused();
  await expect(formulario.getByLabel('Vigente desde')).toHaveValue('');
  await expect(formulario.getByLabel('Observaciones de gestión (privadas)')).toHaveValue('');
  expect(await formulario.locator('input[type=file]').evaluate((node:HTMLInputElement)=>node.files?.length)).toBe(0);
  await expect(formulario.getByRole('alert')).toHaveCount(0);
  await expect(formulario.getByLabel(/He revisado/)).not.toBeChecked();
  await formulario.getByRole('textbox',{name:'Título',exact:true}).fill('Mantener al contraer');
  await page.getByRole('button',{name:'Contraer Agregar una fuente',exact:true}).click();
  await page.getByRole('button',{name:'Expandir Agregar una fuente',exact:true}).click();
  await expect(formulario.getByRole('textbox',{name:'Título',exact:true})).toHaveValue('Mantener al contraer');
  await page.getByRole('button',{name:'Editar / reemplazar',exact:true}).first().click();
  await expect(formulario.getByRole('heading',{name:'Editar / reemplazar fuente',exact:true})).toBeVisible();
  await page.getByRole('button',{name:'Nueva fuente',exact:true}).click();
  await expect(formulario.getByRole('heading',{name:'Agregar una fuente',exact:true})).toBeVisible();
  await expect(formulario.getByRole('textbox',{name:'Título',exact:true})).toHaveValue('');
  await page.getByRole('button',{name:'Contraer Versiones de system prompt',exact:true}).click();
  await expect(page.getByLabel('Descripción / qué permite esta versión')).not.toBeVisible();
  await page.getByRole('button',{name:'Expandir Versiones de system prompt',exact:true}).click();
  await expect(page.getByLabel('Descripción / qué permite esta versión')).toBeVisible();
  await page.getByRole('button',{name:/02.*RAG/}).click();
  await page.getByRole('button',{name:'Contraer Configuración del RAG',exact:true}).click();
  await expect(page.getByRole('button',{name:'Guardar configuración RAG'})).not.toBeVisible();
  await page.getByRole('button',{name:'Expandir Configuración del RAG',exact:true}).click();
  await expect(page.getByRole('button',{name:'Guardar configuración RAG'})).toBeVisible();
  await page.getByRole('button',{name:/03.*Análisis/}).click();
  await page.getByRole('button',{name:'Contraer Laboratorio de prompts',exact:true}).click();
  await expect(page.getByRole('button',{name:/Ejecutar 3 respuestas/})).not.toBeVisible();
  await page.getByRole('button',{name:'Expandir Laboratorio de prompts',exact:true}).click();
  await expect(page.getByRole('button',{name:/Ejecutar 3 respuestas/})).toBeVisible();
});

test('RAG: tooltips y diagrama sincronizado con la traza real',async({page})=>{
  await login(page);
  const uploaded=await page.request.post('/api/admin/documents',{headers:{'X-Admin-Request':'1'},multipart:{metadata:JSON.stringify({title:'Fuente de diagramas',kind:'informativo',source_url:'',valid_from:'2020-01-01',approved:true,enabled:true,notes:''}),file:{name:'diagrama.md',mimeType:'text/markdown',buffer:Buffer.from('Artículo 1. Titulación: solicita orientación con Secretaría Académica. Artículo 2. Matrícula: revisa tu período académico.')}}});
  expect(uploaded.ok()).toBe(true);
  const doc=await uploaded.json();
  await page.reload();
  await page.getByRole('button',{name:/02.*RAG/}).click();
  await page.getByRole('button',{name:'Ayuda: Estrategia',exact:true}).click();
  await expect(page.getByRole('tooltip')).toContainText('Cómo configurarlo');
  await page.getByRole('tooltip').screenshot({path:'test-results/rag-ayuda.png'});
  await page.keyboard.press('Escape');
  await page.getByLabel('Documento',{exact:true}).selectOption(doc.id);
  await page.getByRole('button',{name:'Dividir e indexar documento',exact:true}).click();
  await expect(page.getByLabel('Proceso de indexación realizado',{exact:true})).toBeVisible();
  await page.getByLabel('Consulta de prueba',{exact:true}).fill('titulación');
  await page.getByRole('button',{name:'Buscar evidencia',exact:true}).click();
  const process=page.getByLabel('Proceso de recuperación realizado',{exact:true});
  await expect(process).toBeVisible();
  await process.getByRole('button',{name:'Nodo 4: Consultar vectores',exact:true}).click();
  await expect(process.getByRole('button',{name:'4 Consultar vectores',exact:true})).toHaveAttribute('aria-current','step');
  await expect(process).toContainText('PASO 4 · Omitido');
  await process.getByRole('button',{name:'6 Devolver fragmentos',exact:true}).click();
  await expect(process.getByRole('button',{name:'Nodo 6: Devolver fragmentos',exact:true})).toHaveAttribute('aria-pressed','true');
  await process.screenshot({path:'test-results/rag-proceso.png'});
  await page.setViewportSize({width:390,height:844});
  await page.getByRole('button',{name:'Ayuda: Estrategia',exact:true}).click();
  const rect=await page.getByRole('tooltip').boundingBox();
  expect(rect?.x).toBeGreaterThanOrEqual(0);
  expect((rect?.x??0)+(rect?.width??0)).toBeLessThanOrEqual(390);
  await page.keyboard.press('Escape');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test('fuentes: cancelar limpia un alta y descarta una edición sin guardar',async({page})=>{
  await login(page);
  const upload=await page.request.post('/api/admin/documents',{headers:{'X-Admin-Request':'1'},multipart:{metadata:JSON.stringify({title:'Original de cancelación',kind:'informativo',source_url:'',valid_from:'2020-01-01',approved:false,enabled:true,notes:'Nota original'}),file:{name:'original.md',mimeType:'text/markdown',buffer:Buffer.from('Contenido original que no debe modificarse al cancelar.')}}});
  expect(upload.ok()).toBe(true);
  const original=await upload.json();
  await page.reload();
  const form=page.locator('form.admin-form');
  const mutations:string[]=[];
  page.on('request',request=>{if(request.method()==='POST'&&request.url().includes('/api/admin/documents'))mutations.push(request.url())});
  await form.getByRole('textbox',{name:'Título',exact:true}).fill('Alta incompleta');
  await form.getByLabel('Vigente desde').fill('2020-01-01');
  await form.getByRole('button',{name:'Agregar fuente',exact:true}).click();
  await expect(form.getByRole('alert')).toBeVisible();
  await form.getByLabel('Archivo PDF, DOCX, TXT, MD o CSV').setInputFiles({name:'borrador.md',mimeType:'text/markdown',buffer:Buffer.from('Archivo temporal que no debe subirse.')});
  await form.getByLabel('Observaciones de gestión (privadas)').fill('Descartar nota');
  await form.getByLabel(/He revisado/).check();
  await form.getByRole('button',{name:'Cancelar',exact:true}).click();
  await expect(form.getByRole('textbox',{name:'Título',exact:true})).toHaveValue('');
  await expect(form.getByLabel('Vigente desde')).toHaveValue('');
  await expect(form.getByLabel('Observaciones de gestión (privadas)')).toHaveValue('');
  await expect(form.getByRole('alert')).toHaveCount(0);
  await expect(form.getByLabel(/He revisado/)).not.toBeChecked();
  expect(await form.locator('input[type=file]').evaluate((input:HTMLInputElement)=>input.files?.length)).toBe(0);
  await page.getByRole('row').filter({hasText:'Original de cancelación'}).getByRole('button',{name:'Editar / reemplazar',exact:true}).click();
  await expect(form.getByRole('heading',{name:'Editar / reemplazar fuente',exact:true})).toBeVisible();
  await form.getByRole('textbox',{name:'Título',exact:true}).fill('Cambio que no debe guardarse');
  await form.locator('input[type=file]').setInputFiles({name:'reemplazo.md',mimeType:'text/markdown',buffer:Buffer.from('Reemplazo de prueba que debe descartarse sin enviarse.')});
  await form.getByRole('button',{name:'Cancelar',exact:true}).click();
  await expect(form.getByRole('heading',{name:'Agregar una fuente',exact:true})).toBeVisible();
  await expect(form.getByRole('textbox',{name:'Título',exact:true})).toHaveValue('');
  await expect(page.getByRole('status')).toContainText('Edición cancelada');
  expect(mutations).toHaveLength(0);
  const data=await (await page.request.get('/api/admin/bootstrap')).json();
  const saved=data.documents.find((doc:{id:string})=>doc.id===original.id);
  expect(saved).toMatchObject({title:'Original de cancelación',revision:1,sha256:original.sha256,notes:'Nota original'});
});
