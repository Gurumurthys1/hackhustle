package com.trinetra.fraud.models;

import lombok.Data;

@Data
public class FaceCompareResponse {
    private boolean verified;
    private double distance;
    private double similarity;
}
