package com.trinetra.fraud.models;

import lombok.Data;

@Data
public class ScraperResponse {
    private String status;
    private String cloudinary_url;
    private String error;
}
