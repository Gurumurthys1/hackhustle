package com.trinetra;

import com.github.tomakehurst.wiremock.WireMockServer;
import com.github.tomakehurst.wiremock.client.WireMock;
import com.trinetra.fraud.FraudApplication;
import com.trinetra.fraud.models.FaceRecognitionResult;
import com.trinetra.fraud.repositories.FaceRecognitionResultRepository;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;

import static com.github.tomakehurst.wiremock.client.WireMock.*;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;

@SpringBootTest(classes = FraudApplication.class)
@AutoConfigureMockMvc
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class FraudPipelineIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private FaceRecognitionResultRepository repository;

    private static WireMockServer wireMockServer;

    @BeforeAll
    static void startWireMock() {
        wireMockServer = new WireMockServer(9090);
        wireMockServer.start();
        WireMock.configureFor("localhost", 9090);
    }

    @AfterAll
    static void stopWireMock() {
        wireMockServer.stop();
    }

    @DynamicPropertySource
    static void overrideProperties(DynamicPropertyRegistry registry) {
        registry.add("fastapi.url", () -> "http://localhost:9090");
        registry.add("scraper.url", () -> "http://localhost:9090");
    }

    @BeforeEach
    void reset() {
        WireMock.reset();
        repository.deleteAll();
    }

    @Test
    void testFraudLikelyPath() throws Exception {
        stubFor(post(urlEqualTo("/api/scrape"))
                .willReturn(aResponse().withHeader("Content-Type", "application/json")
                .withBody("{\"status\":\"success\", \"cloudinary_url\":\"http://cloud.com/img.jpg\"}")));
                
        stubFor(post(urlEqualTo("/compare"))
                .willReturn(aResponse().withHeader("Content-Type", "application/json")
                .withBody("{\"verified\":true, \"similarity\":0.87, \"distance\":0.13}")));

        String payload = "{\"claim_id\":\"C-1\", \"user_id\":\"U-1\", \"social_media_url\":\"url\", \"social_media_platform\":\"ig\", \"dress_match_status\":\"MATCH_FOUND\"}";

        mockMvc.perform(MockMvcRequestBuilders.post("/api/fraud/face-check")
                .contentType(MediaType.APPLICATION_JSON)
                .content(payload))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.decision").value("FRAUD_LIKELY"));
    }

    @Test
    void testManualReviewPath() throws Exception {
        stubFor(post(urlEqualTo("/api/scrape"))
                .willReturn(aResponse().withHeader("Content-Type", "application/json")
                .withBody("{\"status\":\"success\", \"cloudinary_url\":\"http://cloud.com/img.jpg\"}")));
                
        stubFor(post(urlEqualTo("/compare"))
                .willReturn(aResponse().withHeader("Content-Type", "application/json")
                .withBody("{\"verified\":false, \"similarity\":0.71, \"distance\":0.29}")));

        String payload = "{\"claim_id\":\"C-2\", \"user_id\":\"U-2\", \"social_media_url\":\"url\", \"social_media_platform\":\"ig\", \"dress_match_status\":\"MATCH_FOUND\"}";

        mockMvc.perform(MockMvcRequestBuilders.post("/api/fraud/face-check")
                .contentType(MediaType.APPLICATION_JSON)
                .content(payload))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.decision").value("MANUAL_REVIEW"));
    }

    @Test
    void testFaceEvidenceIgnored() throws Exception {
        stubFor(post(urlEqualTo("/api/scrape"))
                .willReturn(aResponse().withHeader("Content-Type", "application/json")
                .withBody("{\"status\":\"success\", \"cloudinary_url\":\"http://cloud.com/img.jpg\"}")));
                
        stubFor(post(urlEqualTo("/compare"))
                .willReturn(aResponse().withHeader("Content-Type", "application/json")
                .withBody("{\"verified\":false, \"similarity\":0.45, \"distance\":0.55}")));

        String payload = "{\"claim_id\":\"C-3\", \"user_id\":\"U-3\", \"social_media_url\":\"url\", \"social_media_platform\":\"ig\", \"dress_match_status\":\"MATCH_FOUND\"}";

        mockMvc.perform(MockMvcRequestBuilders.post("/api/fraud/face-check")
                .contentType(MediaType.APPLICATION_JSON)
                .content(payload))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.decision").value("FACE_EVIDENCE_IGNORED"));
    }

    @Test
    void testGatekeepingNOMatchBypasses() throws Exception {
        String payload = "{\"claim_id\":\"C-4\", \"user_id\":\"U-4\", \"social_media_url\":\"url\", \"social_media_platform\":\"ig\", \"dress_match_status\":\"NO_MATCH\"}";

        mockMvc.perform(MockMvcRequestBuilders.post("/api/fraud/face-check")
                .contentType(MediaType.APPLICATION_JSON)
                .content(payload))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.decision").value("FACE_EVIDENCE_IGNORED"));

        verify(0, postRequestedFor(urlEqualTo("/api/scrape")));
        verify(0, postRequestedFor(urlEqualTo("/compare")));
        assertEquals(0, repository.count());
    }

    @Test
    void testScraperDownFallback() throws Exception {
        stubFor(post(urlEqualTo("/api/scrape"))
                .willReturn(aResponse().withStatus(500)));

        String payload = "{\"claim_id\":\"C-5\", \"user_id\":\"U-5\", \"social_media_url\":\"url\", \"social_media_platform\":\"ig\", \"dress_match_status\":\"MATCH_FOUND\"}";

        mockMvc.perform(MockMvcRequestBuilders.post("/api/fraud/face-check")
                .contentType(MediaType.APPLICATION_JSON)
                .content(payload))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.decision").value("FACE_EVIDENCE_IGNORED"));

        verify(0, postRequestedFor(urlEqualTo("/compare")));
    }

    @Test
    void testFastAPIDownFallback() throws Exception {
        stubFor(post(urlEqualTo("/api/scrape"))
                .willReturn(aResponse().withHeader("Content-Type", "application/json")
                .withBody("{\"status\":\"success\", \"cloudinary_url\":\"http://cloud.com/img.jpg\"}")));
                
        stubFor(post(urlEqualTo("/compare"))
                .willReturn(aResponse().withStatus(500)));

        String payload = "{\"claim_id\":\"C-6\", \"user_id\":\"U-6\", \"social_media_url\":\"url\", \"social_media_platform\":\"ig\", \"dress_match_status\":\"MATCH_FOUND\"}";

        mockMvc.perform(MockMvcRequestBuilders.post("/api/fraud/face-check")
                .contentType(MediaType.APPLICATION_JSON)
                .content(payload))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.decision").value("FACE_EVIDENCE_IGNORED"));
    }

    @Test
    void testDatabaseRecordSaved() throws Exception {
        stubFor(post(urlEqualTo("/api/scrape"))
                .willReturn(aResponse().withHeader("Content-Type", "application/json")
                .withBody("{\"status\":\"success\", \"cloudinary_url\":\"http://cloud.com/img.jpg\"}")));
                
        stubFor(post(urlEqualTo("/compare"))
                .willReturn(aResponse().withHeader("Content-Type", "application/json")
                .withBody("{\"verified\":true, \"similarity\":0.87, \"distance\":0.13}")));

        String payload = "{\"claim_id\":\"C-7\", \"user_id\":\"U-7\", \"social_media_url\":\"url\", \"social_media_platform\":\"ig\", \"dress_match_status\":\"MATCH_FOUND\"}";

        mockMvc.perform(MockMvcRequestBuilders.post("/api/fraud/face-check")
                .contentType(MediaType.APPLICATION_JSON)
                .content(payload))
                .andExpect(status().isOk());

        List<FaceRecognitionResult> results = repository.findAll();
        assertEquals(1, results.size());
        assertEquals("C-7", results.get(0).getClaimId());
    }

    @Test
    void testDuplicateClaimId() throws Exception {
        stubFor(post(urlEqualTo("/api/scrape"))
                .willReturn(aResponse().withHeader("Content-Type", "application/json")
                .withBody("{\"status\":\"success\", \"cloudinary_url\":\"http://cloud.com/img.jpg\"}")));
                
        stubFor(post(urlEqualTo("/compare"))
                .willReturn(aResponse().withHeader("Content-Type", "application/json")
                .withBody("{\"verified\":true, \"similarity\":0.87, \"distance\":0.13}")));

        String payload = "{\"claim_id\":\"C-8\", \"user_id\":\"U-8\", \"social_media_url\":\"url\", \"social_media_platform\":\"ig\", \"dress_match_status\":\"MATCH_FOUND\"}";

        mockMvc.perform(MockMvcRequestBuilders.post("/api/fraud/face-check")
                .contentType(MediaType.APPLICATION_JSON)
                .content(payload));
                
        mockMvc.perform(MockMvcRequestBuilders.post("/api/fraud/face-check")
                .contentType(MediaType.APPLICATION_JSON)
                .content(payload))
                .andExpect(status().isOk());
                
        assertEquals(2, repository.count()); 
    }
}
