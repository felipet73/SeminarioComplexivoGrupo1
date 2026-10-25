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
  await expect(page.getByText(/Comparación simulada/)).toBeVisible({timeout:20000});
  await expect(page.locator('.simulation-answer')).toHaveCount(3);
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
  await expect(page.getByText(/Comparación simulada/)).toBeVisible({timeout:20000});
  await expect(page.locator('.simulation-answer')).toHaveCount(3);
  await page.getByRole('button',{name:'Completar datos y repetir comparación'}).first().click();
  const dialog=page.getByRole('dialog');
  await dialog.getByRole('textbox',{name:'Carrera',exact:true}).fill('Software');
  await dialog.getByRole('button',{name:'Volver a consultar'}).click();
  await expect(dialog).not.toBeVisible();
  await expect(page.locator('.simulation-context')).toContainText('Software');
  await expect(page.getByText(/Comparación simulada/)).toBeVisible({timeout:20000});
  await expect(page.locator('.simulation-answer')).toHaveCount(3);
  await expect(page.getByRole('button',{name:'Completar datos y repetir comparación'})).toHaveCount(0);
  await page.setViewportSize({width:390,height:844});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.screenshot({path:'test-results/admin-chat-movil.png',fullPage:true});
});
