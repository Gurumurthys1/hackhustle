package com.trinetra.fraud.models;

import jakarta.persistence.*;
import lombok.Data;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "face_recognition_results")
@Data
public class FaceRecognitionResult {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "claim_id", nullable = false)
    private String claimId;

    @Column(name = "user_id", nullable = false)
    private String userId;

    @Column(name = "registered_image_cloudinary_url", nullable = false)
    private String registeredImageCloudinaryUrl;

    @Column(name = "social_image_cloudinary_url")
    private String socialImageCloudinaryUrl;

    @Column(name = "similarity_score")
    private Double similarityScore;

    @Column(name = "status", nullable = false)
    @Enumerated(EnumType.STRING)
    private ProcessStatus status;

    @Column(name = "decision", nullable = false)
    @Enumerated(EnumType.STRING)
    private FraudDecision decision;

    @Column(name = "enforce_detection_used")
    private Boolean enforceDetectionUsed = false;

    @Column(name = "error_reason")
    private String errorReason;

    @Column(name = "reviewed_by")
    private String reviewedBy;

    @Column(name = "reviewed_at")
    private Instant reviewedAt;

    @Column(name = "created_at", insertable = false, updatable = false)
    private Instant createdAt;
}
