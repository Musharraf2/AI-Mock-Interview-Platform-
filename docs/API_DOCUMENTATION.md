# API Documentation Reference

Complete REST API specification for the **AI Mock Interview Platform**.

---

## 🔐 Base URLs
- **Spring Boot Backend**: `http://localhost:8080/api`
- **LangGraph AI Microservice**: `http://localhost:8000/api/ai`

---

## 1. Authentication Endpoints

### 1.1 Candidate Registration
- **Endpoint**: `POST /api/auth/register`
- **Auth**: Public

#### Request Body
```json
{
  "email": "candidate@example.com",
  "password": "password123",
  "fullName": "John Doe",
  "targetRole": "Java Backend Developer",
  "experienceLevel": "Fresher / Entry Level"
}
```

#### Response (200 OK)
```json
{
  "token": "eyJhbGciOiJIUzI1NiJ9...",
  "email": "candidate@example.com",
  "fullName": "John Doe",
  "userId": 1
}
```

---

### 1.2 Candidate Login
- **Endpoint**: `POST /api/auth/login`
- **Auth**: Public

#### Request Body
```json
{
  "email": "candidate@example.com",
  "password": "password123"
}
```

#### Response (200 OK)
```json
{
  "token": "eyJhbGciOiJIUzI1NiJ9...",
  "email": "candidate@example.com",
  "fullName": "John Doe",
  "userId": 1
}
```

---

## 2. Interview Session Endpoints

### 2.1 Start Interview Session
- **Endpoint**: `POST /api/interview/start`
- **Auth**: Required (`Authorization: Bearer <JWT>`)

#### Request Body
```json
{
  "role": "Java Backend Developer",
  "techStack": "Java 17, Spring Boot, PostgreSQL, Docker",
  "experienceLevel": "Fresher / Entry Level",
  "maxQuestions": 5
}
```

#### Response (200 OK)
```json
{
  "session": {
    "id": 101,
    "userId": 1,
    "role": "Java Backend Developer",
    "techStack": "Java 17, Spring Boot, PostgreSQL, Docker",
    "experienceLevel": "Fresher / Entry Level",
    "maxQuestions": 5,
    "currentQuestionNumber": 1,
    "status": "IN_PROGRESS",
    "createdAt": "2026-09-12T00:15:00"
  },
  "current_question": {
    "id": 501,
    "sessionId": 101,
    "questionNumber": 1,
    "topic": "Spring Boot Dependency Injection",
    "questionText": "Can you explain the difference between @Autowired field injection and constructor injection in Spring Boot?",
    "focusArea": "Dependency Injection & Clean Architecture",
    "isFollowup": false
  }
}
```

---

### 2.2 Submit Candidate Answer
- **Endpoint**: `POST /api/interview/submit-answer`
- **Auth**: Required (`Authorization: Bearer <JWT>`)

#### Request Body
```json
{
  "sessionId": 101,
  "questionId": 501,
  "answerText": "Constructor injection is preferred over field injection because it makes dependencies explicit, allows creating immutable beans with final fields, and simplifies unit testing without Spring context."
}
```

#### Response (200 OK)
```json
{
  "evaluation": {
    "question_number": 1,
    "question_text": "Can you explain the difference between @Autowired field injection and constructor injection in Spring Boot?",
    "technical_score": 9,
    "communication_score": 9,
    "problem_solving_score": 8,
    "overall_question_score": 8.7,
    "strengths": [
      "Explicitly mentioned bean immutability with final fields",
      "Pointed out unit testing simplicity without Spring Context"
    ],
    "improvements": [
      "Could mention circular dependency handling differences"
    ],
    "feedback_summary": "Excellent explanation highlighting clean architecture benefits.",
    "needs_followup": false
  },
  "is_complete": false,
  "next_question": {
    "id": 502,
    "sessionId": 101,
    "questionNumber": 2,
    "topic": "PostgreSQL Indexing",
    "questionText": "How do B-tree indices speed up SQL query performance in PostgreSQL, and when might an index degrade performance?",
    "focusArea": "Database Performance Tuning",
    "isFollowup": false
  }
}
```

---

## 3. AI LangGraph Service Endpoints

### 3.1 AI Question Generation
- **Endpoint**: `POST http://localhost:8000/api/ai/generate-question`

#### Request Body
```json
{
  "role": "Java Backend Developer",
  "tech_stack": "Spring Boot, PostgreSQL",
  "experience_level": "Junior",
  "max_questions": 5
}
```

---

### 3.2 AI Answer Evaluation
- **Endpoint**: `POST http://localhost:8000/api/ai/evaluate`

#### Request Body
```json
{
  "role": "Java Backend Developer",
  "experience_level": "Junior",
  "question_number": 1,
  "topic": "Spring Boot",
  "question_text": "Explain Dependency Injection.",
  "candidate_response": "Dependency Injection passes dependent objects to a class instead of creating them inside."
}
```
