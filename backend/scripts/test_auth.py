import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_user_registration(client):
    response = client.post('/api/register', json={
        'username': 'testuser',
        'password': 'testpass123'
    })
    assert response.status_code == 201
    assert response.json['success'] is True