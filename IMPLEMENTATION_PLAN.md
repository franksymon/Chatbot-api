# Plan de Implementación - Chatbot para Psicólogos

## 🎯 Objetivo
Migrar el chatbot actual a LangGraph siguiendo el tutorial oficial, manteniendo la arquitectura existente y especializándolo para psicólogos.

## 📊 Estado Actual vs Objetivo

### ✅ Ya Implementado
- API REST con Flask
- Integración OpenAI + Gemini
- Validación con Marshmallow
- Documentación Swagger
- Arquitectura modular limpia

### ❌ Faltante (Crítico)
- **Persistencia de conversaciones**
- **Historial de mensajes**
- **Prompts especializados para psicólogos**
- **Frontend React + TypeScript**
- **Gestión de sesiones múltiples**

## 🏗️ Arquitectura Objetivo

```
app/
├── chat/
│   ├── services/
│   │   ├── chat_services.py      # LangGraph implementation
│   │   └── memory_service.py     # Gestión de memoria
│   ├── prompts/
│   │   ├── psychology_prompts.py # Prompts especializados
│   │   └── base_prompts.py       # Prompts base
│   ├── models/
│   │   └── chat_models.py        # Modelos de datos
│   └── schemas/
│       └── chat_schema.py        # Validación extendida
├── core/
│   ├── llm_config.py            # Mantener actual
│   └── graph_config.py          # Nueva configuración LangGraph
└── frontend/                    # Nueva carpeta React
```

## 📋 Fases de Implementación

### **FASE 1: Migración a LangGraph Base** ⏱️ 2-3 horas
**Objetivo**: Reemplazar lógica actual con LangGraph manteniendo funcionalidad

#### Conceptos a Implementar:
- **Messages**: HumanMessage, AIMessage, SystemMessage
- **State**: Estructura para mantener conversación
- **Graph**: Flujo de procesamiento
- **Memory**: Persistencia básica en memoria

#### Archivos a Modificar:
- `chat_services.py` - Migrar a LangGraph
- `requirements.txt` - Agregar langgraph>=0.2.28
- `chat_schema.py` - Extender para session_id

#### Resultado Esperado:
```python
# Antes
messages = [HumanMessage(content=data["message"])]
response = chat_model.invoke(messages)

# Después  
config = {"configurable": {"thread_id": session_id}}
response = app.invoke({"messages": [HumanMessage(content=message)]}, config)
```

### **FASE 2: Especialización Psicológica** ⏱️ 3-4 horas
**Objetivo**: Crear prompts y contexto específico para psicólogos

#### Conceptos a Implementar:
- **Prompt Templates**: Plantillas especializadas
- **System Messages**: Contexto clínico
- **Multi-modal prompts**: Diferentes tipos de consulta

#### Nuevos Archivos:
- `app/chat/prompts/psychology_prompts.py`
- `app/chat/models/psychology_models.py`

#### Funcionalidades:
- Prompt para evaluación inicial
- Prompt para seguimiento
- Prompt para crisis
- Validación de terminología clínica

### **FASE 3: Gestión Avanzada de Memoria** ⏱️ 2-3 horas
**Objetivo**: Optimizar historial y manejo de conversaciones largas

#### Conceptos a Implementar:
- **Message Trimming**: Límites de contexto
- **Session Management**: Múltiples usuarios
- **Persistent Storage**: Base de datos opcional

#### Funcionalidades:
- Límite de tokens por conversación
- Resumen automático de sesiones largas
- Exportar historial de paciente

### **FASE 4: Frontend React + Streaming** ⏱️ 4-5 horas
**Objetivo**: Interfaz de usuario profesional con streaming

#### Tecnologías:
- React + TypeScript
- Streaming de respuestas
- Interfaz tipo chat profesional

#### Funcionalidades:
- Chat en tiempo real
- Indicadores de escritura
- Historial visual
- Exportar conversaciones

### **FASE 5: Optimizaciones y Deploy** ⏱️ 2-3 horas
**Objetivo**: Preparar para producción

#### Funcionalidades:
- Docker containerization
- Variables de entorno
- Logging estructurado
- Tests básicos
- Deploy en Render/Vercel

## 🔧 Detalles Técnicos por Fase

### FASE 1 - Implementación Detallada

#### 1.1 Instalar Dependencias
```bash
pip install langgraph>=0.2.28
```

#### 1.2 Crear State Model
```python
from typing import TypedDict, List
from langchain_core.messages import BaseMessage

class ChatState(TypedDict):
    messages: List[BaseMessage]
    provider: str
    session_id: str
```

#### 1.3 Migrar ChatServices
```python
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver

class ChatServices:
    def __init__(self, request: Request):
        self.request = request
        self.llm_config = LLMConfig()
        self.app = self._create_graph()
    
    def _create_graph(self):
        workflow = StateGraph(state_schema=ChatState)
        workflow.add_node("model", self._call_model)
        workflow.add_edge(START, "model")
        return workflow.compile(checkpointer=MemorySaver())
```

#### 1.4 Actualizar Endpoint
```python
def chat(self, data: ChatSchema, params: dict):
    session_id = data.get("session_id", "default")
    config = {"configurable": {"thread_id": session_id}}
    
    state = {
        "messages": [HumanMessage(content=data["message"])],
        "provider": params.get("provider")
    }
    
    result = self.app.invoke(state, config)
    return jsonify({"response": result["messages"][-1].content})
```

## 📝 Criterios de Éxito por Fase

### Fase 1 ✅
- [ ] Conversación mantiene contexto
- [ ] Múltiples sesiones funcionan
- [ ] API actual sigue funcionando
- [ ] Tests básicos pasan

### Fase 2 ✅  
- [ ] Prompts específicos para psicólogos
- [ ] Respuestas más profesionales
- [ ] Terminología clínica correcta

### Fase 3 ✅
- [ ] Conversaciones largas no fallan
- [ ] Memoria optimizada
- [ ] Exportar historial funciona

### Fase 4 ✅
- [ ] Frontend React funcional
- [ ] Streaming implementado
- [ ] UX profesional

### Fase 5 ✅
- [ ] Deploy exitoso
- [ ] Documentación completa
- [ ] Prueba técnica lista

## 🚀 Próximos Pasos

1. **Revisar este plan** - ¿Algo que agregar/modificar?
2. **Comenzar Fase 1** - Migración básica a LangGraph
3. **Validar cada fase** antes de continuar
4. **Mantener tu estilo de código** en toda la implementación

---
*Tiempo total estimado: 13-18 horas*
*Prioridad: Fases 1-2 son críticas para la prueba técnica*
