# test_app.py - unit tests for the ShopList backend (lesson 8)
# Run: cd app/backend && python -m pytest -v
# No database needed: these tests only touch routes that answer
# before the code connects to postgres.

from app import app

client = app.test_client()


def test_health_returns_ok():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}


def test_categories_list():
    response = client.get('/categories')
    assert response.status_code == 200
    categories = response.get_json()
    assert 'Bakery' in categories
    assert 'Other' in categories


def test_add_product_without_name_is_rejected():
    response = client.post('/products', json={'price': 5})
    assert response.status_code == 400
    assert response.get_json()['error'] == 'name is required'


def test_add_product_with_bad_price_is_rejected():
    response = client.post('/products', json={'name': 'Milk', 'price': 'cheap'})
    assert response.status_code == 400


def test_unknown_route_is_404():
    response = client.get('/no-such-page')
    assert response.status_code == 404
