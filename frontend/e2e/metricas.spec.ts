import { test, expect } from '@playwright/test';

test('el contexto se envía junto a la consulta y muestra respuesta',async({page})=>{
  let cuerpo:Record<string,string>={};
  await page.route('**/api/chat/stream',route=>{
    cuerpo=route.request().postDataJSON();
    return route.fulfill({contentType:'text/event-stream',body:'event: done\ndata: {"respuesta":"Consulta contextual recibida","estado":"abstencion","requiere_revision_humana":true,"fuentes":[],"modelo_utilizado":"doble","fallback_activado":true,"tiempo_segundos":0.1}\n\n'});
  });
  await page.goto('/');
  await page.getByRole('button',{name:/Personaliza tu orientación/}).click();
  await page.getByLabel('Carrera',{exact:true}).fill('Software');
  await page.getByLabel('Nivel / curso').selectOption('Octavo nivel');
  await page.getByLabel('Modelo',{exact:true}).selectOption('openai');
  await page.getByLabel('Tu consulta').fill('Consulta de titulación');
  await page.getByRole('button',{name:'Enviar consulta'}).click();
  await expect(page.getByText('Consulta contextual recibida')).toBeVisible();
  await expect(page.getByText('Consulta de titulación',{exact:true})).toHaveCount(1);
  expect(cuerpo).toMatchObject({carrera:'Software',curso:'Octavo nivel',modelo_preferido:'openai'});
  await page.screenshot({path:'test-results/chat-contexto.png',fullPage:true});
});

test('ruta pública /metricas carga en móvil sin desbordar',async({page})=>{
  await page.setViewportSize({width:390,height:844});
  await page.route('**/api/metricas',route=>route.fulfill({json:{ventana:'Últimos 2000 eventos',consultas:2,llamadas:3,errores:1,fallbacks:1,latencia_media:1.2,latencia_p95:2,tokens_entrada:30,tokens_salida:20,tokens_total:50,sin_uso_reportado:1,tipos_respuesta:{abstencion:2},por_modelo:{gemini:2,openai:1},por_error:{autenticacion:1},recientes:[]}}));
  await page.goto('/metricas');
  await expect(page.getByRole('heading',{name:'Métricas de uso'})).toBeVisible();
  await expect(page.getByText('Actividad reciente')).toBeVisible();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  await page.screenshot({path:'test-results/metricas-movil.png',fullPage:true});
});
