package ai.trinetra.service;

import ai.trinetra.dto.*;
import ai.trinetra.model.ReturnClaim;
import ai.trinetra.repository.ReturnClaimRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@Service
public class ReturnClaimService {

    private static final Logger log = LoggerFactory.getLogger(ReturnClaimService.class);
    private static final String TOPIC_CLAIMS = "trinetra.return.claims";

    private final ReturnClaimRepository repository;
    private final KafkaTemplate<String, String> kafkaTemplate;
    private final ObjectMapper objectMapper;

    public ReturnClaimService(ReturnClaimRepository repository,
                              KafkaTemplate<String, String> kafkaTemplate,
                              ObjectMapper objectMapper) {
        this.repository = repository;
        this.kafkaTemplate = kafkaTemplate;
        this.objectMapper = objectMapper;
    }

    @Transactional
    public ReturnClaimResponse submitClaim(ReturnClaimRequest request,
                                           String deviceFP, String ip) {
        ReturnClaim claim = ReturnClaim.builder()
            .id(UUID.randomUUID())
            .accountId(request.getAccountId())
            .orderId(request.getOrderId())
            .claimType(request.getClaimType())
            .status("SUBMITTED")
            .description(request.getDescription())
            .deviceFingerprint(deviceFP)
            .ipAddress(ip)
            .consentGiven(request.isConsentGiven())
            .createdAt(Instant.now())
            .updatedAt(Instant.now())
            .build();

        repository.save(claim);

        ClaimEvent event = ClaimEvent.builder()
            .claimId(claim.getId())
            .accountId(request.getAccountId())
            .orderId(request.getOrderId())
            .claimType(request.getClaimType())
            .images(request.getImages())
            .receiptImage(request.getReceiptImage())
            .deviceFingerprint(deviceFP)
            .ipAddress(ip)
            .timestamp(Instant.now())
            .build();

        try {
            kafkaTemplate.send(TOPIC_CLAIMS,
                claim.getId().toString(),
                objectMapper.writeValueAsString(event));
            log.info("Claim published to Kafka. claimId={}", claim.getId());
        } catch (Exception e) {
            log.error("Kafka publish failed — scoring will retry from DB", e);
        }

        return ReturnClaimResponse.builder()
            .claimId(claim.getId())
            .status("PROCESSING")
            .message("Your return request has been received. You'll receive an email update shortly.")
            .estimatedResolution(Instant.now().plus(48, ChronoUnit.HOURS))
            .trackingUrl("/api/v1/returns/" + claim.getId())
            .build();
    }

    /**
     * Get claim status for the customer tracker.
     * Only returns claims belonging to the given accountId (ownership check).
     */
    public Optional<Map<String, Object>> getClaimStatus(UUID claimId, UUID accountId) {
        return repository.findById(claimId)
            .filter(c -> c.getAccountId().equals(accountId))
            .map(c -> Map.<String, Object>of(
                "id",        c.getId().toString(),
                "status",    c.getStatus(),
                "claimType", c.getClaimType(),
                "createdAt", c.getCreatedAt().toString(),
                "message",   buildCustomerMessage(c.getStatus()),
                "tier",      c.getFraudTier() != null ? c.getFraudTier() : "PROCESSING"
            ));
    }

    /**
     * DPDPA 2023, Section 9 — Right to Explanation.
     * Returns human-readable text. Never exposes the raw fraud score to customers.
     */
    public Optional<Map<String, Object>> getCustomerExplanation(UUID claimId, UUID accountId) {
        return repository.findById(claimId)
            .filter(c -> c.getAccountId().equals(accountId))
            .map(c -> Map.<String, Object>of(
                "claimId",        c.getId().toString(),
                "status",         c.getStatus(),
                "explanation",    buildCustomerMessage(c.getStatus()),
                "nextSteps",      buildNextSteps(c.getStatus()),
                "contactSupport", "support@trinetra.ai",
                "dpdpaReference", "You have the right to object to this decision under DPDPA 2023"
            ));
    }

    private String buildCustomerMessage(String status) {
        return switch (status) {
            case "SUBMITTED", "PROCESSING", "SCORED" ->
                "Your return is being processed. This usually takes a few minutes.";
            case "APPROVED" ->
                "Your return has been approved. Your refund will be credited in 3–5 business days.";
            case "DENIED" ->
                "We were unable to approve this return. You may appeal this decision.";
            case "UNDER_REVIEW" ->
                "Your return requires additional review. Our team will contact you within 24 hours.";
            case "ESCALATED" ->
                "Your return has been escalated to our senior review team. Expect contact within 4 hours.";
            default -> "Your return is being processed.";
        };
    }

    private String buildNextSteps(String status) {
        return switch (status) {
            case "APPROVED" -> "No action required. Check your bank/UPI in 3–5 business days.";
            case "DENIED"   -> "Email support@trinetra.ai with your order ID to appeal.";
            default         -> "No action needed. We'll notify you by email when your status changes.";
        };
    }
}
