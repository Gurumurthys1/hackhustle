package ai.trinetra.repository;

import ai.trinetra.model.ReturnClaim;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;

public interface ReturnClaimRepository extends JpaRepository<ReturnClaim, UUID> {
}
