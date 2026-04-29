package com.trinetra.fraud.models;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class FraudCheckRequest {
    private String claim_id;
    private String user_id;
    private String social_media_url;
    private String social_media_platform;
    private String dress_match_status;
}
