package com.trinetra.fraud.models;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class FraudCheckResponse {
    private String claim_id;
    private String status;
    private FraudDecision decision;
    private String action;
    private Instant timestamp;
}
