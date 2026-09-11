package com.mockinterview.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.mockinterview.dto.StartSessionRequest;
import com.mockinterview.dto.SubmitAnswerRequest;
import com.mockinterview.entity.*;
import com.mockinterview.repository.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;

@Service
public class InterviewSessionService {

    @Autowired
    private InterviewSessionRepository sessionRepository;

    @Autowired
    private InterviewQuestionRepository questionRepository;

    @Autowired
    private CandidateResponseRepository responseRepository;

    @Autowired
    private FinalReportRepository reportRepository;

    @Autowired
    private AIServiceClient aiServiceClient;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Transactional
    public Map<String, Object> startSession(Long userId, StartSessionRequest request) {
        InterviewSession session = new InterviewSession(
                userId,
                request.getRole(),
                request.getTechStack(),
                request.getExperienceLevel(),
                request.getMaxQuestions() != null ? request.getMaxQuestions() : 5
        );
        session = sessionRepository.save(session);

        // Call AI Service to generate Question 1
        Map<String, Object> aiResponse = aiServiceClient.generateNextQuestion(
                session.getRole(),
                session.getTechStack(),
                session.getExperienceLevel(),
                1,
                session.getMaxQuestions(),
                Collections.emptyList()
        );

        Map<String, Object> qMap = (Map<String, Object>) aiResponse.get("question");

        InterviewQuestion question = new InterviewQuestion(
                session.getId(),
                1,
                (String) qMap.getOrDefault("topic", "General Technical"),
                (String) qMap.getOrDefault("question_text", "Explain core concepts of your tech stack."),
                (String) qMap.getOrDefault("focus_area", "Fundamentals"),
                false
        );
        question = questionRepository.save(question);

        Map<String, Object> result = new HashMap<>();
        result.put("session", session);
        result.put("current_question", question);
        return result;
    }

    @Transactional
    public Map<String, Object> submitAnswer(Long userId, SubmitAnswerRequest request) {
        InterviewSession session = sessionRepository.findById(request.getSessionId())
                .orElseThrow(() -> new RuntimeException("Session not found"));

        InterviewQuestion question = questionRepository.findById(request.getQuestionId())
                .orElseThrow(() -> new RuntimeException("Question not found"));

        // Call AI Service to evaluate answer
        Map<String, Object> aiEvalResponse = aiServiceClient.evaluateAnswer(
                session.getRole(),
                session.getTechStack(),
                session.getExperienceLevel(),
                question.getQuestionNumber(),
                question.getTopic(),
                question.getQuestionText(),
                request.getAnswerText()
        );

        Map<String, Object> evalMap = (Map<String, Object>) aiEvalResponse.get("evaluation");
        Map<String, Object> followupMap = (Map<String, Object>) aiEvalResponse.get("followup");

        // Save Candidate Response
        CandidateResponse candidateResp = new CandidateResponse();
        candidateResp.setSessionId(session.getId());
        candidateResp.setQuestionId(question.getId());
        candidateResp.setCandidateAnswer(request.getAnswerText());
        candidateResp.setTechnicalScore((Integer) evalMap.getOrDefault("technical_score", 7));
        candidateResp.setCommunicationScore((Integer) evalMap.getOrDefault("communication_score", 7));
        candidateResp.setProblemSolvingScore((Integer) evalMap.getOrDefault("problem_solving_score", 7));
        
        Number overallQScore = (Number) evalMap.getOrDefault("overall_question_score", 7.0);
        candidateResp.setOverallScore(overallQScore.doubleValue());
        candidateResp.setFeedbackSummary((String) evalMap.get("feedback_summary"));

        try {
            candidateResp.setStrengthsJson(objectMapper.writeValueAsString(evalMap.get("strengths")));
            candidateResp.setImprovementsJson(objectMapper.writeValueAsString(evalMap.get("improvements")));
        } catch (Exception e) {
            candidateResp.setStrengthsJson("[]");
            candidateResp.setImprovementsJson("[]");
        }

        responseRepository.save(candidateResp);

        Map<String, Object> result = new HashMap<>();
        result.put("evaluation", evalMap);

        // Check if follow-up question returned from AI
        if (followupMap != null && followupMap.containsKey("followup_question_text")) {
            InterviewQuestion followupQ = new InterviewQuestion(
                    session.getId(),
                    question.getQuestionNumber(),
                    question.getTopic() + " (Follow-up)",
                    (String) followupMap.get("followup_question_text"),
                    (String) followupMap.getOrDefault("focus", "Deep Dive"),
                    true
            );
            followupQ = questionRepository.save(followupQ);
            result.put("is_complete", false);
            result.put("next_question", followupQ);
            return result;
        }

        // Advance to next question or complete interview
        int nextQNum = session.getCurrentQuestionNumber() + 1;
        if (nextQNum <= session.getMaxQuestions()) {
            session.setCurrentQuestionNumber(nextQNum);
            sessionRepository.save(session);

            Map<String, Object> nextQResponse = aiServiceClient.generateNextQuestion(
                    session.getRole(),
                    session.getTechStack(),
                    session.getExperienceLevel(),
                    nextQNum,
                    session.getMaxQuestions(),
                    Collections.emptyList()
            );

            Map<String, Object> nextQMap = (Map<String, Object>) nextQResponse.get("question");

            InterviewQuestion nextQuestion = new InterviewQuestion(
                    session.getId(),
                    nextQNum,
                    (String) nextQMap.getOrDefault("topic", "Technical Focus"),
                    (String) nextQMap.getOrDefault("question_text", "Describe your approach to problem solving."),
                    (String) nextQMap.getOrDefault("focus_area", "Technical Depth"),
                    false
            );
            nextQuestion = questionRepository.save(nextQuestion);

            result.put("is_complete", false);
            result.put("next_question", nextQuestion);
        } else {
            // Complete Interview Session
            session.setStatus("COMPLETED");
            sessionRepository.save(session);

            // Generate Final Report
            FinalReport finalReport = buildAndSaveFinalReport(session);
            result.put("is_complete", true);
            result.put("final_report", finalReport);
        }

        return result;
    }

    @Transactional
    public FinalReport endSessionEarly(Long userId, Long sessionId) {
        InterviewSession session = sessionRepository.findById(sessionId)
                .orElseThrow(() -> new RuntimeException("Session not found"));

        session.setStatus("ENDED_EARLY");
        sessionRepository.save(session);

        return buildAndSaveFinalReport(session);
    }

    private FinalReport buildAndSaveFinalReport(InterviewSession session) {
        List<CandidateResponse> responses = responseRepository.findBySessionId(session.getId());
        
        // Check if report already generated
        Optional<FinalReport> existingReport = reportRepository.findBySessionId(session.getId());
        if (existingReport.isPresent()) {
            return existingReport.get();
        }

        List<Map<String, Object>> evalsList = new ArrayList<>();
        for (CandidateResponse r : responses) {
            Map<String, Object> m = new HashMap<>();
            m.put("technical_score", r.getTechnicalScore());
            m.put("communication_score", r.getCommunicationScore());
            m.put("problem_solving_score", r.getProblemSolvingScore());
            m.put("feedback_summary", r.getFeedbackSummary());
            evalsList.add(m);
        }

        Map<String, Object> repMap;
        if (responses.isEmpty()) {
            repMap = new HashMap<>();
            repMap.put("overall_score", 0);
            repMap.put("technical_score", 0);
            repMap.put("communication_score", 0);
            repMap.put("problem_solving_score", 0);
            repMap.put("hiring_recommendation", "Incomplete");
            repMap.put("summary_verdict", "Session ended early before any candidate responses were submitted.");
            repMap.put("top_strengths", List.of("Session initialized"));
            repMap.put("areas_to_improve", List.of("Complete at least 1 technical question"));
            repMap.put("actionable_roadmap", List.of(
                    Map.of("week", 1, "topic", "Mock Practice", "task", "Complete a full 5-question mock interview session")
            ));
        } else {
            Map<String, Object> aiReportResp = aiServiceClient.generateFinalReport(
                    session.getRole(),
                    session.getTechStack(),
                    session.getExperienceLevel(),
                    evalsList
            );
            repMap = (Map<String, Object>) aiReportResp.get("report");
        }

        FinalReport report = new FinalReport();
        report.setSessionId(session.getId());
        report.setOverallScore((Integer) repMap.getOrDefault("overall_score", 80));
        report.setTechnicalScore((Integer) repMap.getOrDefault("technical_score", 80));
        report.setCommunicationScore((Integer) repMap.getOrDefault("communication_score", 80));
        report.setProblemSolvingScore((Integer) repMap.getOrDefault("problem_solving_score", 80));
        report.setHiringRecommendation((String) repMap.getOrDefault("hiring_recommendation", "Hire"));
        report.setSummaryVerdict((String) repMap.get("summary_verdict"));

        try {
            report.setTopStrengthsJson(objectMapper.writeValueAsString(repMap.get("top_strengths")));
            report.setAreasToImproveJson(objectMapper.writeValueAsString(repMap.get("areas_to_improve")));
            report.setActionableRoadmapJson(objectMapper.writeValueAsString(repMap.get("actionable_roadmap")));
        } catch (Exception e) {
            report.setTopStrengthsJson("[]");
            report.setAreasToImproveJson("[]");
            report.setActionableRoadmapJson("[]");
        }

        session.setOverallScore(report.getOverallScore().doubleValue());
        sessionRepository.save(session);

        return reportRepository.save(report);
    }

    public List<InterviewSession> getUserSessions(Long userId) {
        return sessionRepository.findByUserIdOrderByCreatedAtDesc(userId);
    }

    public Map<String, Object> getSessionDetails(Long sessionId) {
        InterviewSession session = sessionRepository.findById(sessionId)
                .orElseThrow(() -> new RuntimeException("Session not found"));
        List<InterviewQuestion> questions = questionRepository.findBySessionIdOrderByQuestionNumberAsc(sessionId);
        List<CandidateResponse> responses = responseRepository.findBySessionId(sessionId);
        Optional<FinalReport> report = reportRepository.findBySessionId(sessionId);

        Map<String, Object> data = new HashMap<>();
        data.put("session", session);
        data.put("questions", questions);
        data.put("responses", responses);
        data.put("final_report", report.orElse(null));
        return data;
    }
}
