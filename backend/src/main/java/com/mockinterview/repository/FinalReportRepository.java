package com.mockinterview.repository;

import com.mockinterview.entity.FinalReport;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface FinalReportRepository extends JpaRepository<FinalReport, Long> {
    Optional<FinalReport> findBySessionId(Long sessionId);
}
