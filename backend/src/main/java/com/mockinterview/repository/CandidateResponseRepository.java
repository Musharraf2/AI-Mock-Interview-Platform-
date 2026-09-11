package com.mockinterview.repository;

import com.mockinterview.entity.CandidateResponse;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.Optional;

public interface CandidateResponseRepository extends JpaRepository<CandidateResponse, Long> {
    List<CandidateResponse> findBySessionId(Long sessionId);
    Optional<CandidateResponse> findByQuestionId(Long questionId);
}
