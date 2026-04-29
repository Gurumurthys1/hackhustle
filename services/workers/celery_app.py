from celery import Celery
import os

app = Celery(
    'trinetra-workers',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    include=[
        'workers.image_worker',
        'workers.receipt_worker',
        'workers.carrier_worker',
        'workers.behavioral_worker',
        'workers.graph_worker',
        'workers.aggregator',
    ]
)

app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    task_acks_late=True,               # Re-queue on worker crash
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,      # ML tasks are heavy — process one at a time
    task_routes={
        'workers.image_worker.*':      {'queue': 'image'},
        'workers.receipt_worker.*':    {'queue': 'receipt'},
        'workers.carrier_worker.*':    {'queue': 'carrier'},
        'workers.behavioral_worker.*': {'queue': 'behavioral'},
        'workers.graph_worker.*':      {'queue': 'graph'},
        'workers.aggregator.*':        {'queue': 'aggregator'},
    },
    task_default_queue='default',
)
