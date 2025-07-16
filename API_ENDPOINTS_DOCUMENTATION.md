# 📚 Documentación de Endpoints - Soft Skills Practice Service

## 🌍 Información General

**Base URL**: `https://teching.tech/softskills`  
**Autenticación**: JWT Token (Kong Gateway)  
**Formato de Respuesta**: JSON  
**Servicio**: Soft Skills Practice Service v1.0.0

### 🔐 Autenticación
Todos los endpoints requieren un JWT token válido en el header:
```
Authorization: Bearer <jwt_token>
```

---

## 📋 Endpoints Disponibles

### 1. Health Check

#### GET `/`
**Descripción**: Verificación básica del estado del servicio  
**Autenticación**: Requerida  
**Parámetros**: Ninguno  

**Respuesta Exitosa (200)**:
```json
{
  "status": "ok",
  "service": "soft-skills-practice-service",
  "message": "Servicio funcionando correctamente"
}
```

#### GET `/health`
**Descripción**: Verificación detallada del estado del servicio  
**Autenticación**: Requerida  
**Parámetros**: Ninguno  

**Respuesta Exitosa (200)**:
```json
{
  "status": "healthy",
  "service": "soft-skills-practice-service",
  "version": "1.0.0",
  "database": "connected"
}
```

---

### 2. Gestión de Soft Skills

#### GET `/softskill/{user_id}`
**Descripción**: Obtener progreso del usuario en todas las soft skills disponibles (paginado)  
**Autenticación**: Requerida  
**Funcionalidad**: Auto-registra usuarios nuevos con progreso 0.0  

**Parámetros**:
- `user_id` (path): ID del usuario
- `page` (query): Número de página (default: 1, min: 1)
- `page_size` (query): Elementos por página (default: 10, min: 1, max: 100)

**Respuesta Exitosa (200)**:
```json
{
  "user_id": "user123",
  "skills": [
    {
      "skill_id": "communication",
      "display_name": "Comunicación",
      "category": "communication",
      "progress_percentage": 75.5,
      "total_sessions": 8,
      "completed_sessions": 6,
      "average_score": 82.3,
      "last_practice_date": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "page_size": 10,
    "total_items": 15,
    "total_pages": 2,
    "has_next": true,
    "has_previous": false
  }
}
```

**Errores**:
- 400: user_id vacío, page < 1, page_size fuera de rango
- 500: Error interno del servidor

---

### 3. Gestión de Escenarios

#### GET `/scenarios/{skill_type}`
**Descripción**: Obtener escenarios disponibles para una soft skill específica (paginado)  
**Autenticación**: Requerida  

**Parámetros**:
- `skill_type` (path): Tipo de habilidad (ej: "communication", "leadership")
- `page` (query): Número de página (default: 1, min: 1)
- `page_size` (query): Elementos por página (default: 10, min: 1, max: 100)

**Respuesta Exitosa (200)**:
```json
{
  "skill_type": "communication",
  "scenarios": [
    {
      "scenario_id": "scenario_123",
      "title": "Reunión con Cliente Difícil",
      "description": "Maneja una reunión con un cliente insatisfecho",
      "difficulty_level": 3,
      "estimated_duration": 25,
      "scenario_icon": "fas fa-users",
      "scenario_color": "#4CAF50",
      "tags": ["cliente", "negociacion", "comunicacion"],
      "is_popular": true,
      "usage_count": 245,
      "created_at": "2024-01-10T08:00:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "page_size": 10,
    "total_items": 25,
    "total_pages": 3,
    "has_next": true,
    "has_previous": false
  }
}
```

**Errores**:
- 400: skill_type vacío, parámetros de paginación inválidos
- 500: Error interno del servidor

#### GET `/popular/scenarios`
**Descripción**: Obtener escenarios más populares del sistema (paginado)  
**Autenticación**: Requerida  

**Parámetros**:
- `page` (query): Número de página (default: 1, min: 1)
- `page_size` (query): Elementos por página (default: 10, min: 1, max: 100)

**Respuesta Exitosa (200)**:
```json
{
  "scenarios": [
    {
      "scenario_id": "scenario_456",
      "title": "Presentación Ejecutiva",
      "description": "Presenta propuesta a directivos",
      "difficulty_level": 4,
      "estimated_duration": 30,
      "scenario_icon": "fas fa-presentation",
      "scenario_color": "#2196F3",
      "tags": ["presentacion", "liderazgo", "comunicacion"],
      "is_popular": true,
      "usage_count": 1250,
      "skill_type": "leadership"
    }
  ],
  "pagination": {
    "current_page": 1,
    "page_size": 10,
    "total_items": 50,
    "total_pages": 5,
    "has_next": true,
    "has_previous": false
  }
}
```

---

### 4. Simulaciones

#### POST `/simulation/softskill/start/`
**Descripción**: Iniciar simulación basada en soft skill específica (genera escenario con IA)  
**Autenticación**: Requerida  

**Request Body**:
```json
{
  "user_id": "user123",
  "skill_type": "communication",
  "difficulty_preference": 3,
  "tecnical_specialization": "Backend Developer",
  "seniority_level": "Senior"
}
```

**Parámetros de Validación**:
- `user_id`: No puede estar vacío
- `skill_type`: No puede estar vacío
- `difficulty_preference`: Entre 1 y 5
- `tecnical_specialization`: No puede estar vacío
- `seniority_level`: No puede estar vacío

**Respuesta Exitosa (200)**:
```json
{
  "session_id": "session_abc123",
  "user_id": "user123",
  "scenario_id": "generated_scenario_456",
  "scenario": {
    "scenario_id": "generated_scenario_456",
    "title": "Comunicación con Stakeholders Técnicos",
    "description": "Explica decisiones técnicas a stakeholders no técnicos",
    "skill_type": "communication",
    "difficulty_level": 3,
    "estimated_duration": 20,
    "scenario_icon": null,
    "scenario_color": null,
    "tags": ["comunicacion", "stakeholders", "tecnico"]
  },
  "initial_situation": "Te encuentras en una reunión donde necesitas explicar...",
  "first_test": {
    "question": "¿Cómo abordarías esta situación?",
    "context": "Contexto específico del escenario",
    "instructions": "Responde basándote en tu experiencia como Senior Backend Developer",
    "expected_skills": ["communication"],
    "estimated_time_minutes": 5,
    "evaluation_criteria": ["clarity", "empathy", "technical_translation"]
  },
  "message": "Simulación iniciada exitosamente"
}
```

#### POST `/simulation/scenario/start`
**Descripción**: Iniciar simulación usando un escenario específico existente  
**Autenticación**: Requerida  

**Request Body**:
```json
{
  "user_id": "user123",
  "scenario_id": "scenario_123",
  "difficulty_preference": 3,
  "tecnical_specialization": "Frontend Developer",
  "seniority_level": "Mid"
}
```

**Parámetros de Validación**:
- `user_id`: No puede estar vacío
- `scenario_id`: No puede estar vacío
- `difficulty_preference`: Entre 1 y 5 (opcional)

**Respuesta Exitosa (200)**:
```json
{
  "session_id": "session_def456",
  "user_id": "user123",
  "scenario_id": "scenario_123",
  "scenario": {
    "scenario_id": "scenario_123",
    "title": "Reunión con Cliente Difícil",
    "description": "Maneja una reunión con un cliente insatisfecho",
    "skill_type": "communication",
    "difficulty_level": 3,
    "estimated_duration": 25,
    "scenario_icon": "fas fa-users",
    "scenario_color": "#4CAF50",
    "tags": ["cliente", "negociacion", "comunicacion"]
  },
  "initial_situation": "El cliente está visiblemente molesto por los retrasos...",
  "first_test": {
    "question": "¿Cuál sería tu primer paso para manejar esta situación?",
    "context": "El cliente ha estado esperando 3 semanas por una funcionalidad",
    "instructions": "Responde considerando tu rol como Mid Frontend Developer",
    "expected_skills": ["communication"],
    "estimated_time_minutes": 5,
    "evaluation_criteria": ["empathy", "problem_solving", "communication"]
  },
  "message": "Simulación iniciada exitosamente"
}
```

#### POST `/simulation/{session_id}/respond`
**Descripción**: Responder a un paso de la simulación activa  
**Autenticación**: Requerida  

**Parámetros**:
- `session_id` (path): ID de la sesión de simulación

**Request Body**:
```json
{
  "user_response": "Mi respuesta sería organizar una reunión para...",
  "response_time_seconds": 120,
  "help_requested": false,
  "confidence_level": 4
}
```

**Parámetros de Validación**:
- `session_id`: No puede estar vacío
- `user_response`: No puede estar vacío
- `response_time_seconds`: No puede ser negativo (opcional)

**Respuesta Exitosa - Paso Intermedio (200)**:
```json
{
  "success": true,
  "session_id": "session_abc123",
  "step_number": 2,
  "user_response": "Mi respuesta sería organizar una reunión para...",
  "ai_feedback": "Excelente enfoque. Tu respuesta muestra empatía y proactividad...",
  "evaluation": {
    "score": 85,
    "strengths": ["Empatía", "Claridad en comunicación"],
    "areas_for_improvement": ["Asertividad"],
    "detailed_feedback": "Tu respuesta demuestra..."
  },
  "next_step": {
    "question": "¿Cómo continuarías la conversación?",
    "context": "El cliente parece más receptivo después de tu primer enfoque...",
    "step_number": 3,
    "instructions": "Continúa construyendo sobre la confianza establecida"
  },
  "is_completed": false,
  "message": "Respuesta evaluada. Continúa con el siguiente paso.",
  "next_action": "continue_simulation"
}
```

**Respuesta Exitosa - Simulación Completada (200)**:
```json
{
  "success": true,
  "session_id": "session_abc123",
  "is_completed": true,
  "completion_feedback": {
    "session_id": "session_abc123",
    "user_id": "user123",
    "scenario_title": "Reunión con Cliente Difícil",
    "skill_type": "communication",
    "completion_status": "completed",
    "performance": {
      "overall_score": 87.5,
      "average_step_score": 85.2,
      "total_time_minutes": 15,
      "average_response_time_seconds": 95,
      "help_requests_count": 1,
      "completion_percentage": 100,
      "confidence_level": 4.2
    },
    "skill_assessments": [
      {
        "skill_name": "Comunicación",
        "score": 90,
        "level": "Avanzado",
        "strengths": ["Empatía", "Claridad"],
        "areas_for_improvement": ["Asertividad"],
        "specific_feedback": "Excelente capacidad para conectar con el cliente"
      }
    ],
    "overall_feedback": "Demostró excelentes habilidades de comunicación...",
    "key_achievements": ["Comunicador Efectivo", "Resolutor de Conflictos"],
    "main_learnings": ["La escucha activa es fundamental", "Empatía genera confianza"],
    "next_steps_recommendations": ["Practica más escenarios de negociación", "Desarrolla asertividad"],
    "percentile_ranking": 85,
    "completed_at": "2024-01-15T10:30:00Z",
    "certificate_earned": true,
    "badge_unlocked": "Experto en Comunicación"
  },
  "message": "¡Simulación completada exitosamente!",
  "next_action": "view_detailed_feedback"
}
```

#### GET `/simulation/{session_id}/status`
**Descripción**: Obtener estado completo de una simulación  
**Autenticación**: Requerida  

**Parámetros**:
- `session_id` (path): ID de la sesión de simulación

**Respuesta Exitosa (200)**:
```json
{
  "success": true,
  "session_info": {
    "session_id": "session_abc123",
    "user_id": "user123",
    "skill_type": "communication",
    "status": "active",
    "current_step": 3,
    "total_steps": 5,
    "difficulty_level": 3,
    "started_at": "2024-01-15T10:00:00Z"
  },
  "scenario_info": {
    "scenario_id": "scenario_123",
    "title": "Reunión con Cliente Difícil",
    "description": "Maneja una reunión con un cliente insatisfecho",
    "estimated_duration": 25
  },
  "steps_completed": [
    {
      "step_number": 1,
      "user_response": "Mi primer enfoque sería...",
      "ai_feedback": "Buena respuesta inicial...",
      "score": 82,
      "completed_at": "2024-01-15T10:05:00Z"
    },
    {
      "step_number": 2,
      "user_response": "Continuaría con...",
      "ai_feedback": "Excelente progreso...",
      "score": 88,
      "completed_at": "2024-01-15T10:10:00Z"
    }
  ],
  "current_step": {
    "step_number": 3,
    "question": "¿Cómo manejarías la objeción del cliente?",
    "context": "El cliente presenta una objeción técnica compleja...",
    "instructions": "Responde manteniendo el balance entre lo técnico y lo comprensible"
  },
  "progress_summary": {
    "completion_percentage": 60,
    "average_score": 85,
    "total_time_minutes": 10,
    "steps_remaining": 2
  },
  "is_active": true,
  "next_action": "respond_to_current_step"
}
```

---

## 🔗 Conexión desde Flutter

### 1. Configuración Base

```dart
// lib/config/api_config.dart
class ApiConfig {
  static const String baseUrl = 'https://teching.tech/softskills';
  static const String authHeader = 'Authorization';
  static const String bearerPrefix = 'Bearer ';
}
```

### 2. Cliente HTTP con JWT

```dart
// lib/services/http_client.dart
class HttpClient {
  final Dio _dio;
  
  HttpClient() : _dio = Dio() {
    _dio.options.baseUrl = ApiConfig.baseUrl;
    _dio.options.headers['Content-Type'] = 'application/json';
    
    // Interceptor para JWT automático
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await TokenStorage.getToken();
        if (token != null) {
          options.headers[ApiConfig.authHeader] = 
              '${ApiConfig.bearerPrefix}$token';
        }
        handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401) {
          // Token expirado, manejar reautenticación
          await TokenStorage.clearToken();
          // Redirigir a login
        }
        handler.next(error);
      },
    ));
  }
}
```

### 3. Servicios por Endpoint

```dart
// lib/services/user_service.dart
class UserService {
  final HttpClient _client;
  
  UserService(this._client);
  
  // GET /softskill/{user_id}
  Future<UserSkillsResponse> getUserSkills(
    String userId, {
    int page = 1,
    int pageSize = 10,
  }) async {
    final response = await _client.get('/softskill/$userId', 
      queryParameters: {'page': page, 'page_size': pageSize});
    return UserSkillsResponse.fromJson(response.data);
  }
}

// lib/services/scenario_service.dart
class ScenarioService {
  final HttpClient _client;
  
  ScenarioService(this._client);
  
  // GET /scenarios/{skill_type}
  Future<ScenariosResponse> getScenariosBySkill(
    String skillType, {
    int page = 1,
    int pageSize = 10,
  }) async {
    final response = await _client.get('/scenarios/$skillType',
      queryParameters: {'page': page, 'page_size': pageSize});
    return ScenariosResponse.fromJson(response.data);
  }
  
  // GET /popular/scenarios
  Future<ScenariosResponse> getPopularScenarios({
    int page = 1,
    int pageSize = 10,
  }) async {
    final response = await _client.get('/popular/scenarios',
      queryParameters: {'page': page, 'page_size': pageSize});
    return ScenariosResponse.fromJson(response.data);
  }
}

// lib/services/simulation_service.dart
class SimulationService {
  final HttpClient _client;
  
  SimulationService(this._client);
  
  // POST /simulation/softskill/start/
  Future<StartSimulationResponse> startSkillSimulation(
    StartSkillSimulationRequest request) async {
    final response = await _client.post('/simulation/softskill/start/',
      data: request.toJson());
    return StartSimulationResponse.fromJson(response.data);
  }
  
  // POST /simulation/scenario/start
  Future<StartSimulationResponse> startScenarioSimulation(
    StartScenarioSimulationRequest request) async {
    final response = await _client.post('/simulation/scenario/start',
      data: request.toJson());
    return StartSimulationResponse.fromJson(response.data);
  }
  
  // POST /simulation/{session_id}/respond
  Future<SimulationResponse> respondToSimulation(
    String sessionId, 
    RespondSimulationRequest request) async {
    final response = await _client.post('/simulation/$sessionId/respond',
      data: request.toJson());
    return SimulationResponse.fromJson(response.data);
  }
  
  // GET /simulation/{session_id}/status
  Future<SimulationStatusResponse> getSimulationStatus(
    String sessionId) async {
    final response = await _client.get('/simulation/$sessionId/status');
    return SimulationStatusResponse.fromJson(response.data);
  }
}
```

### 4. Manejo de Estados

```dart
// lib/controllers/simulation_controller.dart
class SimulationController extends GetxController {
  final SimulationService _simulationService;
  
  final RxBool isLoading = false.obs;
  final RxString error = ''.obs;
  final Rx<SimulationStatusResponse?> currentSimulation = 
      Rx<SimulationStatusResponse?>(null);
  
  Future<void> startSimulation(String skillType) async {
    try {
      isLoading.value = true;
      error.value = '';
      
      final request = StartSkillSimulationRequest(
        userId: UserManager.currentUserId,
        skillType: skillType,
        difficultyPreference: 3,
        technicalSpecialization: UserManager.specialization,
        seniorityLevel: UserManager.seniorityLevel,
      );
      
      final response = await _simulationService.startSkillSimulation(request);
      
      // Guardar sesión actual
      currentSimulation.value = SimulationStatusResponse(
        sessionId: response.sessionId,
        // ... mapear otros campos
      );
      
      // Navegar a pantalla de simulación
      Get.toNamed('/simulation', arguments: response);
      
    } catch (e) {
      error.value = 'Error al iniciar simulación: $e';
    } finally {
      isLoading.value = false;
    }
  }
  
  Future<void> respondToSimulation(String userResponse) async {
    if (currentSimulation.value == null) return;
    
    try {
      isLoading.value = true;
      
      final request = RespondSimulationRequest(
        userResponse: userResponse,
        responseTimeSeconds: 120,
        helpRequested: false,
        confidenceLevel: 4,
      );
      
      final response = await _simulationService.respondToSimulation(
        currentSimulation.value!.sessionId,
        request,
      );
      
      if (response.isCompleted) {
        // Mostrar feedback de completación
        _showCompletionFeedback(response.completionFeedback);
      } else {
        // Actualizar con siguiente paso
        _updateCurrentStep(response);
      }
      
    } catch (e) {
      error.value = 'Error al responder: $e';
    } finally {
      isLoading.value = false;
    }
  }
}
```

### 5. Flujo de Uso Típico

```dart
// Flujo completo de simulación
class SimulationFlow {
  
  // 1. Obtener skills del usuario
  Future<void> loadUserSkills() async {
    final userSkills = await UserService.getUserSkills(userId);
    // Mostrar progreso en UI
  }
  
  // 2. Cargar escenarios populares
  Future<void> loadPopularScenarios() async {
    final scenarios = await ScenarioService.getPopularScenarios();
    // Mostrar en lista
  }
  
  // 3. Iniciar simulación por skill
  Future<void> startSkillSimulation(String skillType) async {
    final response = await SimulationService.startSkillSimulation(request);
    // Mostrar situación inicial y primera pregunta
  }
  
  // 4. Responder pasos iterativamente
  Future<void> respondToStep(String userResponse) async {
    final response = await SimulationService.respondToSimulation(
      sessionId, request);
    
    if (response.isCompleted) {
      // Mostrar feedback final
      showCompletionScreen(response.completionFeedback);
    } else {
      // Mostrar siguiente pregunta
      showNextStep(response.nextStep);
    }
  }
  
  // 5. Consultar estado (opcional)
  Future<void> checkSimulationStatus() async {
    final status = await SimulationService.getSimulationStatus(sessionId);
    // Actualizar UI con progreso
  }
}
```

### 6. Manejo de Errores

```dart
// lib/utils/error_handler.dart
class ErrorHandler {
  static String getErrorMessage(DioException error) {
    switch (error.response?.statusCode) {
      case 400:
        return 'Datos inválidos: ${error.response?.data['detail']}';
      case 401:
        return 'Sesión expirada, inicia sesión nuevamente';
      case 404:
        return 'Recurso no encontrado';
      case 500:
        return 'Error del servidor, intenta más tarde';
      default:
        return 'Error de conexión';
    }
  }
  
  static void handleApiError(DioException error) {
    final message = getErrorMessage(error);
    
    // Mostrar snackbar o dialog
    Get.snackbar(
      'Error',
      message,
      snackPosition: SnackPosition.BOTTOM,
      backgroundColor: Colors.red,
      colorText: Colors.white,
    );
    
    // Log para debugging
    print('API Error: ${error.response?.statusCode} - $message');
  }
}
```

## 🎯 Resumen de Integración

### Endpoints Principales:
1. **Health Check**: `/` y `/health` - Verificar estado
2. **User Skills**: `/softskill/{user_id}` - Progreso del usuario
3. **Scenarios**: `/scenarios/{skill_type}` y `/popular/scenarios` - Cargar escenarios
4. **Simulations**: 
   - `/simulation/softskill/start/` - Iniciar por skill
   - `/simulation/scenario/start` - Iniciar por escenario
   - `/simulation/{session_id}/respond` - Responder pasos
   - `/simulation/{session_id}/status` - Consultar estado

### Flujo de Autenticación:
- JWT token en header Authorization
- Manejo automático de expiración (401)
- Redireccionamiento a login cuando sea necesario

### Consideraciones Técnicas:
- Todas las respuestas son JSON
- Paginación en endpoints de listado
- Validación de parámetros en cliente
- Manejo de errores específico por código HTTP
- Estados reactivos para UI responsiva

¡La integración está lista para ser implementada en Flutter! 🚀
