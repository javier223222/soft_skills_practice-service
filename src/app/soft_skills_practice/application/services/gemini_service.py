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
        "{user_response}"

        IMPORTANT - AUTOMATIC PENALTIES FOR POOR RESPONSES:
        - If response is too short (less than 10 words): Maximum score 20/100
        - If response is vague/generic (like "hello", "ok", "yes", "no"): Maximum score 15/100  
        - If response is nonsensical or random characters: Maximum score 5/100
        - If response doesn't address the scenario: Maximum score 25/100
        - If response is completely unrelated to the skill: Maximum score 20/100

        EVALUATION CRITERIA:
        1. **Skill Application** ({skill_type}): Does the response demonstrate understanding and proper use of this specific skill?
        2. **Communication Clarity**: Is the response clear, well-structured, and professional?
        3. **Scenario Relevance**: Does the response directly address the situation presented?
        4. **Solution Quality**: Are proposed actions realistic and well-thought-out?
        5. **Professionalism**: Is the tone and language appropriate for a workplace setting?

        SCORING GUIDELINES:
        - 90-100: Exceptional response that fully demonstrates the skill with clear, actionable solutions
        - 70-89: Good response with solid skill demonstration and clear communication
        - 50-69: Adequate response but missing some key elements or clarity
        - 30-49: Poor response with minimal skill demonstration or major issues
        - 10-29: Very poor response - vague, irrelevant, or shows no understanding
        - 0-9: Completely inappropriate, nonsensical, or no attempt to engage with the scenario

        Respond ONLY in JSON format:
        {{
            "overall_score": 15,
            "criteria_scores": {{
                "skill_application": 10,
                "communication_clarity": 15,
                "scenario_relevance": 20,
                "solution_quality": 10,
                "professionalism": 20
            }},
            "strengths": ["Any positive aspects, even minimal"],
            "areas_for_improvement": ["Specific areas needing work"],
            "response_quality": "vague|appropriate|excellent",
            "specific_feedback": "Detailed explanation of the evaluation, especially for low scores"
        }}

        Be strict with scoring. A response like "hello", "ddd", "ok" should receive very low scores (5-15/100).
        """


    def _build_feedback_prompt(self, evaluation_result: Dict[str, Any]) -> str:
        """Build prompt to generate personal, concise feedback"""
    
        overall_score = evaluation_result.get('overall_score', 0)
        strengths = evaluation_result.get('strengths', [])
        areas_for_improvement = evaluation_result.get('areas_for_improvement', [])
    
        return f"""
You are a mentor giving direct, personal feedback. Based on this evaluation, write a brief, conversational response as if you're speaking directly to the person.

EVALUATION RESULTS:
- Overall Score: {overall_score}/100
- Strengths: {', '.join(strengths) if strengths else 'None identified'}
- Areas to improve: {', '.join(areas_for_improvement) if areas_for_improvement else 'None identified'}

Write feedback that:
- Uses "I" statements (I noticed, I think, I recommend)
- Is 2-3 sentences maximum
- Sounds like a real person talking
- Focuses on 1-2 key points only
- Ends with a simple, actionable suggestion

Examples of good feedback:
- "I liked how you acknowledged the problem, but I think you could be more specific about next steps. Try breaking down your solution into smaller, concrete actions."
- "I noticed you showed good empathy, though your response felt a bit rushed. Take a moment to pause and ask clarifying questions before jumping to solutions."
- "Your communication was clear and professional! I'd love to see you push further by suggesting specific timelines or resources for your proposed solution."

Keep it conversational, personal, and under 50 words.
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