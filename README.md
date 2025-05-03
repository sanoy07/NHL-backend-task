# FastAPI Supabase Application

This project is a simple FastAPI application that implements user authentication, question retrieval, answer submission, and user statistics using Supabase for data management.

## Features

- User sign-up and login
- Random question retrieval
- Answer submission with validation
- User statistics tracking

## Requirements

- Python 3.7 or higher
- Supabase account

## Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd fastapi-supabase-app
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   Copy the `.env.example` to `.env` and fill in your Supabase credentials:

   ```bash
   cp .env.example .env
   ```

   Update the `.env` file with your Supabase URL and API keys.

5. **Run the application:**

   You can run the FastAPI application using Uvicorn:

   ```bash
   uvicorn main:app --reload
   ```

6. **Access the API:**

   The API will be available at `http://127.0.0.1:8000`. You can access the interactive API documentation at `http://127.0.0.1:8000/docs`.

## Usage Examples

- **Sign Up:**

  POST request to `/signup` with JSON body:

  ```json
  {
    "username": "your_username",
    "password": "your_password"
  }
  ```

- **Login:**

  POST request to `/login` with form data:

  ```
  username: your_username
  password: your_password
  ```

- **Get Random Question:**

  GET request to `/questions/random` with Bearer token in the Authorization header.

- **Submit Answer:**

  POST request to `/answers` with JSON body:

  ```json
  {
    "question_id": 1,
    "answer": "your_answer"
  }
  ```

- **Get User Statistics:**

  GET request to `/stats` with Bearer token in the Authorization header.

## License

This project is licensed under the MIT License. See the LICENSE file for details.