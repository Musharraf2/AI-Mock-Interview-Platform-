package com.mockinterview.controller;

import com.mockinterview.entity.InterviewSession;
import com.mockinterview.entity.User;
import com.mockinterview.service.AuthService;
import com.mockinterview.service.InterviewSessionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.*;

@RestController
@RequestMapping("/api/analytics")
public class AnalyticsController {

    @Autowired
    private InterviewSessionService interviewService;

    @Autowired
    private AuthService authService;

    @GetMapping("/dashboard")
    public ResponseEntity<Map<String, Object>> getDashboardAnalytics(Authentication authentication) {
        User user = authService.getUserByEmail(authentication.getName());
        List<InterviewSession> sessions = interviewService.getUserSessions(user.getId());

        int totalSessions = sessions.size();
        long completedSessions = sessions.stream().filter(s -> "COMPLETED".equalsIgnoreCase(s.getStatus())).count();

        double avgScore = sessions.stream()
                .filter(s -> s.getOverallScore() != null)
                .mapToDouble(InterviewSession::getOverallScore)
                .average()
                .orElse(0.0);

        List<Map<String, Object>> sessionTrends = new ArrayList<>();
        for (InterviewSession s : sessions) {
            Map<String, Object> item = new HashMap<>();
            item.put("id", s.getId());
            item.put("role", s.getRole());
            item.put("tech_stack", s.getTechStack());
            item.put("score", s.getOverallScore() != null ? s.getOverallScore() : 0);
            item.put("created_at", s.getCreatedAt());
            sessionTrends.add(item);
        }

        Map<String, Object> response = new HashMap<>();
        response.put("total_sessions", totalSessions);
        response.put("completed_sessions", completedSessions);
        response.put("average_score", Math.round(avgScore * 10.0) / 10.0);
        response.put("user_profile", user);
        response.put("session_history", sessionTrends);

        return ResponseEntity.ok(response);
    }
}
