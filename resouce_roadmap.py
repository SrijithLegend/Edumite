from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
import re

app = FastAPI(title="Dynamic Roadmap Generator API")

class RoadmapMilestone(BaseModel):
    step: int
    topic: str
    subtopics: List[str]
    estimated_days: int

class RoadmapResponse(BaseModel):
    resource_name: str
    total_estimated_days: int
    roadmap: List[RoadmapMilestone]

def extract_topics_from_text(text: str) -> List[dict]:
    """
    Parses resource text to extract major headers and sub-bullet points.
    Can be replaced or enhanced with an LLM prompt call.
    """
    lines = text.split('\n')
    extracted_roadmap = []
    current_topic = None
    subtopics = []
    step_counter = 1

    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect Major Topics (e.g., "Module 1:", "Chapter 2:", or numbered lines "1. Topic")
        if re.match(r'^(Module|Chapter|\d+\.)', line, re.IGNORECASE) or (line.isupper() and len(line) > 3):
            if current_topic:
                # Save previous topic before starting a new one
                extracted_roadmap.append({
                    "step": step_counter,
                    "topic": current_topic,
                    "subtopics": subtopics if subtopics else ["Introduction and Core Concepts"],
                    "estimated_days": max(3, len(subtopics) * 2) # Dynamic estimation rule
                })
                step_counter += 1
                subtopics = []
            current_topic = re.sub(r'^(Module|Chapter|\d+\.\s*|:\s*)', '', line, flags=re.IGNORECASE).strip()
        
        # Detect Subtopics (lines starting with dashes, bullets, or asterisks)
        elif line.startswith(('-', '*', '•')) and current_topic:
            sub_clean = line.lstrip('-*• ').strip()
            if sub_clean:
                subtopics.append(sub_clean)
                
    # Append the final item
    if current_topic:
        extracted_roadmap.append({
            "step": step_counter,
            "topic": current_topic,
            "subtopics": subtopics if subtopics else ["Introduction and Core Concepts"],
            "estimated_days": max(3, len(subtopics) * 2)
        })

    # Fallback if text format wasn't cleanly structured with modules/headers
    if not extracted_roadmap and text.strip():
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        for idx, para in enumerate(paragraphs[:5]): # Fallback split
            extracted_roadmap.append({
                "step": idx + 1,
                "topic": para.split('.')[0][:50], # Take first sentence snippet as title
                "subtopics": [para[:100] + "..."],
                "estimated_days": 4
            })

    return extracted_roadmap

@app.post("/roadmap/generate", response_model=RoadmapResponse, tags=["Roadmap Generator"])
async def generate_roadmap(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.endswith(('.txt', '.md')):
        raise HTTPException(status_code=400, detail="Please upload a structured .txt or .md file.")
    
    try:
        contents = await file.read()
        decoded_text = contents.decode("utf-8")
        
        # Analyze content and extract major topics
        parsed_milestones = extract_topics_from_text(decoded_text)
        
        if not parsed_milestones:
            raise HTTPException(status_code=422, detail="Unable to extract clear learning topics from the provided resource file.")
        
        # Calculate total timeline duration
        total_days = sum(item["estimated_days"] for item in parsed_milestones)
        
        return RoadmapResponse(
            resource_name=file.filename,
            total_estimated_days=total_days,
            roadmap=parsed_milestones
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing resource file: {str(e)}")