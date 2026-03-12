try:
    from app.main import app
except ImportError as e:
    print(f"Import Error: {e}")
    from fastapi import FastAPI
    app = FastAPI()
    @app.get("/")
    def error():
        return {"error": "Failed to import app.main", "detail": str(e)}
except Exception as e:
    print(f"General Error: {e}")
    from fastapi import FastAPI
    app = FastAPI()
    @app.get("/")
    def error():
        return {"error": "An unexpected error occurred during import", "detail": str(e)}
