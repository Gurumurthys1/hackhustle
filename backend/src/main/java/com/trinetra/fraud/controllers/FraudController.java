package com.trinetra.fraud.controllers;

import com.trinetra.fraud.models.FaceRecognitionResult;
import com.trinetra.fraud.models.FraudCheckRequest;
import com.trinetra.fraud.models.FraudCheckResponse;
import com.trinetra.fraud.models.FraudDecision;
import com.trinetra.fraud.models.ProcessStatus;
import com.trinetra.fraud.repositories.FaceRecognitionResultRepository;
import com.trinetra.fraud.services.FaceVerificationService;
import com.trinetra.fraud.services.ScraperServiceClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;

@RestController
@RequestMapping("/api/fraud")
public class FraudController {

    private final FaceVerificationService faceVerificationService;
    private final ScraperServiceClient scraperServiceClient;
    private final FaceRecognitionResultRepository repository;

    public FraudController(FaceVerificationService faceVerificationService, 
                           ScraperServiceClient scraperServiceClient,
                           FaceRecognitionResultRepository repository) {
        this.faceVerificationService = faceVerificationService;
        this.scraperServiceClient = scraperServiceClient;
        this.repository = repository;
    }

    @PostMapping("/face-check")
    public FraudCheckResponse runFaceCheck(@RequestBody FraudCheckRequest request) {
        
        // 1. Dress Match Check
        if (!"MATCH_FOUND".equalsIgnoreCase(request.getDress_match_status())) {
            return new FraudCheckResponse(
                request.getClaim_id(),
                "COMPLETED",
                FraudDecision.FACE_EVIDENCE_IGNORED,
                "DRESS_NOT_MATCHED_SKIPPING_FACE_CHECK",
                Instant.now()
            );
        }

        // 2. Fetch registered user data (Mocked)
        String registeredImageUrl = "https://res.cloudinary.com/demo/image/upload/v1234/registered_user_" + request.getUser_id() + ".jpg";
        
        // 3. Trigger Scraper
        String scrapedImageUrl = scraperServiceClient.scrapeProfileImage(
            request.getSocial_media_url(), 
            request.getSocial_media_platform()
        );

        if (scrapedImageUrl == null) {
            // Scraper failed or account private
            FaceRecognitionResult result = new FaceRecognitionResult();
            result.setClaimId(request.getClaim_id());
            result.setUserId(request.getUser_id());
            result.setRegisteredImageCloudinaryUrl(registeredImageUrl);
            result.setStatus(ProcessStatus.FAILED_DOWNLOAD);
            result.setDecision(FraudDecision.FACE_EVIDENCE_IGNORED);
            result.setErrorReason("Scraper failed to extract image");
            repository.save(result);

            return new FraudCheckResponse(
                request.getClaim_id(),
                "FAILED_DOWNLOAD",
                FraudDecision.FACE_EVIDENCE_IGNORED,
                "SCRAPER_FAILED_SKIPPING_FACE_CHECK",
                Instant.now()
            );
        }

        // 4. Call Face Verification Service
        FraudDecision decision = faceVerificationService.processFaceVerification(
            registeredImageUrl, 
            scrapedImageUrl
        );

        String action = "";
        switch (decision) {
            case FRAUD_LIKELY:
                action = "ESCALATE_TO_USER_VERIFICATION_CALL";
                break;
            case MANUAL_REVIEW:
                action = "ROUTE_TO_ADMIN_QUEUE";
                break;
            case FACE_EVIDENCE_IGNORED:
                action = "CONTINUE_WITH_DRESS_MATCH_ONLY";
                break;
        }

        // 5. Store Results in DB
        FaceRecognitionResult result = new FaceRecognitionResult();
        result.setClaimId(request.getClaim_id());
        result.setUserId(request.getUser_id());
        result.setRegisteredImageCloudinaryUrl(registeredImageUrl);
        result.setSocialImageCloudinaryUrl(scrapedImageUrl);
        result.setStatus(ProcessStatus.COMPLETED);
        result.setDecision(decision);
        repository.save(result);

        return new FraudCheckResponse(
            request.getClaim_id(),
            "COMPLETED",
            decision,
            action,
            Instant.now()
        );
    }
}
