"""
Domain Exceptions para manejo de errores específicos del dominio
"""
from typing import Optional, Dict, Any


class DomainException(Exception):
    """Base exception para todos los errores de dominio"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}


# ============= SKILL ASSESSMENT EXCEPTIONS =============

class AssessmentException(DomainException):
    """Base exception para errores de evaluación"""
    pass


class AssessmentNotStartedException(AssessmentException):
    """Error cuando se intenta operar sobre una evaluación no iniciada"""
    
    def __init__(self, assessment_id: str):
        super().__init__(
            f"Assessment {assessment_id} has not been started",
            "ASSESSMENT_NOT_STARTED",
            {"assessment_id": assessment_id}
        )


class AssessmentAlreadyCompletedException(AssessmentException):
    """Error cuando se intenta completar una evaluación ya finalizada"""
    
    def __init__(self, assessment_id: str):
        super().__init__(
            f"Assessment {assessment_id} has already been completed",
            "ASSESSMENT_ALREADY_COMPLETED",
            {"assessment_id": assessment_id}
        )


class InvalidAssessmentAnswerException(AssessmentException):
    """Error cuando se proporciona una respuesta inválida"""
    
    def __init__(self, question_id: str, provided_answer: str):
        super().__init__(
            f"Invalid answer '{provided_answer}' for question {question_id}",
            "INVALID_ASSESSMENT_ANSWER",
            {"question_id": question_id, "provided_answer": provided_answer}
        )


class InsufficientQuestionsException(AssessmentException):
    """Error cuando no hay suficientes preguntas para una evaluación"""
    
    def __init__(self, skill_type: str, required: int, available: int):
        super().__init__(
            f"Insufficient questions for skill '{skill_type}': required {required}, available {available}",
            "INSUFFICIENT_QUESTIONS",
            {"skill_type": skill_type, "required": required, "available": available}
        )


# ============= SIMULATION EXCEPTIONS =============

class SimulationException(DomainException):
    """Base exception para errores de simulación"""
    pass


class SimulationNotActiveException(SimulationException):
    """Error cuando se intenta operar sobre una simulación inactiva"""
    
    def __init__(self, session_id: str, current_status: str):
        super().__init__(
            f"Simulation {session_id} is not active (current status: {current_status})",
            "SIMULATION_NOT_ACTIVE",
            {"session_id": session_id, "current_status": current_status}
        )


class InvalidSimulationStepException(SimulationException):
    """Error cuando se intenta acceder a un paso inválido"""
    
    def __init__(self, session_id: str, requested_step: int, current_step: int):
        super().__init__(
            f"Invalid step {requested_step} for simulation {session_id} (current step: {current_step})",
            "INVALID_SIMULATION_STEP",
            {"session_id": session_id, "requested_step": requested_step, "current_step": current_step}
        )


class SimulationAlreadyCompletedException(SimulationException):
    """Error cuando se intenta modificar una simulación completada"""
    
    def __init__(self, session_id: str):
        super().__init__(
            f"Simulation {session_id} has already been completed",
            "SIMULATION_ALREADY_COMPLETED",
            {"session_id": session_id}
        )


class InvalidUserResponseException(SimulationException):
    """Error cuando la respuesta del usuario es inválida"""
    
    def __init__(self, session_id: str, validation_errors: list):
        super().__init__(
            f"Invalid user response for simulation {session_id}",
            "INVALID_USER_RESPONSE",
            {"session_id": session_id, "validation_errors": validation_errors}
        )


# ============= LEARNING PATH EXCEPTIONS =============

class LearningPathException(DomainException):
    """Base exception para errores de ruta de aprendizaje"""
    pass


class NoLearningPathAvailableException(LearningPathException):
    """Error cuando no hay ruta de aprendizaje disponible"""
    
    def __init__(self, user_id: str, reason: str):
        super().__init__(
            f"No learning path available for user {user_id}: {reason}",
            "NO_LEARNING_PATH_AVAILABLE",
            {"user_id": user_id, "reason": reason}
        )


class InvalidProgressUpdateException(LearningPathException):
    """Error cuando se intenta actualizar progreso inválidamente"""
    
    def __init__(self, user_id: str, skill_type: str, invalid_value: Any):
        super().__init__(
            f"Invalid progress update for user {user_id} skill {skill_type}: {invalid_value}",
            "INVALID_PROGRESS_UPDATE",
            {"user_id": user_id, "skill_type": skill_type, "invalid_value": str(invalid_value)}
        )


# ============= CONTENT MANAGEMENT EXCEPTIONS =============

class ContentException(DomainException):
    """Base exception para errores de contenido"""
    pass


class ScenarioNotFoundException(ContentException):
    """Error cuando no se encuentra un escenario"""
    
    def __init__(self, scenario_id: str):
        super().__init__(
            f"Scenario {scenario_id} not found",
            "SCENARIO_NOT_FOUND",
            {"scenario_id": scenario_id}
        )


class InvalidScenarioDataException(ContentException):
    """Error cuando los datos del escenario son inválidos"""
    
    def __init__(self, validation_errors: list):
        super().__init__(
            f"Invalid scenario data: {', '.join(validation_errors)}",
            "INVALID_SCENARIO_DATA",
            {"validation_errors": validation_errors}
        )


class ContentGenerationFailedException(ContentException):
    """Error cuando falla la generación de contenido"""
    
    def __init__(self, content_type: str, reason: str):
        super().__init__(
            f"Failed to generate {content_type}: {reason}",
            "CONTENT_GENERATION_FAILED",
            {"content_type": content_type, "reason": reason}
        )


# ============= USER PROGRESS EXCEPTIONS =============

class UserProgressException(DomainException):
    """Base exception para errores de progreso de usuario"""
    pass


class UserNotFoundException(UserProgressException):
    """Error cuando no se encuentra el usuario"""
    
    def __init__(self, user_id: str):
        super().__init__(
            f"User {user_id} not found",
            "USER_NOT_FOUND",
            {"user_id": user_id}
        )


class InvalidUserDataException(UserProgressException):
    """Error cuando los datos del usuario son inválidos"""
    
    def __init__(self, user_id: str, field: str, value: Any):
        super().__init__(
            f"Invalid data for user {user_id}, field '{field}': {value}",
            "INVALID_USER_DATA",
            {"user_id": user_id, "field": field, "value": str(value)}
        )


# ============= BUSINESS RULE EXCEPTIONS =============

class BusinessRuleViolationException(DomainException):
    """Error cuando se viola una regla de negocio"""
    
    def __init__(self, rule_name: str, details: str):
        super().__init__(
            f"Business rule violation: {rule_name} - {details}",
            "BUSINESS_RULE_VIOLATION",
            {"rule_name": rule_name, "details": details}
        )


class ConcurrencyException(DomainException):
    """Error de concurrencia en operaciones de dominio"""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            f"Concurrency conflict for {resource_type} {resource_id}",
            "CONCURRENCY_CONFLICT",
            {"resource_type": resource_type, "resource_id": resource_id}
        )
