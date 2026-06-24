

🧾 RESUMEN DE 30/04/2026  (GestorCan)
🔧 Backend

✔ Endpoint PDF de estancias funcionando
✔ Uso de joinedload para traer cliente + mascota
✔ Generación de PDF con fpdf
✔ Corrección de errores (temp_dir, imports, etc.)

📄 PDF (albarán)

✔ Estructura profesional tipo CanResort
✔ Cabecera con logo
✔ Pie con logo2 + datos empresa
✔ Datos completos:

cliente
mascota
servicios
totales

✔ Formato mejorado:

columnas
negritas en etiquetas
separadores
sin None
💾 Almacenamiento

✔ Guardado en:

media/albaranes/

✔ Nombre dinámico (anti-caché)

🧠 Decisión importante (muy buena)

✔ Los PDFs NO son críticos
✔ Se regeneran desde la BD
✔ Backups ligeros

👉 Esto es diseño de sistema serio

🚀 ESTADO ACTUAL

👉 Ya tienes:

✔ App funcional
✔ Flujo completo (crear → PDF)
✔ Documento profesional
✔ Base sólida para crecer

👉 Esto ya es un producto real, no un prototipo





05/05/2026

🧠 📌 RESUMEN DEL ESTADO ACTUAL
🚀 Backend (FastAPI)
✔ CRUD de estancias funcionando
✔ Sistema de tarifas dinámico implementado
✔ Cálculo de precios en backend (correcto)
✔ Endpoint:
PUT /estancias/{id}/marcar-pagado
💻 Frontend
✔ Formulario de nueva estancia operativo
✔ Cálculo automático:
días ✔
precio día ✔
extras ✔
cámaras ✔
transporte ✔
veterinario ✔
✔ Dashboard funcionando
🧾 PDF
✔ Albarán funcional y correcto
✔ Desglose de servicios
✔ Total correcto
💰 Pagos
✔ Lógica backend terminada
🔜 Falta interfaz visual (listado)
📋 EN PROCESO

👉 Listado de estancias con:

ver estado pagado
botón marcar pagado
🎯 OBJETIVO PARA MAÑANA

👉 Crear un listado profesional de estancias

Con:

tabla limpia
estado (pagado / pendiente)
botón marcar pagado
navegación desde dashboard




06/05/2026
# GestorCan — Resumen sesión actual

## Estado general del proyecto

SaaS para residencias caninas desarrollado con:

* FastAPI
* SQLAlchemy
* Jinja2
* PostgreSQL / SQLite
* Frontend dashboard HTML + CSS

Arquitectura actual modular:

```text
app/
├── routers/
├── models/
├── templates/
├── static/
├── services/
├── repositories/
├── schemas/
└── main.py
```

---

# Módulo ESTANCIAS — Estado actual

## Backend operativo

* CRUD de estancias funcionando
* Sistema de tarifas dinámico funcionando
* Cálculo de precios backend correcto
* PDF de albarán funcionando
* Endpoint marcar pagado funcionando

Endpoint existente:

```text
PUT /estancias/{id}/marcar-pagado
```

Además se implementó:

```text
POST /estancias/{id}/marcar-pagado-listado
```

---

# LISTADO DE ESTANCIAS — IMPLEMENTADO

Ruta principal:

```text
/estancias/listado
```

## Funcionalidades implementadas

### Tabla profesional de estancias

Columnas actuales:

* Albarán
* Cliente
* DNI Cliente
* Entrada
* Hora salida
* Salida
* Habitación
* Observaciones
* Mascota
* Precio día
* Nº días
* Extras
* Importe extras
* Cámaras
* Veterinario
* Transporte
* Kilómetros
* Total
* Pagado
* Acciones

---

## Estados visuales

### Facturación

Color fila:

* Verde → facturada
* Rojo → no facturada

Campo añadido:

```python
facturado = Column(Boolean, default=False)
```

SQLite actualizado con:

```sql
ALTER TABLE estancias
ADD COLUMN facturado BOOLEAN DEFAULT 0;
```

---

## Pagado

Badge independiente:

* Sí
* No

Separado correctamente de facturación.

---

# Botones operativos

## Facturar

Ruta:

```text
POST /estancias/{id}/facturar
```

Actualmente:

* solo marca `facturado=True`
* cambia color fila
* preparado para futura lógica de facturación real

---

## Cobrar

Ruta:

```text
POST /estancias/{id}/marcar-pagado-listado
```

Marca estancia como pagada.

---

## PDF

Botón operativo:

```text
/albaranes/{id}/pdf
```

---

# Funcionalidades UX implementadas

## Buscador global

Filtra por cualquier texto de la fila.

---

## Ordenación por columnas

JavaScript frontend:

* orden ascendente/descendente
* soporte texto y números

---

## Doble clic → editar estancia

Ruta:

```text
/estancias/{id}/editar
```

Abre formulario de edición.

---

# EXPORTACIÓN EXCEL

Ruta:

```text
/estancias/exportar-excel
```

Implementada con:

```python
openpyxl
StreamingResponse
```

## Pendiente revisión futura

Mejorar:

* formato
* estilos
* anchos automáticos
* fechas
* totales
* filtros
* logos
* exportación profesional

Guardar como tarea futura:
“Revisión módulo listados/exportación Excel”.

---

# DASHBOARD

## Navegación corregida

Ruta dashboard:

```text
/Dashboard
```

Se solucionaron:

* errores 404
* errores 500
* problemas de contexto Jinja

Variables necesarias:

```python
datos
modulos
titulo
```

---

## Sidebar integrado

Enlace lateral operativo:

```text
/estancias/listado
```

---

# Problemas detectados hoy

## Dashboard

`dashboard.html` depende de:

```jinja
datos
modulos
```

No puede renderizarse sin ellas.

---

## base.html

Usa:

```jinja
{{ titulo }}
```

Todas las rutas HTML deben pasar:

```python
"titulo": "..."
```

---

# Próximo bloque: FACTURACIÓN + VERIFACTU

## Objetivo siguiente chat

Diseñar arquitectura completa de:

```text
ESTANCIA
   ↓
ALBARÁN
   ↓
FACTURA
   ↓
VERIFACTU
```

---

# Objetivos del siguiente desarrollo

## Facturación

Implementar:

* tabla facturas
* numeración automática
* series
* PDF factura
* relación estancia-factura
* marcar estancia facturada automáticamente
* listado de facturas
* edición controlada

---

## VeriFactu

Diseñar correctamente desde el inicio:

* hash encadenado
* registro de facturación
* QR AEAT
* firma
* eventos
* estados
* estructura independiente
* compatibilidad SQLite/PostgreSQL
* módulo desacoplado del core SaaS

---

# Importante

Mantener arquitectura modular:

```text
router
→ service
→ repository
→ db
```

Evitar lógica pesada en routers.


11/05/2026
Estado actual — GestorCan
Dashboard Clientes
Edición de clientes funcional.
Gestión visual moderna completada.
Mascotas asociadas mostradas en cards.
Fotos de mascotas funcionando correctamente.
Subida de imágenes mediante selector de archivos (type="file").
Eliminación individual de mascotas implementada.
Tamaños de mascota:
Pequeño
Mediano
Grande
Gigante
Mascotas
Alta y edición funcionando.
Campo observaciones añadido.
Corrección de subida de fotos:
ya no guarda UploadFile en BD
guarda ruta de imagen.
Corrección de edición:
ya no duplica mascotas
ahora modifica correctamente.
PDFs
Albaranes
Generación PDF estable.
Si el PDF ya existe:
abre el existente
no genera duplicados.
Nombre cliente ya incluye:
nombre + apellidos.
Facturas
Flujo completo implementado:
Desde listado de estancias
Botón “Facturar”
Vista previa PDF
Confirmación
Generación real
Registro BD
VeriFactu integrado.
Vista previa PDF embebida en iframe.
Diseño visual integrado con dashboard.
Preview separado de facturas reales.
PDFs preview ya no ensucian facturas_pdf.
VeriFactu
Integración funcionando desde crear_factura_desde_estancia.
Flujo:
factura
registro
hash
pdf
guardado.
CSS / Dashboard
Vista previa PDF responsive ajustada.
Cards mascotas corregidas.
Fotos mascotas:
tamaño final correcto:
width: 110px
height: 150px

Próximo desarrollo
Habitaciones / Perreras

Se comenzará:

diseño de habitaciones
tipos de habitaciones
nombres
capacidad
estados
posiblemente colores/mapa visual
Informes

Inicio del sistema de informes:

ocupación
entradas/salidas
facturación
resúmenes PDF
estadísticas















POLÍTICA DE ARRANQUE VERIFACTU

Las facturas migradas desde sistemas anteriores
se conservan únicamente con fines históricos y de consulta.

No forman parte de la cadena VeriFactu.

La cadena VeriFactu oficial comienza con la primera
factura emitida por GestorCan en producción durante 2027.















PENDIENTES


□ Añadir tipo_documento en clientes
    - DNI
    - NIE
    - CIF
    - PASAPORTE
    - OTRO

□ Validación matemática de letra DNI

□ Validación matemática de letra NIE

□ Validación completa CIF

□ Validación básica Pasaporte

□ Adaptar XML AEAT
    - NIF
    - IDOtro

□ Mostrar validación en alta/edición de clientes

□ Normalizar documentos
    - mayúsculas
    - sin espacios
    - sin guiones



MEJORA FUTURA — Servicios adicionales en estancias

Objetivo:
Permitir añadir servicios parametrizables desde la tabla tarifas,
independientes de los extras.

Ejemplos:
- Pienso
- Medicación
- Adiestramiento
- Paseo extra
- Tratamiento veterinario diario

Funcionamiento:
Tarifa.concepto = "servicio"

unidad = dia
    importe = precio × días

unidad = km
    importe = precio × kilómetros

unidad = unidad
    importe = precio único

Interfaz:
Nueva sección "Servicios adicionales"

Servicio: [desplegable]
Importe: [calculado automáticamente]

Persistencia:
Añadir en estancias:
- servicio_extra
- importe_servicio_extra

Integración:
Incluir en recalcularTotal()
Estado actual de estancias

✅ Precio estancia dinámico desde BD.
✅ Selección automática según comportamiento de mascota.
✅ Extras dinámicos desde BD.
✅ Cámaras dinámicas desde BD.
✅ Transporte dinámico desde BD.
✅ Veterinario dinámico desde BD.
✅ Total recalculado automáticamente.

Pendiente documentado

🔹 Servicios adicionales parametrizables (Pienso, Medicación, etc.).

Con esto el módulo de estancias queda bastante sólido y preparado para seguir creciendo sin tener que volver a tocar precios en el código. 🚀
