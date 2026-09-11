package com.mockinterview.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class AIServiceClient {

    private final RestTemplate restTemplate;

    @Value("${ai-service.url:http://localhost:8000}")
    private String aiServiceUrl;

    public AIServiceClient(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public Map<String, Object> generateNextQuestion(String role, String techStack, String experienceLevel, int questionNumber, int maxQuestions, List<Map<String, Object>> evaluations) {
        String url = aiServiceUrl + "/api/ai/generate-question";

        Map<String, Object> body = new HashMap<>();
        body.put("role", role);
        body.put("tech_stack", techStack);
        body.put("experience_level", experienceLevel);
        body.put("max_questions", maxQuestions);
        body.put("question_number", questionNumber);
        body.put("evaluations", evaluations != null ? evaluations : List.of());

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<Map<String, Object>> request = new HttpEntity<>(body, headers);

        try {
            return restTemplate.postForObject(url, request, Map.class);
        } catch (Exception e) {
            String firstTech = techStack.split(",")[0].trim();
            Map<String, Object> fallback = new HashMap<>();
            Map<String, Object> q = new HashMap<>();
            q.put("question_number", questionNumber);
            
            switch (questionNumber) {
                case 1:
                    q.put("topic", firstTech + " Core Architecture");
                    q.put("question_text", "In " + firstTech + ", how do you design components for high cohesion and low coupling? Can you walk through a production code example?");
                    q.put("focus_area", "Architecture & Clean Code");
                    break;
                case 2:
                    q.put("topic", "Database Optimization & SQL Performance");
                    q.put("question_text", "When working with databases in a " + role + " application, how do you identify slow queries and design composite indices to optimize performance?");
                    q.put("focus_area", "Database Indexing & Query Tuning");
                    break;
                case 3:
                    q.put("topic", "API Security & Authentication");
                    q.put("question_text", "How do you secure REST API endpoints in " + firstTech + " against SQL injection, XSS, and unauthorized token tampering?");
                    q.put("focus_area", "Security & Authorization");
                    break;
                case 4:
                    q.put("topic", "Concurrency & Thread Safety");
                    q.put("question_text", "How do you manage concurrent request processing, race conditions, or async tasks in " + firstTech + " under heavy load?");
                    q.put("focus_area", "Multithreading & Concurrency");
                    break;
                default:
                    q.put("topic", "System Resilience & Production Monitoring");
                    q.put("question_text", "What exception handling, logging, and circuit breaker patterns do you implement in " + firstTech + " to handle third-party service degradation?");
                    q.put("focus_area", "System Reliability & Fault Tolerance");
                    break;
            }
            
            q.put("difficulty", "Medium");
            fallback.put("status", "success_fallback");
            fallback.put("question", q);
            return fallback;
        }
    }

    private boolean isCopiedOrInvalidAnswer(String questionText, String candidateAnswer) {
        if (candidateAnswer == null || candidateAnswer.trim().length() < 12) {
            return true;
        }
        String qClean = questionText.toLowerCase().replaceAll("[^a-z0-9 ]", "");
        String aClean = candidateAnswer.toLowerCase().replaceAll("[^a-z0-9 ]", "");

        if (aClean.equals(qClean) || aClean.contains("i dont know") || aClean.contains("idk") || aClean.equals("test")) {
            return true;
        }

        String[] aWords = aClean.split("\\s+");
        String[] qWords = qClean.split("\\s+");
        java.util.Set<String> qWordSet = new java.util.HashSet<>(java.util.Arrays.asList(qWords));

        int overlap = 0;
        for (String w : aWords) {
            if (qWordSet.contains(w)) {
                overlap++;
            }
        }

        double ratio = (double) overlap / aWords.length;
        return ratio > 0.70 && aWords.length <= qWords.length + 4;
    }

    public Map<String, Object> evaluateAnswer(String role, String techStack, String experienceLevel, int questionNumber, String topic, String questionText, String candidateAnswer) {
        String firstTech = techStack.split(",")[0].trim();
        String idealAns = "An ideal response for '" + questionText + "' should define the core principles of " + topic + ", explain concrete production architecture trade-offs, and address error handling and scalability.";
        String inDepthExpl = "### 📘 In-Depth Technical Deep Dive: " + topic + "\n\n" +
                "1. **Core Architectural Concept**:\nTo answer '" + questionText + "' at a senior level, begin with a clear definition and explain why this design pattern or paradigm is used in " + firstTech + ".\n\n" +
                "2. **Production Best Practices**:\n- Use clean component separation and explicit interfaces.\n- Ensure thread safety, connection pooling, and proper resource cleanup under load.\n\n" +
                "3. **Edge Case Handling & Performance**:\nAlways address fault isolation, retry policies, and database transaction boundaries.";

        if (isCopiedOrInvalidAnswer(questionText, candidateAnswer)) {
            Map<String, Object> fallback = new HashMap<>();
            Map<String, Object> eval = new HashMap<>();
            eval.put("question_number", questionNumber);
            eval.put("question_text", questionText);
            eval.put("technical_score", 0);
            eval.put("communication_score", 0);
            eval.put("problem_solving_score", 0);
            eval.put("overall_question_score", 0.0);
            eval.put("feedback_summary", "No actual technical answer provided. You pasted the question text back or submitted an incomplete response.");
            eval.put("ideal_answer", idealAns);
            eval.put("in_depth_explanation", inDepthExpl);
            eval.put("strengths", List.of());
            eval.put("improvements", List.of("Provide a concrete technical answer instead of repeating the question text"));
            eval.put("needs_followup", false);
            fallback.put("status", "success");
            fallback.put("evaluation", eval);
            return fallback;
        }

        String url = aiServiceUrl + "/api/ai/evaluate";

        Map<String, Object> body = new HashMap<>();
        body.put("role", role);
        body.put("tech_stack", techStack);
        body.put("experience_level", experienceLevel);
        body.put("question_number", questionNumber);
        body.put("topic", topic);
        body.put("question_text", questionText);
        body.put("candidate_response", candidateAnswer);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<Map<String, Object>> request = new HttpEntity<>(body, headers);

        try {
            return restTemplate.postForObject(url, request, Map.class);
        } catch (Exception e) {
            Map<String, Object> fallback = new HashMap<>();
            Map<String, Object> eval = new HashMap<>();
            eval.put("question_number", questionNumber);
            eval.put("question_text", questionText);
            eval.put("technical_score", 6);
            eval.put("communication_score", 6);
            eval.put("problem_solving_score", 6);
            eval.put("overall_question_score", 6.0);
            eval.put("feedback_summary", "Response submitted and analyzed. Review the reference solution and expanded deep-dive explanation below.");
            eval.put("ideal_answer", idealAns);
            eval.put("in_depth_explanation", inDepthExpl);
            eval.put("strengths", List.of("Answer submitted for evaluation"));
            eval.put("improvements", List.of("Provide deeper technical design details and code patterns"));
            eval.put("needs_followup", false);
            fallback.put("status", "success_fallback");
            fallback.put("evaluation", eval);
            return fallback;
        }
    }

    public Map<String, Object> generateBatchQuestions(String role, String techStack, String experienceLevel, int maxQuestions) {
        String url = aiServiceUrl + "/api/ai/generate-questions-batch";

        Map<String, Object> body = new HashMap<>();
        body.put("role", role);
        body.put("tech_stack", techStack);
        body.put("experience_level", experienceLevel);
        body.put("max_questions", maxQuestions);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<Map<String, Object>> request = new HttpEntity<>(body, headers);

        try {
            return restTemplate.postForObject(url, request, Map.class);
        } catch (Exception e) {
            String firstTech = techStack != null ? techStack.split(",")[0].trim() : "Software";
            Map<String, Object> fallback = new HashMap<>();
            List<Map<String, Object>> qList = new java.util.ArrayList<>();

            List<Map<String, String>> pool = List.of(
                    Map.of("topic", firstTech + " Core Architecture", "text", "In " + firstTech + ", how do you design components for high cohesion and low coupling? Can you walk through a production design pattern example?", "focus", "Clean Architecture"),
                    Map.of("topic", "Database Optimization & SQL Performance", "text", "When working with databases in a " + role + " application, how do you identify slow queries and design composite indices to optimize performance?", "focus", "Database Indexing & Query Tuning"),
                    Map.of("topic", "API Security & Authentication", "text", "How do you secure REST API endpoints in " + firstTech + " against SQL injection, XSS, and unauthorized token tampering?", "focus", "Security & Authorization"),
                    Map.of("topic", "Concurrency & Thread Safety", "text", "How do you manage concurrent request processing, race conditions, or async tasks in " + firstTech + " under heavy load?", "focus", "Multithreading & Concurrency"),
                    Map.of("topic", "Caching & Memory Management", "text", "What caching strategies (such as Redis or Cache-Aside) do you implement in " + firstTech + " to minimize database overhead?", "focus", "System Performance & Caching"),
                    Map.of("topic", "System Resilience & Circuit Breakers", "text", "What exception handling, logging, and circuit breaker patterns do you implement in " + firstTech + " to handle third-party service degradation?", "focus", "System Reliability & Fault Tolerance")
            );

            java.util.Collections.shuffle(pool, new java.util.Random(System.currentTimeMillis()));

            for (int i = 1; i <= maxQuestions; i++) {
                Map<String, String> tItem = pool.get((i - 1) % pool.size());
                Map<String, Object> q = new HashMap<>();
                q.put("question_number", i);
                q.put("topic", tItem.get("topic"));
                q.put("question_text", tItem.get("text"));
                q.put("focus_area", tItem.get("focus"));
                q.put("difficulty", "Medium");
                qList.add(q);
            }
            fallback.put("status", "success_fallback");
            fallback.put("questions", qList);
            return fallback;
        }
    }

    public Map<String, Object> generateInDepthExplanation(String topic, String questionText, String idealAnswer, String candidateAnswer, String techStack) {
        String url = aiServiceUrl + "/api/ai/explain";

        Map<String, Object> body = new HashMap<>();
        body.put("topic", topic);
        body.put("question_text", questionText);
        body.put("ideal_answer", idealAnswer);
        body.put("candidate_response", candidateAnswer);
        body.put("tech_stack", techStack);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<Map<String, Object>> request = new HttpEntity<>(body, headers);

        try {
            return restTemplate.postForObject(url, request, Map.class);
        } catch (Exception e) {
            String firstTech = techStack != null ? techStack.split(",")[0].trim() : "Software";
            Map<String, Object> fallback = new HashMap<>();
            String inDepthExpl = "### 📘 In-Depth Technical Deep Dive: " + topic + "\n\n" +
                    "1. **Core Architectural Concept**:\nTo answer '" + questionText + "' at a senior level, begin with a clear definition and explain why this design pattern or paradigm is used in " + firstTech + ".\n\n" +
                    "2. **Production Best Practices**:\n- Use clean component separation and explicit interfaces.\n- Ensure thread safety, connection pooling, and proper resource cleanup under load.\n\n" +
                    "3. **Edge Case Handling & Performance**:\nAlways address fault isolation, retry policies, and database transaction boundaries.";
            fallback.put("status", "success_fallback");
            fallback.put("in_depth_explanation", inDepthExpl);
            return fallback;
        }
    }

    public Map<String, Object> generateFinalReport(String role, String techStack, String experienceLevel, List<Map<String, Object>> evaluations) {
        String url = aiServiceUrl + "/api/ai/final-report";

        Map<String, Object> body = new HashMap<>();
        body.put("role", role);
        body.put("tech_stack", techStack);
        body.put("experience_level", experienceLevel);
        body.put("evaluations", evaluations);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<Map<String, Object>> request = new HttpEntity<>(body, headers);

        try {
            return restTemplate.postForObject(url, request, Map.class);
        } catch (Exception e) {
            Map<String, Object> fallback = new HashMap<>();
            Map<String, Object> rep = new HashMap<>();

            double sumTech = 0, sumComm = 0, sumProb = 0;
            int count = evaluations != null ? evaluations.size() : 0;

            if (evaluations != null) {
                for (Map<String, Object> ev : evaluations) {
                    Number t = (Number) ev.getOrDefault("technical_score", 0);
                    Number c = (Number) ev.getOrDefault("communication_score", 0);
                    Number p = (Number) ev.getOrDefault("problem_solving_score", 0);
                    sumTech += t != null ? t.doubleValue() : 0;
                    sumComm += c != null ? c.doubleValue() : 0;
                    sumProb += p != null ? p.doubleValue() : 0;
                }
            }

            int avgTech = count > 0 ? (int) Math.round((sumTech / count) * 10.0) : 0;
            int avgComm = count > 0 ? (int) Math.round((sumComm / count) * 10.0) : 0;
            int avgProb = count > 0 ? (int) Math.round((sumProb / count) * 10.0) : 0;
            int overall = count > 0 ? (int) Math.round((avgTech + avgComm + avgProb) / 3.0) : 0;

            String rec = overall == 0 || overall < 40 ? "No Hire / Reject" : (overall < 70 ? "Weak Hire" : "Hire");
            String verdict = overall == 0 ? "Candidate did not provide valid technical answers to the interview questions." : "Candidate demonstrated foundational knowledge for the target role.";

            rep.put("overall_score", overall);
            rep.put("technical_score", avgTech);
            rep.put("communication_score", avgComm);
            rep.put("problem_solving_score", avgProb);
            rep.put("hiring_recommendation", rec);
            rep.put("summary_verdict", verdict);
            rep.put("top_strengths", overall == 0 ? List.of("Attempted mock interview session") : List.of("Strong framework understanding", "Clear communication"));
            rep.put("areas_to_improve", List.of("Provide actual technical responses", "Study system design trade-offs"));
            rep.put("actionable_roadmap", List.of(
                    Map.of("week", 1, "topic", "Deep Framework Concepts", "task", "Study internal architecture"),
                    Map.of("week", 2, "topic", "Performance Tuning", "task", "Profile DB queries and memory allocations")
            ));
            fallback.put("status", "success_fallback");
            fallback.put("report", rep);
            return fallback;
        }
    }
}
