package ai.trinetra.dto;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

public class ClaimEvent {
    private UUID claimId;
    private UUID accountId;
    private UUID orderId;
    private String claimType;
    private List<String> images;
    private String receiptImage;
    private String deviceFingerprint;
    private String ipAddress;
    private Instant timestamp;

    public ClaimEvent() {}

    public static class Builder {
        private final ClaimEvent e = new ClaimEvent();
        public Builder claimId(UUID id) { e.claimId = id; return this; }
        public Builder accountId(UUID id) { e.accountId = id; return this; }
        public Builder orderId(UUID id) { e.orderId = id; return this; }
        public Builder claimType(String t) { e.claimType = t; return this; }
        public Builder images(List<String> img) { e.images = img; return this; }
        public Builder receiptImage(String img) { e.receiptImage = img; return this; }
        public Builder deviceFingerprint(String fp) { e.deviceFingerprint = fp; return this; }
        public Builder ipAddress(String ip) { e.ipAddress = ip; return this; }
        public Builder timestamp(Instant t) { e.timestamp = t; return this; }
        public ClaimEvent build() { return e; }
    }

    public static Builder builder() { return new Builder(); }

    // Getters for Jackson
    public UUID getClaimId() { return claimId; }
    public UUID getAccountId() { return accountId; }
    public UUID getOrderId() { return orderId; }
    public String getClaimType() { return claimType; }
    public List<String> getImages() { return images; }
    public String getReceiptImage() { return receiptImage; }
    public String getDeviceFingerprint() { return deviceFingerprint; }
    public String getIpAddress() { return ipAddress; }
    public Instant getTimestamp() { return timestamp; }
}
