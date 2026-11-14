# EditFlo: Instagram DM visuals, source map (Participants A and B)

## Scope

| Participant | Interview method | DM visuals |
|---|---|---|
| A | Text conversation | A_01, A_02 |
| B | Text conversation | B_01, B_02 |
| C | In person | None. Documented in interview summaries elsewhere. |
| D | Phone or in person | None. Documented in interview summaries elsewhere. |
| E | Phone or in person | None. Documented in interview summaries elsewhere. |

**Deliverable:** 4 PNGs.

**Evidence status:** all 4 are illustrative reconstructions. No original chat transcripts were supplied, so none of the screens is an original chat record. The original conversations are not claimed to have taken place on Instagram. The screens are shown in Instagram DM layout for presentation.

## Documented findings

| Code | Finding |
|---|---|
| A1 | Former Instagram and long-form content creator. |
| A2 | A short video took about 1.5–3 hours to edit. |
| A3 | Previously paid about ₹2,000 per post for editing help. |
| A4 | Footage selection was important. The available source footage shaped editing decisions. |
| A5 | Important speaking points had to stay in the final video. |
| A6 | Trimmed roughly every 30 seconds to maintain retention. Unnecessary footage can go, but key explanations must stay. |
| A7 | Interested in AI editing help, but didn't want the system inventing or sourcing B-roll on its own. |
| B1 | Works with video, photography, memes, overlays and other visual assets. |
| B2 | Spends time searching for templates and Blender/3D assets. |
| B3 | Would like to reduce repetitive cutting and trimming. |
| B4 | Editing decisions depend on each project's objective. |
| B5 | Wants creative control over the final output. |
| B6 | Open to optional B-roll suggestions that match the intended direction. |
| B7 | Uses ChatGPT for ideation. |
| B8 | Already pays for Adobe. Prefers predictable pricing over unpredictable token-based charges. |

## Screen map

| File | Theme | Findings shown | Type |
|---|---|---|---|
| `PARTICIPANT_A/A_01.png` | Editing time and effort | A1, A2, A3, A4 (footage selection effort) | Illustrative reconstruction |
| `PARTICIPANT_A/A_02.png` | Retention and keeping what matters | A4 (working with available footage), A5, A6, A7 | Illustrative reconstruction |
| `PARTICIPANT_B/B_01.png` | The repetitive work behind editing | B1, B2, B3 | Illustrative reconstruction |
| `PARTICIPANT_B/B_02.png` | Automation, creative control and pricing | B4, B5, B6, B7, B8 | Illustrative reconstruction |

**Overlap:** A4 appears on both A screens, from two angles. A_01 covers the effort of selecting usable footage. A_02 covers available footage as A's reason for not wanting the tool to invent visuals. No other finding repeats.

## Documented content vs reconstructed wording

| Element | Status |
|---|---|
| Research substance of every participant message: times, the ₹2,000 figure, tools, preferences, concerns | **Documented.** Each message maps to a finding code above. The per-message mapping is in `src/conversations.js`, in each message's `src` field. |
| Exact wording of participant messages | **Reconstructed.** The tone is casual and was approved by the author. It is not verbatim and is not shown in quotation marks. |
| Interviewer questions | **Reconstructed** (`I-recon`). They are neutral prompts and make no product promises. |
| Filler messages ("yo rohan", "yooo", "go for it", "ok follow up from last time", "damn that's a lot of hunting") | **Reconstructed** (`filler`). They carry no research content. |
| Dates, timestamps, read receipts, response delays | **None shown.** The status-bar clock reads 9:41, the standard device-mockup placeholder. |
| Names, usernames, profile pictures | **Anonymised.** Rohan / `rohan.mkv_19` and `keyframe.goblin`. Profile pictures are placeholder cartoon graphics, not photos of participants. |

**Not assigned to either participant:**
- Any claim about B's reasons for wanting control beyond B4 and B5.
- Any statement that A or B would buy or use EditFlo.

## Captions

These sit under each phone, outside the app interface:

- *Participant A · Screen 1 of 2 · Illustrative reconstruction from interview notes — not an original chat record.* A_02, B_01 and B_02 use the equivalent wording.
- *Participant A was interviewed through a text conversation. No original transcript was supplied, so this screen reconstructs the discussion from the interview notes. Shown in Instagram DM layout for presentation. Names and usernames are anonymised; the profile picture is a placeholder image.*

## Design and editable source

| Path | Contents |
|---|---|
| `src/conversations.js` | Approved dialogue, identities and per-message source tags. **The dialogue is locked:** change it only with the author's approval. |
| `src/screen.html` | Instagram dark-mode DM template. Opening `screen.html#A_01` in a browser previews a screen. |
| `src/render.js` | Running `node render.js` from `src/` re-exports the 4 PNGs and `preview_A_B.png`. It needs Playwright and the Inter font. It checks that every thread fits below the header and that Inter loaded. |
| `src/avatars/A.png`, `src/avatars/B.png` | Placeholder profile pictures. |

**Design specs:**
- **Measurements** come from the supplied Instagram screenshots: bubble colours and the position-based purple-to-blue gradient, 60 px line height, 30/40 px bubble padding, 8 px and 36 px message gaps, and the header, composer and status-bar geometry.
- **Font:** Inter, standing in for SF Pro. Text widths were checked against the reference and are within about 1%.
- **Screen size:** 1320 × 2868 px, a larger iPhone with the same aspect ratio as the 1179 × 2556 reference. At the reference size, A_02 and B_02 ran under the header. The larger screen fits them without shrinking the text or changing the approved wording. All text, bubble and icon sizes match the reference.
- **Export:** each PNG is 1520 × 3380 px, with the phone on a white sheet and the caption below it, ready to insert into a PDF.
