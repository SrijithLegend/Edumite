from fastapi import FastAPI, HTTPException, Body
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from pydantic import BaseModel
from datetime import datetime
import random

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# --- IN-MEMORY REPOSITORY STORAGE DEFAULTS ---
# Simulating a live database state for advanced structural components
STUDENT_ROSTER = [
    {"id": 1, "name": "Alex Mercer", "grade": 88, "engagement": 92, "attendance": 95, "cluster": "High Achievers"},
    {"id": 2, "name": "Baird Cooper", "grade": 54, "engagement": 41, "attendance": 72, "cluster": "Critical Attention"},
    {"id": 3, "name": "Chloe Frazer", "grade": 76, "engagement": 89, "attendance": 88, "cluster": "Under-engaged Peers"},
    {"id": 4, "name": "Diana Burnwood", "grade": 91, "engagement": 62, "attendance": 90, "cluster": "Under-engaged Peers"},
    {"id": 5, "name": "Ethan Hunt", "grade": 42, "engagement": 30, "attendance": 55, "cluster": "Critical Attention"},
]

ADMIN_AUTOMATIONS = [
    {"id": "auto_01", "title": "Generate Weekly Attendance Reports", "status": "Idle", "last_run": "2026-06-10 09:00"},
    {"id": "auto_02", "title": "Sync Classroom Portal Submissions", "status": "Active", "last_run": "2026-06-12 11:30"},
    {"id": "auto_03", "title": "Flag Low-Engagement Risk Triggers", "status": "Idle", "last_run": "2026-06-11 17:15"}
]

SUPPORT_TICKETS = [
    {"id": "tk_101", "student": "Baird Cooper", "issue": "Stuck on DB Assignment 2 setup pipeline", "status": "Resolved"},
    {"id": "tk_102", "student": "Ethan Hunt", "issue": "Missing access keys for the virtual test environment", "status": "Pending"}
]

GRADEBOOK = {
    "Database Management Assignment #2": {"Alex Mercer": 92, "Baird Cooper": 45, "Chloe Frazer": 80}
}

class VoicePayload(BaseModel):
    transcript: str

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html")

# --- LEARNING ANALYTICS & CLUSTERING DATA ENGINE ---
@app.get("/api/analytics/summary")
async def get_analytics_summary():
    if not STUDENT_ROSTER:
        return {"avg_grade": 0, "avg_engagement": 0, "cohort_size": 0}
        
    avg_grade = sum(s["grade"] for s in STUDENT_ROSTER) / len(STUDENT_ROSTER)
    avg_engage = sum(s["engagement"] for s in STUDENT_ROSTER) / len(STUDENT_ROSTER)
    
    # Simple algorithmic distribution counting for Cluster groupings
    cluster_counts = {}
    for s in STUDENT_ROSTER:
        cluster_counts[s["cluster"]] = cluster_counts.get(s["cluster"], 0) + 1
        
    return {
        "avg_grade": round(avg_grade, 1),
        "avg_engagement": round(avg_engage, 1),
        "cohort_size": len(STUDENT_ROSTER),
        "clusters": cluster_counts,
        "roster": STUDENT_ROSTER
    }

# --- VOICE-TO-GRADEBOOK UTILITY ---
@app.post("/api/automation/voice-grade")
async def parse_voice_grade(payload: VoicePayload):
    text = payload.transcript.lower()
    # Mock Natural Language processing extract values: "Set grade for Alex Mercer to 95 on Database Management Assignment #2"
    detected_student = None
    detected_grade = None
    detected_task = "Database Management Assignment #2" # Default matched scope fallback
    
    for s in STUDENT_ROSTER:
        if s["name"].lower() in text:
            detected_student = s["name"]
            break
            
    # Simple text token parsing extraction routine for finding numerical patterns
    words = text.split()
    for word in words:
        if word.isdigit():
            val = int(word)
            if 0 <= val <= 100:
                detected_grade = val
                break

    if detected_student and detected_grade is not None:
        if detected_task not in GRADEBOOK:
            GRADEBOOK[detected_task] = {}
        GRADEBOOK[detected_task][detected_student] = detected_grade
        
        # Real-time state synchronization check: adjust student profile grade records dynamically based on incoming logs
        for s in STUDENT_ROSTER:
            if s["name"] == detected_student:
                s["grade"] = round((s["grade"] + detected_grade) / 2) 
        
        return {
            "success": True, 
            "message": f"Successfully committed action! Logged {detected_grade}% for student {detected_student} under task '{detected_task}'."
        }
    
    raise HTTPException(status_code=400, detail="Failed to safely map voice command syntax structure. Ensure format matches: 'Set grade for [Student Name] to [0-100]'.")

# --- ADMINISTRATIVE TASK AUTOMATION ENGINE ---
@app.get("/api/admin/automations")
async def list_automations():
    return {"automations": ADMIN_AUTOMATIONS}

@app.post("/api/admin/trigger/{auto_id}")
async def trigger_automation(auto_id: str):
    for auto in ADMIN_AUTOMATIONS:
        if auto["id"] == auto_id:
            auto["status"] = "Running..."
            auto["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            # In a production app, background workers execute here. We mimic immediate termination loop state.
            auto["status"] = "Active" if auto_id == "auto_02" else "Idle"
            return {"success": True, "target": auto}
    raise HTTPException(status_code=404, detail="Target tracking engine ID not found.")

# --- AUTOMATED SUPPORT SYSTEM DRIVER ---
@app.get("/api/support/tickets")
async def get_tickets():
    return {"tickets": SUPPORT_TICKETS}

@app.post("/api/support/tickets/create")
async def create_ticket(student: str = Body(..., embed=True), issue: str = Body(..., embed=True)):
    new_ticket = {
        "id": f"tk_{random.randint(103, 999)}",
        "student": student,
        "issue": issue,
        "status": "Pending"
    }
    SUPPORT_TICKETS.insert(0, new_ticket)
    return {"success": True, "ticket": new_ticket}