"""
Bridge: Consumes from Kafka → dispatches to Celery workers in parallel.
This is the entry point for all fraud analysis.
"""
from kafka import KafkaConsumer
import json
import os
from celery import group
# Note: These tasks will be defined in the workers directory
from workers.image_worker import analyze_claim_images
from workers.receipt_worker import analyze_claim_receipt
from workers.carrier_worker import validate_claim_carrier
from workers.behavioral_worker import score_claim_behavior
from workers.graph_worker import analyze_claim_graph
import structlog

log = structlog.get_logger()

def start_consumer():
    consumer = KafkaConsumer(
        'trinetra.return.claims',
        bootstrap_servers=os.getenv('KAFKA_BROKERS', 'localhost:9092'),
        group_id='fraud-engine',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=False,  # Manual commit after processing
    )
    
    log.info("Fraud engine consumer started")
    
    for message in consumer:
        claim = message.value
        claim_id = claim.get('claimId')
        
        if not claim_id:
            log.warning("Received claim without ID", claim=claim)
            continue

        log.info("Processing claim", claim_id=claim_id)
        
        try:
            # Dispatch all workers in PARALLEL via Celery group
            job = group([
                analyze_claim_images.s(claim_id, claim),
                analyze_claim_receipt.s(claim_id, claim),
                validate_claim_carrier.s(claim_id, claim),
                score_claim_behavior.s(claim_id, claim),
                analyze_claim_graph.s(claim_id, claim),
            ])
            
            # Chord: when all complete → aggregate scores
            # Note: aggregator task will be defined in aggregator.py
            from workers.aggregator import aggregate_scores
            chord_job = job | aggregate_scores.s(claim_id)
            chord_job.apply_async()
            
            consumer.commit()
        
        except Exception as e:
            log.error("Consumer processing failed", claim_id=claim_id, error=str(e))
            # Don't commit — message will be reprocessed

if __name__ == "__main__":
    start_consumer()
