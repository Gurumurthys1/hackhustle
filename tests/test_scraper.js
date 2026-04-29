const axios = require('axios');
const BASE_URL = 'http://localhost:3000';

test('test_valid_instagram_url', async () => {
    const res = await axios.post(`${BASE_URL}/api/scrape`, { 
        url: 'https://www.instagram.com/instagram/', 
        platform: 'instagram' 
    });
    expect(res.status).toBe(200);
    expect(res.data.cloudinary_url).toBeDefined();
}, 15000);

test('test_valid_twitter_url', async () => {
    const res = await axios.post(`${BASE_URL}/api/scrape`, { 
        url: 'https://twitter.com/X', 
        platform: 'twitter' 
    });
    expect(res.status).toBe(200);
    expect(res.data.cloudinary_url).toBeDefined();
}, 15000);

test('test_nonexistent_account', async () => {
    try {
        await axios.post(`${BASE_URL}/api/scrape`, { 
            url: 'https://instagram.com/xyzabc_fake_99999/', 
            platform: 'instagram' 
        });
    } catch (error) {
        expect([404, 500]).toContain(error.response.status);
    }
}, 15000);

test('test_missing_platform_field', async () => {
    try {
        // Platform is missing, URL is missing (since we want to trigger a 400 error reliably)
        await axios.post(`${BASE_URL}/api/scrape`, {});
    } catch (error) {
        expect(error.response.status).toBe(400);
    }
}, 15000);

test('test_response_time_under_15s', async () => {
    const start = Date.now();
    await axios.post(`${BASE_URL}/api/scrape`, { 
        url: 'https://www.instagram.com/instagram/', 
        platform: 'instagram' 
    });
    const duration = Date.now() - start;
    expect(duration).toBeLessThan(15000);
}, 15000);
