from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models
import secrets

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

def table_prices(num_people, tables):
    prices = {}
    for table in tables:
        total_cost = num_people * table.cost_per_seat if num_people < table.seats else (table.seats - 1) * table.cost_per_seat
        prices[table] = total_cost
    return prices

class BookingRequest(BaseModel):
    num_people: int

class CancelRequest(BaseModel):
    reservation_id: int

class AddTable(BaseModel):
    seats: int
    cost_per_seat: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Header(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.token == token).first()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid token")
    return user.id

@app.get("/generate_token")
def generate_token(db: Session = Depends(get_db)):
    token = secrets.token_hex(16)
    user = models.User(token=token)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"token": token}

@app.post("/book")
def book_table(request: BookingRequest, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    num_people = request.num_people if request.num_people % 2 == 0 else request.num_people + 1
    tables = db.query(models.Table).filter(models.Table.available == True, models.Table.seats >= num_people).all()
    prices = table_prices(num_people, tables)
    if not prices:
        raise HTTPException(status_code=400, detail="No available tables.")
    table = min(prices, key=prices.get)
    total_cost = prices[table]
    reservation = models.Reservation(table_id=table.id, num_seats=num_people, user_id=user_id)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    user.reservations.append(reservation)
    db.add(reservation)
    db.commit()
    table.available = False
    db.commit()
    return {
        "reservation_id": reservation.id,
        "table_id": table.id,
        "num_seats": num_people,
        "total_cost": total_cost
    }

@app.post("/cancel")
def cancel_reservation(request: CancelRequest, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    reservation = db.query(models.Reservation).filter(models.Reservation.id == request.reservation_id, models.Reservation.user_id == user_id).first()
    if not reservation:
        raise HTTPException(status_code=400, detail="Reservation not found or unauthorized.")
    table = db.query(models.Table).filter(models.Table.id == reservation.table_id).first()
    db.delete(reservation)
    db.commit()
    table.available = True
    db.commit()
    return {"message": "Reservation canceled."}

@app.post("/addtable")
def add_table(request: AddTable, db: Session = Depends(get_db)):
    seats = request.seats
    if seats < 4 or seats > 10:
        raise HTTPException(status_code=400, detail="Number of seats must be between 4 and 10.")
    table = models.Table(seats=request.seats, cost_per_seat=request.cost_per_seat)
    db.add(table)
    db.commit()
    return {"message": "Table added."}
