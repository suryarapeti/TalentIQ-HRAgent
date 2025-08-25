from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from werkzeug.utils import secure_filename
import os
from typing import List
import tempfile
import time
from datetime import datetime


from scheduler import schedule_interview
from utils import send_email
from helper import extract_text_from_pdf
from helper import analyze_resume_with_llm, generate_random_link


app = FastAPI(title="TalentIQ API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

results_cache = {}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    try:
        # Try to read from current directory first (for development)
        if os.path.exists("index.html"):
            with open("index.html", "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        # Then try static directory
        elif os.path.exists("static/index.html"):
            with open("static/index.html", "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        else:
            # Return a basic HTML if file not found
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>TalentIQ - File Not Found</title>
                <style>body { font-family: Arial, sans-serif; margin: 40px; }</style>
            </head>
            <body>
                <h1>TalentIQ API</h1>
                <p>Frontend HTML file not found. Please ensure index.html exists in the project root or static directory.</p>
                <p>API is running on <a href="/docs">/docs</a></p>
            </body>
            </html>
            """)
    except Exception as e:
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>TalentIQ - Error</title></head>
        <body>
            <h1>Error Loading Frontend</h1>
            <p>Error: {str(e)}</p>
            <p>API Documentation: <a href="/docs">/docs</a></p>
        </body>
        </html>
        """, status_code=500)

@app.post("/upload-resumes/")
async def upload_resumes(
    job_description: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """Process uploaded resumes and job description"""
    try:
        # Validation
        if not job_description.strip():
            raise HTTPException(status_code=400, detail="Job description is required")
        
        if not files or len(files) == 0:
            raise HTTPException(status_code=400, detail="At least one resume file is required")
        
        # Validate file types and sizes
        max_file_size = 10 * 1024 * 1024  # 10MB
        for file in files:
            if not file.filename:
                raise HTTPException(status_code=400, detail="Invalid file uploaded")
            
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"File '{file.filename}' is not a PDF. Only PDF files are supported.")
            
            # Check file size
            content = await file.read()
            if len(content) > max_file_size:
                raise HTTPException(status_code=400, detail=f"File '{file.filename}' is too large. Maximum size is 10MB.")
            
            # Reset file pointer
            await file.seek(0)
        
        # Create temporary directory for file processing
        temp_dir = tempfile.mkdtemp()
        candidates = []
        
        try:
            for file in files:
                filename = secure_filename(file.filename)
                file_path = os.path.join(temp_dir, filename)
                
                # Save uploaded file
                content = await file.read()
                with open(file_path, 'wb') as f:
                    f.write(content)
                
                # Extract text from PDF
                resume_text = extract_text_from_pdf(file_path)
                
                # Clean up the uploaded file
                try:
                    os.remove(file_path)
                except Exception as cleanup_error:
                    print(f"Warning: Could not delete temp file {file_path}: {cleanup_error}")
                
                # Analyze resume
                if resume_text:
                    analysis = await analyze_resume_with_llm(resume_text, job_description)
                    if analysis:
                        candidates.append(analysis)
            
            # Sort candidates by score in descending order
            sorted_candidates = sorted(candidates, key=lambda x: x.get('score', 0), reverse=True)
            
            # Generate session ID and cache results
            session_id = str(int(time.time() * 1000))  # Use timestamp as session ID
            results_cache[session_id] = {
                "results": sorted_candidates,
                "shortlist": [],
                "timestamp": datetime.now()
            }
            
            return JSONResponse({
                "success": True,
                "session_id": session_id,
                "results": sorted_candidates,
                "total_candidates": len(sorted_candidates),
                "message": f"Successfully processed {len(files)} resume(s)"
            })
        
        finally:
            # Clean up temporary directory
            try:
                for file in os.listdir(temp_dir):
                    os.remove(os.path.join(temp_dir, file))
                os.rmdir(temp_dir)
            except Exception as cleanup_error:
                print(f"Warning: Could not clean up temp directory {temp_dir}: {cleanup_error}")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in upload_resumes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



@app.post("/schedule-interview/{session_id}")
async def schedule_interview_endpoint(
    session_id: str,
    candidate_name: str = Form(...),
    interview_date: str = Form(...),
    interview_time: str = Form(...),
    duration: int = Form(60)  # Default 60 minutes
):
    """Schedule an interview for a candidate"""
    try:
        if session_id not in results_cache:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Validate inputs
        if not candidate_name.strip():
            raise HTTPException(status_code=400, detail="Candidate name is required")
        
        if not interview_date or not interview_time:
            raise HTTPException(status_code=400, detail="Both interview date and time are required")
        
        # Combine date and time
        start_time = f"{interview_date}T{interview_time}:00"
        
        # Validate datetime format
        try:
            interview_datetime = datetime.fromisoformat(start_time)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date or time format")
        
        print(f"Scheduling interview for {candidate_name} at {start_time}")
        
        # Find candidate email from session results
        candidate_email = None
        for candidate in results_cache[session_id]["results"]:
            if candidate.get("name") == candidate_name:
                candidate_email = candidate.get("email")
                break
        
        if not candidate_email:
            print(f"Warning: Email not found for candidate {candidate_name}")
        
        # Schedule the interview using your existing function
        calendar_link = schedule_interview(candidate_name, start_time, duration)
        
        # Send email notification to candidate
        email_sent = False
        if candidate_email and candidate_email.strip():
            subject = f"Interview Scheduled - {candidate_name}"
            
            # Format the datetime for display
            formatted_date = interview_datetime.strftime("%B %d, %Y at %I:%M %p")
            
            body = f"""
Dear {candidate_name},

We are pleased to inform you that an interview has been scheduled for you.

Interview Details:
- Date and Time: {formatted_date}
- Duration: {duration} minutes
- Meet Link: {generate_random_link()}
- Calendar Link: {calendar_link if calendar_link else "Will be provided separately"}

Please confirm your availability for this interview. If you have any questions or need to reschedule, please contact us as soon as possible.

We look forward to speaking with you.

Best regards,
The Hiring Team
            """.strip()
            
            try:
                email_sent = send_email(candidate_email, subject, body)
            except Exception as email_error:
                print(f"Failed to send email to {candidate_email}: {email_error}")
        
        # Update shortlist (remove candidate)
        if candidate_name in results_cache[session_id]["shortlist"]:
            results_cache[session_id]["shortlist"].remove(candidate_name)
        
        print(f"Interview scheduled successfully for {candidate_name}")
        
        response_data = {
            "success": True,
            "message": f"Interview scheduled successfully for {candidate_name}",
            "calendar_link": calendar_link,
            "candidate": candidate_name,
            "candidate_email": candidate_email,
            "interview_datetime": start_time,
            "duration": duration,
            "email_sent": email_sent
        }
        
        if email_sent:
            response_data["email_message"] = f"Email notification sent to {candidate_email}"
        elif candidate_email:
            response_data["email_message"] = f"Failed to send email to {candidate_email}"
        else:
            response_data["email_message"] = "Email not found for candidate"
        
        return JSONResponse(response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error scheduling interview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule interview: {str(e)}")




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
