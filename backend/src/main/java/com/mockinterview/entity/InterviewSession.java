package com.mockinterview.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "interview_sessions")
public class InterviewSession {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(nullable = false)
    private String role;

    @Column(name = "tech_stack", nullable = false)
    private String techStack;

    @Column(name = "experience_level", nullable = false)
    private String experienceLevel;

    @Column(name = "max_questions")
    private Integer maxQuestions = 5;

    @Column(name = "current_question_number")
    private Integer currentQuestionNumber = 0;

    @Column(nullable = false)
    private String status; // IN_PROGRESS, COMPLETED

    @Column(name = "overall_score")
    private Double overallScore;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
        if (this.status == null) {
            this.status = "IN_PROGRESS";
        }
    }

    public InterviewSession() {}

    public InterviewSession(Long userId, String role, String techStack, String experienceLevel, Integer maxQuestions) {
        this.userId = userId;
        this.role = role;
        this.techStack = techStack;
        this.experienceLevel = experienceLevel;
        this.maxQuestions = maxQuestions;
        this.status = "IN_PROGRESS";
        this.currentQuestionNumber = 1;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }

    public String getTechStack() { return techStack; }
    public void setTechStack(String techStack) { this.techStack = techStack; }

    public String getExperienceLevel() { return experienceLevel; }
    public void setExperienceLevel(String experienceLevel) { this.experienceLevel = experienceLevel; }

    public Integer getMaxQuestions() { return maxQuestions; }
    public void setMaxQuestions(Integer maxQuestions) { this.maxQuestions = maxQuestions; }

    public Integer getCurrentQuestionNumber() { return currentQuestionNumber; }
    public void setCurrentQuestionNumber(Integer currentQuestionNumber) { this.currentQuestionNumber = currentQuestionNumber; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public Double getOverallScore() { return overallScore; }
    public void setOverallScore(Double overallScore) { this.overallScore = overallScore; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
