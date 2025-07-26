import requests
import json

def test_simulation_status():
    """Probar el endpoint de estado de simulación"""
    base_url = "http://localhost:8000"
    
    print("🔍 Probando endpoint de estado de simulación...")
    
    # 1. Primero iniciar una simulación para tener un session_id
    print("\n1. 📋 Iniciando simulación para obtener session_id...")
    start_data = {
        "user_id": "status_test_user",
        "scenario_id": "68671d8ee0fb8100716b7ff2"
    }
    
    response = requests.post(f"{base_url}/simulation/start", json=start_data)
    if response.status_code != 200:
        print(f"❌ Error starting simulation: {response.status_code}")
        return
    
    start_result = response.json()
    session_id = start_result["session_id"]
    print(f"✅ Simulation started - Session ID: {session_id}")
    
    # 2. Test initial status
    print(f"\n2. 📊 Getting initial status...")
    response = requests.get(f"{base_url}/simulation/{session_id}/status")
    if response.status_code != 200:
        print(f"❌ Error getting status: {response.status_code}")
        print(response.text)
        return
    
    status_result = response.json()
    print(f"✅ Status obtained successfully")
    print(f"📈 Progreso: {status_result['progress_summary']['progress_percentage']}%")
    print(f"⏱️ Tiempo transcurrido: {status_result['progress_summary']['time_spent_minutes']} min")
    print(f"🎯 Estado: {status_result['progress_summary']['status_description']}")
    
    # 3. Responder al test inicial
    print(f"\n3. 💬 Respondiendo al test inicial...")
    response_data = {
        "user_response": "Tengo experiencia moderada en escucha activa. He trabajado en equipos donde he tenido que mediar conflictos técnicos, especialmente cuando hay diferentes opiniones sobre tecnologías a utilizar.",
        "response_time_seconds": 150,
        "help_requested": False
    }
    
    response = requests.post(f"{base_url}/simulation/{session_id}/respond", json=response_data)
    if response.status_code != 200:
        print(f"❌ Error al responder: {response.status_code}")
        return
    
    print("✅ Respuesta enviada")
    
    # 4. Verificar estado después de responder
    print(f"\n4. 📊 Obteniendo estado después de responder...")
    response = requests.get(f"{base_url}/simulation/{session_id}/status")
    if response.status_code != 200:
        print(f"❌ Error al obtener estado: {response.status_code}")
        return
    
    final_status = response.json()
    print(f"✅ Estado actualizado obtenido")
    print(f"📈 Progreso actualizado: {final_status['progress_summary']['progress_percentage']}%")
    print(f"📝 Pasos completados: {final_status['progress_summary']['completed_steps']}/{final_status['progress_summary']['total_steps']}")
    print(f"🎯 Puntuación promedio: {final_status['progress_summary']['average_score']}/100")
    
    # 5. Mostrar resumen detallado
    print(f"\n5. 📋 Resumen detallado:")
    print(f"   • Usuario: {final_status['session_info']['user_id']}")
    print(f"   • Habilidad: {final_status['session_info']['skill_type']}")
    print(f"   • Escenario: {final_status['scenario_info']['title']}")
    print(f"   • Dificultad: {final_status['session_info']['difficulty_level']}/5")
    print(f"   • Estado activo: {'Sí' if final_status['is_active'] else 'No'}")
    
    if final_status['steps_completed']:
        print(f"\n6. 📚 Pasos completados:")
        for step in final_status['steps_completed']:
            print(f"   • Paso {step['step_number']}: {step['evaluation']['score'] if step.get('evaluation') else 'Sin evaluar'}/100")
    
    if final_status['current_step']:
        print(f"\n7. ▶️ Paso actual:")
        print(f"   • Tipo: {final_status['current_step']['step_type']}")
        print(f"   • Pregunta: {final_status['current_step']['question'][:100]}...")
    
    print(f"\n✅ Prueba de estado de simulación completada!")

if __name__ == "__main__":
    try:
        test_simulation_status()
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
