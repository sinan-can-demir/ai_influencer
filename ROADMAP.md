# Roadmap

Phased build plan for the AI influencer. Each phase produces something
runnable/checkable on its own — we're not writing a giant pipeline and
turning it on at the end. Concepts we'll cover while building each phase are
listed under it; treat those as the syllabus for that phase.

Scope locked in so far:
- **Platform:** X is the real target, but we're building/testing against
  Bluesky (junogrows.bsky.social) first as a free, zero-risk sandbox — X
  gets added once the pipeline is proven.
- **Content:** text + images, video added once the first two are solid.
- **Posting model:** draft-and-approve. Full autonomy is a possible *later*
  phase, not a starting assumption.
- **Persona:** stylized/CGI "digital being" named Juno, personality-first
  (not a narrow-niche expert account). Defined in [docs/persona-brief.md](docs/persona-brief.md).
- **Pace:** side-project — cheap tools, incremental phases.
- **LLM provider:** Groq (free tier), model `openai/gpt-oss-120b`.

---

## Phase 0 — Foundations

Get the boring stuff decided once so later phases don't stall on it.

- [x] Lock the persona brief (name, voice, backstory, visual spec, content
      pillars) — see `docs/persona-brief.md`. Juno, v1.
- [ ] Pick and provision an X Developer App. As of Feb 2026, X moved new
      developers to pay-as-you-go pricing: $0.015/post created ($0.20 if it
      contains a link), $0.005/post read (capped 2M reads/mo), no monthly
      minimum. At side-project posting volume this is cheap (a few
      dollars/month) — verify current pricing before committing, but it's no
      longer the blocker it used to be. Deferred until Bluesky pipeline is
      proven out.
- [x] Prototype against Bluesky (AT Protocol) first — account created
      (junogrows.bsky.social), app password scoped without DM access,
      connectivity verified end-to-end via `bluesky_test.py`.
- [x] Decide secrets management — `.env` + `.env.example` + `.gitignore`
      pattern in place.
- [x] Pick the LLM provider for persona text generation — Groq, free tier,
      model `openai/gpt-oss-120b`.

**Concepts:** API key hygiene / never committing secrets, X API tiers &
rate limits, what a "developer app" even is on X.

---

## Phase 1 — Persona bible → text generation (MVP)

The smallest useful thing: given the persona brief, generate an on-voice
draft tweet, and let a human approve/reject/edit it. No posting automation
yet — output can just print to console or write to a file you copy-paste.

- [x] Turn the persona brief into a system prompt — `pipeline/persona.py`.
- [x] Build a minimal script: prompt → draft text → print for review —
      `pipeline/draft.py`, grounded with the real current date so it
      doesn't hallucinate temporal claims.
- [x] Add lightweight persona "memory" so drafts don't repeat themselves or
      contradict earlier posts — `pipeline/history.py` (`log_post` /
      `get_recent_posts`), storage bounded separately from what's fed to
      the LLM (`data/post_history.jsonl` grows unbounded, only the last 5
      posts get fed into the prompt). Verified end to end.
- [ ] Manually post a handful of approved drafts (Bluesky for now, X once
      added) by hand, see how they read in the wild — two posted so far.

**Concepts:** system prompts vs. user prompts, prompt engineering for voice
consistency, context windows, why "memory" for an LLM app is usually just
"what you choose to put back into the prompt," temperature/sampling basics.

---

## Phase 2 — Visual identity pipeline

Now give the persona a consistent face/look for images.

- [ ] Decide the concrete visual spec from the persona brief (this is a
      prerequisite input, not a code task).
- [ ] Prototype character consistency with a hosted diffusion API (e.g.
      Replicate or Fal.ai running SDXL/Flux) using a fixed reference image +
      image-to-image or IP-Adapter — cheaper and faster to iterate on than
      training a LoRA.
- [ ] If consistency isn't good enough, escalate to training a small LoRA on
      a curated reference set of the character.
- [ ] Wire image generation into the draft-review script from Phase 1, so a
      draft is (text, image) reviewed together.

**Concepts:** diffusion models at a high level, why "character consistency"
is the hard problem in AI image generation, LoRA vs. IP-Adapter vs.
ControlNet (what each actually does), hosted inference vs. running models
yourself.

---

## Phase 3 — Review workflow

Replace "print to console" with something you'd actually want to use daily.

- [ ] Simple local review UI (Streamlit is the lowest-effort option for a
      Python side project — a page listing pending drafts with
      approve/edit/reject).
- [ ] Approved drafts get posted to X via the API (this is where posting
      automation actually enters the picture — still human-gated).
- [ ] Basic logging: what was posted, when, and the draft that produced it
      (a flat file or SQLite is enough — no need for a real database yet).

**Ideas to consider for this phase (not committed to yet):**
- An `editor.py`-style second LLM pass that critiques/polishes a draft
  before it reaches human review (voice-consistency check, tightening) —
  assists the review, doesn't replace it. The human still makes the final
  call; an LLM should never auto-approve its own output.
- Email as a remote trigger for review, so you're not tied to being at a
  terminal when a draft is ready. A full closed-loop "approve by replying
  to the email" flow needs something watching the inbox (real work); a
  lighter version — email a notification + link to a small approval page —
  gets most of the value for much less complexity.

**Concepts:** what a "review queue" pattern buys you, X API v2 posting
(tweets, media upload), why you want an audit log before you trust
automation more.

---

## Phase 4 — Video

Only start this once text+image is producing consistent, on-brand output
you're happy with — video is the most expensive and hardest-to-iterate-on
medium, so validate the persona before spending here.

- [ ] Decide approach: animate existing stills (cheaper, more limited) vs. a
      generative video API (Runway/Kling/Luma — pricier, more capable).
- [ ] Extend the review workflow to handle video drafts.

**Concepts:** current state of AI video gen (and its cost/latency tradeoffs
vs. image gen), where the field is moving fast enough that this phase's
tool choice should be revisited right before you start it, not locked in now.

---

## Phase 5 — Feedback loop (stretch)

Only after the above is running for a while and producing real engagement
data.

- [ ] Pull engagement metrics back in (likes/replies/impressions).
- [ ] Use that signal to inform persona/content adjustments — human-reviewed,
      not auto-tuned.
- [ ] Revisit whether any part of the draft-and-approve gate can safely
      loosen for low-risk content types.

**Concepts:** feedback loops in content systems, why auto-tuning a
personality on engagement metrics is a real ethical/quality risk (optimizing
for engagement tends to degrade personality coherence over time) and should
be resisted, not defaulted into.

---

## Explicitly out of scope for now

- Multi-platform (Instagram/TikTok/etc.) — X only until the pipeline proves
  itself.
- Full autonomy / unattended posting — draft-and-approve is the standing
  model; revisit later, deliberately.
- Monetization mechanics (sponsorships, affiliate, etc.) — not blocking the
  build, address once there's an audience.
