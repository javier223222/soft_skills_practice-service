
#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Agregar src al path de Python
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Solo cargar .env si existe (para desarrollo local)
try:
    from dotenv import load_dotenv
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print("📄 Archivo .env cargado")
    else:
        print("⚙️ Usando variables de entorno del contenedor")
except ImportError:
    print("⚙️ python-dotenv no disponible, usando variables de entorno del sistema")

def check_env_vars():
    """Verificar que las variables de entorno requeridas estén disponibles"""
    required_vars = ["GEMINI_API_KEY", "MONGODB_URL", "MONGODB_DB_NAME"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables faltantes: {', '.join(missing_vars)}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando Soft Skills Practice Service")
    print("=" * 50)
    
    if not check_env_vars():
        print("❌ Variables de entorno requeridas no encontradas")
        sys.exit(1)
    
    try:
        import uvicorn
        
        print(f"🌐 Servidor iniciando en: http://0.0.0.0:8001")
        print(f"📁 Directorio: {project_root}")
        print(f"🔑 API Key configurada: ✅")
        print(f"🗄️ MongoDB URL: {os.getenv('MONGODB_URL')}")
        print("=" * 50)
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8001,
            reload=False,  # Desactivado para Docker
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Instala las dependencias: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error al iniciar el servidor: {e}")