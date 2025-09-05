from flask import jsonify, Request
from langchain_core.messages import HumanMessage

# Schema
from app.chat.schemas.chat_schema import ChatSchema

# Core
from app.core.llm_config import LLMConfig

class ChatServices:
    def __init__(self, request: Request):
        self.request = request
        self.llm_config = LLMConfig()

    def chat(self, data: ChatSchema, params: dict):
        if not params.get("provider"):
            raise ValueError("Proveedor no especificado")

        data = ChatSchema().load(data)
        chat_model = self.llm_config.get_chat_model(params.get("provider"))
        messages = [HumanMessage(content=data["message"])]
        response = chat_model.invoke(messages)
        return jsonify({"response": response.content})

    def test_connection(self, params: dict):
        """
        Prueba la conexión con el proveedor LLM configurado.
        """
        try:
            if not params.get("provider"):
                raise ValueError("Proveedor no especificado")
            result = self.llm_config.test_model_connection(params.get("provider"))
            return jsonify(result)
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"❌ Error inicializando LLM: {str(e)}",
                "error": str(e)
            }), 500