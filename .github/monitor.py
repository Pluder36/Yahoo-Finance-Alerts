import yfinance as yf
import urllib.request
import json
import os
import time

TICKER = "GILD"
STATE_FILE = "seen_urls.txt"

def load_seen_urls():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return set(line.strip() for line in f)
    return set()

def load_seen_urls():
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w") as f:
            pass 
        return set()
        
    with open(STATE_FILE, "r") as f:
        return set(line.strip() for line in f)

def send_alert(title, url):
    webhook_url = os.environ.get('WEBHOOK_URL')
    
    if not webhook_url:
        print("Error: WEBHOOK_URL environment variable is not set.")
        return False

    payload = json.dumps({"content": f"New {TICKER} News: {title}\n{url}"}).encode('utf-8')
    
    req = urllib.request.Request(webhook_url, data=payload, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'Mozilla/5.0')
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Success: '{title}' sent. HTTP {response.status}")
            return True
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        print(f"Details: {e.read().decode('utf-8')}")
        return False
    except Exception as e:
        print(f"Error sending to Discord: {e}")
        return False

def main():
    print(f"Fetching news for {TICKER}...")
    try:
        ticker = yf.Ticker(TICKER)
        news = ticker.news
    except Exception as e:
        print(f"Failed to fetch news from yfinance: {e}")
        return

    if not news:
        print("No articles found.")
        return
    
    seen_urls = load_seen_urls()
    new_articles_found = False
    
    for article in news:
        if 'content' in article:
            url = article['content'].get('canonicalUrl', {}).get('url', '')
            title = article['content'].get('title', 'No Title')
        else:
            url = article.get('link', '')
            title = article.get('title', 'No Title')
            
        if url and url not in seen_urls:
            if send_alert(title, url):
                seen_urls.add(url)
                new_articles_found = True
                time.sleep(1) 

    if new_articles_found:
        save_seen_urls(seen_urls)
    else:
        print("No new articles found.")

if __name__ == "__main__":
    main()
