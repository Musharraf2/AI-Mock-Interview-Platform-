package com.mockinterview.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "final_reports")
public class FinalReport {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "session_id", nullable = false, unique = true)
    private Long sessionId;

    @Column(name = "overall_score")
    private Integer overallScore;

    @Column(name = "technical_score")
    private Integer technicalScore;

    @Column(name = "communication_score")
    private Integer communicationScore;

    @Column(name = "problem_solving_score")
    private Integer problemSolvingScore;

    @Column(name = "hiring_recommendation")
    private String hiringRecommendation;

    @Column(name = "summary_verdict", length = 2000)
    private String summaryVerdict;

    @Column(name = "top_strengths_json", length = 2000)
    private String topStrengthsJson;

    @Column(name = "areas_to_improve_json", length = 2000)
    private String areasToImproveJson;

    @Column(name = "actionable_roadmap_json", length = 4000)
    private String actionableRoadmapJson;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
    }

    public FinalReport() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getSessionId() { return sessionId; }
    public void setSessionId(Long sessionId) { this.sessionId = sessionId; }

    public Integer getOverallScore() { return overallScore; }
    public void setOverallScore(Integer overallScore) { this.overallScore = overallScore; }

    public Integer getTechnicalScore() { return technicalScore; }
    public void setTechnicalScore(Integer technicalScore) { this.technicalScore = technicalScore; }

    public Integer getCommunicationScore() { return communicationScore; }
    public void setCommunicationScore(Integer communicationScore) { this.communicationScore = communicationScore; }

    public Integer getProblemSolvingScore() { return problemSolvingScore; }
    public void setProblemSolvingScore(Integer problemSolvingScore) { this.problemSolvingScore = problemSolvingScore; }

    public String getHiringRecommendation() { return hiringRecommendation; }
    public void setHiringRecommendation(String hiringRecommendation) { this.hiringRecommendation = hiringRecommendation; }

    public String getSummaryVerdict() { return summaryVerdict; }
    public void setSummaryVerdict(String summaryVerdict) { this.summaryVerdict = summaryVerdict; }

    public String getTopStrengthsJson() { return topStrengthsJson; }
    public void setTopStrengthsJson(String topStrengthsJson) { this.topStrengthsJson = topStrengthsJson; }

    public String getAreasToImproveJson() { return areasToImproveJson; }
    public void setAreasToImproveJson(String areasToImproveJson) { this.areasToImproveJson = areasToImproveJson; }

    public String getActionableRoadmapJson() { return actionableRoadmapJson; }
    public void setActionableRoadmapJson(String actionableRoadmapJson) { this.actionableRoadmapJson = actionableRoadmapJson; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
