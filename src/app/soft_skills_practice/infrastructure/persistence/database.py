from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from ...application.config.app_config import config
from .models.simulation_models import (
    SimulationSession, 
    SimulationStep, 
    UserRecommendations, 
    Scenario,
    SkillCatalog
)
from .models.assessment_models import (
    AssessmentQuestion,
    InitialAssessment
)
import logging

class DatabaseConnection:
    def __init__(self):
        self.client = None
        self.database = None
        self.logger = logging.getLogger(__name__)
    
    async def connect(self):
        
        try:
            self.client = AsyncIOMotorClient(config.mongodb_url)
            self.database = self.client[config.mongodb_db_name]
            
           
            await init_beanie(
                database=self.database,
                document_models=[
                    SimulationSession,
                    SimulationStep,
                    UserRecommendations,
                    Scenario,
                    SkillCatalog,
                    AssessmentQuestion,
                    InitialAssessment
                ]
            )
            
            self.logger.info("MongoDB connection established successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            raise Exception(f"Database connection failed: {e}")
    
    async def disconnect(self):
        """Cerrar conexión a MongoDB"""
        if self.client:
            self.client.close()
            self.logger.info("MongoDB connection closed")
    
    async def health_check(self) -> bool:
        """Verificar estado de la conexión"""
        try:
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return False


db_connection = DatabaseConnection()