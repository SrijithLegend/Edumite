from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, date, timedelta
from typing import Dict

app = FastAPI(title="Streak Tracker API")

# Mock Database
# In production, swap this with an ORM like SQLAlchemy or Tortoise ORM
user_streaks_db: Dict[int, dict] = {}

class ActivityLog(BaseModel):
    user_id: int

@app.post("/streak/log-activity", tags=["Streak Tracker"])
async def log_activity(activity: ActivityLog):
    user_id = activity.user_id
    today = date.today()
    
    # Check if user already has a streak record
    if user_id not in user_streaks_db:
        # Core fix: Initializing the streak tracking at 1
        user_streaks_db[user_id] = {
            "current_streak": 1,
            "longest_streak": 1,
            "last_activity_date": today
        }
        return {
            "message": "Activity logged successfully! Welcome to day 1!",
            "streak_data": user_streaks_db[user_id]
        }
    
    streak_data = user_streaks_db[user_id]
    last_date = streak_data["last_activity_date"]
    
    # Case 1: Already logged activity today -> Do nothing, keep current streak
    if last_date == today:
        return {
            "message": "Activity already logged for today.",
            "streak_data": streak_data
        }
    
    # Case 2: Consecutive day (yesterday was the last activity) -> Increment streak
    elif last_date == today - timedelta(days=1):
        streak_data["current_streak"] += 1
        if streak_data["current_streak"] > streak_data["longest_streak"]:
            streak_data["longest_streak"] = streak_data["current_streak"]
    
    # Case 3: Streak broken (last activity was before yesterday) -> Reset to 1
    else:
        streak_data["current_streak"] = 1
        
    streak_data["last_activity_date"] = today
    return {
        "message": "Activity logged successfully! Keep up the momentum!",
        "streak_data": streak_data
    }

@app.get("/streak/{user_id}", tags=["Streak Tracker"])
async def get_streak(user_id: int):
    if user_id not in user_streaks_db:
        # If no history exists, return a baseline of 0 until they log their first activity
        return {
            "user_id": user_id,
            "current_streak": 0,
            "longest_streak": 0,
            "last_activity_date": None
        }
    return user_streaks_db[user_id]