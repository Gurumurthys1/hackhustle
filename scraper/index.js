require('dotenv').config();
const express = require('express');
const { chromium } = require('playwright');
const cloudinary = require('cloudinary').v2;

const app = express();
app.use(express.json());

cloudinary.config({
  cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
  api_key: process.env.CLOUDINARY_API_KEY,
  api_secret: process.env.CLOUDINARY_API_SECRET
});

app.post('/api/scrape', async (req, res) => {
    const { url, platform } = req.body;
    if (!url) return res.status(400).json({ error: "Missing url" });

    let browser;
    try {
        browser = await chromium.launch({ headless: true });
        const page = await browser.newPage();
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });

        let imageSrc = null;
        if (platform === 'instagram') {
            imageSrc = await page.getAttribute('header img[data-testid="user-avatar"]', 'src', { timeout: 5000 }).catch(() => null);
        } else if (platform === 'facebook') {
            imageSrc = await page.getAttribute('svg[role="img"] image', 'xlink:href', { timeout: 5000 }).catch(() => null);
        } else if (platform === 'twitter') {
            imageSrc = await page.getAttribute('a[href$="/photo"] img', 'src', { timeout: 5000 }).catch(() => null);
        } else {
            // Generic fallback
            imageSrc = await page.getAttribute('img', 'src', { timeout: 5000 }).catch(() => null);
        }

        if (!imageSrc) {
            return res.status(404).json({ error: "Profile image not found or scraper blocked." });
        }

        // Upload to Cloudinary
        const uploadResponse = await cloudinary.uploader.upload(imageSrc, {
            folder: "trinetra_fraud_evidence",
            timeout: 10000
        });

        res.json({
            status: "success",
            cloudinary_url: uploadResponse.secure_url
        });
        
    } catch (error) {
        res.status(500).json({ error: error.message });
    } finally {
        if (browser) await browser.close();
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Scraper service running on port ${PORT}`);
});
