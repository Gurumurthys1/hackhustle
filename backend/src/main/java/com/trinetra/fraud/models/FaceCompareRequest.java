package com.trinetra.fraud.models;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class FaceCompareRequest {
    private String registered_image_url;
    private String social_image_url;
}
