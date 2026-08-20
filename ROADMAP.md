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

- [x] Decide the concrete visual spec from the persona brief — locked in
      docs/persona-brief.md. Revised from the original "3D CGI render" plan
      to warm painterly digital illustration (sage green + cream,
      copper/auburn wavy hair, warm brown eyes, leaf/sprout motif) after
      the bootstrap batch consistently converged there instead.
- [x] Gather 5-10 reference images matching the locked spec — done. 10
      images generated (not sourced) to bootstrap her identity from
      scratch, in `assets/reference/`. These double as the actual
      multi-reference input for generation, not just style inspiration.
- [x] ~~Google AI Studio / Gemini 2.5 Flash Image~~ — dead end. The
      account dashboard showed a hard `0/0` rate limit for the image model
      specifically on the free tier (confirmed: Google pulled free-tier API
      access to image generation in March 2026, even though free access to
      Gemini's *text* models and the *consumer app's* image tier are both
      still real). Billing would be required for any image access at all.
- [x] Pivoted to **Hugging Face** instead — no card required. Two-step plan:
  - [x] **Step 1 (done, verified working):** plain text-to-image via
        `huggingface_hub.InferenceClient`, pinned to `provider="hf-inference"`
        specifically (avoids "auto" silently routing to a paid third-party
        provider). Model: `stabilityai/stable-diffusion-3-medium-diffusers`
        (FLUX.1-dev is NOT available on `hf-inference` — confirmed via HF's
        own docs, it 410'd when tried; FLUX is only routed through paid
        providers). Requires a fine-grained token with the specific
        "Inference Providers" permission checked (a plain read-scoped
        fine-grained token 403's). Result: correct identity traits
        (hair/eyes/motif/palette) but a flatter, more generic render style
        than the bootstrap reference set — expected, since this is a
        weaker free model with no reference-image conditioning at all yet.
  - [x] **Step 2 (done, verified working):** feeds Juno's actual reference
        images in for real identity-conditioned generation, via
        `gradio_client` calling `black-forest-labs/flux-klein-9b-kv`
        (official org Space, running on free ZeroGPU compute) — HF's clean
        `InferenceClient` doesn't support image-to-image on the free tier
        at all (only paid providers), so this Space-based path was the
        real free option. Result is noticeably closer to the bootstrap
        reference set than step 1, in both identity and render style.
        Two real constraints hit along the way: more than 1 reference
        image triggered an unhelpful ZeroGPU `RuntimeError` (currently
        sending just 1 — worth revisiting whether 2-3 works, since more
        references generally means better consistency); anonymous calls
        get almost no ZeroGPU quota, so the client authenticates with
        `token=` (confirmed the correct kwarg via `inspect.signature()`
        against the installed library — `hf_token` doesn't exist on this
        version, another API-naming surprise).
- [ ] If Step 2 consistency isn't good enough, escalate to training a
      small LoRA on the curated reference set (unchanged fallback plan).
- [x] **Log image generations**, same pattern as `pipeline/history.py`'s
      post logging: `IMAGE_HISTORY_PATH = "data/image_history.jsonl"` +
      `log_image(prompt, reference_images, seed, output_path)`, called
      from `image_pipeline()` after a successful save. Gives an audit
      trail and lets a good result's seed be reproduced/riffed on later.
      Along the way, `image.py` stopped having functions silently reach
      for their own dependencies (`input_images()`, `generate_conditioned_image()`
      now take `paths`/`images` as real parameters instead of fetching them
      internally) — needed so the logged `reference_images`/`seed`/
      `output_path` reflect what was actually sent to the model.
- [x] **Have Groq generate the image prompt per-post**, instead of the
      static `IMAGE_PROMPT`. New `IMAGE_SYSTEM_PROMPT` in `persona.py`
      (describes scene/pose/mood, explicitly excludes physical traits —
      those come from reference images now, repeating them in text fights
      the conditioning instead of helping it); new
      `generate_image_prompt(post_text)` in `draft.py`, reusing the
      existing `groq_client()`/`DRAFT_MODEL`; `image.py`'s `get_prompt()`
      and `image_pipeline()` both take `post_text` as a parameter now.
      Verified end to end with a real `generate_draft()` output — the
      generated scene (ceiling-gazing, a one-minute timer on a desk)
      matched that day's actual draft content while keeping Juno's
      established render style. Caller still supplies the post text
      manually for now — full auto-chaining of draft → matching image is
      the item below, not this one.
- [x] Wire image generation into the draft-review script from Phase 1, so a
      draft is (text, image) reviewed together — `driver.py` at repo root.
      Initially built review-only (posting deliberately left out, since
      wiring it in as a side effect of building this file would've bypassed
      the draft-and-approve model rather than honoring it) — posting was
      added right after, but gated behind an explicit `input("Post this?
      y/n")` confirmation, same category as the image-inclusion prompt.
      That distinction (auto-posting vs. a real human checkpoint) is why
      it was safe to add in the same file. `driver.py` now supersedes
      `bluesky_test.py` as the actual posting tool — `bluesky_test.py`
      stays for now as a manual fallback, to be retired later. Along the
      way, `pipeline/` became a real Python package
      (`pipeline/__init__.py`, internal imports switched to explicit
      `from pipeline.x import y`), resolving the import/path
      inconsistency that had been flagged twice before — single-file
      testing now goes through `python -m pipeline.draft` etc. instead of
      running scripts directly. `image_pipeline()` now returns `save_path`
      on success / `None` on failure so callers have a real signal instead
      of guessing; `driver.py` reports success/partial-failure based on
      that, rather than a blanket "success" regardless of what happened.

**Concepts:** diffusion models at a high level, why "character consistency"
is the hard problem in AI image generation, LoRA vs. IP-Adapter vs.
ControlNet (what each actually does), hosted inference vs. running models
yourself.

---

## Phase 3 — Review workflow

Replace "print to console" with something you'd actually want to use daily.

- [ ] Simple local review UI (Streamlit is the lowest-effort option for a
      Python side project — a page listing pending drafts with
      approve/edit/reject). `driver.py`'s CLI y/n prompts are a working
      but minimal version of this for Bluesky already — a real UI is
      still worth it once this feels limiting, and is the natural place
      to add review for X once that's connected.
- [x] Approved drafts get posted via the API — done for Bluesky
      (`driver.py`'s `post_draft()`, human-gated behind a CLI prompt,
      verified end to end with a real live post). Still open for X once
      Phase 0's X Developer App is provisioned.
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
- Let Juno herself decide whether a given post gets an image, instead of
  the human choosing every time (currently `driver.py` asks y/n per run).
  It's a more honest fit for the "dynamic, personality-driven being"
  framing — a real posting habit isn't "human picks image on/off," it's
  "this moment felt worth a photo, that one didn't." Deferred for now
  since it needs a real signal (structured output from `generate_draft()`,
  or a second small Groq call) rather than a human toggle, and the
  toggle works fine as a starting point.

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

## Phase 5 — Engagement (replies & memory)

Give Juno a way to notice and respond to people, not just post outward.
Reactive first, deliberately — proactive engagement is a later, separate
decision once the reactive system has run long enough to trust.

- [ ] Pull mentions/replies via the platform API (Bluesky notifications
      endpoint first, matching the existing build-on-Bluesky-first
      pattern). This is a new *read* path — nothing like it exists yet;
      `pipeline/` currently only ever writes outward.
- [ ] Content filtering before anything reaches review: skip
      harassment/hate/spam/explicit content, same spirit as the interest
      exclusions already made when setting up the Bluesky account
      (Politics/Finance were deliberately skipped as high-controversy,
      low-fit for an earnest persona).
- [ ] Reply drafts go through the same draft-and-approve gate as original
      posts — no exception, no auto-reply, even for reactive mentions.
      Likely surfaces as a review queue ("3 pending replies") rather than
      one-at-a-time like `driver.py`'s current single-post flow, since
      replies can arrive in a batch.
- [ ] **Juno's own memory file** — distinct from `data/post_history.jsonl`
      (which is a posting audit log, not self-knowledge). Tracks things
      like: specific people she's talked to and what about, running
      themes she's been exploring, self-observations that accumulate over
      time. This is the mechanism for real character evolution: instead
      of growth being purely narrative (what she happens to write about),
      accumulated memory gets fed back into future `generate_draft()`/
      reply-generation calls, the same way `get_recent_posts()` already
      feeds bounded context in — just deeper and more structured than
      "last 5 posts." Exact schema (jsonl vs. something richer, what
      counts as memory-worthy) is a design task for when this gets built,
      not decided here.
- [ ] Proactive engagement (Juno browsing the platform and initiating
      replies to posts she wasn't tagged in) — explicitly deferred until
      the reactive system above has been running and trusted. Bigger
      feature: needs timeline browsing plus real judgment about what's
      worth engaging with, and carries more reputational risk if that
      judgment is ever wrong. Do not build this alongside reactive
      replies; revisit as its own deliberate decision once reactive is
      proven, matching how autonomy itself stays a deliberate, separate
      decision (see "Explicitly out of scope for now").

**On the current architecture, for context:** `generate_draft()` and
`generate_image_prompt()` are both single-shot calls to
`openai/gpt-oss-120b` via Groq — no extended multi-step reasoning, no
chain-of-thought. That's adequate for short creative writing, but reply
generation (understanding a stranger's post, judging tone, avoiding
missteps) is a harder task; a two-pass approach (draft the reply, then a
second critique/polish pass — see the `editor.py` idea under Phase 3) is
worth revisiting once real reply volume exists. Memory today is
intentionally shallow: `get_recent_posts(n=5)` bounds what's fed into
each generation call regardless of how much history has accumulated in
storage. The new memory file above is what deepens that.

**Safeguards, restated plainly:** every reply — reactive or (eventually)
proactive — goes through draft-and-approve, same as original posts. This
phase does not reopen the autonomy question; "Full autonomy / unattended
posting... revisit later, deliberately" (see below) still applies
unchanged, including to replies.

**Concepts:** notification/mention APIs, why reply generation is a harder
task than origination (needs to understand and respond to someone else's
content, not just Juno's own voice), structured memory vs. unbounded log
storage, why proactive engagement carries a different risk profile than
reactive.

---

## Phase 6 — Feedback loop (stretch)

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
