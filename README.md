# youtube-content-help
## Plugins

### github-top-repos

Finds the 10 most-starred GitHub repositories for any topic and shows them ranked by stars.

Install it in Claude Code:

```
/plugin install github-top-repos --marketplace senkugen66-cmyk/youtube-content-help
```

Then ask "top GitHub repos for <topic>" or run `/github-top-repos <topic>`.

### skill-first

Before planning or doing a task, Claude goes through all your skills, picks the ones that fit, shows which it's using, then plans (big or risky tasks) or executes (small ones). A hook reminds Claude on every message, so this happens without you asking.

```
/plugin install skill-first --marketplace senkugen66-cmyk/youtube-content-help
```

You can also run it by hand: `/skill-first <task>`.
