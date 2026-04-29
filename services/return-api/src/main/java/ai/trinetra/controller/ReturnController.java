package ai.trinetra.controller;

import ai.trinetra.dto.ReturnClaimRequest;
import ai.trinetra.dto.ReturnClaimResponse;
import ai.trinetra.model.ReturnClaim;
import ai.trinetra.service.ReturnClaimService;
import ai.trinetra.service.AuditService;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1")
@CrossOrigin(origins = {"http://localhost:5173", "http://localhost:5174"})
public class ReturnController {

    private static final Logger log = LoggerFactory.getLogger(ReturnController.class);

    private final ReturnClaimService returnClaimService;
    private final AuditService auditService;

    public ReturnController(ReturnClaimService returnClaimService, AuditService auditService) {
        this.returnClaimService = returnClaimService;
        this.auditService = auditService;
    }

    /** POST /api/v1/returns — Submit a new return claim */
    @PostMapping("/returns")
    public ResponseEntity<ReturnClaimResponse> submitReturn(
            @Valid @RequestBody ReturnClaimRequest request,
            @RequestHeader(value = "X-Device-Fingerprint", required = false) String deviceFP,
            @RequestHeader(value = "X-Forwarded-For", required = false) String ipAddress) {

        // COMPLIANCE: consent_given MUST be true — cannot proceed without it
        if (!request.isConsentGiven()) {
            return ResponseEntity.badRequest().build();
        }

        log.info("Return claim submitted. account={}, order={}, type={}",
                request.getAccountId(), request.getOrderId(), request.getClaimType());

        ReturnClaimResponse response = returnClaimService.submitClaim(request, deviceFP, ipAddress);

        auditService.log("return_claims", response.getClaimId(),
                        "CLAIM_SUBMITTED", "CUSTOMER", request.getAccountId(),
                        null, Map.of("status", "SUBMITTED", "type", request.getClaimType()),
                        ipAddress);

        return ResponseEntity.accepted().body(response);
    }

    /** GET /api/v1/returns/{claimId}?accountId= — Track return status */
    @GetMapping("/returns/{claimId}")
    public ResponseEntity<?> getReturnStatus(
            @PathVariable UUID claimId,
            @RequestParam UUID accountId) {

        return returnClaimService.getClaimStatus(claimId, accountId)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    /** GET /api/v1/returns/{claimId}/explanation — DPDPA Right to Explanation */
    @GetMapping("/returns/{claimId}/explanation")
    public ResponseEntity<?> getExplanation(
            @PathVariable UUID claimId,
            @RequestParam UUID accountId) {

        // Customer's right to explanation — required by DPDPA 2023, Section 9
        return returnClaimService.getCustomerExplanation(claimId, accountId)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    /** GET /api/v1/health — Simple health check */
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of("status", "UP", "service", "return-api"));
    }
}

