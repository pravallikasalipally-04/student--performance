# Student Performance Analytics System

## Stack
Flask, MySQL, SQLAlchemy, JWT, Jinja2, Pandas, NumPy, Bootstrap, Postman.

## Main features
- Admin JWT authentication
- Student role with own-data access
- Student/Course/Grade CRUD
- PUT, PATCH and DELETE API operations
- Pandas/NumPy analytics
- CSV upload
- CSV and Excel export
- MySQL persistence
- Postman-ready REST API

## Setup
1. Install MySQL and MySQL Workbench.
2. Run `schema.sql` in MySQL Workbench.
3. Open terminal in this project.
4. Create environment: `python -m venv venv`
5. Activate Windows: `venv\Scripts\activate`
6. Install: `pip install -r requirements.txt`
7. Copy `.env.example` to `.env` and put your MySQL password.
8. Run: `python app.py`
9. Open `http://127.0.0.1:5000`
10. Create an admin account at `/admin/create`.

## API
First call POST `/api/login` with JSON:
{"email":"admin@example.com","password":"admin123"}

Copy `access_token` and use it in Postman:
Authorization -> Bearer Token -> paste token.

Admin API:
GET/POST `/api/students`
GET/PUT/PATCH/DELETE `/api/students/<id>`
GET/POST `/api/courses`
GET/PUT/PATCH/DELETE `/api/courses/<id>`
GET/POST `/api/grades`
GET/PUT/PATCH/DELETE `/api/grades/<id>`

Student accounts can only access their own student/grade records.
