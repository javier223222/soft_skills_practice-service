"""
Configuración DDD - Dependency Injection Container
"""
from typing import Protocol
import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Domain Layer
from ..domain.skill_assessment.repositories import (
    AssessmentRepository, AssessmentQuestionRepository, SkillResultRepository
)
from ..domain.skill_assessment.domain_services import (
    SkillEvaluationService, AssessmentAnalyticsService
)
from ..domain.shared.domain_events import DomainEventPublisher

# Application Layer
from ..application.skill_assessment.handlers import (
    StartAssessmentCommandHandler, SubmitAnswerCommandHandler, 
    CompleteAssessmentCommandHandler
)

# Infrastructure Layer
from ..infrastructure.persistence.skill_assessment.mongo_assessment_repository import MongoAssessmentRepository
from ..infrastructure.messaging.domain_event_publisher_impl import DomainEventPublisherImpl
from ..infrastructure.external_services.gemini_service_impl import GeminiServiceImpl


class DIContainer:
    """Dependency Injection Container para DDD"""
    
    def __init__(self):
        self._database: AsyncIOMotorDatabase = None
        self._repositories = {}
        self._services = {}
        self._handlers = {}
        self._initialized = False
    
    async def initialize(self):
        """Inicializa el container con todas las dependencias"""
        if self._initialized:
            return
        
        # Configurar base de datos
        await self._setup_database()
        
        # Configurar repositorios
        await self._setup_repositories()
        
        # Configurar servicios de dominio
        await self._setup_domain_services()
        
        # Configurar servicios de aplicación
        await self._setup_application_services()
        
        # Configurar handlers
        await self._setup_handlers()
        
        self._initialized = True
    
    async def _setup_database(self):
        """Configura la conexión a la base de datos"""
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        database_name = os.getenv("DATABASE_NAME", "soft_skills_practice")
        
        client = AsyncIOMotorClient(mongodb_url)
        self._database = client[database_name]
    
    async def _setup_repositories(self):
        """Configura repositorios de infraestructura"""
        # Assessment repositories
        self._repositories['assessment'] = MongoAssessmentRepository()
        
        # Question repository (placeholder - implementar según necesidad)
        from ..infrastructure.persistence.skill_assessment.mongo_question_repository import MongoAssessmentQuestionRepository
        self._repositories['question'] = MongoAssessmentQuestionRepository()
        
        # Skill result repository (placeholder)
        from ..infrastructure.persistence.skill_assessment.mongo_skill_result_repository import MongoSkillResultRepository
        self._repositories['skill_result'] = MongoSkillResultRepository()
    
    async def _setup_domain_services(self):
        """Configura servicios de dominio"""
        # Skill evaluation service
        self._services['skill_evaluation'] = SkillEvaluationService(
            self._repositories['question']
        )
        
        # Assessment analytics service
        self._services['assessment_analytics'] = AssessmentAnalyticsService(
            self._repositories['skill_result']
        )
        
        # Domain event publisher
        self._services['domain_event_publisher'] = DomainEventPublisherImpl()
        
        # External AI service
        self._services['gemini_service'] = GeminiServiceImpl()
    
    async def _setup_application_services(self):
        """Configura servicios de aplicación adicionales"""
        # Aquí se pueden agregar más servicios de aplicación
        # como servicios de notificación, cache, etc.
        pass
    
    async def _setup_handlers(self):
        """Configura command y query handlers"""
        # Assessment command handlers
        self._handlers['start_assessment'] = StartAssessmentCommandHandler(
            self._repositories['assessment'],
            self._repositories['question'],
            self._services['domain_event_publisher']
        )
        
        self._handlers['submit_answer'] = SubmitAnswerCommandHandler(
            self._repositories['assessment'],
            self._repositories['question']
        )
        
        self._handlers['complete_assessment'] = CompleteAssessmentCommandHandler(
            self._repositories['assessment'],
            self._repositories['question'],
            self._services['skill_evaluation'],
            self._services['assessment_analytics'],
            self._services['domain_event_publisher']
        )
    
    # Getters para dependency injection
    
    def get_assessment_repository(self) -> AssessmentRepository:
        return self._repositories['assessment']
    
    def get_question_repository(self) -> AssessmentQuestionRepository:
        return self._repositories['question']
    
    def get_skill_result_repository(self) -> SkillResultRepository:
        return self._repositories['skill_result']
    
    def get_skill_evaluation_service(self) -> SkillEvaluationService:
        return self._services['skill_evaluation']
    
    def get_assessment_analytics_service(self) -> AssessmentAnalyticsService:
        return self._services['assessment_analytics']
    
    def get_domain_event_publisher(self) -> DomainEventPublisher:
        return self._services['domain_event_publisher']
    
    def get_start_assessment_handler(self) -> StartAssessmentCommandHandler:
        return self._handlers['start_assessment']
    
    def get_submit_answer_handler(self) -> SubmitAnswerCommandHandler:
        return self._handlers['submit_answer']
    
    def get_complete_assessment_handler(self) -> CompleteAssessmentCommandHandler:
        return self._handlers['complete_assessment']


# Singleton instance
_container: DIContainer = None

async def get_container() -> DIContainer:
    """Obtiene el container singleton"""
    global _container
    if _container is None:
        _container = DIContainer()
        await _container.initialize()
    return _container


# Funciones helper para FastAPI dependency injection

async def get_start_assessment_handler() -> StartAssessmentCommandHandler:
    container = await get_container()
    return container.get_start_assessment_handler()

async def get_submit_answer_handler() -> SubmitAnswerCommandHandler:
    container = await get_container()
    return container.get_submit_answer_handler()

async def get_complete_assessment_handler() -> CompleteAssessmentCommandHandler:
    container = await get_container()
    return container.get_complete_assessment_handler()

async def get_assessment_repository() -> AssessmentRepository:
    container = await get_container()
    return container.get_assessment_repository()

async def get_domain_event_publisher() -> DomainEventPublisher:
    container = await get_container()
    return container.get_domain_event_publisher()


# Configuration classes para diferentes entornos

class DevelopmentConfig:
    """Configuración para desarrollo"""
    DEBUG = True
    MONGODB_URL = "mongodb://localhost:27017"
    DATABASE_NAME = "soft_skills_practice_dev"
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    LOG_LEVEL = "DEBUG"

class ProductionConfig:
    """Configuración para producción"""
    DEBUG = False
    MONGODB_URL = os.getenv("MONGODB_URL")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "soft_skills_practice")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    LOG_LEVEL = "INFO"

class TestConfig:
    """Configuración para tests"""
    DEBUG = True
    MONGODB_URL = "mongodb://localhost:27017"
    DATABASE_NAME = "soft_skills_practice_test"
    GEMINI_API_KEY = "test_key"
    LOG_LEVEL = "DEBUG"


def get_config():
    """Obtiene la configuración basada en el entorno"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "test":
        return TestConfig()
    else:
        return DevelopmentConfig()
