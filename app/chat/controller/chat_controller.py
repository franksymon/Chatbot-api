
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
					session_id:
						type: string
						example: "user_123"
						description: "ID de sesión para mantener contexto"
					prompt_type:
						type: string
						example: "general"
						description: "Tipo de consulta: general, case_analysis, documentation, resources"
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

@chat_controller.route("/history/<session_id>", methods=["GET"])
def get_history(session_id):
	"""
	Obtener historial de conversación
	---
	tags:
		- Chatbot
	summary: Obtener historial de una sesión
	produces:
		- application/json
	parameters:
		-	in: path
			name: session_id
			required: true
			type: string
			example: "user_123"
	responses:
		200:
			description: Historial obtenido
			schema:
				type: object
				properties:
					messages:
						type: array
						items:
							type: object
		400:
			description: Error
	"""
	return chat_services.get_history(session_id)

@chat_controller.route("/prompt-types", methods=["GET"])
def get_prompt_types():
	"""
	Obtener tipos de prompt disponibles
	---
	tags:
		- Chatbot
	summary: Obtener tipos de consulta disponibles
	produces:
		- application/json
	responses:
		200:
			description: Tipos de prompt disponibles
			schema:
				type: object
				properties:
					prompt_types:
						type: object
					default:
						type: string
	"""
	return chat_services.get_prompt_types()

@chat_controller.route("/export-pdf/<session_id>", methods=["GET"])
def export_history_pdf(session_id):
	"""
	Exportar historial como PDF profesional
	---
	tags:
		- Chatbot
	summary: Exportar historial de sesión como informe PDF
	produces:
		- application/pdf
	parameters:
		-	in: path
			name: session_id
			required: true
			type: string
			example: "user_123"
	responses:
		200:
			description: PDF generado y descargado
			content:
				application/pdf:
					schema:
						type: string
						format: binary
		400:
			description: Error
			schema:
				type: object
				properties:
					error:
						type: string
	"""
	return chat_services.export_history_pdf(session_id)
