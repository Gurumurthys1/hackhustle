package com.trinetra.fraud.services;

import com.trinetra.fraud.models.ScraperResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Service
public class ScraperServiceClient {

    @Value("${scraper.url}")
    private String scraperUrl;

    private final RestTemplate restTemplate;

    public ScraperServiceClient(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public String scrapeProfileImage(String socialMediaUrl, String platform) {
        Map<String, String> request = new HashMap<>();
        request.put("url", socialMediaUrl);
        request.put("platform", platform);

        try {
            ResponseEntity<Map> response = restTemplate.postForEntity(scraperUrl + "/api/scrape", request, Map.class);
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return (String) response.getBody().get("cloudinary_url");
            }
        } catch (Exception e) {
            System.err.println("Scraper failed: " + e.getMessage());
        }
        return null;
    }
}
