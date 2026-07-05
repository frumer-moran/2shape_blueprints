const puppeteer = require('puppeteer');

async function run() {
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    try {
        console.log("Navigating directly to http://localhost:8000/table_slice.png...");
        await page.goto('http://localhost:8000/table_slice.png', { waitUntil: 'networkidle2' });
        await page.screenshot({ path: 'table_slice_direct.png' });
        console.log("Saved table_slice_direct.png");
        
        console.log("Navigating directly to http://localhost:8000/stitched_first_floor.png...");
        await page.goto('http://localhost:8000/stitched_first_floor.png', { waitUntil: 'networkidle2' });
        await page.screenshot({ path: 'stitched_direct.png' });
        console.log("Saved stitched_direct.png");
        
    } catch (err) {
        console.error(err);
    } finally {
        await browser.close();
    }
}

run();
