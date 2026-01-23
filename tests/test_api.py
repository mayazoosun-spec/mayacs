"""API测试"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    """测试客户端"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_root(client):
    """测试根路径"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "status" in data


@pytest.mark.asyncio
async def test_health(client):
    """测试健康检查"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_category(client):
    """测试创建分类"""
    response = await client.post(
        "/api/v1/products/categories",
        json={"name": "测试分类", "description": "这是一个测试分类"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "测试分类"


@pytest.mark.asyncio
async def test_create_product(client):
    """测试创建产品"""
    # 先创建分类
    cat_response = await client.post(
        "/api/v1/products/categories",
        json={"name": "电子产品"}
    )
    category_id = cat_response.json()["id"]

    # 创建产品
    response = await client.post(
        "/api/v1/products",
        json={
            "sku": "TEST001",
            "name": "测试产品",
            "retail_price": "99.99",
            "product_type": "own",
            "category_id": category_id,
            "sell_online": True,
            "sell_offline": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sku"] == "TEST001"
    assert data["product_type"] == "own"


@pytest.mark.asyncio
async def test_create_store(client):
    """测试创建门店"""
    response = await client.post(
        "/api/v1/stores",
        json={
            "code": "STORE001",
            "name": "测试门店",
            "store_type": "retail_store",
            "city": "北京"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "STORE001"


@pytest.mark.asyncio
async def test_create_channel(client):
    """测试创建销售渠道"""
    response = await client.post(
        "/api/v1/stores/channels",
        json={
            "code": "TMALL001",
            "name": "天猫旗舰店",
            "channel_type": "online_tmall"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["channel_type"] == "online_tmall"
