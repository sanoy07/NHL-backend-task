This is a FastAPI-based backend application implementing user authentication, hourly question assignments, answer submission, and daily wallet updates using MongoDB for persistent data storage.
Features

    User sign-up and login using JWT tokens

    Automatic hourly question assignment to each user

    Random question selection from a predefined pool

    Answer submission and validation

    Daily gem wallet updates based on answer accuracy

    User statistics for daily performance

Requirements

    Python 3.7 or higher

    MongoDB connection URL (MongoDB Atlas or local instance)

    Environment variables for configuration

Setup Instructions

    Clone the repository:

git clone <repository-url>
cd fastapi-quiz-app

Create a virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

Install dependencies:

pip install -r requirements.txt

Set up environment variables:

Copy the .env.example to .env and fill in your MongoDB and JWT secrets:

cp .env.example .env

Example .env file:

MONGO_URL=mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
JWT_SECRET=your_jwt_secret

Run the application:

    uvicorn main:app --reload

    Access the API:

        Swagger UI: http://127.0.0.1:8000/docs

        ReDoc: http://127.0.0.1:8000/redoc

API Endpoints
Sign Up

    POST /signup

Request Body:

{
  "email": "user@example.com",
  "password": "yourpassword"
}

Response:

{
  "token": "<JWT token>"
}

Login

    POST /login

Request Body:

{
  "email": "user@example.com",
  "password": "yourpassword"
}

Response:

{
  "token": "<JWT token>"
}

Get Current Hourly Question

    GET /current-question

    Requires Bearer token in Authorization header

Response:

{
  "question_id": 5,
  "question": "Who painted the Mona Lisa?",
  "assigned_at": "2025-05-04T09:00:00"
}

Submit Answer

    POST /answer

    Requires Bearer token

Request Body:

{
  "question_id": 5,
  "user_answer": "Leonardo da Vinci"
}

Response:

{
  "correct": true,
  "correct_answer": "Leonardo da Vinci",
  "message": "Your answer has been recorded. Gem wallet will be updated at the end of the day."
}

Get User Stats

    GET /stats

    Requires Bearer token

Response:

{
  "wallet_gems": 30,
  "total_questions_today": 3,
  "answered_today": 3,
  "correct_today": 2
}

Scheduled Jobs

    Hourly Question Assignment: Assigns a new random question to every user at the top of each hour.

    Daily Wallet Update: At 11:59 PM daily, user gem balances are updated:

        +20 gems if ≥50% correct

        −10 gems otherwise (minimum balance: 0)

License

This project is licensed under the MIT License. See the LICENSE file for details.