
import sys
import os
from pathlib import Path
from dotenv import load_dotenv


project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


load_dotenv(project_root / ".env")

def check_env_file():
    """Verificar que el archivo .env existe y tiene las variables necesarias"""
    env_file = project_root / ".env"
    if not env_file.exists():
        
        return False
    
    required_vars = ["GEMINI_API_KEY", "MONGODB_URL", "MONGODB_DB_NAME"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        
        return False
    
    return True

if __name__ == "__main__":
    if not check_env_file():
        sys.exit(1)
    
    try:
        import uvicorn
        
      
        
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8001,
            reload=True,
            reload_dirs=[str(src_path)]
        )
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Instala las dependencias: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error al iniciar el servidor: {e}")