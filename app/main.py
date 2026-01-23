"""
零售平台主应用入口

支持功能:
- 产品管理: 自有产品和第三方产品
- 库存管理: 多门店/仓库库存追踪
- 销售渠道: 线上(官网/天猫/京东/抖音/微信) + 线下门店
- 订单管理: 统一订单处理系统
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    yield
    # 关闭时的清理工作(如果需要)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## 零售平台 API

支持线上商城和线下门店的产品运营管理系统

### 功能模块

- **产品管理** - 自有产品和第三方产品的增删改查
- **库存管理** - 多门店/仓库的库存追踪和调整
- **门店管理** - 门店和销售渠道的管理
- **订单管理** - 线上线下统一订单处理

### 产品类型

- `own` - 自有产品
- `third_party` - 第三方产品(代销)

### 销售渠道

**线上渠道:**
- 官网商城
- 天猫
- 京东
- 抖音
- 微信小程序

**线下渠道:**
- 零售门店
- 批发
    """,
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["健康检查"])
async def root():
    """根路径健康检查"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}
