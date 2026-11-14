# EditFlo: conversation visuals, source map

**All 10 screens are illustrative reconstructions. None of them is an original chat record.** No genuine DM or interview transcripts were available. Each screen is reconstructed from the participant notes in the project brief.

Instagram's DM layout is only a presentation format. It does not indicate where or how any interview took place. A caption under every phone says this. Names, usernames and avatars are anonymised. Avatars are simple shapes or initials, not photographs.

## Conventions

- **No dates and no message timestamps.** The status-bar clock shows `9:41`, the standard device-mockup placeholder.
- **No read receipts, reactions, emojis or typing indicators.**
- **Interviewer lines are reconstructed (`I-recon`)**, except D_02's MCP explanation, which is documented in the notes (`I-doc`).
- **`ack`** marks a connective acknowledgement such as "yeah that makes sense". It carries no research claim.
- **Every participant line traces to a numbered note below.** The per-line mapping is in `src/conversations.js`, in each message's `src` field.

## Participant notes (from the brief)

| Note | Content |
|---|---|
| A1 | Previously made Instagram and longer-form video content. |
| A2 | A short video took about 1.5–3 hours to edit. |
| A3 | Paid about ₹2,000 per post for editing help. |
| A4 | Footage selection was a major part of the process. The available footage decided which clips could be used. |
| A5 | Important speaking points and explanations had to be kept. Automation must not remove the key message. |
| A6 | Edited roughly every 30 seconds for retention. Unnecessary footage could be trimmed, but key explanations had to stay. |
| A7 | Interested in AI help with editing. Didn't want it inventing B-roll or planning footage. Wanted control over sourcing and selecting footage. |
| B2 | Works with video, photos, memes, overlays and other visual assets. |
| B3 | Spends time finding templates and Blender/3D assets. |
| B4 | Some work is frame-by-frame. |
| B5 | Would most like to eliminate cutting and trimming. |
| B6 | Footage needs depend on each project's objective. |
| B7 | Wants full creative control over the final edit. |
| B8 | Open to optional B-roll suggestions that match the intended direction. |
| B9 | Uses ChatGPT for ideation. |
| B10 | Already pays for Adobe. Prefers predictable subscription pricing over token-based charges. |
| C1 | Previously made YouTube and gym-related content. |
| C2 | Reviewed several camera angles or pieces of footage. |
| C3 | Often used only a small selection of the available footage. |
| C4 | Equipment and workload were challenges. |
| C5 | The amount of footage available affected what could realistically be edited. |
| D1 | Creates performance-marketing education content professionally, full-time. |
| D2 | Works from company-provided scripts and instructions. Has a structured production process. |
| D3 | Repetitive editing is a major concern. |
| D4 | Discussed delegating repetitive editing and B-roll selection and placement. |
| D5 | Comfortable with AI trimming, but wants to restore important timestamped sections manually. |
| D6 | Asked about the cost of alternative clips and token use. |
| D7 | Would consider paying only if the results justified the cost. Did not agree to buy. |
| I-doc (D) | The interviewer explained the proposed one-time MCP repository approach and that it needs a capable/pro AI model. |
| E1 | Interested in making short-form content. Described as an aspiring creator. |
| E2 | Uses CapCut. |
| E3 | Has tried different editing styles. |
| E4 | Wants a polished final output. |
| E5 | Less experienced than B and D. Used only to set E's tone. |

## Screen-by-screen map

| File | Topic | Notes used | Type |
|---|---|---|---|
| `PARTICIPANT_A/A_01.png` | Editing time, footage choice, paid editor | A1, A2, A3, A4 | Illustrative reconstruction |
| `PARTICIPANT_A/A_02.png` | 30-second rhythm, keeping key explanations, no auto B-roll, footage control | A5, A6, A7 | Illustrative reconstruction |
| `PARTICIPANT_B/B_01.png` | Mixed media, asset hunting, frame-by-frame work, ChatGPT ideation, project-dependent footage | B2, B3, B4, B6, B9 | Illustrative reconstruction |
| `PARTICIPANT_B/B_02.png` | Automate cutting and trimming, keep creative control, optional B-roll, predictable pricing | B5, B7, B8, B10 | Illustrative reconstruction |
| `PARTICIPANT_C/C_01.png` | Gym YouTube channel, equipment and workload, footage limits | C1, C4, C5 | Illustrative reconstruction (short: limited notes) |
| `PARTICIPANT_C/C_02.png` | Several angles, only a small portion used | C2, C3 | Illustrative reconstruction (short: limited notes) |
| `PARTICIPANT_D/D_01.png` | Script-led production, repetitive editing, delegating B-roll | D1, D2, D3, D4 | Illustrative reconstruction |
| `PARTICIPANT_D/D_02.png` | Restoring sections by timestamp, clip and token costs, MCP explanation, conditional willingness to pay | D5, D6, D7, I-doc | Illustrative reconstruction |
| `PARTICIPANT_E/E_01.png` | Getting into short-form, CapCut | E1, E2, E5 | Illustrative reconstruction (short: limited notes) |
| `PARTICIPANT_E/E_02.png` | Trying styles in CapCut, wanting a polished result | E2, E3, E4 | Illustrative reconstruction (short: limited notes) |

**Original-evidence screens: 0 of 10. Illustrative reconstructions: 10 of 10.**

**Not assigned to anyone:**
- C: specific equipment, software, editing time, or any opinion on AI or EditFlo.
- E: any editing difficulty, frustration, spending habit, or AI opinion.
- No participant is shown agreeing to buy.

## Editable source

| Path | Contents |
|---|---|
| `src/conversations.js` | All message text, participant identities and per-line source tags. Edit this file to change content. |
| `src/screen.html` | Instagram dark-mode DM template. Measurements in native iPhone px (1179 × 2556) were taken from the supplied reference screenshots: bubble colours and position-based gradient, 60 px line height, 30/40 px bubble padding, 8 px and 36 px message gaps, and header, composer and status-bar geometry. Font: Inter, standing in for SF Pro. Open `src/screen.html#B_02` in a browser to preview any screen. |
| `src/render.js` | `node render.js`, run from `src/`, re-exports all ten PNGs and `preview_all_ten.png`. It needs Playwright and the Inter font installed. It also checks that every thread fits below the header and that Inter loaded. |

Each PNG is 1379 × 3026 px. The phone screen is at native 1179 × 2556, followed by a white caption area so the image can go straight into a PDF.
