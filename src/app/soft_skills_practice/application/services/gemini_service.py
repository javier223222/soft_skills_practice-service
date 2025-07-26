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
        You are an expert in soft skills development. Generate a realistic practice scenario for the skill "{skill_type}" with a difficulty level of {difficulty_level}/5.

        The scenario must include:
        1. An attractive and descriptive title
        2. A detailed description of the situation
        3. The context (location, participants, objectives)
        4. A specific situation that requires using the skill "{skill_type}"
        5. Estimated duration in minutes

        Respond ONLY in JSON format with this structure:
        {{
        "title": "Scenario title",
        "description": "Detailed description of the situation",
        "context": {{
            "setting": "Location where it takes place",
            "participants": ["Role 1", "Role 2"],
            "objective": "Main objective of the scenario"
        }},
        "estimated_duration": 15,
        "initial_situation": "Initial situation presenting the challenge"
        }}

    Make sure the scenario is:
    - Realistic and professional
    - Appropriate for difficulty level {difficulty_level}
    - Specific to the skill "{skill_type}"
    - Requires an active response from the user
    """



    def _build_evaluation_prompt(self, scenario_context: str, user_response: str, skill_type: str) -> str:
        """Construir prompt para evaluar respuestas"""
        return f"""
    You are an expert evaluator of soft skills. Evaluate the following user response to a practice scenario.

    SCENARIO CONTEXT:
    {scenario_context}

    SKILL TO EVALUATE: {skill_type}

    USER RESPONSE:
    {user_response}

    Evaluate the response considering:
    1. Effective application of the skill "{skill_type}"
    2. Clarity and structure of communication
    3. Consideration of the stakeholders involved
    4. Feasibility of the proposed solution
    5. Professionalism and appropriate tone

    Respond ONLY in JSON format:
    {{
        "overall_score": 85,
        "criteria_scores": {{
        "skill_application": 80,
        "communication_clarity": 90,
        "stakeholder_consideration": 85,
        "solution_viability": 80,
        "professionalism": 90
        }},
        "strengths": ["Strength 1", "Strength 2"],
        "areas_for_improvement": ["Area 1", "Area 2"],
        "specific_feedback": "Specific comments about the response"
    }}

    Score: 0-100 where 100 is excellent.
    """


    def _build_feedback_prompt(self, evaluation_result: Dict[str, Any]) -> str:
        """Build prompt to generate feedback"""
        return f"""
    Based on this evaluation, generate constructive and motivating feedback:

    EVALUATION:
    {json.dumps(evaluation_result, indent=2)}

    Generate feedback that:
    1. Recognizes specific strengths
    2. Provides concrete suggestions for improvement
    3. Is motivating and constructive
    4. Includes specific examples when possible
    5. Ends with a recommendation to continue practicing

    The feedback should be personalized, professional, and focused on growth.
    """
    def _parse_scenario_response(self, response_text: str) -> Dict[str, Any]:
        """Parsear respuesta JSON del escenario"""
        try:

            
            cleaned_response = response_text.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            
            
       
             
            
            return json.loads(cleaned_response.strip())
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse scenario JSON: {e}")
            self.logger.error(f"Response text: {response_text}")
            raise GeminiAPIException(f"Invalid JSON response from Gemini: {str(e)}")
    
    def _parse_evaluation_response(self, response_text: str) -> Dict[str, Any]:
        """Parsear respuesta JSON de la evaluación"""
        try:
            
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