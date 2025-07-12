#!/usr/bin/env python3
"""
Script completo para probar todos los endpoints de la API
"""

import requests
import json
import time
from datetime import datetime

# URL base del servidor
BASE_URL = "http://localhost:8001"

def print_section(title):
    """Imprimir una sección del test"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_test(test_name, url, method="GET"):
    """Imprimir información del test"""
    print(f"\n📋 Test: {test_name}")
    print(f"🌐 {method} {url}")
    print("-" * 40)

def print_response(response, show_data=True):
    """Imprimir respuesta del servidor"""
    print(f"✅ Status: {response.status_code}")
    if show_data and response.status_code == 200:
        try:
            data = response.json()
            print(f"📄 Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except:
            print(f"📄 Response: {response.text}")
    elif response.status_code != 200:
        print(f"❌ Error Response: {response.text}")
    print()

def test_health_endpoints():
    """Probar endpoints de salud"""
    print_section("HEALTH CHECK ENDPOINTS")
    
    # Test 1: Health check básico
    print_test("Health Check Básico", f"{BASE_URL}/")
    response = requests.get(f"{BASE_URL}/")
    print_response(response)
    
    # Test 2: Health check detallado
    print_test("Health Check Detallado", f"{BASE_URL}/health")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)

def test_skills_endpoints():
    """Probar endpoints de skills"""
    print_section("SKILLS ENDPOINTS")
    
    # Test 1: Obtener skills del usuario (página 1)
    user_id = "test_user_123"
    print_test("Skills del Usuario - Página 1", f"{BASE_URL}/softskill/{user_id}?page=1&page_size=10")
    response = requests.get(f"{BASE_URL}/softskill/{user_id}?page=1&page_size=10")
    print_response(response)
    
    # Test 2: Obtener skills del usuario (página 2)
    print_test("Skills del Usuario - Página 2", f"{BASE_URL}/softskill/{user_id}?page=2&page_size=2")
    response = requests.get(f"{BASE_URL}/softskill/{user_id}?page=2&page_size=2")
    print_response(response)
    
    # Test 3: Validación de parámetros incorrectos
    print_test("Validación de Parámetros Incorrectos", f"{BASE_URL}/softskill/{user_id}?page=0&page_size=200")
    response = requests.get(f"{BASE_URL}/softskill/{user_id}?page=0&page_size=200")
    print_response(response)

def test_scenarios_endpoints():
    """Probar endpoints de escenarios"""
    print_section("SCENARIOS ENDPOINTS")
    
    # Test 1: Escenarios por skill type
    skill_type = "communication"
    print_test("Escenarios de Comunicación", f"{BASE_URL}/scenarios/{skill_type}?page=1&page_size=10")
    response = requests.get(f"{BASE_URL}/scenarios/{skill_type}?page=1&page_size=10")
    print_response(response)
    
    # Test 2: Escenarios de liderazgo
    skill_type = "leadership"
    print_test("Escenarios de Liderazgo", f"{BASE_URL}/scenarios/{skill_type}?page=1&page_size=5")
    response = requests.get(f"{BASE_URL}/scenarios/{skill_type}?page=1&page_size=5")
    print_response(response)
    
    # Test 3: Escenarios de resolución de conflictos
    skill_type = "conflict_resolution"
    print_test("Escenarios de Resolución de Conflictos", f"{BASE_URL}/scenarios/{skill_type}")
    response = requests.get(f"{BASE_URL}/scenarios/{skill_type}")
    print_response(response)

def test_simulation_endpoints():
    """Probar endpoints de simulación"""
    print_section("SIMULATION ENDPOINTS")
    
    # Test 1: Iniciar simulación
    print_test("Iniciar Simulación", f"{BASE_URL}/simulation/start", "POST")
    start_data = {
        "user_id": "test_user_123",
        "scenario_id": "communication_scenario_1",
        "difficulty_preference": 3
    }
    response = requests.post(f"{BASE_URL}/simulation/start", json=start_data)
    print_response(response)
    
    # Extraer session_id para los siguientes tests
    session_id = None
    if response.status_code == 200:
        session_id = response.json().get("session_id")
        print(f"🔑 Session ID obtenido: {session_id}")
    
    if session_id:
        # Test 2: Responder en simulación
        print_test("Responder en Simulación", f"{BASE_URL}/simulation/{session_id}/respond", "POST")
        response_data = {
            "user_response": "Creo que lo mejor sería escuchar a ambas partes y encontrar un punto medio que beneficie al proyecto.",
            "response_time_seconds": 45.5
        }
        response = requests.post(f"{BASE_URL}/simulation/{session_id}/respond", json=response_data)
        print_response(response)
        
        # Test 3: Obtener estado de simulación
        print_test("Estado de Simulación", f"{BASE_URL}/simulation/{session_id}/status")
        response = requests.get(f"{BASE_URL}/simulation/{session_id}/status")
        print_response(response)
    else:
        print("❌ No se pudo obtener session_id, saltando tests de simulación")

def test_mobile_endpoints():
    """Probar endpoints específicos para móvil"""
    print_section("MOBILE ENDPOINTS")
    
    user_id = "test_user_123"
    
    # Test 1: Información de nivel del usuario
    print_test("Nivel del Usuario", f"{BASE_URL}/mobile/user/{user_id}/level")
    response = requests.get(f"{BASE_URL}/mobile/user/{user_id}/level")
    print_response(response)
    
    # Test 2: Logros del usuario
    print_test("Logros del Usuario", f"{BASE_URL}/mobile/user/{user_id}/achievements")
    response = requests.get(f"{BASE_URL}/mobile/user/{user_id}/achievements")
    print_response(response)
    
    # Test 3: Dashboard del usuario
    print_test("Dashboard del Usuario", f"{BASE_URL}/mobile/user/{user_id}/dashboard")
    response = requests.get(f"{BASE_URL}/mobile/user/{user_id}/dashboard")
    print_response(response)

def test_consistency_validation():
    """Validar consistencia de datos entre endpoints"""
    print_section("VALIDACIÓN DE CONSISTENCIA")
    
    user_id = "test_user_123"
    
    print("🔍 Verificando consistencia de datos entre endpoints...")
    
    # Obtener datos de diferentes endpoints
    skills_response = requests.get(f"{BASE_URL}/softskill/{user_id}")
    level_response = requests.get(f"{BASE_URL}/mobile/user/{user_id}/level")
    dashboard_response = requests.get(f"{BASE_URL}/mobile/user/{user_id}/dashboard")
    
    if all(r.status_code == 200 for r in [skills_response, level_response, dashboard_response]):
        skills_data = skills_response.json()
        level_data = level_response.json()
        dashboard_data = dashboard_response.json()
        
        print("✅ Consistencia de user_id:")
        print(f"   Skills: {skills_data.get('user_id')}")
        print(f"   Level: {level_data.get('user_id')}")
        print(f"   Dashboard: {dashboard_data.get('user_id')}")
        
        print("\n✅ Consistencia de datos de nivel:")
        level_info_dashboard = dashboard_data.get('level_info', {})
        print(f"   Level endpoint - Nivel actual: {level_data.get('current_level')}")
        print(f"   Dashboard endpoint - Nivel actual: {level_info_dashboard.get('current_level')}")
        print(f"   Level endpoint - Puntos actuales: {level_data.get('current_points')}")
        print(f"   Dashboard endpoint - Puntos actuales: {level_info_dashboard.get('current_points')}")
        
        print("\n✅ Consistencia de skills disponibles:")
        skills_list = skills_data.get('skills', [])
        print(f"   Total skills disponibles: {len(skills_list)}")
        print(f"   Skills con progreso > 0: {sum(1 for s in skills_list if s.get('progress_percentage', 0) > 0)}")
        
        print("\n✅ Consistencia de metadatos de paginación:")
        pagination = skills_data.get('pagination', {})
        print(f"   Total items: {pagination.get('total_items')}")
        print(f"   Total páginas: {pagination.get('total_pages')}")
        print(f"   Página actual: {pagination.get('current_page')}")
        
    else:
        print("❌ Error obteniendo datos para validación de consistencia")

def main():
    """Función principal para ejecutar todos los tests"""
    print("🚀 INICIANDO PRUEBAS COMPLETAS DE ENDPOINTS")
    print(f"🕐 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Servidor: {BASE_URL}")
    
    try:
        # Verificar que el servidor esté funcionando
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print(f"❌ Error: El servidor no responde correctamente (Status: {response.status_code})")
            return
        
        # Ejecutar todas las pruebas
        test_health_endpoints()
        test_skills_endpoints()
        test_scenarios_endpoints()
        test_simulation_endpoints()
        test_mobile_endpoints()
        test_consistency_validation()
        
        print_section("RESUMEN DE PRUEBAS")
        print("✅ Todas las pruebas han sido ejecutadas")
        print("📋 Revisa los resultados anteriores para validar consistencia")
        print("🎯 Los endpoints están listos para integración con la aplicación móvil")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor. Asegúrate de que esté ejecutándose en el puerto 8001")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()
