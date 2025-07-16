from typing import List,Optional,Dict,Any
from datetime import datetime,timedelta
from ..models.simulation_models import UserRecommendations
from ..models.base_models import UserSkillProgress
from .base_repository import BaseRepository


class UserRecommendationsRepository(BaseRepository[UserRecommendations]):
    """Repositorio para gestionar recomendaciones de usuarios"""
    
    def __init__(self):
        super().__init__(UserRecommendations)
    
    async def find_by_user_id(self, user_id: str) -> Optional[UserRecommendations]:
        """Buscar recomendaciones de un usuario"""
        return await UserRecommendations.find_one(
            UserRecommendations.user_id == user_id
        )
    
    async def get_or_create_user_recommendations(self, user_id: str) -> UserRecommendations:
        """Obtener o crear recomendaciones para un usuario"""
        recommendations = await self.find_by_user_id(user_id)
        if not recommendations:
            recommendations = UserRecommendations(user_id=user_id)
            await recommendations.insert()
        return recommendations
    
    async def update_skill_progress(self, user_id: str, skill_name: str, 
                                  score: float, session_duration: int) -> bool:
        """Actualizar progreso de una habilidad"""
        recommendations = await self.get_or_create_user_recommendations(user_id)
        
        if skill_name not in recommendations.skills_analytics:
            recommendations.skills_analytics[skill_name] = UserSkillProgress(
                skill_name=skill_name,
                times_practiced=0,
                average_score=0.0,
                best_score=0,
                last_practiced=None,
                difficulty_level=1,
                is_neglected=False,
                natural_ability=None
            )
        
        skill_progress = recommendations.skills_analytics[skill_name]
        
        
        skill_progress.times_practiced += 1
        skill_progress.last_practiced = datetime.utcnow()
        
        
        current_total = skill_progress.average_score * (skill_progress.times_practiced - 1)
        skill_progress.average_score = (current_total + score) / skill_progress.times_practiced
        
        
        if score > skill_progress.best_score:
            skill_progress.best_score = int(score)
        
        
        if skill_progress.natural_ability is None:
            skill_progress.natural_ability = int(score / 10) 
        
       
        if skill_name not in recommendations.usage_patterns.favorite_skills:
            recommendations.usage_patterns.favorite_skills.append(skill_name)
        
        
        if skill_name not in recommendations.recommendation_data.skills_practiced:
            recommendations.recommendation_data.skills_practiced.append(skill_name)
        
        recommendations.recommendation_data.last_skill_practiced = skill_name
        recommendations.recommendation_data.skill_performance[skill_name] = skill_progress.average_score
        
        recommendations.updated_at = datetime.utcnow()
        await recommendations.save()
        
        return True
    
    async def get_neglected_skills(self, user_id: str, days_threshold: int = 30) -> List[str]:
        """Obtener habilidades descuidadas"""
        recommendations = await self.find_by_user_id(user_id)
        if not recommendations:
            return []
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)
        neglected_skills = []
        
        for skill_name, progress in recommendations.skills_analytics.items():
            if progress.last_practiced and progress.last_practiced < cutoff_date:
                neglected_skills.append(skill_name)
        
        return neglected_skills
    
    async def get_recommended_skills(self, user_id: str) -> List[str]:
        """Obtener habilidades recomendadas"""
        recommendations = await self.find_by_user_id(user_id)
        if not recommendations:
            return []
        
        return recommendations.recommendation_data.recommended_next_skills
    
    async def add_skill_recommendation(self, user_id: str, skill_name: str, 
                                     reason: str = None) -> bool:
        """Agregar recomendación de habilidad"""
        recommendations = await self.get_or_create_user_recommendations(user_id)
        
        if skill_name not in recommendations.recommendation_data.recommended_next_skills:
            recommendations.recommendation_data.recommended_next_skills.append(skill_name)
            recommendations.recommendation_data.last_recommendation_date = datetime.utcnow()
            recommendations.updated_at = datetime.utcnow()
            await recommendations.save()
            return True
        
        return False
    
    async def mark_skill_as_neglected(self, user_id: str, skill_name: str) -> bool:
        """Marcar habilidad como descuidada"""
        recommendations = await self.find_by_user_id(user_id)
        if not recommendations or skill_name not in recommendations.skills_analytics:
            return False
        
        recommendations.skills_analytics[skill_name].is_neglected = True
        
        if skill_name not in recommendations.recommendation_data.neglected_skills:
            recommendations.recommendation_data.neglected_skills.append(skill_name)
        
        recommendations.updated_at = datetime.utcnow()
        await recommendations.save()
        
        return True
    
    async def get_user_skill_analytics(self, user_id: str) -> Dict[str, Any]:
        """Obtener análiticas de habilidades del usuario"""
        recommendations = await self.find_by_user_id(user_id)
        if not recommendations:
            return {
                "total_skills": 0,
                "skills_practiced": [],
                "favorite_skills": [],
                "neglected_skills": [],
                "average_performance": 0.0,
                "most_improved_skill": None
            }
        
        skills_data = recommendations.skills_analytics
        
        all_scores = [skill.average_score for skill in skills_data.values()]
        average_performance = sum(all_scores) / len(all_scores) if all_scores else 0.0
        
      
        most_improved_skill = None
        best_improvement = 0
        
        for skill_name, skill_data in skills_data.items():
            if skill_data.times_practiced > 1:
                improvement = skill_data.best_score - (skill_data.natural_ability or 0) * 10
                if improvement > best_improvement:
                    best_improvement = improvement
                    most_improved_skill = skill_name
        
        return {
            "total_skills": len(skills_data),
            "skills_practiced": list(skills_data.keys()),
            "favorite_skills": recommendations.usage_patterns.favorite_skills,
            "neglected_skills": recommendations.recommendation_data.neglected_skills,
            "average_performance": average_performance,
            "most_improved_skill": most_improved_skill
        }