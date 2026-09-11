# Database Schema & Data Dictionary

This document details the relational data dictionary for the **PostgreSQL** database (with H2 in-memory local fallback).

---

## 📊 Entity Relationship Diagram

```
+------------------+         +--------------------------+
|      users       |         |    interview_sessions    |
+------------------+         +--------------------------+
| id (PK)          |<-------1| id (PK)                  |
| email (UK)       |        *| user_id (FK)             |
| password         |         | role                     |
| full_name        |         | tech_stack               |
| target_role      |         | experience_level         |
| experience_level |         | status                   |
| created_at       |         | overall_score            |
+------------------+         +--------------------------+
                                       |
                                       | 1
                                       v *
                             +--------------------------+
                             |   interview_questions    |
                             +--------------------------+
                             | id (PK)                  |
                             | session_id (FK)          |
                             | question_number          |
                             | topic                    |
                             | question_text            |
                             | focus_area               |
                             | is_followup              |
                             +--------------------------+
                                       |
                                       | 1
                                       v 1
                             +--------------------------+
                             |   candidate_responses    |
                             +--------------------------+
                             | id (PK)                  |
                             | question_id (FK)         |
                             | session_id (FK)          |
                             | candidate_answer         |
                             | technical_score          |
                             | communication_score      |
                             | problem_solving_score    |
                             | feedback_summary         |
                             | strengths_json           |
                             | improvements_json        |
                             +--------------------------+
```

---

## 🗄️ Tables Reference

### 1. `users` Table
Stores candidate authentication details and career targets.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `BIGINT` | `PRIMARY KEY AUTO_INCREMENT` | Unique user identifier |
| `email` | `VARCHAR(255)` | `NOT NULL, UNIQUE` | Candidate login email |
| `password` | `VARCHAR(255)` | `NOT NULL` | BCrypt encrypted password hash |
| `full_name` | `VARCHAR(255)` | `NOT NULL` | Candidate display name |
| `target_role` | `VARCHAR(255)` | `NULLABLE` | Desired job role (e.g. Java Developer) |
| `experience_level` | `VARCHAR(255)` | `NULLABLE` | Experience category (Fresher, Junior, Mid) |
| `created_at` | `TIMESTAMP` | `NOT NULL` | Account registration timestamp |

---

### 2. `interview_sessions` Table
Tracks individual mock interview attempts and state.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `BIGINT` | `PRIMARY KEY AUTO_INCREMENT` | Unique session identifier |
| `user_id` | `BIGINT` | `FOREIGN KEY -> users(id)` | User who owns this session |
| `role` | `VARCHAR(255)` | `NOT NULL` | Configured job title for session |
| `tech_stack` | `VARCHAR(255)` | `NOT NULL` | Target skills/frameworks |
| `experience_level` | `VARCHAR(255)` | `NOT NULL` | Configured experience tier |
| `max_questions` | `INT` | `DEFAULT 5` | Number of questions in session |
| `current_question_number` | `INT` | `DEFAULT 1` | Progress pointer |
| `status` | `VARCHAR(50)` | `NOT NULL` | `IN_PROGRESS` or `COMPLETED` |
| `overall_score` | `DOUBLE` | `NULLABLE` | Weighted final score (0-100) |
| `created_at` | `TIMESTAMP` | `NOT NULL` | Session start timestamp |

---

### 3. `interview_questions` Table
Stores generated technical questions and adaptive probes.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `BIGINT` | `PRIMARY KEY AUTO_INCREMENT` | Unique question identifier |
| `session_id` | `BIGINT` | `FOREIGN KEY -> interview_sessions(id)` | Parent interview session |
| `question_number` | `INT` | `NOT NULL` | Sequence number (1 to N) |
| `topic` | `VARCHAR(255)` | `NOT NULL` | Technical topic/concept |
| `question_text` | `VARCHAR(2000)` | `NOT NULL` | Actual question body |
| `focus_area` | `VARCHAR(255)` | `NULLABLE` | Key assessment area |
| `is_followup` | `BOOLEAN` | `DEFAULT FALSE` | Flag for adaptive probes |

---

### 4. `candidate_responses` Table
Stores candidate answers, real-time AI scoring, and feedback JSON.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `BIGINT` | `PRIMARY KEY AUTO_INCREMENT` | Unique response identifier |
| `question_id` | `BIGINT` | `FOREIGN KEY -> interview_questions(id)` | Question answered |
| `session_id` | `BIGINT` | `FOREIGN KEY -> interview_sessions(id)` | Parent session |
| `candidate_answer` | `VARCHAR(4000)` | `NULLABLE` | Typed or spoken answer text |
| `technical_score` | `INT` | `NULLABLE` | Tech score (1-10) |
| `communication_score` | `INT` | `NULLABLE` | Communication score (1-10) |
| `problem_solving_score` | `INT` | `NULLABLE` | Problem solving score (1-10) |
| `overall_score` | `DOUBLE` | `NULLABLE` | Aggregated response score |
| `feedback_summary` | `VARCHAR(2000)` | `NULLABLE` | Textual feedback |
| `strengths_json` | `VARCHAR(2000)` | `NULLABLE` | JSON array of strength strings |
| `improvements_json` | `VARCHAR(2000)` | `NULLABLE` | JSON array of improvement strings |

---

### 5. `final_reports` Table
Stores overall session scorecard and personalized 4-week learning roadmap.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `BIGINT` | `PRIMARY KEY AUTO_INCREMENT` | Unique report identifier |
| `session_id` | `BIGINT` | `FOREIGN KEY -> interview_sessions(id), UNIQUE` | Session tied to this report |
| `overall_score` | `INT` | `NULLABLE` | Overall candidate score (0-100) |
| `technical_score` | `INT` | `NULLABLE` | Weighted technical score |
| `communication_score` | `INT` | `NULLABLE` | Weighted communication score |
| `problem_solving_score` | `INT` | `NULLABLE` | Weighted problem-solving score |
| `hiring_recommendation` | `VARCHAR(50)` | `NULLABLE` | `Strong Hire`, `Hire`, `Weak Hire` |
| `summary_verdict` | `VARCHAR(2000)` | `NULLABLE` | Overall hiring verdict |
| `top_strengths_json` | `VARCHAR(2000)` | `NULLABLE` | Top 3 strengths JSON array |
| `areas_to_improve_json` | `VARCHAR(2000)` | `NULLABLE` | Priority focus areas JSON array |
| `actionable_roadmap_json` | `VARCHAR(4000)` | `NULLABLE` | 4-Week learning roadmap JSON |
| `created_at` | `TIMESTAMP` | `NOT NULL` | Report generation timestamp |
