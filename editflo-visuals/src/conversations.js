// EditFlo — Instagram DM illustrative reconstructions, Participants A and B only.
// A and B were interviewed by text conversation; no original transcripts were supplied.
// Dialogue below is the version APPROVED by the author — do not change it without approval.
// `src` tags: A1–A7 / B1–B8 = documented finding (see SOURCE_MAP.md);
// "I-recon" = reconstructed interviewer wording; "filler" = casual connective message, no research content.
// `from`: "me" = interviewer (outgoing), "them" = participant (incoming).
// Edit text here, then re-run `node render.js` from this folder.

window.PARTICIPANTS = {
  A: { name: "Rohan", username: "rohan.mkv_19",    avatar: { kind: "image", src: "avatars/A.png" } },
  B: { name: null,    username: "keyframe.goblin", avatar: { kind: "image", src: "avatars/B.png" } },
};

window.CONVERSATIONS = {
  A_01: { participant: "A", screen: 1, topic: "Editing time and effort", messages: [
    { from: "me",   text: "yo rohan", src: "filler" },
    { from: "me",   text: "random q, you used to make reels and longer vids right? doing some research on how creators edit", src: "I-recon" },
    { from: "them", text: "yeah did both for a while", src: "A1" },
    { from: "me",   text: "how long would a short one take you to edit", src: "I-recon" },
    { from: "them", text: "like 1.5 to 3 hrs ngl", src: "A2" },
    { from: "me",   text: "for one short??", src: "I-recon" },
    { from: "them", text: "yeah lol", src: "A2" },
    { from: "them", text: "most of it is going through the footage and picking what's actually usable", src: "A4" },
    { from: "me",   text: "did you ever just pay an editor", src: "I-recon" },
    { from: "them", text: "yeah for a bit. like ₹2,000 a post", src: "A3" },
  ]},
  A_02: { participant: "A", screen: 2, topic: "Retention and keeping what matters", messages: [
    { from: "me",   text: "ok follow up from last time", src: "filler" },
    { from: "me",   text: "you mentioned making cuts roughly every 30 seconds right?", src: "I-recon" },
    { from: "them", text: "yeah roughly, keeps retention up", src: "A6" },
    { from: "me",   text: "so if something auto trimmed the extra bits would that help", src: "I-recon" },
    { from: "them", text: "for the useless parts sure", src: "A6" },
    { from: "them", text: "but the main explanation has to stay", src: "A5" },
    { from: "them", text: "if it cuts the part where i actually explain stuff the video's kinda pointless", src: "A5, A6" },
    { from: "me",   text: "fair. and if it filled gaps with b-roll it found itself?", src: "I-recon" },
    { from: "them", text: "nah", src: "A7" },
    { from: "them", text: "what i can use depends on what i actually shot", src: "A4" },
    { from: "them", text: "ai helping with the edit is cool but it shouldn't be making up or pulling in footage on its own", src: "A7" },
  ]},
  B_01: { participant: "B", screen: 1, topic: "The repetitive work behind editing", messages: [
    { from: "me",   text: "yooo", src: "filler" },
    { from: "me",   text: "you edit a lot right, can i ask you some stuff for a project", src: "I-recon" },
    { from: "them", text: "go for it", src: "filler" },
    { from: "me",   text: "what does a normal project look like for you", src: "I-recon" },
    { from: "them", text: "usually a mix. footage, photos, memes, overlays", src: "B1" },
    { from: "me",   text: "where does most of the time go", src: "I-recon" },
    { from: "them", text: "honestly finding stuff", src: "B2" },
    { from: "them", text: "templates, blender assets, whatever actually fits the look", src: "B2" },
    { from: "them", text: "and then cutting and trimming, which is the same thing every single time", src: "B3" },
    { from: "me",   text: "damn that's a lot of hunting", src: "filler" },
  ]},
  B_02: { participant: "B", screen: 2, topic: "Automation, creative control and pricing", messages: [
    { from: "me",   text: "ok so say the cutting and trimming was automated", src: "I-recon" },
    { from: "me",   text: "would you let it do more than that", src: "I-recon" },
    { from: "them", text: "nah, the final edit stays with me", src: "B5" },
    { from: "them", text: "what i need changes every project anyway", src: "B4" },
    { from: "me",   text: "what about it suggesting b-roll", src: "I-recon" },
    { from: "them", text: "as an option maybe", src: "B6" },
    { from: "them", text: "only if it matches the direction i'm going for", src: "B6" },
    { from: "me",   text: "do you use any ai rn", src: "I-recon" },
    { from: "them", text: "chatgpt for ideation", src: "B7" },
    { from: "me",   text: "and pricing, how would you want that to work", src: "I-recon" },
    { from: "them", text: "i already pay for adobe", src: "B8" },
    { from: "them", text: "a subscription is fine. token stuff where i can't predict the cost is a no from me", src: "B8" },
  ]},
};
