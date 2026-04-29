package ai.trinetra.model;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "return_claims")
public class ReturnClaim {
    @Id
    private UUID id;
    
    @Column(name = "account_id")
    private UUID accountId;
    
    @Column(name = "order_id")
    private UUID orderId;
    
    @Column(name = "claim_type")
    private String claimType;
    
    private String status;
    private String description;
    
    @Column(name = "fraud_score")
    private Integer fraudScore;
    
    @Column(name = "fraud_tier")
    private String fraudTier;
    
    @Column(name = "device_fingerprint")
    private String deviceFingerprint;
    
    @Column(name = "ip_address")
    private String ipAddress;
    
    @Column(name = "consent_given")
    private boolean consentGiven;
    
    @Column(name = "created_at")
    private Instant createdAt;
    
    @Column(name = "updated_at")
    private Instant updatedAt;

    // Manual Builder Pattern
    public static class Builder {
        private final ReturnClaim claim = new ReturnClaim();
        public Builder id(UUID id) { claim.id = id; return this; }
        public Builder accountId(UUID id) { claim.accountId = id; return this; }
        public Builder orderId(UUID id) { claim.orderId = id; return this; }
        public Builder claimType(String type) { claim.claimType = type; return this; }
        public Builder status(String s) { claim.status = s; return this; }
        public Builder description(String d) { claim.description = d; return this; }
        public Builder deviceFingerprint(String f) { claim.deviceFingerprint = f; return this; }
        public Builder ipAddress(String ip) { claim.ipAddress = ip; return this; }
        public Builder consentGiven(boolean c) { claim.consentGiven = c; return this; }
        public Builder createdAt(Instant t) { claim.createdAt = t; return this; }
        public Builder updatedAt(Instant t) { claim.updatedAt = t; return this; }
        public ReturnClaim build() { return claim; }
    }
    
    public static Builder builder() { return new Builder(); }

    // Getters
    public UUID getId() { return id; }
    public UUID getAccountId() { return accountId; }
    public UUID getOrderId() { return orderId; }
    public String getClaimType() { return claimType; }
    public String getStatus() { return status; }
    public String getDescription() { return description; }
    public Integer getFraudScore() { return fraudScore; }
    public String getFraudTier() { return fraudTier; }
    public String getDeviceFingerprint() { return deviceFingerprint; }
    public String getIpAddress() { return ipAddress; }
    public boolean isConsentGiven() { return consentGiven; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }

    // Setters
    public void setId(UUID id) { this.id = id; }
    public void setStatus(String status) { this.status = status; }
    public void setFraudScore(Integer score) { this.fraudScore = score; }
    public void setFraudTier(String tier) { this.fraudTier = tier; }
}
