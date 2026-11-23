---
name: github-top-repos
description: Find the 10 most-starred GitHub repositories for a topic and present them ranked by stars. Use when the user asks for the best, top, most popular or most-starred GitHub repos or projects on a subject (e.g. "top repos for video editing", "best GitHub projects on LLM agents", "most starred Rust web frameworks").
argument-hint: "<topic> [language:<lang>] [count]"
---

# GitHub Top Repos

Find the most-starred repositories on GitHub for a topic and present a ranked top 10.

## Steps

1. **Work out the topic** from the request. If the user asks for something narrower, turn it into GitHub search qualifiers:
   - a language → `language:python`
   - recently maintained → `pushed:>YYYY-MM-DD` (about a year before today)
   - a minimum popularity → `stars:>1000`
   - a different count ("top 20") → change the count argument

   If no topic is given, ask for one.

2. **Run the helper script** (it sits next to this file):

   ```bash
   bash .claude/skills/github-top-repos/scripts/top_repos.sh "<topic>" 10 "<optional qualifiers>"
   ```

   It searches both the GitHub topic tag (`topic:<slug>`) and repos whose name, description or topics mention the words. It merges the two, drops forks and archived repos, and ranks by stars. Each output line is one repo as JSON: `rank, name, url, stars, forks, language, description, topics, last_push, license`.

3. **Check the results are relevant.** Keyword search can pull in off-topic repos, such as giant awesome-lists or unrelated projects that mention the word. If an entry clearly isn't about the topic, drop it and fill the gap: rerun with a count of 20 and take the next relevant ones. Say what you removed and why. Don't reorder anything; the ranking is by stars.

4. **If the script returns nothing,** try a broader or differently spelled topic (e.g. `llm` vs `large language model`, a singular form). If it still fails, the likely cause is a GitHub API rate limit or a network block. Say so; never make up repos or star counts.

## Output format

Start with a heading line: `## Top 10 GitHub repos: <topic>`. Under it, give the date the numbers were fetched and any qualifiers used.

Then a markdown table:

| # | Repo | ⭐ Stars | Language | Last push | What it is |
|---|------|---------|----------|-----------|------------|
| 1 | [owner/name](url) | 201.7k | Python | 2026-11-20 | one-line description |

- Format stars compactly: `201.7k`, `9,850`.
- Keep "What it is" to one short line, rewritten in plain words if the GitHub description is vague or marketing-heavy.
- Mark a repo with ⚠️ if its last push is more than 2 years old (possibly unmaintained).

After the table, add 2–4 bullets of quick takeaways. For example: which one to start with, which is the most actively maintained, any standout alternative. Base these only on the data returned.
