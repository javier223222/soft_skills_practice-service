import google.generativeai as genai
from typing import Dict,List,Optional,Any
import json 
import logging 
from dataclasses import dataclass

from ..config.app_config import config
from ...core.exceptions.ai_exceptions import(
    GeminiConnectionException,
    GeminiAPIException,
    InvalidPromptException
)

@dataclass
class GeminiResponse:
    content:str
    usage_metadata: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None

class GeminiService:
    def __init__(self):
        self.logger= logging.getLogger(__name__) 
        self.model=None
        self._configure_gemini()
        
    def _configure_gemini(self):
        try:
            genai.configure(api_key=config.gemini_api_key)
            self.model=genai.GenerativeModel('gemini-1.5-flash')
            self.logger.info("Gemini API configured successfully.")
        except Exception as e:
            self.logger.error(f"Error configuring Gemini API: {e}")
            raise GeminiConnectionException("Failed to connect to Gemini API.", original_error=e)
    async def generate_scenario(self,skill_type:str,difficulty_level:int)->Dict[str,Any]:
        prompt=self._build_scenario_prompt(skill_type,difficulty_level)
        try:
            response = await self._generate_content(prompt)
            scenario_data = self._parse_scenario_response(response.content)
            return scenario_data
        except GeminiAPIException as e:
            self.logger.error(f"Error generating scenario: {e}")
            raise   GeminiAPIException("Failed to generate scenario.", original_error=e)
    
    async def evaluate_response(self, scenario_context: str, user_response: str, skill_type: str) -> Dict[str, Any]:
        
        prompt = self._build_evaluation_prompt(scenario_context, user_response, skill_type)
        
        try:
            response = await self._generate_content(prompt)
            return self._parse_evaluation_response(response.content)
        except Exception as e:
            self.logger.error(f"Error evaluating response: {str(e)}")
            raise GeminiAPIException(f"Error evaluating response: {str(e)}", e)
    async def generate_feedback(self, evaluation_result: Dict[str, Any]) -> str:
        """Generar feedback constructivo basado en la evaluación"""
        prompt = self._build_feedback_prompt(evaluation_result)
        
        try:
            response = await self._generate_content(prompt)
            return response.content
        except Exception as e:
            self.logger.error(f"Error generating feedback: {str(e)}")
            raise GeminiAPIException(f"Error generating feedback: {str(e)}", e)
    async def _generate_content(self, prompt: str) -> GeminiResponse:
        """Método base para generar contenido con Gemini"""
        if not prompt or not prompt.strip():
            raise InvalidPromptException("Prompt cannot be empty")
        
        try:
            self.logger.debug(f"Sending prompt to Gemini: {prompt[:100]}...")
            
            response = self.model.generate_content(prompt)
            
            if not response.text:
                raise GeminiAPIException("Empty response from Gemini")
            
            self.logger.debug(f"Received response from Gemini: {response.text[:100]}...")
            
            return GeminiResponse(
                content=response.text,
                finish_reason=getattr(response, 'finish_reason', None)
            )
            
        except Exception as e:
            if isinstance(e, (GeminiAPIException, InvalidPromptException)):
                raise
            self.logger.error(f"Unexpected error in Gemini API call: {str(e)}")
            raise GeminiAPIException(f"Unexpected error: {str(e)}", e)
    def _build_scenario_prompt(self, skill_type: str, difficulty_level: int) -> str:
        """Construir prompt para generar escenarios"""
        return f"""
        Eres un experto en desarrollo de habilidades blandas. Genera un escenario de práctica realista para la habilidad "{skill_type}" con nivel de dificultad {difficulty_level}/5.

        El escenario debe incluir:
        1. Un título atractivo y descriptivo
        2. Una descripción detallada de la situación
        3. El contexto (lugar, participantes, objetivos)
        4. Una situación específica que requiera usar la habilidad "{skill_type}"
        5. Duración estimada en minutos

        Responde ÚNICAMENTE en formato JSON con esta estructura:
    {{
        "title": "Título del escenario",
        "description": "Descripción detallada de la situación",
        "context": {{
            "setting": "Lugar donde ocurre",
            "participants": ["Rol 1", "Rol 2"],
            "objective": "Objetivo principal del escenario"
        }},
    "estimated_duration": 15,
    "initial_situation": "Situación inicial que presenta el desafío"
    }}

Asegúrate de que el escenario sea:
- Realista y profesional
- Apropiado para el nivel de dificultad {difficulty_level}
- Específico para la habilidad "{skill_type}"
- Que requiera una respuesta activa del usuario
"""



    def _build_evaluation_prompt(self, scenario_context: str, user_response: str, skill_type: str) -> str:
        """Construir prompt para evaluar respuestas"""
        return f"""
Eres un experto evaluador de habilidades blandas. Evalúa la siguiente respuesta del usuario a un escenario de práctica.

CONTEXTO DEL ESCENARIO:
{scenario_context}

HABILIDAD A EVALUAR: {skill_type}

RESPUESTA DEL USUARIO:
{user_response}

Evalúa la respuesta considerando:
1. Aplicación efectiva de la habilidad "{skill_type}"
2. Claridad y estructura de la comunicación
3. Consideración de las partes involucradas
4. Viabilidad de la solución propuesta
5. Profesionalismo y tono apropiado

Responde ÚNICAMENTE en formato JSON:
{{
    "overall_score": 85,
    "criteria_scores": {{
        "skill_application": 80,
        "communication_clarity": 90,
        "stakeholder_consideration": 85,
        "solution_viability": 80,
        "professionalism": 90
    }},
    "strengths": ["Fortaleza 1", "Fortaleza 2"],
    "areas_for_improvement": ["Área 1", "Área 2"],
    "specific_feedback": "Comentarios específicos sobre la respuesta"
}}

Puntuación: 0-100 donde 100 es excelente.
"""


    def _build_feedback_prompt(self, evaluation_result: Dict[str, Any]) -> str:
        """Construir prompt para generar feedback"""
        return f"""
Basándote en esta evaluación, genera feedback constructivo y motivador:

EVALUACIÓN:
{json.dumps(evaluation_result, indent=2)}

Genera un feedback que:
1. Reconozca las fortalezas específicas
2. Proporcione sugerencias concretas de mejora
3. Sea motivador y constructivo
4. Incluya ejemplos específicos cuando sea posible
5. Termine con una recomendación para seguir practicando

El feedback debe ser personalizado, profesional y enfocado en el crecimiento.
"""
    def _parse_scenario_response(self, response_text: str) -> Dict[str, Any]:
        """Parsear respuesta JSON del escenario"""
        try:
            
            cleaned_response = response_text.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            
            
            cleaned_response = cleaned_response.replace('\n', ' ')
            cleaned_response = ' '.join(cleaned_response.split())
            cleaned_response = cleaned_response.replace('\"', '"') 
             
            
            return json.loads(cleaned_response.strip())
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse scenario JSON: {e}")
            self.logger.error(f"Response text: {response_text}")
            raise GeminiAPIException(f"Invalid JSON response from Gemini: {str(e)}")
    
    def _parse_evaluation_response(self, response_text: str) -> Dict[str, Any]:
        """Parsear respuesta JSON de la evaluación"""
        try:
            # Limpiar la respuesta si contiene markdown
            cleaned_response = response_text.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            
            return json.loads(cleaned_response.strip())
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse evaluation JSON: {e}")
            self.logger.error(f"Response text: {response_text}")
            raise GeminiAPIException(f"Invalid JSON response from Gemini: {str(e)}")