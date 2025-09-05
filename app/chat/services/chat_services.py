from flask import jsonify, Request
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver

# Schema
from app.chat.schemas.chat_schema import ChatSchema

# Models
from app.chat.models.chat_models import ChatState

# Prompts
from app.chat.prompts.prompt_manager import PromptManager

# Core
from app.core.llm_config import LLMConfig

class ChatServices:
    def __init__(self, request: Request):
        self.request = request
        self.llm_config = LLMConfig()
        self.app = self._create_graph()

    def _create_graph(self):
        """
        Crea el grafo de ejecución de LangGraph.
        """
        workflow = StateGraph(state_schema=ChatState)
        workflow.add_node("model", self._call_model)
        workflow.add_edge(START, "model")
        return workflow.compile(checkpointer=MemorySaver())

    def _call_model(self, state: ChatState):
        """
        Llama al modelo LLM con el estado actual usando prompts especializados.
        """
        chat_model = self.llm_config.get_chat_model(state["provider"])
        prompt_template = PromptManager.get_prompt(state["prompt_type"])

        # Aplicar el prompt template a los mensajes
        formatted_messages = prompt_template.format_messages(messages=state["messages"])
        response = chat_model.invoke(formatted_messages)
        return {"messages": [response]}

    def chat(self, data: ChatSchema, query_params: dict):
        """
        Servicio para enviar mensajes al chatbot.
        :param data: Datos de la petición in body
        :param query_params: Parámetros de la petición in query
        :return: Respuesta del chatbot
        """

        if not query_params.get("provider"):
            raise ValueError("Proveedor no especificado")

        data = ChatSchema().load(data)
        session_id = data.get("session_id", "default")
        prompt_type = data.get("prompt_type", "general")

        config = {"configurable": {"thread_id": session_id}}

        state = {
            "messages": [HumanMessage(content=data["message"])],
            "provider": query_params.get("provider"),
            "session_id": session_id,
            "prompt_type": prompt_type
        }

        result = self.app.invoke(state, config)
        response = result["messages"][-1].content.replace("\n", "").strip()
        return jsonify({"response": response})

    def get_history(self, session_id: str):
        """
        Obtiene el historial de una sesión específica.
        
        :param session_id: ID de la sesión
        :return: Historial de la sesión
        """
        config = {"configurable": {"thread_id": session_id}}
        try:
            state = self.app.get_state(config)
            messages = []
            for msg in state.values.get("messages", []):
                messages.append({
                    "type": msg.__class__.__name__,
                    "content": msg.content
                })
            return jsonify({"messages": messages})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_prompt_types(self):
        """Obtiene los tipos de prompt disponibles"""
        return jsonify({
            "prompt_types": PromptManager.get_available_types(),
            "default": "auto"
        })

    def test_connection(self, query_params: dict):
        """
        Prueba la conexión con el proveedor LLM configurado.
        """
        try:
            if not query_params.get("provider"):
                raise ValueError("Proveedor no especificado")
            result = self.llm_config.test_model_connection(query_params.get("provider"))
            return jsonify(result)
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"❌ Error inicializando LLM: {str(e)}",
                "error": str(e)
            }), 500