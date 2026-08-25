import json, time, urllib.request, os, ssl

PAIRS = ['BTC','ETH','SOL','XRP','LINK','AVAX','SUI','DOGE']
START = 1787184000000  # 2026-08-16 00:00 UTC
END   = 1788048000000  # 2026-08-26 00:00 UTC
OUT = '/home/user/tradingstudy/postmortem/mkt'
os.makedirs(OUT, exist_ok=True)

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'curl/8'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())

for p in PAIRS:
    inst = f'{p}-USDT-SWAP'
    rows = []
    after = END
    while True:
        url = f'https://www.okx.com/api/v5/market/history-candles?instId={inst}&bar=15m&after={after}&limit=100'
        d = get(url)
        if d['code'] != '0' or not d['data']:
            break
        batch = d['data']  # newest first
        rows.extend(batch)
        oldest = int(batch[-1][0])
        if oldest <= START:
            break
        after = oldest
        time.sleep(0.15)
    rows = [r for r in rows if int(r[0]) >= START]
    rows.sort(key=lambda r: int(r[0]))
    with open(f'{OUT}/{p}_15m.csv', 'w') as f:
        f.write('ts,open,high,low,close,vol\n')
        for r in rows:
            f.write(','.join([r[0], r[1], r[2], r[3], r[4], r[5]]) + '\n')
    print(p, len(rows), 'bars', rows[0][0], '->', rows[-1][0])
