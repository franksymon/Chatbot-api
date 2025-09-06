# 🧠 Medea Mind - Chatbot API

**API Backend para Asistente Clínico Inteligente especializado en Psicología**

[![Backend API](https://img.shields.io/badge/Backend-Flask%20API-blue.svg)](https://chatbot-api-xfum.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-red.svg)](https://flask.palletsprojects.com/)

## 🎯 **Descripción**

API REST desarrollada en Flask que proporciona servicios de chatbot inteligente para psicólogos profesionales. Utiliza LangChain y LangGraph para integrar múltiples modelos de IA (OpenAI GPT y Google Gemini) con prompts especializados para diferentes tipos de consulta clínica.

## ✨ **Características Principales**

- 🤖 **Múltiples proveedores de IA** (OpenAI GPT y Google Gemini)
- 🔄 **Streaming en tiempo real** con Server-Sent Events
- 📋 **Prompts especializados** para consultas clínicas
- 💾 **Gestión de sesiones** con LangGraph checkpoints
- 📄 **Exportación PDF** de informes clínicos
- 📚 **Documentación Swagger** automática
- 🔒 **Configuración segura** de variables de entorno

## 🏗️ **Arquitectura**

### **Stack Tecnológico**
- **Framework**: Flask + extensiones
- **IA**: LangChain + LangGraph
- **Validación**: Marshmallow
- **PDF**: ReportLab
- **CORS**: Flask-CORS
- **Documentación**: Swagger/Flasgger


## 🚀 **Instalación y Configuración**

### **Prerrequisitos**
- Python 3.8+
- pip
- API Keys de OpenAI y/o Google Gemini

### **1. Clonar e Instalar**
```bash
git clone https://github.com/franksymon/Chatbot-api.git
cd Chatbot-api
pip install -r requirements.txt
```

### **2. Configurar Variables de Entorno**
Crear archivo `.env`:
```env
# API Keys (Requeridas)
OPENAI_API_KEY=tu_openai_api_key
GEMINI_API_KEY=tu_gemini_api_key

# Configuración de Modelos
OPENAI_MODEL=gpt-3.5-turbo
GEMINI_MODEL=gemini-2.5-flash
TEMPERATURE=0.7

# Entorno
FLASK_ENV=development
```

### **3. Ejecutar Servidor**
```bash
# Desarrollo
python entrypoint.py

# Producción
gunicorn entrypoint:app
```

**Servidor disponible en**: `http://localhost:5000`
**Documentación Swagger**: `http://localhost:5000/apidocs`

## 📚 **API Endpoints**

### **Base URL**: `/api/v1`

| Método | Endpoint | Descripción | Parámetros |
|--------|----------|-------------|------------|
| `POST` | `/chat` | Enviar mensaje al chatbot | `provider`, `stream` (opcional) |
| `GET` | `/history/{session_id}` | Obtener historial de sesión | `session_id` |
| `GET` | `/prompt-types` | Obtener tipos de consulta disponibles | - |
| `GET` | `/export-pdf/{session_id}` | Exportar historial como PDF | `session_id` |
| `GET` | `/test-connection` | Probar conexión con proveedor IA | `provider` |

### **Ejemplo de Uso**

#### **Streaming**
```bash
curl -X POST "http://localhost:5000/api/v1/chat?provider=openai&stream=true" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Necesito ayuda con documentación clínica",
    "session_id": "session_123",
    "prompt_type": "documentation"
  }'
```

## 🎨 **Tipos de Consulta**

La API soporta 4 tipos especializados de prompts:

1. **`general`**: Asistente clínico general
2. **`case_analysis`**: Análisis y evaluación de casos
3. **`documentation`**: Ayuda con documentación clínica
4. **`resources`**: Técnicas terapéuticas y recursos


## 🌐 **Despliegue en Render**


### **Health Check**
La API incluye un endpoint de salud en `/health` que retorna `"OK"` para verificar el estado del servicio.

## 🔒 **Seguridad**

- ✅ **API Keys** configuradas como variables de entorno
- ✅ **CORS** configurado para permitir orígenes específicos
- ✅ **Validación** de entrada con Marshmallow schemas
- ✅ **Manejo de errores** seguro sin exposición de información sensible
- ✅ **Rate limiting** implícito por proveedor de IA

## 📊 **Características Técnicas**

### **Gestión de Estado**
- **LangGraph**: Orquestación de conversaciones
- **MemorySaver**: Persistencia de sesiones en memoria
- **Checkpoints**: Recuperación de historial por session_id

### **Streaming**
- **Server-Sent Events**: Respuestas en tiempo real
- **Chunked responses**: Procesamiento incremental
- **Error handling**: Manejo robusto de interrupciones

### **Prompts Especializados**
- **Contexto clínico**: Prompts específicos para psicología
- **Terminología DSM-5**: Uso de terminología profesional
- **Ética profesional**: Consideraciones éticas integradas

## 🛠️ **Desarrollo**

### **Estructura de Archivos**
```
├── entrypoint.py           # Punto de entrada
├── requirements.txt        # Dependencias
├── app/
│   ├── __init__.py        # Factory de aplicación Flask
│   ├── chat/
│   │   ├── controller/    # chat_controller.py
│   │   ├── services/      # chat_services.py, pdf_service.py
│   │   ├── models/        # chat_models.py
│   │   ├── schemas/       # chat_schema.py
│   │   └── prompts/       # prompt_manager.py, psychology_prompts.py
│   ├── config/
│   │   ├── config.py      # Configuración global
│   │   └── swagger.py     # Template Swagger
│   └── core/
│       ├── llm_config.py  # Configuración LLM
│       └── base_schema.py # Schema base
```

## 🤝 **Contribuir**

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

## 📄 **Licencia**

Este proyecto está bajo la Licencia MIT.

## 👨‍💻 **Autor**

**Frank Symon**
- GitHub: [@franksymon](https://github.com/franksymon)
- Email: franksymonurbina@gmail.com


### **Logs y Debug**
- Los logs se muestran en consola durante desarrollo
- Para producción, configurar logging apropiado
- Swagger UI disponible en `/apidocs` para testing


⭐ **¡Si te gusta este proyecto, dale una estrella!** ⭐