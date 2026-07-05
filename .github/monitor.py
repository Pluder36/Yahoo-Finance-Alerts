import yfinance as yf
import os
import json
import urllib.request

TICKER = "AAPL"
STATE_FILE = "seen_urls.txt"
WEBHOOK_URL = os.environ.get("https://discordapp.com/api/webhooks/1523334052491563048/YICnA8YiqKBlkTayRLWurF-gmbr7VjrD64zR-szLHWnM0YGCwY2YCRwlizB07EWqwJvr") 

def load_seen_urls():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return set(f.read().splitlines())
    return set()

def save_seen_urls(urls):
    with open(STATE_FILE, "w") as f:
        for url in urls:
            f.write(f"{url}\n")

def send_alert(title, link):
    if not WEBHOOK_URL:
        print(f"New Article Detected: {title} - {link}")
        return

    payload = json.dumps({"content": f"New {TICKER} News: {title}\n{link}"}).encode('utf-8')
    req = urllib.request.Request(WEBHOOK_URL, data=payload, headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"Failed to send alert: {e}")

def main():
    seen_urls = load_seen_urls()
    ticker_data = yf.Ticker(TICKER)
    news = ticker_data.news
    
    new_articles_found = False
    
    for article in news:
        if 'content' in article:
            url = article['content'].get('canonicalUrl', {}).get('url', '')
            title = article['content'].get('title', 'No Title')
        else:
            url = article.get('link', '')
            title = article.get('title', 'No Title')
            
        if url and url not in seen_urls:
            send_alert(title, url)
            seen_urls.add(url)
            new_articles_found = True

if __name__ == "__main__":
    main()
