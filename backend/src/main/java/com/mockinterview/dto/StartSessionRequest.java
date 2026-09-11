package com.mockinterview.dto;

import jakarta.validation.constraints.NotBlank;

public class StartSessionRequest {

    @NotBlank(message = "Role is required")
    private String role;

    @NotBlank(message = "Tech stack is required")
    private String techStack;

    @NotBlank(message = "Experience level is required")
    private String experienceLevel;

    private Integer maxQuestions = 5;

    public StartSessionRequest() {}

    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }

    public String getTechStack() { return techStack; }
    public void setTechStack(String techStack) { this.techStack = techStack; }

    public String getExperienceLevel() { return experienceLevel; }
    public void setExperienceLevel(String experienceLevel) { this.experienceLevel = experienceLevel; }

    public Integer getMaxQuestions() { return maxQuestions; }
    public void setMaxQuestions(Integer maxQuestions) { this.maxQuestions = maxQuestions; }
}
