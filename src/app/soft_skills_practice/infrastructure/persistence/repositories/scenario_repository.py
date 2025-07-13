from typing import List, Optional, Dict, Any
from ..models.simulation_models import Scenario
from .base_repository import BaseRepository

class ScenarioRepository(BaseRepository[Scenario]):
    """Repositorio para gestionar escenarios"""
    
    def __init__(self):
        super().__init__(Scenario)
    
    async def find_by_scenario_id(self, scenario_id: str) -> Optional[Scenario]:
        """Buscar escenario por scenario_id"""
        return await Scenario.find_one(
            Scenario.scenario_id == scenario_id
        )
    
    async def find_by_skill_type(self,skill_type: str,page:int=1,limit:int=10) ->tuple[List[Scenario],int]:
        
        skip=(page-1)*limit
        total_count = await Scenario.find(
            Scenario.skill_type == skill_type
        ).count()
        scenario=await Scenario.find(
            Scenario.skill_type == skill_type
        ).sort(-Scenario.is_popular, -Scenario.usage_count).skip(skip).limit(limit).to_list()

      

        
        return scenario,total_count
    
    async def find_by_difficulty(self, difficulty_level: int) -> List[Scenario]:
        """Buscar escenarios por nivel de dificultad"""
        return await Scenario.find(
            Scenario.difficulty_level == difficulty_level
        ).sort(-Scenario.is_popular).to_list()
    
    async def find_by_skill_and_difficulty(self, skill_type: str, 
                                         difficulty_level: int) -> List[Scenario]:
        """Buscar escenarios por habilidad y dificultad"""
        return await Scenario.find(
            Scenario.skill_type == skill_type,
            Scenario.difficulty_level == difficulty_level
        ).sort(-Scenario.is_popular, -Scenario.usage_count).to_list()
    
    async def find_popular_scenarios(self,page:int=1,limit:int=10) ->tuple[List[Scenario],int]:
        """Buscar escenarios populares"""
        skip=(page-1)*limit
        total_count=await Scenario.find(
            Scenario.is_popular == True
        ).count()

        scenarios=await Scenario.find(
            Scenario.is_popular == True
        ).sort(-Scenario.usage_count).skip(skip).limit(limit).to_list()
        return scenarios,total_count


    
    async def find_scenarios(self)->List[Scenario]:
        
        return await Scenario.find(
            Scenario.is_popular == False
        ).sort( -Scenario.usage_count).to_list()
    async def find_by_tags(self, tags: List[str]) -> List[Scenario]:
        """Buscar escenarios por etiquetas"""
        return await Scenario.find(
            Scenario.tags.in_(tags)
        ).sort(-Scenario.is_popular).to_list()
    
    async def increment_usage_count(self, scenario_id: str) -> bool:
        """Incrementar contador de uso de un escenario"""
        scenario = await self.find_by_scenario_id(scenario_id)
        if scenario:
            scenario.usage_count += 1
            await scenario.save()
            return True
        return False
    
    async def get_random_scenario(self, skill_type: str, difficulty_level: int = None) -> Optional[Scenario]:
        """Obtener un escenario aleatorio"""
        query = {"skill_type": skill_type}
        if difficulty_level:
            query["difficulty_level"] = difficulty_level
        
        scenarios = await Scenario.find(query).to_list()
        if scenarios:
            import random
            return random.choice(scenarios)
        return None
    
    async def get_skill_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de habilidades"""
        pipeline = [
            {
                "$group": {
                    "_id": "$skill_type",
                    "total_scenarios": {"$sum": 1},
                    "total_usage": {"$sum": "$usage_count"},
                    "avg_difficulty": {"$avg": "$difficulty_level"},
                    "popular_count": {
                        "$sum": {"$cond": [{"$eq": ["$is_popular", True]}, 1, 0]}
                    }
                }
            }
        ]
        
        result = await Scenario.aggregate(pipeline).to_list()
        return {item["_id"]: item for item in result}
    
    async def search_scenarios(self, query: str, skill_type: str = None) -> List[Scenario]:
        
        search_filter = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"tags": {"$in": [query.lower()]}}
            ]
        }
        
        if skill_type:
            search_filter["skill_type"] = skill_type
        
        return await Scenario.find(search_filter).sort(-Scenario.is_popular).to_list()
    def calculate_pagination_info(self,page:int,limit:int,total_counts:int)->dict:
        total_pages=(total_counts + limit - 1) // limit
        has_next=page<total_pages
        has_previous=page>1
        return {
                    "current_page":page,
                    "page_size":limit,
                    "total_item":total_counts,
                    "total_pages":total_pages,
                    "has_next":has_next,
                    "has_previous":has_previous,
        }
    async def create_scenario(self, scenario) -> Scenario:
    
       
        new_scenario=Scenario(**scenario)
        await new_scenario.insert()
        return new_scenario

        
        
        



