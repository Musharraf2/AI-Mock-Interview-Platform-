<div align="center">

  # 🤖 AI Mock Interview Platform
  ### *Empowering Candidates with Stateful Multi-Agent AI & Enterprise Architecture*

  [![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.2.3-6DB33F?style=for-the-badge&logo=springboot&logoColor=white)](https://spring.io/projects/spring-boot)
  [![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-FF6F61?style=for-the-badge&logo=python&logoColor=white)](https://langchain-ai.github.io/langgraph/)
  [![React](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
  [![Gemini API](https://img.shields.io/badge/Gemini%20API-2.5%20Flash-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white)](https://ai.google.dev/)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
  [![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

  <p align="center">
    <b>An end-to-end multi-agent interview platform that simulates realistic technical interviews, evaluates candidate answers in real-time, asks adaptive follow-up probes, and generates personalized performance scorecards with 4-week learning roadmaps.</b>
  </p>

</div>

---

## 📌 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Multi-Agent LangGraph Workflow](#-multi-agent-langgraph-workflow)
- [Tech Stack & Rationale](#-tech-stack--rationale)
- [Database Schema](#-database-schema)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [1. AI Microservice Setup](#1-ai-microservice-setup)
  - [2. Spring Boot Backend Setup](#2-spring-boot-backend-setup)
  - [3. React Frontend Setup](#3-react-frontend-setup)
- [API Endpoints Reference](#-api-endpoints-reference)
- [Project Documentation](#-project-documentation)
- [License & Acknowledgments](#-license--acknowledgments)

---

## 🌟 Overview

The **AI Mock Interview Platform** goes beyond traditional single-prompt chatbot wrappers by leveraging **LangGraph's stateful multi-agent orchestration**. 

Instead of generating basic static questions, our multi-agent pipeline acts like a hiring panel at a top tech firm:
1. **Targeted Questioning**: Generates role-specific, difficulty-calibrated technical questions based on candidate profile.
2. **Real-time Evaluation**: Analyzes technical correctness, communication clarity, and system design depth.
3. **Adaptive Probing**: If a candidate misses key edge cases or gives an incomplete answer, an adaptive follow-up agent steps in to probe deeper.
4. **Comprehensive Analysis**: Synthesizes structured scorecards, identifies core strengths, highlights improvement areas, and generates an actionable **4-week learning roadmap**.

---

## ✨ Key Features

- 🤖 **LangGraph Multi-Agent Engine**: Modular graph state machine with 4 specialized agents powered by **Google Gemini API**.
- 🔒 **Enterprise JWT Security**: Secure Spring Boot 3 REST APIs backed by Spring Security and BCrypt password encryption.
- 🎙️ **Interactive Voice & Speech-to-Text**: Built-in Web Speech API integration allowing candidates to speak or type technical responses.
- 📊 **Visual Scorecards & Analytics**: Interactive radar breakdown for Technical Depth, Communication Clarity, and System Architecture.
- 🗺️ **Personalized 4-Week Roadmap**: AI-generated weekly study plan addressing candidate skill gaps.
- 🗄️ **Relational Persistence**: PostgreSQL schema storing full interview transcripts, scoring history, and user profiles.

---

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph Client ["Frontend Layer (React.js + Vite)"]
        UI[Glassmorphic React SPA]
        Voice[Speech-to-Text Dictation]
        Dashboard[Analytics & Scorecard UI]
    end

    subgraph Backend ["Backend Layer (Java Spring Boot 3)"]
        Gateway[REST Controllers]
        Security[Spring Security & JWT Filter]
        Service[Interview & Session Service]
        AIServiceClient[AI WebClient Proxy]
        JPA[Spring Data JPA Repositories]
    end

    subgraph AIService ["AI Layer (Python FastAPI + LangGraph)"]
        Router[FastAPI Microservice]
        GraphState[LangGraph InterviewState]
        Agent1[1. Question Generation Agent]
        Agent2[2. Answer Evaluation Agent]
        Agent3[3. Adaptive Follow-up Agent]
        Agent4[4. Final Report Agent]
    end

    subgraph External ["External Services & Storage"]
        Gemini[Google Gemini API Engine]
        DB[(PostgreSQL Database)]
    end

    UI -->|HTTPS REST / JWT| Gateway
    Gateway --> Security
    Security --> Service
    Service --> JPA --> DB
    Service --> AIServiceClient
    AIServiceClient -->|HTTP POST| Router
    Router --> GraphState
    GraphState --> Agent1 & Agent2 & Agent3 & Agent4
    Agent1 & Agent2 & Agent3 & Agent4 <-->|LLM Invocation| Gemini
```

---

## 🔄 Multi-Agent LangGraph Workflow

```mermaid
flowchart TD
    Start([Candidate Starts Session]) --> QAgent[Question Generation Agent]
    QAgent --> CandidateInput[Candidate Answers via Speech / Text]
    CandidateInput --> EvalAgent[Answer Evaluation Agent]
    EvalAgent --> Condition{Needs Deep Probe / Follow-up?}
    Condition -- Yes (Incomplete Details) --> FollowAgent[Adaptive Follow-up Agent]
    FollowAgent --> CandidateInput
    Condition -- No (Complete / Max Qs Reached) --> CheckNext{More Questions?}
    CheckNext -- Yes --> QAgent
    CheckNext -- No --> SummaryAgent[Final Report Agent]
    SummaryAgent --> Scorecard([Generate Scorecard & 4-Week Roadmap])
```

### Agent Roles & Responsibilities:

| Agent | Purpose | LLM Output |
| :--- | :--- | :--- |
| **1. Question Agent** | Formulates role-tailored technical questions | `topic`, `question_text`, `focus_area`, `difficulty` |
| **2. Evaluator Agent** | Scores technical accuracy, clarity & depth (1-10) | `technical_score`, `strengths`, `improvements`, `needs_followup` |
| **3. Follow-up Agent** | Probes missing edge cases or ambiguous statements | `followup_question_text`, `focus`, `hint` |
| **4. Summary Agent** | Aggregates session performance & creates roadmap | `overall_score`, `hiring_recommendation`, `actionable_roadmap` |

---

## 🛠️ Tech Stack & Rationale

| Layer | Technology | Why We Used It |
| :--- | :--- | :--- |
| **Frontend** | React 18, Vite, Lucide Icons, Recharts | Fast SPA rendering, component modularity, interactive score visualization. |
| **Backend API** | Spring Boot 3, Java 17+ | Enterprise-grade stability, dependency injection, robust security ecosystem. |
| **Security** | Spring Security, JJWT | Stateless authentication with JWT token lifecycle management. |
| **AI Orchestrator** | LangGraph, Python 3.11, FastAPI | Stateful graph state control for multi-agent LLM execution loops. |
| **LLM Provider** | Google Gemini API | Low latency, fast structured JSON extractions, long context window. |
| **Database** | PostgreSQL / H2 In-Memory | Relational transaction safety, indexing, structured data persistence. |

---

## 🗄️ Database Schema

```mermaid
erDiagram
    USERS ||--o{ INTERVIEW_SESSIONS : owns
    INTERVIEW_SESSIONS ||--o{ INTERVIEW_QUESTIONS : contains
    INTERVIEW_QUESTIONS ||--o| CANDIDATE_RESPONSES : answered_by
    INTERVIEW_SESSIONS ||--o| FINAL_REPORTS : generates

    USERS {
        bigint id PK
        string email UK
        string password
        string full_name
        string target_role
        string experience_level
    }

    INTERVIEW_SESSIONS {
        bigint id PK
        bigint user_id FK
        string role
        string tech_stack
        string experience_level
        string status
        double overall_score
    }

    INTERVIEW_QUESTIONS {
        bigint id PK
        bigint session_id FK
        int question_number
        string topic
        string question_text
        boolean is_followup
    }

    CANDIDATE_RESPONSES {
        bigint id PK
        bigint question_id FK
        bigint session_id FK
        string candidate_answer
        int technical_score
        int communication_score
        string feedback_summary
    }

    FINAL_REPORTS {
        bigint id PK
        bigint session_id FK
        int overall_score
        string hiring_recommendation
        string top_strengths_json
        string areas_to_improve_json
        string actionable_roadmap_json
    }
```

---

## 🚀 Getting Started

### Prerequisites
- **Java**: JDK 17 or higher
- **Node.js**: v18.0 or higher
- **Python**: v3.11 or higher
- **Maven**: 3.8+ (or included Maven wrapper)
- **Gemini API Key**: Obtain from [Google AI Studio](https://aistudio.google.com/)

---

### 1. AI Microservice Setup (Python LangGraph)

```bash
# Navigate to AI service
cd ai-service

# Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure Environment Variables
cp .env.example .env
# Open .env and add your GEMINI_API_KEY=your_actual_key

# Run FastAPI Server
python app/main.py
```
> Server will start at: `http://localhost:8000` (Swagger docs available at `http://localhost:8000/docs`)

---

### 2. Spring Boot Backend Setup (Java)

```bash
# Navigate to backend
cd backend

# Build application
mvn clean package -DskipTests

# Run Spring Boot Application
mvn spring-boot:run
```
> REST API will start at: `http://localhost:8080` (H2 Console: `http://localhost:8080/h2-console`)

---

### 3. React Frontend Setup (Vite)

```bash
# Navigate to frontend
cd frontend

# Install Node modules
npm install

# Start Vite Development Server
npm run dev
```
> Open browser at: `http://localhost:5173`

---

## 🔗 API Endpoints Reference

### Authentication Endpoints (`/api/auth`)
- `POST /api/auth/register` - Create user profile and return JWT token.
- `POST /api/auth/login` - Authenticate user credentials and return JWT token.
- `GET /api/auth/me` - Fetch authenticated user details.

### Interview Session Endpoints (`/api/interview`)
- `POST /api/interview/start` - Initialize session and generate Q1 via AI Service.
- `POST /api/interview/submit-answer` - Submit answer for evaluation & receive next question/follow-up.
- `GET /api/interview/my-sessions` - Retrieve candidate's interview history.
- `GET /api/interview/session/{id}` - Fetch session details, questions, answers, and final report.

### Analytics Endpoints (`/api/analytics`)
- `GET /api/analytics/dashboard` - Get high-level candidate metrics and progress trends.

---

## 📚 Project Documentation

For in-depth architecture specs, API dictionaries, database schemas, and AI agent prompt design, explore our documentation directory:

- 📑 [Architecture Specifications (`docs/ARCHITECTURE.md`)](docs/ARCHITECTURE.md)
- 🔌 [API Specs & Payload Dictionary (`docs/API_DOCUMENTATION.md`)](docs/API_DOCUMENTATION.md)
- 🗄️ [Database Dictionary (`docs/DATABASE_SCHEMA.md`)](docs/DATABASE_SCHEMA.md)
- 🧠 [LangGraph Agent Workflow Guide (`docs/AGENT_WORKFLOW.md`)](docs/AGENT_WORKFLOW.md)

---

## 📄 License & Acknowledgments

Distributed under the **MIT License**. See `LICENSE` for more information.

Built with ❤️ by [Musharraf](https://github.com/Musharraf2) using Spring Boot, LangGraph, React.js, and Google Gemini.