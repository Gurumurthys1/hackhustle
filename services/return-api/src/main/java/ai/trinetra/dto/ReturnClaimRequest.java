package ai.trinetra.dto;

import java.util.List;
import java.util.UUID;

public class ReturnClaimRequest {
    private UUID accountId;
    private UUID orderId;
    private String claimType;
    private String description;
    private List<String> images;
    private String receiptImage;
    private boolean consentGiven;

    public ReturnClaimRequest() {}

    // Getters
    public UUID getAccountId() { return accountId; }
    public UUID getOrderId() { return orderId; }
    public String getClaimType() { return claimType; }
    public String getDescription() { return description; }
    public List<String> getImages() { return images; }
    public String getReceiptImage() { return receiptImage; }
    public boolean isConsentGiven() { return consentGiven; }

    // Setters
    public void setAccountId(UUID accountId) { this.accountId = accountId; }
    public void setOrderId(UUID orderId) { this.orderId = orderId; }
    public void setClaimType(String claimType) { this.claimType = claimType; }
    public void setDescription(String description) { this.description = description; }
    public void setImages(List<String> images) { this.images = images; }
    public void setReceiptImage(String receiptImage) { this.receiptImage = receiptImage; }
    public void setConsentGiven(boolean consentGiven) { this.consentGiven = consentGiven; }
}
