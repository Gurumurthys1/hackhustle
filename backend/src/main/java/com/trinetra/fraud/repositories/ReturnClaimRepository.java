package com.trinetra.fraud.repositories;

import com.trinetra.fraud.models.ReturnClaim;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.UUID;

@Repository
public interface ReturnClaimRepository extends JpaRepository<ReturnClaim, UUID> {
}
