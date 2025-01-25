from mangum import Adapter
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import os

from idea2draft2 import ThoughtProcessor
from Draft2Blog import Draft2Blog, BlogConfig

# Load API key from environment variable
API_KEY = os.environ.get("GEMINI_API_KEY")

class IdeaRequest(BaseModel):
    idea: str

class RefinementRequest(BaseModel):
    refinement: str

class Orchestrator:
    def __init__(self):
        self.thought_processor = ThoughtProcessor(API_KEY)
        self.blog_converter = Draft2Blog(API_KEY)
        self.current_state = None

    def process_initial_idea(self, idea: str) -> Dict:
        result = self.thought_processor.process_brain_dump(idea)
        self.current_state = result
        return result

    def refine_content(self, refinement: str) -> Dict:
        result = self.thought_processor.refine_narrative(refinement)
        self.current_state = result
        return result

    def finalize_to_blog(self) -> str:
        if not self.current_state:
            raise ValueError("No content to finalize")
        return self.blog_converter.convert_draft(self.current_state["connected_narrative"])

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()

@app.post("/process")
async def process_idea(request: IdeaRequest):
    try:
        result = orchestrator.process_initial_idea(request.idea)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refine")
async def refine_content(request: RefinementRequest):
    try:
        result = orchestrator.refine_content(request.refinement)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/finalize")
async def finalize_to_blog():
    try:
        blog_post = orchestrator.finalize_to_blog()
        return {"blog_post": blog_post}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create handler for AWS Lambda
handler = Adapter(app)