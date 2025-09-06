from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import io

class PDFService:

    def generate_clinical_report(self, session_id: str, messages: list, llm_config=None) -> bytes:
        """Genera informe clínico en PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,
            textColor=colors.darkblue
        )
        story.append(Paragraph("INFORME CLÍNICO PSICOLÓGICO", title_style))
        story.append(Spacer(1, 20))

        # Datos de sesión
        session_data = [
            ["ID Sesión:", session_id],
            ["Fecha:", datetime.now().strftime('%Y-%m-%d %H:%M')],
            ["Psicólogo:", "Sistema de Apoyo Clínico"],
            ["Número de intercambios:", str(len(messages))]
        ]
        
        session_table = Table(session_data, colWidths=[2*inch, 3*inch])
        session_table.setStyle(self._get_table_style())
        story.append(session_table)
        story.append(Spacer(1, 20))

        # Resumen ejecutivo
        if messages:
            story.append(Paragraph("RESUMEN EJECUTIVO", styles['Heading2']))
            summary = self.generate_ai_summary(messages, llm_config) if llm_config else self._generate_summary(messages)
            story.append(Paragraph(summary, styles['Normal']))
            story.append(Spacer(1, 20))

        # Desarrollo de la sesión
        story.append(Paragraph("DESARROLLO DE LA SESIÓN", styles['Heading2']))
        story.append(Spacer(1, 12))

        for i, msg in enumerate(messages, 1):
            msg_type = "PSICÓLOGO" if msg.__class__.__name__ == "HumanMessage" else "ASISTENTE CLÍNICO"
            
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

        doc.build(story)
        buffer.seek(0)
        return buffer

    def create_download_response(self, buffer: io.BytesIO, session_id: str):
        """Crea respuesta Flask para descarga"""
        filename = f"informe_clinico_{session_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    def _get_table_style(self):
        """Estilo para tablas"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])

    def _generate_summary(self, messages: list) -> str:
        """Genera resumen básico"""
        if not messages:
            return "No hay mensajes en esta sesión."

        return f"Sesión con {len(messages)} intercambios. Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M')}."

    def generate_ai_summary(self, messages: list, llm_config) -> str:
        """Genera resumen usando IA"""
        try:
            if not messages:
                return "No hay mensajes en esta sesión."

            summary_prompt = """Basándote en esta conversación clínica, genera un resumen profesional de máximo 200 palabras que incluya:
            1. Principales temas tratados
            2. Síntomas o situaciones identificadas
            3. Técnicas o recomendaciones sugeridas
            4. Observaciones relevantes

            Conversación:
            """

            for msg in messages[-10:]:
                msg_type = "Psicólogo" if msg.__class__.__name__ == "HumanMessage" else "Asistente"
                summary_prompt += f"\n{msg_type}: {msg.content}"

            from langchain_core.messages import HumanMessage
            chat_model = llm_config.get_chat_model("gemini")
            summary_msg = HumanMessage(content=summary_prompt)
            response = chat_model.invoke([summary_msg])

            return response.content

        except Exception as e:
            return f"No se pudo generar resumen automático: {str(e)}"
