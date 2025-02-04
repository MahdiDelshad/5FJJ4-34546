from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, SessionLocal
from main import app, get_db
import models


SQLALCHEMY_DATABASE_URL = "postgresql://test_user:test_password@db:5432/test_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)
test_token = None

def test_generate_token():
    global test_token
    response = client.get("/generate_token")
    assert response.status_code == 200
    assert "token" in response.json()
    test_token = response.json()["token"]

def test_add_table():
    response = client.post("/addtable", json={"seats": 3, "cost_per_seat": 10})
    assert response.status_code == 400
    assert response.json() == {"detail": "Number of seats must be between 4 and 10."}
    response = client.post("/addtable", json={"seats": 11, "cost_per_seat": 10})
    assert response.status_code == 400
    assert response.json() == {"detail": "Number of seats must be between 4 and 10."}
    response = client.post("/addtable", json={"seats": 6, "cost_per_seat": 10})
    response = client.post("/addtable", json={"seats": 6, "cost_per_seat": 20})
    assert response.status_code == 200
    assert response.json() == {"message": "Table added."}

def test_book_table():
    global test_token
    headers = {"token": test_token}
    response = client.post("/book", json={"num_people": 4}, headers=headers)
    assert response.status_code == 200
    assert "reservation_id" in response.json()
    assert "table_id" in response.json()
    assert "num_seats" in response.json()
    assert "total_cost" in response.json()

def test_cancel_reservation():
    global test_token
    headers = {"token": test_token}
    book_response = client.post("/book", json={"num_people": 4}, headers=headers)
    assert book_response.status_code == 200
    reservation_id = book_response.json()["reservation_id"]
    cancel_response = client.post("/cancel", json={"reservation_id": reservation_id}, headers=headers)
    assert cancel_response.status_code == 200
    assert cancel_response.json() == {"message": "Reservation canceled."}
    cancel_response = client.post("/cancel", json={"reservation_id": reservation_id}, headers=headers)
    assert cancel_response.status_code == 400
    assert cancel_response.json() == {"detail": "Reservation not found."}
