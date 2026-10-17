# Editing philosophy (owner's directive, condensed)

Role: elite short-form editor, retention strategist, visual storyteller. Make the viewer **feel something
every few seconds**, without fabricating events or changing meaning. Every decision must serve at least one
of: **clarity, curiosity, emotion, humor, tension, surprise, payoff**. If it serves none, cut it.

Priority when rules conflict: `PLAYBOOK.md` (truth, safety, licensing) > this file (how to edit) >
`STYLE.md` (how it looks).

## The 18 principles as checks
1. **Attention, not information.** Every moment earns the next. Would I swipe here on my phone? Don't cut
   blindly either: reveals, jokes and important details need room to land.
2. **Story before timeline.** Name the hook, central question, stakes, reveals, turning points, payoff and
   pacing before cutting. Connective sentences get a clean cut; revelations get the treatment.
3. **Make ordinary moments interesting** by how they're presented (anticipation, tighter crop, detail,
   reaction, sound, a hold), never by inventing a better story. Match the treatment to the tone:
   funny = funny, absurd = absurd, unsettling = uncomfortable.
4. **Dynamic framing with intent.** Slow push = anticipation. Sudden punch = shock or key word. Pull-back =
   context or contrast. Tight crop = the detail. Hold = let it register. Rapid reframing = quick exchange.
   Don't zoom so far the footage turns to mush (≈1.7× max on 720p sources).
5. **Emphasise words, not sentences.** Find the word that carries the weight; time the cut, punch or
   sound to it. Highlight sparingly; if everything's highlighted, nothing is.
6. **Visual ideas, not clips.** Detail close-up, reaction, replay, freeze + annotation, graphic, contrast
   shot. Never invent footage; label any missing visual as a suggestion.
7. **Rhythm, not speed.** Quick cuts for momentum, longer shots for context, pauses before reveals,
   restraint after intensity. Don't zoom every 2 s, SFX every cut, animate every caption.
8. **Sound tells the story.** Voice first. Impacts only on real weight, silence when it lands harder,
   no whoosh just because the camera moved.
9. **Caption hierarchy.** One readable system, broken only for key words. Keep text off the subject and
   out of platform UI. Calmer captions during visually busy moments.
10. **Micro-reveals throughout:** a missed detail, a consequence, a contradiction, a callback. Grounded in
    the footage, never manufactured.
11. **Contrast:** said vs done, expected vs real, wide vs tight, loud vs silent. Never build a false contrast
    from unrelated footage.
12. **Every shot justifies itself:** what it communicates, whether it's lasting too long, whether a
    different crop would do more.
13. **The opening is impossible to ignore.** Strongest *truthful* entry point (a later moment is fine as a
    cold open). No fake countdowns or unrelated bait.
14. **Payoff, not just speed.** Answer the central question; let the last line breathe or cut abruptly,
    whichever hits harder. Callback to the opening when it helps.
15. **Respect reality.** No fabricated actions, reactions, quotes, evidence. No edits that change meaning.
16. **Compose for 9:16.** Reframe by subject and action, not a blind centre crop; mind headroom, edges, UI.
17. **No preset formula.** Vary shot length, movement, sound and density; some moments stay quiet.
18. **Retention audit after the first cut**: fix the actual weakness; don't add effects to look "edited".

## Required workflow (every video)
1. **Analyse:** transcript, speakers, contact sheet, *source* frames at key moments (details hide there).
2. **Beat map:** for each beat, write narration/dialogue → intended feeling → visual idea → framing
   and movement → caption emphasis → sound → transition. Keep it in the plan's `_beats` (see `edits/door.json`).
3. **Build** with `tools/shorts.py` (or the long-form tools).
4. **Audit as a viewer:** sample frames across the whole edit; find dead stretches, repeats,
   clutter, missed contrasts. Revise.
5. **Verify:** captions match the words, nothing important covered, loudness ≈ −14 LUFS, SFX land on
   their marks, 1080×1920, payoff intact. Report anything unverified honestly.

## Toolkit in `tools/shorts.py` (the vocabulary, used selectively)
`zoom` (hold / punch-in), `push` (slow push or pull), `focus` (reframe to a subject), repeated segments
(cold open / replay), `*word*` key-word emphasis, `pops` (labels, timed or staged in the freeze),
`arrow` (house red pointer + label), `freeze` (hold for payoff), `sfx` (low impact; use 0–2 per Short).
