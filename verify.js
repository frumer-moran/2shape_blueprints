const puppeteer = require('puppeteer');

async function run() {
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900 });
    
    try {
        console.log("Navigating to http://localhost:8000/view_results.html...");
        await page.goto('http://localhost:8000/view_results.html', { waitUntil: 'networkidle2' });
        
        console.log("Clicking #btn-stitch...");
        const stitchButton = await page.$('#btn-stitch');
        await stitchButton.click();
        
        console.log("Waiting 2.5 seconds for rendering...");
        await new Promise(resolve => setTimeout(resolve, 2500));
        
        console.log("Taking screenshot (verify_grounding.png)...");
        await page.screenshot({ path: 'verify_grounding.png' });
        
    } catch (err) {
        console.error(err);
    } finally {
        await browser.close();
    }
}

run();
