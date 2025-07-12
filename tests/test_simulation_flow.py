import requests
import json
import time

def test_simulation_flow():
    """Probar el flujo completo de simulación"""
    base_url = "http://localhost:8000"
    
    print("🚀 Iniciando prueba del flujo de simulación...")
    
    # 1. Iniciar simulación
    print("\n1. 📋 Iniciando simulación...")
    start_data = {
        "user_id": "test_user_456",
        "scenario_id": "68671d8ee0fb8100716b7ff2"
    }
    
    response = requests.post(f"{base_url}/simulation/start", json=start_data)
    if response.status_code != 200:
        print(f"❌ Error al iniciar simulación: {response.status_code}")
        print(response.text)
        return
    
    start_result = response.json()
    session_id = start_result["session_id"]
    print(f"✅ Simulación iniciada - Session ID: {session_id}")
    print(f"📝 Test inicial: {start_result['initial_test']['question'][:100]}...")
    
    # 2. Responder al test inicial
    print("\n2. 💬 Respondiendo al test inicial...")
    initial_response_data = {
        "user_response": "He tenido experiencia mediando conflictos técnicos en mi equipo anterior. Una vez tuvimos una discusión sobre si usar microservicios o arquitectura monolítica. Escuché ambos puntos de vista, hice preguntas para entender las preocupaciones de cada parte, y facilitamos una sesión donde evaluamos pros y contras objetivamente. Al final llegamos a un consenso.",
        "response_time_seconds": 180,
        "help_requested": False
    }
    
    response = requests.post(f"{base_url}/simulation/{session_id}/respond", json=initial_response_data)
    if response.status_code != 200:
        print(f"❌ Error al responder: {response.status_code}")
        print(response.text)
        return
    
    response_result = response.json()
    print(f"✅ Respuesta procesada - Puntuación: {response_result['evaluation']['score']}/100")
    print(f"🤖 Feedback IA: {response_result['ai_feedback'][:100]}...")
    
    if response_result["is_completed"]:
        print("🎉 Simulación completada!")
        return
    
    # 3. Responder al siguiente paso si existe
    if response_result.get("next_step"):
        print(f"\n3. 🎯 Siguiente paso: {response_result['next_step']['question'][:100]}...")
        
        # Esperar un poco para simular tiempo de pensamiento
        time.sleep(2)
        
        next_response_data = {
            "user_response": "En esta situación, aplicaría escucha activa escuchando completamente a ambos desarrolladores sin interrumpir, parafrasearía sus puntos para confirmar entendimiento, haría preguntas abiertas para explorar las razones detrás de sus posiciones, y buscaría puntos en común antes de proponer una solución colaborativa.",
            "response_time_seconds": 120,
            "help_requested": False
        }
        
        response = requests.post(f"{base_url}/simulation/{session_id}/respond", json=next_response_data)
        if response.status_code != 200:
            print(f"❌ Error en segundo paso: {response.status_code}")
            print(response.text)
            return
        
        final_result = response.json()
        print(f"✅ Segundo paso completado - Puntuación: {final_result['evaluation']['score']}/100")
        print(f"🤖 Feedback final: {final_result['ai_feedback'][:100]}...")
        
        if final_result["is_completed"]:
            print("🎉 Simulación completada exitosamente!")
        else:
            print("➡️ Continúa la simulación...")
    
    print("\n✅ Prueba del flujo de simulación completada!")

if __name__ == "__main__":
    try:
        test_simulation_flow()
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
