# Instrucciones de Desarrollo — Proyecto TeleMedLink

Este documento define reglas de codificación, arquitectura y comportamiento para GitHub Copilot al trabajar en este repositorio.  
**Objetivo:** mantener consistencia, calidad, seguridad y evitar regresiones entre microservicios.

---

## 1) Contexto del Proyecto

TeleMedLink es una plataforma de telemedicina integral para Bolivia.

- **Arquitectura:** Ecosistema de **microservicios desacoplados**, con interacción **asíncrona** y segura.
- **Contexto regional:** Bolivia (C.I., Matrícula Profesional MSyD, moneda en Bs.).
- **Bases de datos:**
  - **Supabase (PostgreSQL)** para datos transaccionales.
  - **MongoDB Atlas** para datos clínicos no estructurados.

---

## Documentación funcional y requisitos (referencia obligatoria)

Para cualquier cambio (nuevo feature, bugfix, endpoint, evento asíncrono, UI o regla):
- Revisar flujos: ../docs/ARQUITECTURA.md
- Revisar los microservicios: ../docs/MICROSERVICIOS.md

Regla de trabajo:
1) Identificar la HU objetivo y el flujo/malla afectado.
2) Listar RN aplicables y Pruebas de Aceptación relevantes.
3) Proponer plan por pasos pequeños y verificación (tests/PA).
4) Recién entonces generar/editar código.

Si durante el trabajo detectas que falta un detalle o hay contradicciones en los flujos, sugiere actualizar docs/WORKFLOWS.md.
Puedes sugerir nuevas HU o subtareas técnicas si identificas un gap funcional o técnico, pero siempre con justificación basada en los requisitos y flujos definidos.

- NO QUIERO QUE SE ROMPA EL FUNCIONAMIENTO QUE SE TIENE ANTES DE UNA NUEVA ITERACIÓN, SIEMPRE DEBE FUNCIONAR CORRECTAMENTE Y CUMPLIR CON LOS REQUISITOS FUNCIONALES Y DE NEGOCIO DEFINIDOS EN LOS DOCUMENTOS DE REFERENCIA.
- CONSIDERA TODO LO QUE SE NECESITA EN EL PROYECTO, BACKEND Y FRONTEND, ASÍ COMO LOS FLUJOS, HU, PA Y SUBTAREAS TÉCNICAS DEFINIDAS EN LOS DOCUMENTOS DE REFERENCIA.
- CONSIDERA TODO LO AVANZADO Y LOS ARCHIVOS QUE SE TIENE EN EL PROYECTO ANTES DE LA SIGUIENTE O NUEVA ITERACIÓN, NO PROPONGAS NADA QUE HAYA SIDO ELIMINADO O QUE NO ESTÉ EN EL PROYECTO ACTUAL.
- responde y da explicaciones en español.
- LOS NUEVOS CAMBIOS NO DEBEN AFECTAR AL FUNCIONAMIENTO DEL PROYECTO, DEBEN CUMPLIR Y FUNCIONAR CORRECTAMENTE, AL IGUAL QUE DEBEN ESTAR DESARROOLLADOS COMPLETOS Y CON NIVEL LOGICO ALTO DE PROGRAMACIÓN
---

## 2) Estándares de Código (MANDATORIOS)

### 2.1 Nomenclatura
- Usar **camelCase** para:
  - variables
  - funciones
  - nombres de archivos
  - claves de JSON
- **No usar caracteres especiales** como “ñ” en ninguna parte del código (usar “nn”).
- Clases y tipos en **PascalCase**.
- Constantes en **UPPER_SNAKE_CASE** (si aplica al lenguaje o al estándar del módulo).
- Evitar abreviaturas ambiguas (`tmp`, `foo`, `bar`) salvo ejemplos mínimos.
- Nombres de variables y funciones deben ser **descriptivos** y reflejar claramente su propósito.
- Nombres de variables, funcione y metodos deben ser **en español** para mantener consistencia y facilitar colaboración internacional.
- usar '-' para separar palabras en nombres de archivos (ej: `auth-service.py`).

### 2.2 Formato
- Usar **tabulaciones (tabs)** en lugar de espacios para indentación.
- Código limpio y **autodocumentado** (nombres expresivos y comentarios solo cuando aporten valor).
- **Tipado estricto**:
  - Type hints en Python.
  - En **JavaScript**, usar **JSDoc** para documentar tipos/contratos (parámetros, retornos, objetos) y mejorar autocompletado/validación.
  - No usar TypeScript en este repositorio (no .ts / .tsx). Usar JavaScript (.js / .jsx).
- Evitar `any` o tipos genéricos sin especificar claramente su propósito y limitaciones.
- NO USAR EMOJIS DE NINGUNA CLASE PARA COMENTARIOS NI EN NOMBRES DE ARCHIVOS, FUNCIONES O VARIABLES.

### 2.3 Principios de diseño
- **Alta cohesión:** cada función/clase debe hacer una sola cosa bien.
- **Bajo acoplamiento:** un servicio no debe depender de la implementación interna de otro.
- **Modularidad:** separar claramente:
  - lógica de negocio (domain/service)
  - acceso a datos (Repository Pattern)
  - controladores (API / handlers)
- Aplicar principios **SOLID** en toda la estructura.

### 2.4 Estilo de código
- **Evitar “God classes”** o módulos con responsabilidades múltiples.
- Manejar errores con **try/except** (Python) o **try/catch** (JS) y siempre proporcionar mensajes de error descriptivos (sin filtrar secretos).
- Usar códigos HTTP correctos en respuestas de API (4xx para errores del cliente,
- 5xx para errores del servidor) y mantener consistencia en el formato de respuesta (ej. `{ success: false, error: "Mensaje descriptivo" }`).

### 2.5 Frontend
- Para el frontend, seguir las convenciones de React y Tailwind CSS, manteniendo la estructura de componentes clara y reutilizable.
- Cada componente debe estar en su propio archivo, con estilos específicos aplicados mediante clases de Tailwind.
- Evitar lógica compleja dentro de los componentes; extraerla a hooks personalizados o servicios cuando sea necesario.
- Priorizar el estilo Responsive y la accesibilidad (usar etiquetas semánticas, atributos ARIA, etc.).

### 2.6 Backend
- Para el backend, seguir las mejores prácticas de FastAPI, como usar Pydantic para validación de datos y mantener una estructura clara entre routers, servicios y repositorios.
- Implementar autenticación y autorización de manera consistente, utilizando JWT y respetando las políticas de RLS de Supabase o MongoDB.
- Mantener la lógica de negocio separada de la lógica de acceso a datos, y evitar acoplamientos innecesarios entre microservicios.

---

## 3) Estructura de Microservicios

El proyecto se divide en las siguientes carpetas/servicios (respetar límites y responsabilidades):

1. **authService**  
   Gestión de identidades, roles y JWT (Supabase Auth).

2. **directoryService**  
   Buscador de médicos, especialidades y geolocalización.

3. **schedulingService**  
   Gestión de agendas, slots y transacciones de citas.

4. **storageService**  
   Gestión de archivos (estudios médicos) con Supabase Storage.

5. **clinicalService**  
   Historiales médicos, recetas y auditoría (MongoDB Atlas).

6. **communicationService**  
   Señalización WebRTC y chat en tiempo real (Redis).

---

## 4) Reglas de Interacción y Generación (Cómo debe trabajar Copilot)

### 4.1 Iteración antes de “código masivo”
- Antes de generar muchos archivos o cambios grandes:
    1) explicar la lógica propuesta,
    2) enumerar pasos,
    3) confirmar supuestos,
    4) recién entonces proponer el código final.
- Iterar sobre el mensaje: si falta información, hacer **máximo 3 preguntas** concretas.
- Si el usuario no especifica lenguaje/entorno, sugiere uno y explica el porqué.

### 4.2 No Breaking Changes
- Al editar funciones existentes:
    - **no romper dependencias** en otros módulos/servicios.
    - si el cambio es drástico, proponer estrategia de:
        - migración gradual, o
        - versionado de API/contratos, o
        - feature flags (si aplica).
- Evitar cambios globales innecesarios; encapsular lo nuevo en módulos/funciones nuevas.

### 4.3 Modularidad en archivos
- Preferir **muchos archivos pequeños y especializados** en vez de uno grande.
- Evitar “God classes” y módulos con responsabilidades múltiples.

### 4.4 Manejo de errores
- Implementar siempre manejo de errores (try/except o try/catch según lenguaje).
- Mensajes de error **descriptivos** (sin filtrar secretos).
- Usar **códigos HTTP correctos** (4xx cliente, 5xx servidor) y respuestas consistentes.

### 4.5 Diseño y separación de capas (aplicar siempre)
- Separar:
    - dominio/servicios (reglas de negocio)
    - repositorios (acceso a datos)
    - controladores/handlers (API)
- Preferir dependencias hacia abstracciones cuando reduzca acoplamiento.

---

## 5) Tecnologías Recomendadas (Preferencias)

- **Backend:** Python con **FastAPI** (asíncrono).
- **Frontend:** React con Tailwind CSS.
- **Seguridad:**
    - cifrar datos sensibles cuando corresponda,
    - cumplir políticas de **RLS** en Supabase.

---

## 6) Formato de respuesta recomendado (para el chat)

Siempre responder con esta estructura:

1) **Resumen** (1–2 líneas)  
2) **Siguiente paso** (concretísimo)  
3) **Explicación** (breve, en puntos)  
4) **Ejemplo de código** (pequeño, modular, tipado y consistente)  
5) **Checklist de buenas prácticas aplicadas**  
6) **Pregunta(s) de validación** (1–2) para iterar  

---

## 7) Checklist rápido (usar antes de finalizar una respuesta)

- ¿Cumple naming (camelCase/PascalCase, sin “ñ” → usar “nn”)?  
- ¿Indentación con tabs (no espacios)?  
- ¿Tipado estricto aplicado (sin `any`, con type hints)?  
- ¿Alta cohesión y bajo acoplamiento?  
- ¿Cambios encapsulados, sin romper contratos?  
- ¿Errores manejados con mensajes claros + HTTP status correcto?  
- ¿Arquitectura respeta límites entre microservicios?  

