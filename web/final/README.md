# APEX Intelligence · Google Apps Script

Web app de lectura basada en la paleta D. Portada: bases del concurso y las cinco respuestas. Pestañas adicionales: análisis y cómo se obtuvo. Sin paquetes npm, autenticación propia ni APIs en tiempo real. La portada incluye una fotografía alojada en Wikimedia Commons.

## Publicar

1. Crear un proyecto independiente en [script.google.com](https://script.google.com/).
2. Sustituir `Code.gs` con el contenido de este directorio.
3. Crear un archivo HTML llamado **`Index`** en el editor de Apps Script; pegar el contenido de `Index.html` (incluidos `<!doctype html>` y el script final).
4. En **Configuración del proyecto**, habilitar **Mostrar archivo de manifiesto `appsscript.json` en el editor** y sustituirlo por el de este directorio.
5. Guardar y usar **Implementar → Nueva implementación → Aplicación web**. Elegir **Ejecutar como: yo** y el nivel de acceso que corresponda a las reglas internas de BBVA; no seleccionar acceso público sin autorización. Abrir la URL de prueba o del despliegue y comprobar las tres pestañas.

No se requiere `.clasp.json`: ese archivo contiene el identificador de un proyecto propio y solo sería necesario si más adelante se automatiza la sincronización con `clasp`. `Index.html` usa una plantilla de Apps Script (`<?!= payload ?>`), por lo que **no** se puede abrir directamente como HTML local; para comparar el diseño sin despliegue está `web/prototypes/paleta-d.html`.

## Fotografía

- No hace falta subir `web/images/`: la portada carga una versión optimizada de la vista aérea directamente desde Wikimedia Commons. Si la red de BBVA bloquea Wikimedia, la foto no aparecerá, pero el pronóstico seguirá legible.
- Autor: [ProtoplasmaKid](https://commons.wikimedia.org/wiki/File:Vista_a%C3%A9rea_del_Aut%C3%B3dromo_Hermanos_Rodr%C3%ADguez_01.jpg); licencia [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). La atribución y el aviso del encuadre adaptado aparecen bajo la imagen.
- Las fotografías de Checo en `web/images/` no se publican: comprobar sus permisos de uso antes de incorporarlas.

## Datos y actualización

- La instantánea del pronóstico está en `getPredictionData_()` de `Code.gs`, basada en `reports/strategy_prediction_dto.json`. Los porcentajes de victoria provienen de `reports/informe_cientifico.md`; la categoría «4 o más Safety Cars» es el complemento (1,75 %) de los valores 0 a 3 del DTO.
- Las reglas están transcritas de `docs/reto_f1_transcripcion.md`. El modelo **no se ejecuta** en Apps Script: se publica su predicción previa a la clasificación.
- No se muestran resultados de carrera ni puntos obtenidos: la página conserva solo el pronóstico previo. Antes de incorporar datos posteriores a la carrera, verificar una fuente oficial y preservar la instantánea de predicciones, fecha y versión desplegada.
- El backtest histórico utiliza un modelo distinto y una puntuación publicada que incluye categorías fijadas como aciertos. Por ello, la web no lo presenta como validación del pronóstico actual.

Autores: Alejandro Rodriguez Rodriguez (`alejandro.rodriguez8@bbva.com`) y Camilo Serrano Fuentes (`camilo.serrano.fuentes@bbva.com`).
