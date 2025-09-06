from flask import jsonify, Request, Response
from langchain_core.messages import HumanMessage, trim_messages
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
import json

# Schema
from app.chat.schemas.chat_schema import ChatSchema

# Models
from app.chat.models.chat_models import ChatState

# Services
from app.chat.services.pdf_service import PDFService

# Prompts
from app.chat.prompts.prompt_manager import PromptManager

# Core
from app.core.llm_config import LLMConfig

class ChatServices:
    def __init__(self, request: Request):
        self.request = request
        self.llm_config = LLMConfig()
        self.pdf_service = PDFService()
        self.app = self._create_graph()

    def _create_graph(self):
        """
        Crea el grafo de ejecución de LangGraph.
        """
        workflow = StateGraph(state_schema=ChatState)
        workflow.add_node("model", self._call_model)
        workflow.add_edge(START, "model")
        return workflow.compile(checkpointer=MemorySaver())

    def _trim_messages_if_needed(self, messages, provider: str):
        """
        Recorta mensajes si son demasiados 
        """
        try:
            chat_model = self.llm_config.get_chat_model(provider)

            trimmed = trim_messages(
                messages,
                max_tokens=4000,
                strategy="last",
                token_counter=chat_model,
                include_system=True,
                allow_partial=False,
                start_on="human"
            )

            return trimmed
        except Exception as e:
            print(f"Warning: Trimming failed: {e}")
            return messages

    def _call_model(self, state: ChatState):
        """
        Llama al modelo LLM con el estado actual usando prompts especializados.
        """
        chat_model = self.llm_config.get_chat_model(state["provider"])
        prompt_template = PromptManager.get_prompt(state["prompt_type"])

        # Trim messages
        trimmed_messages = self._trim_messages_if_needed(state["messages"], state["provider"])

        # Aplicar el prompt template a los mensajes recortados
        formatted_messages = prompt_template.format_messages(messages=trimmed_messages)
        response = chat_model.invoke(formatted_messages)
        return {"messages": [response]}

    def _stream_model_response(self, state: dict, config: dict):
        """
        Genera streaming de respuesta del modelo LLM.

        :param state: Estado actual de la conversación
        :param config: Configuración de la sesión
        :return: Generador de chunks de texto
        """
        chat_model = self.llm_config.get_chat_model(state["provider"])
        prompt_template = PromptManager.get_prompt(state["prompt_type"])

        trimmed_messages = self._trim_messages_if_needed(state["messages"], state["provider"])
        formatted_messages = prompt_template.format_messages(messages=trimmed_messages)

        accumulated_content = ""
        for chunk in chat_model.stream(formatted_messages):
            if hasattr(chunk, 'content') and chunk.content:
                accumulated_content += chunk.content  
                yield accumulated_content  
        try:
            full_response = chat_model.invoke(formatted_messages)
            self.app.update_state(config, {"messages": [full_response]})
        except Exception as e:
            print(f"Warning: Could not save complete message to state: {e}")

    def _stream_response(self, state: dict, config: dict):
        """
        Genera respuesta streaming usando Server-Sent Events (SSE).
        :param state: Estado inicial para LangGraph
        :param config: Configuración de la sesión
        :return: Response con streaming SSE
        """
        def generate():
            try:
                yield f"data: {json.dumps({'type': 'start'})}\n\n"

                for chunk in self._stream_model_response(state, config):
                    if chunk:
                        yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"

                yield f"data: {json.dumps({'type': 'done'})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Cache-Control'
            }
        )

    def chat(self, data: ChatSchema, query_params: dict):
        """
        Servicio para enviar mensajes al chatbot.
        Soporta tanto respuestas normales como streaming según el parámetro 'stream'.
        :param data: Datos de la petición in body
        :param query_params: Parámetros de la petición in query
        :return: Respuesta del chatbot (JSON normal o SSE stream)
        """

        if not query_params.get("provider"):
            raise ValueError("Proveedor no especificado")

        data = ChatSchema().load(data)
        session_id = data.get("session_id", "default")
        prompt_type = data.get("prompt_type", "general")
        stream = query_params.get("stream", "false").lower() == "true"

        config = {"configurable": {"thread_id": session_id}}

        state = {
            "messages": [HumanMessage(content=data["message"])],
            "provider": query_params.get("provider"),
            "session_id": session_id,
            "prompt_type": prompt_type
        }

        if stream:
            return self._stream_response(state, config)
        else:
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

    def export_history_pdf(self, session_id: str):
        """Exporta historial como PDF profesional"""
        try:
            config = {"configurable": {"thread_id": session_id}}
            state = self.app.get_state(config)
            messages = state.values.get("messages", [])

            buffer = self.pdf_service.generate_clinical_report(session_id, messages, self.llm_config)
            return self.pdf_service.create_download_response(buffer, session_id)

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

        :param query_params: Parámetros de la petición in query
        :return: Resultado de la prueba
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