#!/usr/bin/env bash
# Fetch the survivorship-bias-free Binance USDT-perp dataset used by SHITCOIN_FINDINGS.md.
# No API key needed. Binance's REST API is geo-blocked in some regions (451); the public
# data archive used here is not.
#
# Usage:  ./fetch_data.sh            (4h klines + funding, ~290MB)
#         ./fetch_data.sh --with-15m (adds 15m bars for signal symbols, ~1.6GB)
set -euo pipefail
cd "$(dirname "$0")"
S3="https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
CDN="https://data.binance.vision"

# --- 1. enumerate every USDT perp ever listed, including delisted ones ---
echo "enumerating symbol universe..."
tok=""; : > syms.txt
for _ in $(seq 1 30); do
  if [ -z "$tok" ]; then url="$S3?delimiter=/&prefix=data/futures/um/monthly/klines/"
  else enc=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$tok")
       url="$S3?delimiter=/&prefix=data/futures/um/monthly/klines/&continuation-token=$enc"; fi
  curl -s -m 60 "$url" -o page.xml
  grep -o "klines/[A-Z0-9_]*/</Prefix>" page.xml | sed 's|klines/||;s|/</Prefix>||' >> syms.txt
  [ "$(grep -o '<IsTruncated>[a-z]*</IsTruncated>' page.xml | sed 's/<[^>]*>//g')" = "true" ] || break
  tok=$(grep -o '<NextContinuationToken>[^<]*</NextContinuationToken>' page.xml | sed 's/<[^>]*>//g')
done
sort -u syms.txt -o syms.txt; grep 'USDT$' syms.txt > usdt.txt
rm -f page.xml
echo "  $(wc -l < usdt.txt) USDT perps (delisted symbols included)"

# --- generic: list then download one interval/type for every symbol ---
grab() {  # grab <archive-subpath> <listdir> <outdir> <filelist>
  local sub="$1" ld="$2" od="$3" fl="$4"
  mkdir -p "$ld" "$od"
  xargs -P 24 -I{} sh -c "curl -s -m 60 \"$S3?delimiter=/&prefix=data/futures/um/monthly/$sub\" -o $ld/{}.xml" < usdt.txt
  grep -ho "<Key>[^<]*\.zip</Key>" "$ld"/*.xml | sed 's/<[^>]*>//g' | sort -u > "$fl"
  rm -rf "$ld"
  echo "  $(wc -l < "$fl") files"
  xargs -P 32 -I{} sh -c "f=\$(basename {}); [ -s $od/\$f ] || curl -s -m 90 \"$CDN/{}\" -o $od/\$f" < "$fl"
}

echo "downloading 4h klines..."
grab 'klines/{}/4h/' klists zips files.txt
echo "downloading funding rates..."
grab 'fundingRate/{}/' flists fzips ffiles.txt

python3 build.py
python3 build_funding.py

if [ "${1:-}" = "--with-15m" ]; then
  echo "downloading 15m klines for signal symbols..."
  python3 - <<'PY'
import pandas as pd
t = pd.read_parquet("trades_pessimistic.parquet")
open("sig_syms.txt","w").write("\n".join(sorted(t.symbol.unique())))
PY
  mkdir -p m15lists m15
  xargs -P 24 -I{} sh -c "curl -s -m 60 \"$S3?delimiter=/&prefix=data/futures/um/monthly/klines/{}/15m/\" -o m15lists/{}.xml" < sig_syms.txt
  grep -ho "<Key>[^<]*\.zip</Key>" m15lists/*.xml | sed 's/<[^>]*>//g' | sort -u > m15files.txt
  rm -rf m15lists
  xargs -P 32 -I{} sh -c 'f=$(basename {}); [ -s m15/$f ] || curl -s -m 90 "'"$CDN"'/{}" -o m15/$f' < m15files.txt
fi
echo "done."
