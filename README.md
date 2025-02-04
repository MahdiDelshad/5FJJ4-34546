# 5FJJ4-34546

# Restaurant Reservation System

This project is a restaurant table reservation system built using FastAPI and PostgreSQL. Users can generate a token and use it to reserve and cancel reservations for tables at the restaurant. Additionally, new tables can be added to the system.

## Features

- Generate a token for new users
- Reserve tables based on the number of people
- Cancel table reservations
- Add new tables to the system

## Prerequisites

To run this project, you need the following software:

- Docker
- Docker Compose
- Python 3.10 or higher

## Setup & Run

### **Run the Project**

```bash
docker-compose up --build
```

This will start:

- **PostgreSQL** database container.
- **FastAPI** server on **port 8000**.

### **Access API Documentation**

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### **Stop the Project**

```bash
docker-compose down
```

### **Edit Code**

Stop the containers (`docker-compose down`), then modify files like **`main.py`**, **`models.py`**, or **`database.py`**.

### **Restart After Changes**

```bash
docker-compose up --build
```

## **Additional Commands**

**Check running containers**:

```bash
docker ps
```

**View logs**:

```bash
docker-compose logs -f
```

**Access PostgreSQL inside Docker**:

```bash
docker exec -it postgres_db psql -U admin -d restaurant
```
