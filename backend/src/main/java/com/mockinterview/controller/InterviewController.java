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

    @GetMapping("/my-sessions")
    public ResponseEntity<List<InterviewSession>> getMySessions(Authentication authentication) {
        User user = authService.getUserByEmail(authentication.getName());
        return ResponseEntity.ok(interviewService.getUserSessions(user.getId()));
    }

    @GetMapping("/session/{id}")
    public ResponseEntity<Map<String, Object>> getSessionDetails(@PathVariable("id") Long id) {
        return ResponseEntity.ok(interviewService.getSessionDetails(id));
    }
}
