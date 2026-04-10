#!/bin/bash
# refresh-postiz.sh - Fetches posts from Postiz API and saves to postiz-calendar.json
# Run via cron or manually to keep content board data fresh.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/../public"
OUTPUT_FILE="$OUTPUT_DIR/postiz-calendar.json"
API_BASE="https://api.postiz.com/public/v1"

if [ -z "${POSTIZ_API_KEY:-}" ]; then
  echo "Error: POSTIZ_API_KEY not set" >&2
  exit 1
fi

# Date range: 2 weeks back + 4 weeks forward
START_DATE=$(date -u -v-14d +"%Y-%m-%dT00:00:00Z" 2>/dev/null || date -u -d "14 days ago" +"%Y-%m-%dT00:00:00Z")
END_DATE=$(date -u -v+28d +"%Y-%m-%dT23:59:59Z" 2>/dev/null || date -u -d "28 days" +"%Y-%m-%dT23:59:59Z")
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "Fetching Postiz posts: $START_DATE to $END_DATE"

# Fetch posts
POSTS=$(curl -sf -H "Authorization: $POSTIZ_API_KEY" \
  "$API_BASE/posts?startDate=$START_DATE&endDate=$END_DATE" 2>/dev/null || echo '{"posts":[]}')

# Fetch integrations
INTEGRATIONS=$(curl -sf -H "Authorization: $POSTIZ_API_KEY" \
  "$API_BASE/integrations" 2>/dev/null || echo '[]')

# Build combined JSON
python3 -c "
import json, sys

posts_raw = json.loads('''$POSTS''')
integrations = json.loads('''$INTEGRATIONS''')

posts = posts_raw.get('posts', []) if isinstance(posts_raw, dict) else posts_raw

output = {
    'lastUpdated': '$NOW',
    'posts': posts,
    'integrations': integrations
}

json.dump(output, sys.stdout, indent=2)
" > "$OUTPUT_FILE"

POST_COUNT=$(python3 -c "import json; d=json.load(open('$OUTPUT_FILE')); print(len(d.get('posts',[])))")
echo "Saved $POST_COUNT posts to $OUTPUT_FILE"
echo "Last updated: $NOW"
