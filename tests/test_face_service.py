import pytest
import httpx
import time

BASE_URL = "http://localhost:8000"

IMG1_URL = "https://raw.githubusercontent.com/serengil/deepface/master/tests/dataset/img1.jpg"
IMG2_URL = "https://raw.githubusercontent.com/serengil/deepface/master/tests/dataset/img2.jpg"
IMG3_URL = "https://raw.githubusercontent.com/serengil/deepface/master/tests/dataset/img3.jpg"
NO_FACE_URL = "https://upload.wikimedia.org/wikipedia/commons/3/3a/Cat03.jpg"
INVALID_URL = "https://notreal.xyz/fake.jpg"

def test_same_person_high_score():
    response = httpx.post(f"{BASE_URL}/compare", json={
        "registered_image_url": IMG1_URL,
        "social_image_url": IMG2_URL
    }, timeout=60.0)
    assert response.status_code == 200
    data = response.json()
    assert data["verified"] is True
    assert data["similarity"] >= 0.80

def test_different_people_low_score():
    response = httpx.post(f"{BASE_URL}/compare", json={
        "registered_image_url": IMG1_URL,
        "social_image_url": IMG3_URL
    }, timeout=60.0)
    assert response.status_code == 200
    data = response.json()
    assert data["verified"] is False
    assert data["similarity"] < 0.60

def test_no_face_no_crash():
    response = httpx.post(f"{BASE_URL}/compare", json={
        "registered_image_url": NO_FACE_URL,
        "social_image_url": IMG1_URL
    }, timeout=60.0)
    assert response.status_code == 200
    data = response.json()
    assert "similarity" in data

def test_invalid_url_returns_error():
    response = httpx.post(f"{BASE_URL}/compare", json={
        "registered_image_url": INVALID_URL,
        "social_image_url": IMG1_URL
    }, timeout=60.0)
    assert response.status_code in [400, 422, 500]
    assert "detail" in response.json() or "error" in response.json()

def test_response_schema():
    response = httpx.post(f"{BASE_URL}/compare", json={
        "registered_image_url": IMG1_URL,
        "social_image_url": IMG2_URL
    }, timeout=60.0)
    data = response.json()
    assert "verified" in data
    assert "similarity" in data
    assert "distance" in data
    # model isn't returned by default in the implementation, but we check what we can.
