
from flask import Blueprint, request
from ..services.chat_services import ChatServices

chat_controller = Blueprint("chat", __name__)
chat_services = ChatServices(request)

@chat_controller.route("/chat", methods=["POST"])
def chat():
	"""
	Endpoint para enviar mensajes al chatbot
	---
	tags:
		- Chatbot
	summary: Enviar mensaje al chatbot
	produces:
		- application/json
	parameters:
		-	in: body
			name: body
			required: true
			schema:
				type: object
				properties:
					message:
						type: string
						example: "Hola, ¿cómo estás?"
		-	in: query
			name: provider
			required: true
			type: string
			enum: ["openai", "gemini"]
			example: "openai"
	responses:
		200:
			description: Respuesta exitosa
			schema:
				type: string
				example: "Okay"
		400:
			description: Solicitud inválida
			schema:
				type: string
				example: "Bad Request"
	"""
	return chat_services.chat(request.json, request.args)

@chat_controller.route("/test-connection", methods=["GET"])
def test():
	"""
	Endpoint para probar la conexión con OpenAI
	---
	tags:
		- Chatbot
	summary: Probar conexión con OpenAI
	produces:
		- application/json
	parameters:
		-	in: query
			name: provider
			required: true
			type: string
			enum: ["openai", "gemini"]
			example: "openai"
	responses:
		200:
			description: Respuesta exitosa
			schema:
				type: string
				example: "OK"
		400:
			description: Solicitud inválida
			schema:
					type: string
					example: "Bad Request"
		"""
	return chat_services.test_connection(request.args)
