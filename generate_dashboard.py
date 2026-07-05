import os
import json
import glob

def get_latest_cache_data():
    cache_files = glob.glob("cache/*.json")
    # Exclude grounding cache, circle coords, and stitch transform files
    cache_files = [f for f in cache_files if "grounding_" not in f and "_circles_coords" not in f and "stitch_transform" not in f]
    if not cache_files:
        return None
    # Sort by modification time, newest first
    latest_file = max(cache_files, key=os.path.getmtime)
    print(f"Reading data from latest cache file: {latest_file}")
    with open(latest_file, "r") as f:
        return json.load(f)

def get_latest_grounding_data():
    cache_files = glob.glob("cache/grounding_*.json")
    if not cache_files:
        return []
    latest_file = max(cache_files, key=os.path.getmtime)
    print(f"Reading grounding data from latest cache file: {latest_file}")
    with open(latest_file, "r") as f:
        try:
            data = json.load(f)
            return data.get("apartments", [])
        except Exception as e:
            print(f"Error parsing grounding JSON: {e}")
            return []

def get_hex_color(hebrew_color):
    color_map = {
        "אדום": "#ef4444",
        "כחול": "#3b82f6",
        "ירוק": "#22c55e",
        "ירקרק": "#84cc16", # lime green
        "אפור": "#6b7280",
        "תכלת": "#06b6d4",
        "צהוב": "#eab308",
        "שחור": "#27272a",
        "סגול": "#a855f7",
        "בורדו": "#991b1b",
        "כתום": "#f97316",
        "חום": "#78350f"
    }
    return color_map.get(hebrew_color, "#71717a") # zinc-500 default

def get_color_style(hebrew_color):
    # Maps Hebrew colors from the blueprint to Tailwind/CSS classes
    color_map = {
        "אדום": "bg-red-500/10 text-red-300 border-red-500/30",
        "כחול": "bg-blue-500/10 text-blue-300 border-blue-500/30",
        "ירוק": "bg-green-500/10 text-green-300 border-green-500/30",
        "ירקרק": "bg-lime-500/10 text-lime-300 border-lime-500/30",
        "אפור": "bg-gray-500/10 text-gray-300 border-gray-500/30",
        "תכלת": "bg-cyan-500/10 text-cyan-300 border-cyan-500/30",
        "צהוב": "bg-yellow-500/10 text-yellow-300 border-yellow-500/30",
        "שחור": "bg-zinc-800 text-zinc-300 border-zinc-700",
        "סגול": "bg-purple-500/10 text-purple-300 border-purple-500/30",
        "בורדו": "bg-rose-950/30 text-rose-300 border-rose-800/40",
        "כתום": "bg-orange-500/10 text-orange-300 border-orange-500/30",
        "חום": "bg-amber-950/30 text-amber-300 border-amber-800/40"
    }
    return color_map.get(hebrew_color, None) # Return None if unrecognized to raise flag

def main():
    data = get_latest_cache_data()
    if not data:
        print("Error: No cache files found. Run poc_extract.py first.")
        return

    grounding_data = get_latest_grounding_data()
    grounding_js = json.dumps(grounding_data, ensure_ascii=False)

    # Generate rows HTML
    rows_html = ""
    for apt in data.get("apartments", []):
        apt_num = apt.get("apartment_number", "")
        apt_color = apt.get("color", "")
        
        # Color style lookup and flag mechanism
        color_cls = get_color_style(apt_color)
        flag_html = ""
        
        if color_cls is None:
            # Unrecognized color - raise a visual flag!
            color_cls = "bg-yellow-500/10 text-yellow-400 border-yellow-500/40"
            flag_html = f"""
            <span class="inline-flex items-center gap-1 text-yellow-500 text-[10px] bg-yellow-500/10 border border-yellow-500/30 px-1.5 py-0.5 rounded font-sans font-semibold animate-pulse ml-1" title="Unmatched color from blueprint">
                ⚠️ שגיאת צבע
            </span>
            """
            
        hex_color = get_hex_color(apt_color)
        
        # Color circle layout next to unit number
        apt_num_html = f"""
        <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-full border border-zinc-700/80 shadow-sm" style="background-color: {hex_color}; box-shadow: 0 0 6px {hex_color}40;"></span>
            <span>{apt_num}</span>
        </div>
        """

        # Attachments cell content (inherits apartment color)
        attachments_html = ""
        for att in apt.get("attachments", []):
            attachments_html += f"""
            <div class="flex items-center gap-2 mb-1.5 p-1.5 rounded border {color_cls} text-xs">
                <span class="font-bold">{att.get('description', '')}</span>
                <span class="opacity-75 font-mono">({att.get('sign', '')})</span>
                <span class="ml-auto font-mono">{att.get('area_sqm', '')} מ"ר</span>
            </div>
            """
        if not attachments_html:
            attachments_html = '<span class="text-zinc-700 text-xs">-</span>'

        rows_html += f"""
        <tr id="apt-row-{apt_num}" class="border-b border-zinc-900 hover:bg-zinc-900/40 transition-colors" onmouseenter="highlightGroundingBox('{apt_num}')" onmouseleave="clearGroundingBoxHighlight('{apt_num}')">
            <td class="px-4 py-3 font-mono text-zinc-100 font-bold">{apt_num_html}</td>
            <td class="px-4 py-3 text-zinc-300 text-sm">{apt.get('floor', '')}</td>
            <td class="px-4 py-3 text-zinc-300 text-sm max-w-xs">{apt.get('description', '')}</td>
            <td class="px-4 py-3 font-mono text-emerald-400 font-semibold">{apt.get('area_sqm', '')} מ"ר</td>
            <td class="px-4 py-3 font-mono text-zinc-400 text-sm">{apt.get('share_common', '')}</td>
            <td class="px-4 py-3">{attachments_html}</td>
            <td class="px-4 py-3 text-xs" style="color: {hex_color}d0;">
                <div class="flex items-center gap-1">
                    <span>{apt_color}</span>
                    {flag_html}
                </div>
            </td>
            <td class="px-4 py-3 text-zinc-500 text-xs">{apt.get('remarks', '') or '-'}</td>
        </tr>
        """

    html_template = f"""<!DOCTYPE html>
<html lang="he" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>מבט על נתוני תשריט - אוסטרובסקי 31</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
        body {{
            font-family: 'Assistant', sans-serif;
        }}
        .font-mono {{
            font-family: 'JetBrains Mono', monospace;
        }}
        /* Hide scrollbars but keep functionality */
        .no-scrollbar::-webkit-scrollbar {{
            display: none;
        }}
        .no-scrollbar {{
            -ms-overflow-style: none;
            scrollbar-width: none;
        }}
        #viewer-container, #pan-zoom-content, .grounding-box {{
            direction: ltr !important;
            text-align: left !important;
        }}
        #pan-zoom-content {{
            left: 0px !important;
            right: auto !important;
            transform-origin: top left !important;
        }}
    </style>
</head>
<body class="bg-zinc-950 text-zinc-100 min-h-screen flex flex-col overflow-hidden" dir="ltr">

    <!-- Top Header -->
    <header class="h-14 border-b border-zinc-900 bg-zinc-950 flex items-center justify-between px-6 z-10" dir="rtl">
        <div class="flex items-center gap-3">
            <span class="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <h1 class="text-lg font-bold tracking-tight">בודק תשריט בית משותף - אוסטרובסקי 31, רעננה</h1>
        </div>
        <div class="text-zinc-500 text-xs font-mono">גוש 6583 / חלקה 392</div>
    </header>

    <!-- Main Workspace -->
    <main class="flex overflow-hidden" style="height: calc(100vh - 3.5rem);">
        
        <!-- Left: Image Viewer (with Pan & Zoom) -->
        <div class="w-1/2 h-full border-l border-zinc-900 relative bg-zinc-900 overflow-hidden select-none" id="viewer-container" dir="ltr">
            <!-- Canvas Selector Buttons -->
            <div class="absolute top-4 left-4 z-20 flex gap-2">
                <button onclick="setImage('table_slice.jpg')" id="btn-table" class="px-3 py-1.5 rounded bg-zinc-950/80 hover:bg-zinc-900 text-zinc-300 border border-zinc-800 text-xs shadow-lg transition-all font-semibold">טבלת שטחים (OCR)</button>
                <button onclick="setImage('stitched_first_floor_v2.jpg')" id="btn-stitch" class="px-3 py-1.5 rounded bg-emerald-600 text-zinc-100 border border-emerald-500 text-xs shadow-lg transition-all font-semibold">תוכנית קומה ראשונה (Stitched)</button>
            </div>

            <!-- Zoom controls -->
            <div class="absolute top-4 right-4 z-20 flex gap-2">
                <button onclick="zoomIn()" class="p-2 rounded bg-zinc-950/80 hover:bg-zinc-900 text-zinc-300 border border-zinc-800 text-sm font-bold shadow-lg transition-colors">+</button>
                <button onclick="zoomOut()" class="p-2 rounded bg-zinc-950/80 hover:bg-zinc-900 text-zinc-300 border border-zinc-800 text-sm font-bold shadow-lg transition-colors">-</button>
                <button onclick="resetZoom()" class="px-3 py-2 rounded bg-zinc-950/80 hover:bg-zinc-900 text-zinc-300 border border-zinc-800 text-xs shadow-lg transition-colors">איפוס</button>
            </div>
            
            <div class="absolute bottom-4 right-4 z-20 bg-black/60 px-3 py-1.5 rounded text-[11px] text-zinc-400">
                הנחיה: גרור את התמונה כדי להזיז, והשתמש בגלגלת העכבר כדי לזום. תיבות צבעוניות מסמנות מיקומי דירות.
            </div>

            <!-- Draggable & Zoomable Wrapper -->
            <div id="pan-zoom-content" class="absolute top-0 left-0 cursor-grab active:cursor-grabbing transition-transform duration-75 ease-out origin-top-left will-change-transform" style="transform: translate3d(0px, 0px, 0px) scale(0.45);">
                <img src="about:blank" alt="תשריט מקורי" class="pointer-events-none" style="max-width: none;" />
            </div>
        </div>

        <!-- Right: JSON Table -->
        <div class="w-1/2 flex flex-col h-full bg-zinc-950 overflow-y-auto" dir="rtl">
            <div class="p-6 border-b border-zinc-900 bg-zinc-950 sticky top-0 backdrop-blur z-10 flex justify-between items-center">
                <div>
                    <h2 class="text-base font-semibold text-zinc-200">נתוני טבלת השטחים (מתוך קובץ ה-JSON)</h2>
                    <p class="text-xs text-zinc-500 mt-1">מצג ויזואלי של פלט ה-OCR מול קובץ התמונה לביצוע אימות אנושי</p>
                </div>
                <div class="text-xs px-2.5 py-1 rounded bg-zinc-900 border border-zinc-800 text-zinc-400 font-mono">
                    סה"כ דירות: {len(data.get('apartments', []))}
                </div>
            </div>

            <!-- Table Container -->
            <div class="p-6">
                <table class="w-full text-right border-collapse">
                    <thead>
                        <tr class="border-b border-zinc-800 text-zinc-400 text-xs font-semibold uppercase tracking-wider bg-zinc-900/30">
                            <th class="px-4 py-3 rounded-r">מס' דירה</th>
                            <th class="px-4 py-3">קומה</th>
                            <th class="px-4 py-3">תיאור</th>
                            <th class="px-4 py-3">שטח דירה</th>
                            <th class="px-4 py-3">חלק ברכוש</th>
                            <th class="px-4 py-3">הצמדות</th>
                            <th class="px-4 py-3">צבע יחידה</th>
                            <th class="px-4 py-3 rounded-l">הערות</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-zinc-900">
                        {rows_html}
                    </tbody>
                </table>
            </div>
        </div>
    </main>

    <!-- Drag & Zoom Script -->
    <script>
        const container = document.getElementById('viewer-container');
        const content = document.getElementById('pan-zoom-content');
        const imgEl = content.querySelector('img');
        const btnTable = document.getElementById('btn-table');
        const btnStitch = document.getElementById('btn-stitch');
        
        // Grounding data injected from Python cache
        const groundingData = {grounding_js};
        
        let scale = 0.45;
        let pointX = 0;
        let pointY = 0;
        let start = {{ x: 0, y: 0 }};
        let isDragging = false;

        const colorMap = {{
            "אדום": "#ef4444",
            "כחול": "#3b82f6",
            "ירוק": "#22c55e",
            "ירקרק": "#84cc16",
            "אפור": "#6b7280",
            "תכלת": "#06b6d4",
            "צהוב": "#eab308",
            "שחור": "#27272a",
            "סגול": "#a855f7",
            "בורדו": "#991b1b",
            "כתום": "#f97316",
            "חום": "#78350f"
        }};
        
        function getHexColor(hebrew_color) {{
            return colorMap[hebrew_color] || "#71717a";
        }}

        function setTransform() {{
            content.style.transform = `translate3d(${{pointX}}px, ${{pointY}}px, 0px) scale(${{scale}})`;
        }}

        // Render visual overlays for grounded units
        function renderGroundingBoxes() {{
            // Remove existing boxes
            const existing = content.querySelectorAll('.grounding-box');
            existing.forEach(el => el.remove());
            
            // Only draw boxes on the stitched floor plan
            if (imgEl.src.includes('table_slice.jpg')) return;
            
            groundingData.forEach(apt => {{
                const [ymin, xmin, ymax, xmax] = apt.label_box;
                
                // Convert 0-1000 coordinate values to percentages
                const top = ymin / 10;
                const left = xmin / 10;
                const width = (xmax - xmin) / 10;
                const height = (ymax - ymin) / 10;
                
                const box = document.createElement('div');
                box.id = `grounding-box-${{apt.apartment_number}}`;
                box.className = 'grounding-box absolute border-2 rounded transition-all duration-150 hover:scale-110 hover:z-30 cursor-pointer flex items-center justify-center';
                
                const colorHex = getHexColor(apt.border_color);
                box.style.top = `${{top}}%`;
                box.style.left = `${{left}}%`;
                box.style.width = `${{width}}%`;
                box.style.height = `${{height}}%`;
                box.style.borderColor = colorHex;
                box.style.backgroundColor = `${{colorHex}}15`; // ~8% opacity fill
                box.style.boxShadow = `0 0 8px ${{colorHex}}30`;
                
                // Add a text label inside
                box.innerHTML = `<span class="bg-black/90 text-white text-[8px] font-bold px-1 rounded border border-zinc-700/80 pointer-events-none">${{apt.apartment_number}}</span>`;
                
                // Link hover behaviors (box -> table row)
                box.addEventListener('mouseenter', () => {{
                    const row = document.getElementById(`apt-row-${{apt.apartment_number}}`);
                    if (row) {{
                        row.classList.add('bg-zinc-800/80');
                        row.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
                    }}
                }});
                
                box.addEventListener('mouseleave', () => {{
                    const row = document.getElementById(`apt-row-${{apt.apartment_number}}`);
                    if (row) {{
                        row.classList.remove('bg-zinc-800/80');
                    }}
                }});
                
                content.appendChild(box);
            }});
        }}

        // Link hover behaviors (table row -> box)
        window.highlightGroundingBox = function(apt_num) {{
            const box = document.getElementById(`grounding-box-${{apt_num}}`);
            if (box) {{
                const colorHex = getHexColor(groundingData.find(a => a.apartment_number === apt_num)?.border_color || "");
                box.style.transform = 'scale(1.15)';
                box.style.boxShadow = `0 0 16px ${{colorHex}}d0`;
                box.style.borderWidth = '3px';
                box.style.zIndex = '30';
            }}
        }};

        window.clearGroundingBoxHighlight = function(apt_num) {{
            const box = document.getElementById(`grounding-box-${{apt_num}}`);
            if (box) {{
                const colorHex = getHexColor(groundingData.find(a => a.apartment_number === apt_num)?.border_color || "");
                box.style.transform = 'none';
                box.style.boxShadow = `0 0 8px ${{colorHex}}30`;
                box.style.borderWidth = '2px';
                box.style.zIndex = 'auto';
            }}
        }};

        // Dynamic Fitting & Centering on Image Load
        imgEl.onload = function() {{
            let containerWidth = container.clientWidth;
            let containerHeight = container.clientHeight;
            
            // Fallback to window dimensions if browser rendering is delayed
            if (!containerWidth || containerWidth < 50) containerWidth = window.innerWidth / 2;
            if (!containerHeight || containerHeight < 50) containerHeight = window.innerHeight - 56;
            
            const imgWidth = imgEl.naturalWidth;
            const imgHeight = imgEl.naturalHeight;
            
            if (!imgWidth || !imgHeight) return;
            
            // Explicitly set the width and height of the wrapper to match the image
            content.style.width = imgWidth + 'px';
            content.style.height = imgHeight + 'px';
            
            // Calculate perfect fit scale (with 5% padding)
            const scaleX = containerWidth / imgWidth;
            const scaleY = containerHeight / imgHeight;
            scale = Math.min(scaleX, scaleY) * 0.95;
            
            // Center the image inside the container
            pointX = (containerWidth - imgWidth * scale) / 2;
            pointY = (containerHeight - imgHeight * scale) / 2;
            
            setTransform();
            
            // Draw grounding overlay boxes
            renderGroundingBoxes();
            
            console.log('Image fitted successfully:', imgEl.src);
            console.log('Fitted dimensions:', imgWidth, 'x', imgHeight, 'Scale:', scale);
        }};

        // Set the initial image source dynamically with a unique timestamp to force browser cache bypass on page refresh
        imgEl.src = "stitched_first_floor_v2.jpg?t=" + new Date().getTime();

        function setImage(src) {{
            console.log('setImage called with:', src);
            if (imgEl) {{
                // Add timestamp query parameter to bust browser caches
                imgEl.src = src + '?t=' + new Date().getTime();
            }}
            if (src === 'table_slice.jpg') {{
                btnTable.className = 'px-3 py-1.5 rounded bg-emerald-600 text-zinc-100 border border-emerald-500 text-xs shadow-lg transition-all font-semibold';
                btnStitch.className = 'px-3 py-1.5 rounded bg-zinc-950/80 hover:bg-zinc-900 text-zinc-300 border border-zinc-800 text-xs shadow-lg transition-all font-semibold';
            }} else {{
                btnTable.className = 'px-3 py-1.5 rounded bg-zinc-950/80 hover:bg-zinc-900 text-zinc-300 border border-zinc-800 text-xs shadow-lg transition-all font-semibold';
                btnStitch.className = 'px-3 py-1.5 rounded bg-emerald-600 text-zinc-100 border border-emerald-500 text-xs shadow-lg transition-all font-semibold';
            }}
        }}

        container.addEventListener('mousedown', (e) => {{
            e.preventDefault();
            isDragging = true;
            start = {{ x: e.clientX - pointX, y: e.clientY - pointY }};
        }});

        container.addEventListener('mousemove', (e) => {{
            if (!isDragging) return;
            pointX = e.clientX - start.x;
            pointY = e.clientY - start.y;
            setTransform();
        }});

        window.addEventListener('mouseup', () => {{
            isDragging = false;
        }});

        container.addEventListener('wheel', (e) => {{
            e.preventDefault();
            const xs = (e.clientX - container.getBoundingClientRect().left - pointX) / scale;
            const ys = (e.clientY - container.getBoundingClientRect().top - pointY) / scale;
            const delta = -e.deltaY;
            
            // Smooth zoom steps: 6% per notch
            if (delta > 0) {{
                scale *= 1.06;
            }} else {{
                scale /= 1.06;
            }}
            
            // Zoom bounds
            scale = Math.min(Math.max(0.01, scale), 6);
            
            pointX = e.clientX - container.getBoundingClientRect().left - xs * scale;
            pointY = e.clientY - container.getBoundingClientRect().top - ys * scale;
            
            setTransform();
        }});

        function zoomIn() {{
            scale *= 1.15; // smooth 15% manual zoom steps
            scale = Math.min(scale, 6);
            // Zoom centered on container midpoint
            const containerWidth = container.clientWidth;
            const containerHeight = container.clientHeight;
            const centerX = containerWidth / 2;
            const centerY = containerHeight / 2;
            const xs = (centerX - pointX) / (scale / 1.15);
            const ys = (centerY - pointY) / (scale / 1.15);
            pointX = centerX - xs * scale;
            pointY = centerY - ys * scale;
            setTransform();
        }}

        function zoomOut() {{
            scale /= 1.15;
            scale = Math.max(0.01, scale);
            // Zoom centered on container midpoint
            const containerWidth = container.clientWidth;
            const containerHeight = container.clientHeight;
            const centerX = containerWidth / 2;
            const centerY = containerHeight / 2;
            const xs = (centerX - pointX) / (scale * 1.15);
            const ys = (centerY - pointY) / (scale * 1.15);
            pointX = centerX - xs * scale;
            pointY = centerY - ys * scale;
            setTransform();
        }}

        function resetZoom() {{
            const containerWidth = container.clientWidth;
            const containerHeight = container.clientHeight;
            const imgWidth = imgEl.naturalWidth;
            const imgHeight = imgEl.naturalHeight;
            
            if (!imgWidth || !imgHeight) return;
            
            const scaleX = containerWidth / imgWidth;
            const scaleY = containerHeight / imgHeight;
            scale = Math.min(scaleX, scaleY) * 0.95;
            
            pointX = (containerWidth - imgWidth * scale) / 2;
            pointY = (containerHeight - imgHeight * scale) / 2;
            
            setTransform();
        }}
    </script>
    <!-- Live Debug Panel for Layout Diagnostics -->
    <div id="debug-panel" class="fixed bottom-4 left-4 z-50 bg-black/90 border border-zinc-800 rounded p-4 text-[11px] font-mono text-zinc-400 max-w-sm shadow-2xl flex flex-col gap-1.5 pointer-events-auto">
        <div class="font-bold text-zinc-200 border-b border-zinc-800 pb-1 flex justify-between">
            <span>מחוון דיאגנוסטיקה (Debug)</span>
            <button onclick="updateDebugMetrics()" class="text-emerald-400 hover:text-emerald-300 font-bold">רענן ↻</button>
        </div>
        <div>מספר דירות בטבלה: <span id="dbg-rows" class="text-zinc-200">-</span></div>
        <div>גודל תמונה מקורי: <span id="dbg-img-size" class="text-zinc-200">-</span></div>
        <div>גודל מעטפת (#pan-zoom-content): <span id="dbg-wrapper-size" class="text-zinc-200">-</span></div>
        <div>גודל מיכל (#viewer-container): <span id="dbg-container-size" class="text-zinc-200">-</span></div>
        <div class="border-t border-zinc-900 pt-1.5 mt-0.5">
            <div class="font-semibold text-zinc-300 mb-1">נתוני תיבות אינטראקטיביות (DOM):</div>
            <div id="dbg-boxes-list" class="max-h-36 overflow-y-auto flex flex-col gap-1 pr-1 select-text">
                <!-- Filled dynamically -->
            </div>
        </div>
    </div>

    <script>
        function updateDebugMetrics() {{
            const dbgRows = document.getElementById('dbg-rows');
            const dbgImgSize = document.getElementById('dbg-img-size');
            const dbgWrapperSize = document.getElementById('dbg-wrapper-size');
            const dbgContainerSize = document.getElementById('dbg-container-size');
            const dbgBoxesList = document.getElementById('dbg-boxes-list');
            
            if (dbgRows) dbgRows.textContent = document.querySelectorAll('tbody tr').length;
            if (dbgImgSize) dbgImgSize.textContent = `${{imgEl.naturalWidth}}x${{imgEl.naturalHeight}} (src: ${{imgEl.src.split('/').pop().split('?')[0]}})`;
            if (dbgWrapperSize) dbgWrapperSize.textContent = `${{content.offsetWidth}}x${{content.offsetHeight}} (dir: ${{getComputedStyle(content).direction}})`;
            if (dbgContainerSize) dbgContainerSize.textContent = `${{container.clientWidth}}x${{container.clientHeight}} (dir: ${{getComputedStyle(container).direction}})`;
            
            if (dbgBoxesList) {{
                dbgBoxesList.innerHTML = '';
                const boxes = document.querySelectorAll('.grounding-box');
                if (boxes.length === 0) {{
                    dbgBoxesList.innerHTML = '<span class="text-zinc-600">- אין תיבות ב-DOM -</span>';
                }}
                boxes.forEach(box => {{
                    const aptNum = box.id.split('-').pop();
                    const leftPct = box.style.left;
                    const topPct = box.style.top;
                    const widthPct = box.style.width;
                    const heightPct = box.style.height;
                    
                    const item = document.createElement('div');
                    item.className = 'border-b border-zinc-900 pb-1';
                    item.innerHTML = `
                        <span class="font-bold text-zinc-300">דירה ${{aptNum}}</span>: 
                        left:${{leftPct}}, top:${{topPct}}, w:${{widthPct}}, h:${{heightPct}} 
                        <br/>
                        <span class="text-zinc-500">פיקסלים (DOM): left:${{box.offsetLeft}}px, top:${{box.offsetTop}}px, w:${{box.offsetWidth}}px, h:${{box.offsetHeight}}px</span>
                    `;
                    dbgBoxesList.appendChild(item);
                }});
            }}
        }}
        
        // Run update after rendering
        const oldRender = renderGroundingBoxes;
        renderGroundingBoxes = function() {{
            oldRender();
            setTimeout(updateDebugMetrics, 100);
        }};
    </script>
</body>
</html>
"""
    
    output_html_path = "view_results_v4.html"
    with open(output_html_path, "w") as f:
        f.write(html_template)
    print(f"Successfully generated visual dashboard at: {output_html_path}")

if __name__ == "__main__":
    main()
