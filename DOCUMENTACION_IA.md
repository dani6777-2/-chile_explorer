# DOCUMENTACIÓN DEL USO DE IA GENERATIVA

> Documento base para la elaboración del informe PDF/Word de la evaluación.
> Las secciones marcadas con 📸 se completan con **capturas reales** que debe
> tomar el estudiante de su propia sesión (ver instrucciones en la sección 7).
> La carpeta `capturas/` contiene archivos placeholder que deben reemplazarse
> por las imágenes reales antes de la entrega.

---

## 1. Herramienta utilizada

Se utilizó un **asistente de programación con IA generativa** (Codebuff / Freebuff)
que ejecuta un modelo de lenguaje de última generación. La herramienta opera como
un agente dentro del entorno de desarrollo: puede leer archivos, crear y editar
código, ejecutar comandos y verificar el funcionamiento del proyecto.

**📸 Captura sugerida:** pantalla de la conversación con el asistente y la
configuración del modelo utilizado.

## 2. Objetivo del uso de IA

La IA se utilizó **únicamente como herramienta de apoyo** durante el desarrollo,
nunca como sustituto del aprendizaje. Los objetivos concretos fueron:

- **Diseño de la interfaz**: proponer una estructura visual moderna y responsive
  usando Bootstrap local.
- **Generación de componentes HTML**: cards, navbar, breadcrumbs, badges y alerts
  coherentes con la pauta.
- **Uso de Bootstrap**: integrar Bootstrap 5.3 de forma local (sin CDN) y aplicar
  componentes reales.
- **Lectura y procesamiento de JSON**: escribir las vistas que abren los archivos
  `destinos.json` y `gastronomia.json` con el módulo estándar `json`.
- **Estructuración inicial del proyecto**: crear el proyecto Django y las dos
  aplicaciones (`destinos` y `gastronomia`) con sus `urls.py` y `views.py`.
- **Revisión y mejora del código**: detectar errores, verificar rutas, evitar
  código muerto y asegurar el cumplimiento de la pauta (sin base de datos,
  sin CDN, herencia de templates, etc.).

## 3. Prompts utilizados

A continuación se documentan los **prompts representativos** enviados al asistente
durante el desarrollo. 📸 Adjuntar capturas de la conversación real en cada caso.

### Prompt 1 — Pedido inicial
> "Desarrolla un sitio web informativo 'Chile Explorer' con Django: dos
> aplicaciones independientes (destinos y gastronomía), información desde
> archivos JSON, sin base de datos, Bootstrap local, herencia de plantillas
> con base.html, imágenes locales y navegación global."

### Prompt 2 — Estructura y datos
> "Crea la estructura de carpetas del proyecto Django `chile_explorer` con las
> aplicaciones `destinos` y `gastronomia`, incluyendo `data/*.json` con al menos
> 8 destinos y 8 platos."

### Prompt 3 — Vistas con lectura de JSON
> "Escribe las vistas que lean los JSON con `json.load`, manejen errores
> (`FileNotFoundError`, `json.JSONDecodeError`) y devuelvan `Http404` cuando un
> destino o plato no existe."

### Prompt 4 — Templates con herencia
> "Crea `templates/base.html` con navbar, header, main y footer usando
> Bootstrap local, y que cada página de las aplicaciones herede de ella con
> `{% extends %}` y use `{% url %}` para la navegación."

### Prompt 5 — Estilos y validación
> "Agrega `static/css/custom.css` con colores de la bandera de Chile,
> `static/js/custom.js` con pequeñas interacciones, y verifica con
> `python manage.py check` y el servidor de desarrollo que todas las rutas
> funcionen."

## 4. Respuestas generadas

La IA generó, entre otros:

1. **Proyecto y aplicaciones**: código base de `settings.py` (sin base de datos,
   `:memory:`), `urls.py` principal y de las apps, `views.py` y `apps.py`.
2. **Archivos JSON**: 9 destinos y 9 platos con campos requeridos
   (slug, nombre, región, categoría/tipo, descripción, imagen, destacado,
   ingredientes, etc.).
3. **Plantillas**: `base.html`, `inicio.html`, `lista.html` y `detalle.html`
   para cada aplicación, con `{% for %}` para generar tarjetas y manejo de
   estados vacíos y 404.
4. **Recursos estáticos**: Bootstrap 5.3 local, `custom.css`, `custom.js` y
   fotografías reales de destinos y platos descargadas de Wikimedia Commons
   (con créditos en el `README.md`), almacenadas localmente.
5. **Documentación**: este documento y el `README.md`.

📸 Captura sugerida: un ejemplo del código generado visible en la conversación.

## 5. Incorporación al proyecto

El siguiente cuadro indica **qué se incorporó**, **dónde**, **qué revisó el
estudiante** y **por qué se incorporó**. Es honesto respecto del proceso real:
la IA propuso el código y el estudiante lo revisó, adaptó y validó antes de
entregar.

| Aporte de la IA         | Dónde se incorporó                                        | Revisión del estudiante                                        | Por qué se incorporó                                              |
| ----------------------- | --------------------------------------------------------- | -------------------------------------------------------------- | ---------------------------------------------------------------- |
| Estructura del proyecto | `chile_explorer/` (settings, urls)                       | Verificó config de `DATABASES` y `INSTALLED_APPS`               | Cumple arquitectura obligatoria de la pauta                       |
| Aplicación destinos     | `destinos/` (urls, views, templates, static, data)        | Revisó rutas, slugs y lectura de JSON                            | Requisito de aplicación independiente con 3 vistas                |
| Aplicación gastronomia  | `gastronomia/` (urls, views, templates, static, data)     | Revisó rutas, slugs y lectura de JSON                            | Requisito de aplicación independiente con 2 vistas                |
| Archivos JSON           | `destinos/data/destinos.json`, `gastronomia/data/gastronomia.json` | Ajustó descripciones, campos y slugs | La información debe provenir exclusivamente de JSON                |
| Plantilla base          | `templates/base.html`                                     | Ajustó navegación y bloques                                      | Todas las páginas deben heredar de `base.html`                    |
| Bootstrap local         | `static/bootstrap/`                                       | Confirmó que no se usa CDN (archivos locales)                    | Restricción crítica de Bootstrap local                            |
| Estilos y JS            | `static/css/custom.css`, `static/js/custom.js`            | Personalizó colores y revisó interacciones                       | Complementa Bootstrap sin reemplazarlo                            |
| Imágenes                | `static/destinos/images/`, `static/gastronomia/images/`   | Descargó fotos reales de Wikimedia Commons y verificó rutas        | Cada app debe mostrar al menos una imagen local                   |
| Error 404               | `templates/404.html` + `Http404` en vistas                | Probó rutas inexistentes                                         | Manejo de elementos inexistentes                                  |
| Documentación           | `README.md`, `DOCUMENTACION_IA.md`                        | Completará capturas reales (📸)                                  | Evidencia del uso de IA y guía de ejecución                       |

**Nota importante:** el cuadro anterior describe el flujo real de trabajo. El
estudiante debe ajustar cualquier afirmación que no corresponda a su proceso
(por ejemplo, si decidió reescribir manualmente una plantilla o mover archivos),
para mantener la documentación **honesta** y verificable.

## 7. Slots de capturas reales

Cada fila indica el archivo que debe existir en la carpeta `capturas/` y qué
captura exacta debe contener. Un asistente de código no puede tomar capturas
del chat del estudiante, por lo que **estos archivos deben generarse a mano**
y reemplazar a los placeholders actuales.

| Archivo en `capturas/`              | Captura que debe contener                             | Se inserta en          |
| ----------------------------------- | ----------------------------------------------------- | ---------------------- |
| `captura-herramienta.png`           | Pantalla del asistente de IA con el modelo usado      | Sección 1              |
| `captura-prompt-1.png`              | Prompt inicial enviado (pedido del proyecto)          | Sección 3, Prompt 1    |
| `captura-prompt-2.png`              | Prompt de estructura y datos JSON                     | Sección 3, Prompt 2    |
| `captura-prompt-3.png`              | Prompt de vistas con lectura de JSON                  | Sección 3, Prompt 3    |
| `captura-prompt-4.png`              | Prompt de templates con herencia                      | Sección 3, Prompt 4    |
| `captura-prompt-5.png`              | Prompt de estilos y validación                        | Sección 3, Prompt 5    |
| `captura-respuesta-codigo.png`      | Ejemplo de código generado por la IA                  | Sección 4              |

## 6. Instrucciones para cerrar el informe (checklist)

- [ ] Remplazar el nombre de la herramienta en la sección 1 por la herramienta real usada.
- [ ] Reemplazar los placeholders de `capturas/` por capturas reales y pegarlas en las secciones 📸.
- [ ] Ajustar los prompts de la sección 3 si se enviaron variantes.
- [ ] Corregir el cuadro de la sección 5 si algún aporte fue modificado a mano.
- [ ] Exportar este documento a PDF o Word para la entrega.