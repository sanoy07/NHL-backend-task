import os
import time
import random
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.models import APIKey, APIKeyIn, SecuritySchemeType
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, EmailStr
from fastapi import Security
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

load_dotenv()

# Setup
app = FastAPI()
MONGO_URL = os.getenv("MONGO_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
client = AsyncIOMotorClient(MONGO_URL)
db = client.quiz_app
users = db.users
user_questions = db.user_questions  # Collection to store user questions

# Security scheme
bearer_scheme = HTTPBearer()

# Expanded Questions with more variety
QUESTIONS = [
    {"id": 1, "question": "What is 2 + 2?", "answer": "4"},
    {"id": 2, "question": "Capital of France?", "answer": "Paris"},
    {"id": 3, "question": "Fastest land animal?", "answer": "Cheetah"},
    {"id": 4, "question": "What is the chemical symbol for water?", "answer": "H2O"},
    {"id": 5, "question": "Who painted the Mona Lisa?", "answer": "Leonardo da Vinci"},
    {"id": 6, "question": "What is the largest planet in our solar system?", "answer": "Jupiter"},
    {"id": 7, "question": "How many continents are there?", "answer": "7"},
    {"id": 8, "question": "What is the capital of Japan?", "answer": "Tokyo"},
    {"id": 9, "question": "Who wrote 'Romeo and Juliet'?", "answer": "William Shakespeare"},
    {"id": 10, "question": "What is the square root of 81?", "answer": "9"},
    {"id": 11, "question": "What gas do plants absorb from the atmosphere?", "answer": "Carbon dioxide"},
    {"id": 12, "question": "Which planet is known as the Red Planet?", "answer": "Mars"},
    {"id": 13, "question": "What is the hardest natural substance on Earth?", "answer": "Diamond"},
    {"id": 14, "question": "What is the capital of Australia?", "answer": "Canberra"},
    {"id": 15, "question": "Who developed the theory of relativity?", "answer": "Albert Einstein"},
    {"id": 16, "question": "What is the largest ocean on Earth?", "answer": "Pacific Ocean"},
    {"id": 17, "question": "How many sides does a pentagon have?", "answer": "5"},
    {"id": 18, "question": "What is the currency of Japan?", "answer": "Yen"},
    {"id": 19, "question": "What is the boiling point of water in Celsius?", "answer": "100"},
    {"id": 20, "question": "Which element has the chemical symbol 'Au'?", "answer": "Gold"},
    {"id": 21, "question": "What is the capital of Brazil?", "answer": "Brasília"},
    {"id": 22, "question": "Who is the author of 'To Kill a Mockingbird'?", "answer": "Harper Lee"},
    {"id": 23, "question": "What is the smallest prime number?", "answer": "2"},
    {"id": 24, "question": "Which planet is closest to the sun?", "answer": "Mercury"}
]

# Pydantic Models
class Signup(BaseModel):
    email: str
    password: str

class Login(BaseModel):
    email: str
    password: str

class Answer(BaseModel):
    question_id: int
    user_answer: str

class UserQuestion(BaseModel):
    user_id: str
    question_id: int
    timestamp: float
    answered: bool = False
    correct: Optional[bool] = None
    user_answer: Optional[str] = None

# Utils
def create_jwt(user_id: str) -> str:
    return jwt.encode({"sub": user_id}, JWT_SECRET, algorithm="HS256")

def compare_answers(correct_answer: str, user_answer: str) -> bool:
    """Compare answers while handling case sensitivity and whitespace"""
    return correct_answer.strip().lower() == user_answer.strip().lower()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload["sub"]
        user = await users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user")
        return user
    except (InvalidTokenError, Exception) as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# Scheduled Tasks

async def assign_hourly_questions():
    """Assigns a question to all users at the start of every hour"""
    print(f"Running hourly question assignment at {datetime.now()}")
    
    try:
        # Get all users
        all_users = await users.find().to_list(length=None)
        current_time = time.time()
        
        for user in all_users:
            # Randomly select a question
            question = random.choice(QUESTIONS)
            
            # Store the question assignment
            await user_questions.insert_one({
                "user_id": str(user["_id"]),
                "question_id": question["id"],
                "timestamp": current_time,
                "answered": False
            })
            
            # Update user's last question timestamp
            await users.update_one(
                {"_id": user["_id"]},
                {"$set": {"last_question_ts": current_time}}
            )
        
        print(f"Successfully assigned questions to {len(all_users)} users")
    except Exception as e:
        print(f"Error in hourly question assignment: {str(e)}")

async def daily_wallet_update():
    """Updates user wallets based on their daily performance"""
    print(f"Running daily wallet update at {datetime.now()}")
    
    try:
        # Get all users
        all_users = await users.find().to_list(length=None)
        
        # Get yesterday's timestamp range
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        yesterday_start = yesterday.timestamp()
        yesterday_end = today.timestamp()
        
        for user in all_users:
            user_id = str(user["_id"])
            
            # Get questions from yesterday for this user
            user_questions_cursor = user_questions.find({
                "user_id": user_id,
                "timestamp": {"$gte": yesterday_start, "$lt": yesterday_end},
                "answered": True  # Consider only answered questions
            })
            
            user_questions_list = await user_questions_cursor.to_list(length=None)
            
            if not user_questions_list:
                print(f"No answered questions yesterday for user {user_id}")
                continue
            
            # Calculate performance
            total_questions = len(user_questions_list)
            correct_answers = sum(1 for q in user_questions_list if q.get("correct", False))
            
            # Calculate success rate
            success_rate = correct_answers / total_questions if total_questions > 0 else 0
            
            # Update wallet based on 50% threshold
            delta = 20 if success_rate >= 0.5 else -10
            new_gems = user["gems"] + delta
            
            # Ensure wallet doesn't go negative
            new_gems = max(0, new_gems)
            
            # Update user wallet
            await users.update_one(
                {"_id": user["_id"]},
                {"$set": {"gems": new_gems}}
            )
            
            print(f"Updated wallet for user {user_id}: {delta} gems ({correct_answers}/{total_questions} correct)")
    
    except Exception as e:
        print(f"Error in daily wallet update: {str(e)}")

# Set up the scheduler
scheduler = AsyncIOScheduler()
scheduler.add_job(assign_hourly_questions, CronTrigger(minute=0))  # Run at the start of every hour
scheduler.add_job(daily_wallet_update, CronTrigger(hour=23, minute=59))  # Run at the end of each day
scheduler.start()

# Routes

@app.post("/signup")
async def signup(data: Signup):
    if await users.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = {
        "email": data.email,
        "password": data.password,  # WARNING: No hashing for simplicity
        "gems": 10,
        "answered": [],
        "correct": 0,
        "total": 0,
        "last_question_ts": 0
    }
    result = await users.insert_one(user)
    token = create_jwt(str(result.inserted_id))
    return {"token": token}

@app.post("/login")
async def login(data: Login):
    user = await users.find_one({"email": data.email})
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_jwt(str(user["_id"]))
    return {"token": token}

@app.get("/current-question")
async def get_current_question(current_user=Depends(get_current_user)):
    """Get the current hourly question for the logged-in user"""
    user_id = str(current_user["_id"])
    
    # Find the most recent question assigned to this user
    latest_question = await user_questions.find_one(
        {"user_id": user_id, "answered": False},
        sort=[("timestamp", -1)]
    )
    
    if not latest_question:
        return {"message": "No current question available. Wait for the next hour or check back later."}
    
    # Get the question details
    q = next((q for q in QUESTIONS if q["id"] == latest_question["question_id"]), None)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return {
        "question_id": q["id"],
        "question": q["question"],
        "assigned_at": datetime.fromtimestamp(latest_question["timestamp"]).isoformat()
    }

@app.post("/answer")
async def answer_question(data: Answer, current_user=Depends(get_current_user)):
    user_id = str(current_user["_id"])
    
    # Find the question assignment
    question_assignment = await user_questions.find_one({
        "user_id": user_id,
        "question_id": data.question_id,
        "answered": False
    })
    
    if not question_assignment:
        raise HTTPException(
            status_code=400, 
            detail="You haven't been assigned this question or already answered it."
        )
    
    # Get the question details
    q = next((q for q in QUESTIONS if q["id"] == data.question_id), None)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if the answer is correct
    correct = compare_answers(q["answer"], data.user_answer)
    
    # Update the question assignment
    await user_questions.update_one(
        {"_id": question_assignment["_id"]},
        {"$set": {
            "answered": True,
            "correct": correct,
            "user_answer": data.user_answer
        }}
    )
    
    # Update user stats
    await users.update_one(
        {"_id": current_user["_id"]},
        {"$inc": {
            "total": 1,
            "correct": 1 if correct else 0
        }}
    )
    
    return {
        "correct": correct,
        "correct_answer": q["answer"],
        "message": "Your answer has been recorded. Gem wallet will be updated at the end of the day."
    }

@app.get("/stats")
async def stats(current_user=Depends(get_current_user)):
    user_id = str(current_user["_id"])
    
    # Get today's questions
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    
    today_questions = await user_questions.find({
        "user_id": user_id,
        "timestamp": {"$gte": today_start}
    }).to_list(length=None)
    
    # Calculate today's stats
    today_total = len(today_questions)
    today_answered = sum(1 for q in today_questions if q.get("answered", False))
    today_correct = sum(1 for q in today_questions if q.get("correct", False))
    
    return {
        "wallet_gems": current_user["gems"],
        "total_questions_answered": current_user["total"],
        "total_correct_answers": current_user["correct"],
        "today_questions": today_total,
        "today_answered": today_answered,
        "today_correct": today_correct,
        "last_question_timestamp": datetime.fromtimestamp(current_user["last_question_ts"]).isoformat() if current_user["last_question_ts"] > 0 else None
    }

@app.get("/")
async def root():
    return {"message": "Quiz App API is running"}

# Gracefully shutdown the scheduler when the app shuts down
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()