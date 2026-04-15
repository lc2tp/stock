from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from models.database import Database

# 创建FastAPI应用
app = FastAPI(
    title="股票交易系统API",
    description="股票涨停数据管理系统API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)

# 启动时初始化数据库
@app.on_event("startup")
def startup_event():
    db = Database()
    db.connect()
    db.create_tables()
    db.close()

@app.get("/")
def read_root():
    return {"message": "股票交易系统API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
