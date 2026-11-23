---
name: skill-first
description: Review every available skill before planning or doing a task, pick the ones that fit, then plan or execute using them. Use at the start of any real task (building, writing, editing, researching, fixing, creating content), or when the user says "check your skills first", "use the right skills" or "skill-first".
argument-hint: "<task>"
---

# Skill First

Before planning or doing a task, check which skills already cover it, then work through them instead of improvising.

## 1. Go through all skills

- Read the full list of available skills in your context (name + description), including skills from plugins.
- If the list might be incomplete, also look on disk:
  - `~/.claude/skills/*/SKILL.md` (personal)
  - `.claude/skills/*/SKILL.md` (this project)
  - installed plugin skills under `~/.claude/plugins/`
- Don't skip any. Check each against the task.

## 2. Pick the matching skills

For each skill, decide: **use**, **maybe**, or **not relevant**. Choose a skill only when its description truly matches part of the task. Don't force one in.

Show the user a short summary before going on:

```
Skills checked: 24
Using:  github-top-repos (find repos), pdf (read the brief)
Maybe:  marketing:draft-content (if you want a post written after)
```

If no skill fits, say "No matching skill. Doing this directly" and continue.

## 3. Plan or execute

Decide based on the task size:

- **Small and clear** (one step, low risk): execute right away.
- **Bigger, unclear, or risky** (several steps, deletes or overwrites files, publishes something, costs money): write a short numbered plan first. Name which skill handles each step. Ask the user to confirm before doing it.

## 4. Do the work through the skills

- Load each chosen skill with the Skill tool *before* doing that part, and follow its instructions over your own defaults.
- Do the parts no skill covers directly.
- At the end, say in one line which skills were used.

## Skip this when

The message is just chat, a quick question, or a one-line fix where checking skills adds nothing. Then answer normally.
