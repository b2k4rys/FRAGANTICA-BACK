# Fragrantica-Like Fragrance Platform Backend

Welcome to the backend for a fragrance platform inspired by **Fragrantica**!  
This project provides a robust API to manage fragrances, notes, user wishlists, reviews, and more — built with modern Python technologies.

It replicates key features of Fragrantica, such as the note pyramid (top, middle, base notes), fragrance categorization, and user interactions.

---

## 🚀 Project Overview

This backend supports a fragrance community platform with the following core features:

- **Fragrance Management**: Store and retrieve fragrance details (e.g., name, type, price, notes).
- **Note Pyramid**: Categorize notes into top, middle, and base for each fragrance.
- **User Wishlist**: Allow users to mark fragrances as owned, wanted, or used.
- **Reviews**: Enable users to rate and review fragrances.
- **Company Data**: Associate fragrances with companies.

### 🛠 Tech Stack

- **FastAPI** – High-performance async web framework.
- **SQLAlchemy** – ORM for database interactions.
- **Pydantic** – Data validation and schema management.
- **Alembic** – Database migrations.
- **PostgreSQL** – Relational database.

---

## 📦 Prerequisites

- Python 3.10 or higher  
- PostgreSQL 12 or higher  
- `pip` and `virtualenv` (recommended)  
- Git  

---

## 🔧 Installation

### 1. Clone the Repository

```
git clone https://github.com/your-username/fragrance-backend.git
cd fragrance-backend
```
### 2. Set Up a Virtual Environment
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
### 3. Clone the Repository
```
pip install -r requirements.txt
```
### 3. Configure Environment Variables
Create a .env file in the root directory based on .env.example (if provided), or add the following variables:  
```
DATABASE_URL=postgresql://user:password@localhost:5432/fragrance_db
SECRET_KEY=your-secure-secret-key
CSRF_SECRET=your-csrf-secret-key
```


## Set Up the Database

### 1. Create the Database
```
CREATE DATABASE fragrance_db;
```

### 2. Run migrations
```
alembic upgrade head
```

## Running the Application
```
uvicorn backend.main:app --reload --port 8000
```


## Usage
### Fragrances
* GET /api/fragrances: List all fragrances

* GET /api/fragrances/{fragrance_id}: Get fragrance with notes

* POST /api/fragrances/{fragrance_id}/notes: Add a note (with type)

### Notes
* GET /api/notes: List all notes

* POST /api/notes: Create a new note

### Wishlist
* POST /api/wishlist: Add/update fragrance in wishlist (owned, wanted, used)

* GET /api/wishlist: View wishlist

### Reviews
* POST /api/reviews: Submit a review with rating (1–10, steps of 0.5)

* GET /api/reviews/{fragrance_id}: View reviews for a fragrance


## 🔐 Authentication
* JWT-based authentication is used.

* Endpoints like wishlist and review operations require a valid token.

* CSRF protection is enabled for POST requests.


## Role-Based Access Control (RBAC)
* Admins can manage fragrances and notes.

* Regular users can manage their wishlist and reviews.

