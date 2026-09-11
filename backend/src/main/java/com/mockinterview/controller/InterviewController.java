package com.mockinterview.controller;

import com.mockinterview.dto.StartSessionRequest;
import com.mockinterview.dto.SubmitAnswerRequest;
import com.mockinterview.entity.InterviewSession;
import com.mockinterview.entity.User;
import com.mockinterview.service.AuthService;
import com.mockinterview.service.InterviewSessionService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/interview")
public class InterviewController {

    @Autowired
    private InterviewSessionService interviewService;

    @Autowired
    private com.mockinterview.service.AIServiceClient aiServiceClient;

    @Autowired
    private AuthService authService;

    @PostMapping("/start")
    public ResponseEntity<Map<String, Object>> startSession(
            Authentication authentication,
            @Valid @RequestBody StartSessionRequest request) {
        User user = authService.getUserByEmail(authentication.getName());
        return ResponseEntity.ok(interviewService.startSession(user.getId(), request));
    }

    @PostMapping("/submit-answer")
    public ResponseEntity<Map<String, Object>> submitAnswer(
            Authentication authentication,
            @Valid @RequestBody SubmitAnswerRequest request) {
        User user = authService.getUserByEmail(authentication.getName());
        return ResponseEntity.ok(interviewService.submitAnswer(user.getId(), request));
    }

    @PostMapping("/explain")
    public ResponseEntity<Map<String, Object>> explainConcept(@RequestBody Map<String, Object> payload) {
        String topic = (String) payload.getOrDefault("topic", "");
        String questionText = (String) payload.getOrDefault("questionText", "");
        String idealAnswer = (String) payload.getOrDefault("idealAnswer", "");
        String candidateAnswer = (String) payload.getOrDefault("candidateAnswer", "");
        String techStack = (String) payload.getOrDefault("techStack", "");

        return ResponseEntity.ok(aiServiceClient.generateInDepthExplanation(topic, questionText, idealAnswer, candidateAnswer, techStack));
    }

    @GetMapping("/my-sessions")
    public ResponseEntity<List<InterviewSession>> getMySessions(Authentication authentication) {
        User user = authService.getUserByEmail(authentication.getName());
        return ResponseEntity.ok(interviewService.getUserSessions(user.getId()));
    }

    @GetMapping("/session/{id}")
    public ResponseEntity<Map<String, Object>> getSessionDetails(@PathVariable("id") Long id) {
        return ResponseEntity.ok(interviewService.getSessionDetails(id));
    }

    @PostMapping("/end-session/{id}")
    public ResponseEntity<com.mockinterview.entity.FinalReport> endSession(
            Authentication authentication,
            @PathVariable("id") Long id) {
        User user = authService.getUserByEmail(authentication.getName());
        return ResponseEntity.ok(interviewService.endSessionEarly(user.getId(), id));
    }
}
