from ..config.config import config
from langchain_core.messages import HumanMessage


class LLMConfig:
    def __init__(self):
        self.config = config

    def _init_openai(self):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=self.config.openai_api_key,
            model=self.config.openai_model,
            temperature=self.config.temperature,
        )

    def _init_gemini(self):
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            google_api_key=self.config.gemini_api_key,
            model=self.config.gemini_model,
            temperature=self.config.temperature,
        )

    def get_chat_model(self, provider: str):
        models = {
            "openai": self._init_openai,
            "gemini": self._init_gemini
        }
        if provider not in models:
            raise ValueError(f"Proveedor no soportado: {provider}")
        return models[provider]()

    def get_model_info(self, provider: str):
        info_map = {
            "openai": {
                "provider": "openai",
                "model_name": self.config.openai_model,
            },
            "gemini": {
                "provider": "gemini",
                "model_name": self.config.gemini_model,
            }
        }
        base_info = info_map.get(provider, {})
        base_info["temperature"] = self.config.temperature
        return base_info

    def test_model_connection(self, provider: str):
        try:
            chat_model = self.get_chat_model(provider)
            test_message = [HumanMessage(content="Hello, test message.")]
            response = chat_model.invoke(test_message)

            if not response or not response.content:
                raise RuntimeError("Respuesta vacía del modelo")

            result = {
                "success": True,
                "message": f"✅ Conexión con {provider.upper()} OK",
                "provider": provider,
                "model_info": self.get_model_info(provider),
                "test_response": response.content[:100] + ("..." if len(response.content) > 100 else "")
            }

            print(result["message"])
            return result

        except Exception as e:
            error_result = {
                "success": False,
                "message": f"❌ Error con {provider.upper()}",
                "error": str(e),
                "provider": provider,
                "model_info": self.get_model_info(provider)
            }

            print(f"{error_result['message']}: {error_result['error']}")
            return error_result

