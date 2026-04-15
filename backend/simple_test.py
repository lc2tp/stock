from fastapi import FastAPI
from api.routes import router

app = FastAPI()
app.include_router(router)

print("=== 路由 ===")
for route in app.routes:
    if hasattr(route, 'path'):
        print(f"{route.methods} {route.path}")
