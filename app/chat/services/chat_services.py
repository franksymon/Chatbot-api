from flask import jsonify, Request, send_file
from langchain_core.messages import HumanMessage, trim_messages
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io
import os

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

        # Trim messages si es necesario
        trimmed_messages = self._trim_messages_if_needed(state["messages"], state["provider"])

        # Aplicar el prompt template a los mensajes recortados
        formatted_messages = prompt_template.format_messages(messages=trimmed_messages)
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

    def export_history_pdf(self, session_id: str):
        """
        Exporta historial como PDF profesional

        :param session_id: ID de la sesión
        :return: Archivo PDF
        """
        try:
            config = {"configurable": {"thread_id": session_id}}
            state = self.app.get_state(config)
            messages = state.values.get("messages", [])

            # Crear PDF en memoria
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Título del informe
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1,  # Centrado
                textColor=colors.darkblue
            )
            story.append(Paragraph("INFORME CLÍNICO PSICOLÓGICO", title_style))
            story.append(Spacer(1, 20))

            # Datos de la sesión
            session_data = [
                ["ID Sesión:", session_id],
                ["Fecha:", datetime.now().strftime('%Y-%m-%d %H:%M')],
                ["Psicólogo:", "Sistema de Apoyo Clínico"],
                ["Número de intercambios:", str(len(messages))]
            ]

            session_table = Table(session_data, colWidths=[2*inch, 3*inch])
            session_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(session_table)
            story.append(Spacer(1, 20))

            # Resumen ejecutivo
            if messages:
                story.append(Paragraph("RESUMEN EJECUTIVO", styles['Heading2']))
                summary = self.generate_session_summary(messages)
                story.append(Paragraph(summary, styles['Normal']))
                story.append(Spacer(1, 20))

            # Desarrollo de la sesión
            story.append(Paragraph("DESARROLLO DE LA SESIÓN", styles['Heading2']))
            story.append(Spacer(1, 12))

            for i, msg in enumerate(messages, 1):
                msg_type = "PSICÓLOGO" if msg.__class__.__name__ == "HumanMessage" else "ASISTENTE CLÍNICO"

                # Estilo para el tipo de mensaje
                msg_style = ParagraphStyle(
                    'MessageType',
                    parent=styles['Normal'],
                    fontSize=10,
                    textColor=colors.darkblue if msg_type == "PSICÓLOGO" else colors.darkgreen,
                    fontName='Helvetica-Bold'
                )

                story.append(Paragraph(f"{i}. {msg_type}:", msg_style))
                story.append(Paragraph(msg.content, styles['Normal']))
                story.append(Spacer(1, 12))

            # Generar PDF
            doc.build(story)
            buffer.seek(0)

            return send_file(
                buffer,
                as_attachment=True,
                download_name=f"informe_clinico_{session_id}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mimetype='application/pdf'
            )

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def generate_session_summary(self, messages):
        """
        Genera un resumen automático de la sesión usando IA
        """
        try:
            if not messages:
                return "No hay mensajes en esta sesión."

            # Crear prompt para resumen
            summary_prompt = """Basándote en esta conversación clínica, genera un resumen profesional de máximo 200 palabras que incluya:
            1. Principales temas tratados
            2. Síntomas o situaciones identificadas
            3. Técnicas o recomendaciones sugeridas
            4. Observaciones relevantes

            Conversación:
            """

            # Agregar mensajes al prompt
            for msg in messages[-10:]:  # Solo últimos 10 mensajes para el resumen
                msg_type = "Psicólogo" if msg.__class__.__name__ == "HumanMessage" else "Asistente"
                summary_prompt += f"\n{msg_type}: {msg.content}"

            # Usar el LLM para generar resumen
            chat_model = self.llm_config.get_chat_model("openai")  # Usar OpenAI por defecto
            summary_msg = HumanMessage(content=summary_prompt)
            response = chat_model.invoke([summary_msg])

            return response.content

        except Exception as e:
            return f"No se pudo generar resumen automático: {str(e)}"

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