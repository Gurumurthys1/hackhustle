package ai.trinetra.dto;

import java.time.Instant;
import java.util.UUID;

public class ReturnClaimResponse {
    private UUID claimId;
    private String status;
    private String message;
    private Instant estimatedResolution;
    private String trackingUrl;

    public ReturnClaimResponse() {}

    public static class Builder {
        private final ReturnClaimResponse r = new ReturnClaimResponse();
        public Builder claimId(UUID id) { r.claimId = id; return this; }
        public Builder status(String s) { r.status = s; return this; }
        public Builder message(String m) { r.message = m; return this; }
        public Builder estimatedResolution(Instant t) { r.estimatedResolution = t; return this; }
        public Builder trackingUrl(String u) { r.trackingUrl = u; return this; }
        public ReturnClaimResponse build() { return r; }
    }

    public static Builder builder() { return new Builder(); }

    public UUID getClaimId() { return claimId; }
    public String getStatus() { return status; }
}
