const puppeteer = require('puppeteer');

async function run() {
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900 });
    
    page.on('console', msg => {
        console.log(`[PAGE CONSOLE] ${msg.type().toUpperCase()}: ${msg.text()}`);
    });
    
    page.on('pageerror', err => {
        console.error(`[PAGE ERROR] ${err.toString()}`);
    });
    
    try {
        console.log("Navigating to http://localhost:8000/view_results.html...");
        await page.goto('http://localhost:8000/view_results.html', { waitUntil: 'networkidle2' });
        
        console.log("Clicking #btn-stitch...");
        const stitchButton = await page.$('#btn-stitch');
        await stitchButton.click();
        
        console.log("Waiting 2.5 seconds for rendering...");
        await new Promise(resolve => setTimeout(resolve, 2500));
        
        // Count grounding-box elements
        const count = await page.evaluate(() => {
            return document.querySelectorAll('.grounding-box').length;
        });
        console.log(`Number of grounding boxes in DOM: ${count}`);
        
    } catch (err) {
        console.error(err);
    } finally {
        await browser.close();
    }
}

run();
