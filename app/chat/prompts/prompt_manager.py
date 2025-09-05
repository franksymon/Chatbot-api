from .psychology_prompts import PsychologyPrompts

class PromptManager:
    """Gestor de prompts para diferentes tipos de consulta"""

    PROMPT_TYPES = {
        "general": "Asistente clínico general",
        "case_analysis": "Análisis de casos",
        "documentation": "Documentación clínica",
        "resources": "Recursos terapéuticos"
    }
    
    @staticmethod
    def get_prompt(prompt_type: str = "general"):
        """
        Obtiene el prompt según el tipo de consulta
        """
        prompts = {
            "general": PsychologyPrompts.get_general_prompt(),
            "case_analysis": PsychologyPrompts.get_case_analysis_prompt(),
            "documentation": PsychologyPrompts.get_documentation_prompt(),
            "resources": PsychologyPrompts.get_resources_prompt()
        }

        return prompts.get(prompt_type, prompts["general"])
    

    @staticmethod
    def get_available_types():
        """Retorna los tipos de prompt disponibles"""
        return PromptManager.PROMPT_TYPES
