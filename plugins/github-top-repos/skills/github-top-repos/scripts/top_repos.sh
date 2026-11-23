#!/usr/bin/env bash
# Find the most-starred GitHub repositories for a topic.
#
# Usage: top_repos.sh "<topic>" [count] [extra qualifiers]
#   top_repos.sh "machine learning"
#   top_repos.sh "rust web framework" 10 "language:rust"
#   top_repos.sh "game engine" 10 "pushed:>2025-01-01"
#
# It runs two searches and merges them:
#   1. topic:<slug>  - repos tagged with the GitHub topic (e.g. machine-learning)
#   2. <words> in:name,description,topics - repos that mention the words
# Duplicates are removed, forks/archived repos are skipped, and the result is
# ranked by stars. Output is JSON lines, one repo per line, best first.
#
# Uses `gh api` when available (authenticated, higher rate limit), otherwise
# curl against api.github.com (set GITHUB_TOKEN to raise the rate limit).

set -euo pipefail

topic="${1:?usage: top_repos.sh \"<topic>\" [count] [extra qualifiers]}"
count="${2:-10}"
extra="${3:-}"

slug="$(printf '%s' "$topic" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g')"

search() {
  local q="$1"
  if command -v gh >/dev/null 2>&1; then
    gh api -X GET search/repositories -f q="$q" -f sort=stars -f order=desc -f per_page=50 2>/dev/null || echo '{"items":[]}'
  else
    local auth=()
    [ -n "${GITHUB_TOKEN:-}" ] && auth=(-H "Authorization: Bearer $GITHUB_TOKEN")
    curl -fsSL "${auth[@]}" -H "Accept: application/vnd.github+json" -G \
      --data-urlencode "q=$q" -d sort=stars -d order=desc -d per_page=50 \
      https://api.github.com/search/repositories 2>/dev/null || echo '{"items":[]}'
  fi
}

filters="fork:false archived:false ${extra}"
{
  search "topic:${slug} ${filters}"
  search "${topic} in:name,description,topics ${filters}"
} | jq -c --argjson n "$count" -s '
  [ .[].items[]? ]
  | unique_by(.full_name)
  | sort_by(-.stargazers_count)
  | .[:$n]
  | to_entries[]
  | {
      rank: (.key + 1),
      name: .value.full_name,
      url: .value.html_url,
      stars: .value.stargazers_count,
      forks: .value.forks_count,
      language: (.value.language // "-"),
      description: ((.value.description // "") | gsub("[\r\n|]"; " ") | .[:160]),
      topics: (.value.topics // [])[:6],
      last_push: (.value.pushed_at // "" | .[:10]),
      license: (.value.license.spdx_id // "-")
    }'
