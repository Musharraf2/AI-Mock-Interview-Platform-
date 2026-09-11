package com.mockinterview.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "interview_questions")
public class InterviewQuestion {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "session_id", nullable = false)
    private Long sessionId;

    @Column(name = "question_number", nullable = false)
    private Integer questionNumber;

    @Column(nullable = false)
    private String topic;

    @Column(name = "question_text", length = 2000, nullable = false)
    private String questionText;

    @Column(name = "focus_area")
    private String focusArea;

    @Column(name = "is_followup")
    private Boolean isFollowup = false;

    public InterviewQuestion() {}

    public InterviewQuestion(Long sessionId, Integer questionNumber, String topic, String questionText, String focusArea, Boolean isFollowup) {
        this.sessionId = sessionId;
        this.questionNumber = questionNumber;
        this.topic = topic;
        this.questionText = questionText;
        this.focusArea = focusArea;
        this.isFollowup = isFollowup != null ? isFollowup : false;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getSessionId() { return sessionId; }
    public void setSessionId(Long sessionId) { this.sessionId = sessionId; }

    public Integer getQuestionNumber() { return questionNumber; }
    public void setQuestionNumber(Integer questionNumber) { this.questionNumber = questionNumber; }

    public String getTopic() { return topic; }
    public void setTopic(String topic) { this.topic = topic; }

    public String getQuestionText() { return questionText; }
    public void setQuestionText(String questionText) { this.questionText = questionText; }

    public String getFocusArea() { return focusArea; }
    public void setFocusArea(String focusArea) { this.focusArea = focusArea; }

    public Boolean getIsFollowup() { return isFollowup; }
    public void setIsFollowup(Boolean isFollowup) { this.isFollowup = isFollowup; }
}
