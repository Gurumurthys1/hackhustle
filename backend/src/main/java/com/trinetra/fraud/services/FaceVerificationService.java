package com.trinetra.fraud.services;

import com.trinetra.fraud.models.FaceCompareRequest;
import com.trinetra.fraud.models.FaceCompareResponse;
import com.trinetra.fraud.models.FraudDecision;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

@Service
public class FaceVerificationService {
    
    @Value("${fastapi.url}")
    private String fastApiUrl;
    private final RestTemplate restTemplate;
    
    public FaceVerificationService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public FraudDecision processFaceVerification(String registeredImageUrl, String socialImageUrl) {
        FaceCompareRequest request = new FaceCompareRequest(registeredImageUrl, socialImageUrl);
        try {
            FaceCompareResponse response = restTemplate.postForObject(
                fastApiUrl + "/compare", request, FaceCompareResponse.class);
                
            if (response == null) {
                return FraudDecision.FACE_EVIDENCE_IGNORED;
            }
            
            double similarity = response.getSimilarity();
            
            if (similarity >= 0.80) {
                return FraudDecision.FRAUD_LIKELY;
            } else if (similarity >= 0.60) {
                return FraudDecision.MANUAL_REVIEW;
            } else {
                return FraudDecision.FACE_EVIDENCE_IGNORED;
            }
        } catch (Exception e) {
            // Fallback behaviour if the step cannot complete
            System.err.println("Face verification failed: " + e.getMessage());
            return FraudDecision.FACE_EVIDENCE_IGNORED; 
        }
    }
}
