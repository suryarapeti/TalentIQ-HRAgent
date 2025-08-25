# TalentIQ - HR AI Agent

**TalentIQ** is an AI-powered HR automation platform that streamlines the hiring process from resume screening to interview scheduling. Using large language models, it eliminates manual tasks by analyzing PDF resumes, matching candidates to jobs with natural language processing, ranking applicants through customizable scoring, automating emails, and syncing with calendar systems for interview scheduling. With its intelligent analysis and intuitive design, TalentIQ helps HR teams hire faster, reduce bias, and focus on candidate engagement and strategic workforce planning instead of administrative work.

## 🚀 Features

### Core Features

- **📄 Resume Analysis** : Upload multiple PDF resumes for AI-powered analysis
- **🎯 Smart Matching** : Intelligent candidate-job matching with scoring
- **📊 Candidate Ranking** : Automatic ranking based on job requirements
- **📅 Interview Scheduling** : One-click interview scheduling with Google Calendar integration
- **📧 Email Automation** : Automatic email notifications to candidates
- **💼 Session Management** : Persistent session handling for batch processing

### AI-Powered Insights

- **Resume Parsing** : Extract and analyze text from PDF resumes
- **Skill Matching** : Match candidate skills against job requirements
- **Experience Evaluation** : Assess relevant work experience
- **Cultural Fit Analysis** : Evaluate candidate alignment with company values
- **Detailed Scoring** : Comprehensive scoring with explanations

## 🛠️ Technology Stack

### Backend

- **FastAPI** : Modern, fast web framework for building APIs
- **Python 3.8+** : Core programming language
- **PDF Processing** : Text extraction from resume PDFs
- **AI/LLM Integration** : Advanced resume analysis capabilities

### Frontend

- **HTML5/CSS3** : Modern web standards
- **Tailwind CSS** : Utility-first CSS framework
- **Vanilla JavaScript** : Client-side interactivity
- **Responsive Design** : Mobile and desktop optimized

### Integrations

- **Google Calendar API** : Interview scheduling
- **Email Services** : Automated candidate notifications
- **File Upload** : Secure PDF resume handling

## 📁 Project Structure

```
talentiq/
├── main.py                 # FastAPI application and API endpoints
├── index.html             # Frontend user interface
├── scheduler.py           # Interview scheduling logic
├── utils.py              # Email and utility functions
├── helper.py             # PDF processing and AI analysis
├── static/               # Static assets (if needed)
├── requirements.txt      # Python dependencies
└── README.md            # Project documentation
```

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/talentiq.git
   cd talentiq
   ```
2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up environment variables**
   ```bash
   # Create a .env file with your configurations
   ```
5. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

## 🎯 Usage Guide

### Step 1: Upload Job Description

1. Navigate to the TalentIQ web interface
2. Paste your complete job description in the text area
3. Include requirements, responsibilities, and qualifications

### Step 2: Upload Resumes

1. Click the file upload button
2. Select one or more PDF resume files (max 10MB each)
3. Review the uploaded files in the file list

### Step 3: Process and Review

1. Click "Screen & Rank Candidates"
2. Wait for AI analysis to complete
3. Review ranked candidates with scores and analysis

### Step 4: Schedule Interviews

1. For each candidate, select interview date and time
2. Click "Confirm Interview Schedule"
3. Calendar invite and email notification sent automatically

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# AI/LLM Configuration
GROQ_API_KEY=your_api_key

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Google Calendar API
GOOGLE_CALENDAR_CREDENTIALS_PATH=path/to/credentials.json
CALENDAR_ID=your_calendar_id
```
