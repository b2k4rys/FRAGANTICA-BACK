Fragrantica-Like Fragrance Platform Backend
Welcome to the backend for a fragrance platform inspired by Fragrantica! This project provides a robust API to manage fragrances, notes, user wishlists, reviews, and more, built with modern Python technologies. It aims to replicate key features of Fragrantica, such as the note pyramid (top, middle, base notes), fragrance categorization, and user interactions.
Project Overview
This backend is designed to support a fragrance community platform with the following core features:

Fragrance Management: Store and retrieve fragrance details (e.g., name, type, price, notes).
Note Pyramid: Categorize notes into top, middle, and base for each fragrance.
User Wishlist: Allow users to mark fragrances as owned, wanted, or used.
Reviews: Enable users to rate and review fragrances.
Company Data: Associate fragrances with companies.

The project leverages:

FastAPI: For building a high-performance, async API.
SQLAlchemy: For ORM and database interactions with PostgreSQL.
Pydantic: For data validation and schema management.
Alembic: For database migrations.
PostgreSQL: As the relational database.

Prerequisites

Python 3.10 or higher
PostgreSQL 12 or higher
pip and virtualenv (recommended)
Git (for cloning the repository)

Installation

Clone the Repository:
git clone https://github.com/your-username/fragrance-backend.git
cd fragrance-backend


Set Up a Virtual Environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:
pip install -r requirements.txt


Configure Environment Variables:

Create a .env file in the project root based on .env.example (if provided) or set the following variables:
DATABASE_URL: PostgreSQL connection string (e.g., postgresql://user:password@localhost:5432/fragrance_db)
SECRET_KEY: JWT secret key for authentication
CSRF_SECRET: Secret for CSRF protection


Example .env:DATABASE_URL=postgresql://user:password@localhost:5432/fragrance_db
SECRET_KEY=your-secure-secret-key
CSRF_SECRET=your-csrf-secret-key




Set Up the Database:

Create the database in PostgreSQL:CREATE DATABASE fragrance_db;


Run migrations to set up the schema:alembic upgrade head





Running the Application

Start the Application:
uvicorn backend.main:app --reload --port 8000


Access the API at http://localhost:8000.


API Documentation:

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc



Usage
Key Endpoints

Fragrances:
GET /api/fragrances: List all fragrances.
GET /api/fragrances/{fragrance_id}: Get a specific fragrance with its notes.
POST /api/fragrances/{fragrance_id}/notes: Add a note to a fragrance with a note type (top, middle, base).


Notes:
GET /api/notes: List all notes.
POST /api/notes: Create a new note.


Wishlist:
POST /api/wishlist: Add or update a fragrance in a user’s wishlist (owned, wanted, used).
GET /api/wishlist: View a user’s wishlist.


Reviews:
POST /api/reviews: Submit a review with a rating (1-10, multiples of 0.5).
GET /api/reviews/{fragrance_id}: View reviews for a fragrance.



Authentication

Use JWT-based authentication with endpoints requiring a valid token (e.g., wishlist and review operations).
CSRF protection is enabled for POST requests.

Role-Based Access Control (RBAC)

Admins can manage fragrances and notes; regular users can manage their wishlist and reviews.

Project Structure
fragrance-backend/
├── backend/
│   ├── core/
│   │   ├── db/              # Database configuration and models
│   │   ├── security/        # Authentication and CSRF logic
│   │   └── settings.py      # Pydantic settings
│   ├── api/                 # API routes (e.g., fragrances, wishlist)
│   └── main.py              # FastAPI application entry point
├── migrations/              # Alembic migration scripts
├── requirements.txt         # Project dependencies
├── .env                     # Environment variables
└── README.md                # This file

Contributing

Fork the repository.
Create a feature branch (git checkout -b feature-name).
Commit your changes (git commit -m "Add feature X").
Push to the branch (git push origin feature-name).
Open a pull request.

Inspired by Fragrantica’s fragrance community platform.
Built with contributions from the open-source community and tools like FastAPI and SQLAlchemy.

Contact
For questions or support, reach out via the repository’s issue tracker or contact the maintainers.

Last Updated: May 24, 2025
