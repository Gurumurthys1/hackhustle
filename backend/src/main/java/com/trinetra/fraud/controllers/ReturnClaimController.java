package com.trinetra.fraud.controllers;

import com.trinetra.fraud.models.ReturnClaim;
import com.trinetra.fraud.repositories.ReturnClaimRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/returns")
@CrossOrigin(origins = "*") // Allow frontend access
public class ReturnClaimController {

    private final ReturnClaimRepository repository;

    public ReturnClaimController(ReturnClaimRepository repository) {
        this.repository = repository;
    }

    @PostMapping
    public ResponseEntity<ReturnClaim> submitClaim(@RequestBody ReturnClaim claim) {
        return ResponseEntity.ok(repository.save(claim));
    }

    @GetMapping
    public ResponseEntity<List<ReturnClaim>> getAllClaims() {
        return ResponseEntity.ok(repository.findAll());
    }

    @PatchMapping("/{id}")
    public ResponseEntity<ReturnClaim> updateStatus(@PathVariable UUID id, @RequestParam String status) {
        return repository.findById(id)
                .map(claim -> {
                    claim.setStatus(status);
                    return ResponseEntity.ok(repository.save(claim));
                })
                .orElse(ResponseEntity.notFound().build());
    }
}
