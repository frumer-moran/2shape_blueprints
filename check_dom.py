import urllib.request
import re

def main():
    try:
        url = "http://localhost:8000/view_results.html"
        print(f"Fetching {url}...")
        with urllib.request.urlopen(url) as response:
            html = response.read().decode('utf-8')
            
        print("HTML length:", len(html))
        
        # Check if groundingData is populated correctly
        match = re.search(r'const groundingData = \[(.*?)\];', html)
        if match:
            print("Found groundingData in HTML!")
            print(match.group(0)[:200] + "...")
        else:
            print("ERROR: groundingData not found in HTML!")
            
    except Exception as e:
        print("Error fetching page:", e)

if __name__ == "__main__":
    main()
