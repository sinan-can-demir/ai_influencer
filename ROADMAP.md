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
- [ ] **Threads, scoped as a real alternative to X (not yet built).**
      Considered instead of Instagram specifically because Threads is
      text-first with replies and a character limit — structurally close
      to Bluesky/X, unlike Instagram's image/carousel-first model, which
      would need real pipeline rework (mandatory images, different
      comment/DM engagement shape). The free-vs-paid tradeoff versus X is
      really free-but-more-setup vs. paid-but-simpler-integration, not
      free-with-no-cost:
      - **API cost:** $0 — no dollar cost found in Meta's docs for the
        Threads API (unlike X's pay-as-you-go pricing above).
      - **Setup, verified against Meta's own docs:** full Meta App Review
        is normally required before an app can act on other users'
        accounts, **but is skippable for a single self-owned account** by
        adding Juno's Threads account as a "Threads Tester" on the
        developer app — no waiting on Meta's review process. Still real
        one-time setup: create a Meta Developer app with the Threads use
        case, add the Tester, implement the OAuth authorization-window
        flow (different auth model than Bluesky's simple handle + app
        password), exchange for a short-lived token (1hr) then a
        long-lived token (60 days).
      - **Real ongoing maintenance risk, not present on Bluesky:** the
        long-lived token isn't permanent — it must be refreshed via
        `POST https://graph.threads.net/refresh_access_token` between 24
        hours and 60 days after issue, or it's **permanently dead** and
        requires the full manual re-authorization flow again. Needs
        either a scheduled refresh job or a very reliable manual
        reminder before this is safe to rely on — a genuinely new
        operational concern this project hasn't had to handle before.
      - **Publishing model differs from `atproto`'s single-call
        `send_post()`:** a two-step container flow — `POST /threads` to
        create a container (`media_type`: TEXT/IMAGE/VIDEO/CAROUSEL),
        then `POST /threads_publish` with the returned `creation_id`.
      - **Scopes needed:** `threads_basic` (required for all endpoints),
        `threads_content_publish` (posting), `threads_manage_replies`
        (replying) — a near-direct match to what `driver.py`/
        `reply_review.py` already do on Bluesky.
      - **Rate limit:** 250 posts/24h per profile — far more than this
        project's actual posting volume, not a real constraint.
      - **Likely architecture:** a new `pipeline/threads_client.py` (or
        similar), mirroring how `pipeline/notifications.py` holds
        Bluesky-specific logic — `generate_draft()`/`generate_reply()`/
        `should_generate_image()` etc. are all platform-agnostic already
        and should port over directly; only the posting/auth/notification
        layer is genuinely new.
      - **Idea flagged, not scoped:** once Threads has a real, working
        client alongside Bluesky's, worth looking at whether `driver.py`/
        `review_ui.py` should unify into a joint review flow (pick a
        platform, or post to both) instead of parallel platform-specific
        drivers. Deliberately not designed in detail yet — there's no
        second real implementation to design the shared shape against,
        same reasoning as why `generate_text()` wasn't extracted until
        two real call sites already existed. Revisit once Threads
        actually has a working `threads_driver.py` to compare against.
      Not started — this is scoping only, same as Phase 5 was before it
      was built.
- [x] Prototype against Bluesky (AT Protocol) first — account created
      (junogrows.bsky.social), app password scoped without DM access,
      connectivity verified end-to-end via `bluesky_test.py`.
- [x] Decide secrets management — `.env` + `.env.example` + `.gitignore`
      pattern in place.
- [x] Pick the LLM provider for persona text generation — Groq, free tier,
      model `openai/gpt-oss-120b`.

**Concepts:** API key hygiene / never committing secrets, X API tiers &
rate limits, what a "developer app" even is on X, OAuth token lifecycles
(short-lived vs. long-lived vs. permanent) as a different model from
Bluesky's app passwords.

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
- [x] Manually post a handful of approved drafts and see how they read
      in the wild — done, 12+ real posts on Bluesky as of this writing.
      X still pending Phase 0's Developer App.

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

**Ideas to consider for `image_pipeline()`'s error handling (not committed
to yet):** the current `except Exception` in `image_pipeline()`
(`pipeline/image.py`) is deliberate and works well for interactive use —
confirmed live when a HF ZeroGPU "no GPU available after 60s" timeout
(a transient free-tier queue issue, not a code bug) was caught cleanly and
degraded to `(None, None)` instead of crashing `review_ui.py`, with the
per-step print breadcrumbs (`"X: success"` / `"X: failure"`) making it
possible to pinpoint exactly which step failed just by reading the
terminal. Two gaps in that design worth revisiting before anything in this
project runs unattended (e.g. Phase 5's proactive engagement, which is
cron-driven with no one watching stdout):
  - The bare `except Exception` doesn't distinguish an expected external
    failure (HF queue busy, network blip) from a real bug in the pipeline
    code (e.g. a typo'd kwarg) — both print an identical
    `"Image pipeline complete: failure"` line, and only the exception text
    itself (visible in an interactive terminal, easy to miss otherwise)
    tells them apart.
  - Failures aren't persisted anywhere — only `print(f"Error: {e}")` to
    stdout, nothing written to `data/image_history.jsonl` or elsewhere. No
    way to later ask "how often does this fail, and on what error?" without
    having been watching the terminal live when it happened.
  Not urgent while a human is driving `review_ui.py`/`driver.py`
  interactively — becomes relevant once something in this pipeline runs
  unattended.
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
      it was safe to add in the same file. `driver.py` superseded
      `bluesky_test.py` as the actual posting tool; `bluesky_test.py` has
      since been removed (it was a one-off connectivity test, not a
      dedicated tool, and had no remaining references anywhere in the
      codebase). Along the way, `pipeline/` became a real Python package
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

- [x] Simple local review UI — done (`review_ui.py`, Streamlit): generates
      a draft live, lets you edit the text, optionally generate an image,
      then post or reject/start over. Same underlying functions as
      `driver.py` (which stays as the CLI alternative). Verified end to
      end with a real live post through the UI. Still the natural place
      to add review for X once that's connected.
- [x] Approved drafts get posted via the API — done for Bluesky
      (`driver.py`'s `post_draft()`, human-gated behind a CLI prompt,
      verified end to end with a real live post). Still open for X once
      Phase 0's X Developer App is provisioned.
- [x] Basic logging: what was posted, when, and the draft that produced
      it — done, `log_post()`/`data/post_history.jsonl` (a flat JSONL
      file, no database needed).
- [ ] **Scheduled posting via an approved-queue.** Goal: posts go out at
      consistent, human-like times instead of only whenever someone
      happens to be at the terminal. Scoped, not started — build this
      yourself function-by-function, ask for help per-step as needed.
      Deliberately does **not** reopen "Full autonomy / unattended
      posting" (see "Explicitly out of scope for now" below): a human
      still approves every draft's content before it can ever post,
      same as today. The only thing moving to a timer is the *posting
      moment* of an already-approved draft, not the judgment of whether
      it should exist.
      - **Design:** an "approved queue" — `data/approved_queue.jsonl`,
        one line per approved-but-not-yet-posted draft
        (`{timestamp, text, image_path, image_alt}`). Different from
        the existing JSONL logs in `pipeline/history.py` (which are
        append-only, never read back except for the last N) because
        items here need to be **removed** once posted — FIFO, oldest
        approved goes out first.
      - **Why this shape, not a simpler one:** keeps "what's allowed
        into the queue" (today: human approval via `review_ui.py`)
        fully decoupled from "what pulls off the queue and posts"
        (`scheduled_poster.py`). If unattended posting is ever
        deliberately revisited later, only the enqueue side would need
        to change — the poster script wouldn't, since it already
        doesn't know or care how an item got approved.
      - **Build order:**
        - [ ] A small queue module (e.g. `pipeline/queue.py`) with two
              functions: `enqueue_draft(text, image_path, image_alt)`
              (append a JSON line, same pattern as `log_post()` in
              `pipeline/history.py`) and `pop_next_draft()` (read the
              oldest line, remove it from the file, return it as a
              dict — or `None` if the queue is empty).
        - [ ] **Decide pop-timing before wiring it into the poster:**
              should `pop_next_draft()` remove the item from the file
              immediately (simpler), or should the item only be removed
              *after* a confirmed successful post (safer — a failed
              post, e.g. Bluesky being down, currently would otherwise
              silently lose that draft off the queue)? Worth resolving
              deliberately, not defaulting into whichever is easiest to
              write first.
        - [ ] `review_ui.py`: add an "Approve for scheduled posting"
              button next to the existing "Post" (posts immediately)
              and "Reject" — calls `enqueue_draft()` instead of posting
              live.
        - [ ] New root script `scheduled_poster.py`, mirroring
              `driver.py`'s posting half (`get_bluesky_client()` /
              `get_bluesky_account()` / `login()` / `post_draft()`,
              reusable via import from `driver.py` the same way
              `review_ui.py` already does) minus any generation logic —
              it only ever posts what's already in the queue. If the
              queue's empty, log that plainly and exit; it should never
              generate a draft itself.
        - [ ] **Cron gotchas to handle, not skip:** cron runs with a
              minimal environment, not your interactive shell — the
              crontab entry needs the absolute path to the venv's
              `python` (not a bare `python`/`streamlit` that only
              resolves because your shell's activated), and `cd` into
              the repo directory first so relative paths (`data/...`,
              `.env` via `load_dotenv()`) still resolve. Also redirect
              output (`>> some.log 2>&1`) since cron output isn't
              visible in any terminal — there's no "watch it run" the
              way there is today.
        - [ ] Manually test the full loop before trusting cron with it:
              approve a draft in `review_ui.py`, run
              `scheduled_poster.py` by hand and confirm it posts and
              removes the item, then only after that works add the
              actual crontab entry for your chosen times.

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
- [x] Let Juno herself decide whether a given post gets an image — done.
  `IMAGE_DECISION_SYSTEM_PROMPT` (persona.py) + `should_generate_image()`
  (draft.py, built on `generate_text()`) judge whether a post describes a
  visual moment worth a photo, replacing the old human y/n toggle in
  `driver.py` and the checkbox + separate button in `review_ui.py`. No
  human override by design — the existing post/reject gate stays the
  only human checkpoint. Verified end to end via both entry points,
  including a real live post.
- [x] Shared `generate_text(system_prompt, user_content)` helper in
  `draft.py` — done. `generate_draft()` and `generate_image_prompt()`
  both call it now instead of duplicating the client-creation/
  `chat.completions.create`/response-extraction boilerplate; each just
  builds its own prompt. Phase 5's reply generation will be a further
  consumer.
- [x] Alt text for posted images — done. `ALT_TEXT_SYSTEM_PROMPT`
  (persona.py) + `generate_alt_text()` (draft.py, built on
  `generate_text()`) turn the image-generation scene prompt into
  screen-reader-appropriate alt text. `image_pipeline()` now returns
  `(save_path, alt_text)`; `driver.py` and `review_ui.py` thread
  `image_alt` through to `send_image()`, replacing the hardcoded `""`.
  Verified end to end with a real live post carrying real alt text.

**Concepts:** what a "review queue" pattern buys you, X API v2 posting
(tweets, media upload), why you want an audit log before you trust
automation more.

---

## Phase 4 — Video

Only start this once text+image is producing consistent, on-brand output
you're happy with — video is the most expensive and hardest-to-iterate-on
medium, so validate the persona before spending here. Also explicitly
deferred on cost grounds, not just maturity: unlike text (Groq) and images
(Hugging Face), quality video generation (Runway/Kling/Luma) has no
meaningful free tier — it's a real departure from the free/open-tooling
principle that's shaped every other tool choice so far, so this phase
waits until that's a deliberate decision, not a default.

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

**Adjacent, done outside this phase's scope:** `follow_accounts.py`
(repo root) has Juno follow a small, manually-curated list of real
accounts — a legitimate, low-risk way to get initial visibility,
distinct from (and much lower-risk than) proactive engagement below.
`log_follow()`/`data/follows.jsonl` (history.py) log it, mirroring
`log_post()`. Candidates were sourced from Bluesky starter-pack
directories, then verified one by one against the real API rather than
trusted as scraped — most turned out to be personal accounts with
political bios despite matching category tags. Only 3 of 14 checked
held up as genuine, apolitical fits for Juno's declared interests:
`epollard.bsky.social` (biodiversity/butterfly conservation),
`thejokebot.bsky.social` (dad-joke bot), `jillybee72.bsky.social`
(improv comedy) — all 3 followed live.

Also `follow_back.py` (repo root): judges and follows back new
followers automatically, no per-item human approval — same reasoning as
above, a follow-back generates no public content so it doesn't carry
reply/comment-level stakes. `should_follow_back()` (draft.py, new
`FOLLOW_BACK_SYSTEM_PROMPT`) checks a new follower's bio + recent posts
(via `get_author_feed()`), skips spam/bot-farms/harassment/political-or-
financial content, errs toward yes otherwise. `get_new_followers()`
(pipeline/notifications.py) filters to followers Juno doesn't already
follow back. Verified end to end (correctly finds 0 candidates right
now — Juno's one follower, `thejokebot`, is already followed back); the
actual judge-and-follow path hasn't fired against a live new-follower
case yet.

**Topic-based discovery for who to follow — done.**
`discover_follows.py` (repo root) automates what `follow_accounts.py`
did manually: `search_candidate_authors()` (`pipeline/notifications.py`)
runs `search_posts()` against a fixed interest-term list, pulls each
matched post's *author* as a follow candidate (never the post for
commenting — deliberately **not** proactive engagement, doesn't wait on
its gate, since the risk that gates proactive engagement is generating
public content directed at a stranger unprompted, and following does
neither). `should_follow_back()` reused as-is for judgment. Rate-capped
at 2 new follows/run. Runs automatically, no approval gate, same as
`follow_back.py`.

Two real bugs surfaced and fixed while building this:
- `search_posts()`'s lighter `ProfileViewBasic` author objects lack a
  `description` field (unlike `get_profile()`'s fuller type) — judging
  candidates on post text alone let an automated Bridgy Fed news-bot
  through twice, since its post content read as genuinely on-topic with
  no bot signal visible. Fixed by fetching the full profile via
  `get_profile()` per candidate before judgment, same as `follow_back.py`
  already does — verified the bot's real bio ("bridged from... follow
  @ap.brid.gy to interact") now correctly gets rejected.
- **A real reliability bug in `follow_account()` itself, not specific to
  this feature:** `client.follow()` can return a false-positive success
  response (valid `uri`/`cid`) for a write that never actually persists
  to the repo — confirmed via direct `com.atproto.repo.list_records`
  queries (ground truth, bypassing the AppView's separately-lagging
  `viewer.following`/`get_follows()` reads). Two follows silently failed
  this way. `follow_account()` (`follow_accounts.py`) now verifies via a
  new `is_already_following()` helper (checks the actual repo) and
  retries once before logging success — this fix benefits every caller
  (`follow_accounts.py`, `follow_back.py`, `discover_follows.py`), not
  just this feature.

- [x] Pull mentions/replies via the platform API — done.
      `pipeline/notifications.py`'s `get_notifications(client)` calls
      Bluesky's notifications endpoint filtered server-side to
      mentions/replies; `check_notifications.py` (repo root, mirrors
      `driver.py`'s shape) logs in and prints them. First real *read*
      path in the project — `pipeline/` had only ever written outward
      before this. Verified against the real account (0 notifications
      currently, as expected with 0 followers). No filtering, drafting,
      or memory yet — just visibility.
- [x] Content filtering before anything reaches review — done.
      `CONTENT_FILTER_SYSTEM_PROMPT` (persona.py) +
      `should_surface_notification()` (draft.py, built on
      `generate_text()`) skip harassment/hate/spam/explicit content
      while still surfacing critical or disagreeing messages —
      disagreement alone isn't grounds to discard something. Same spirit
      as the interest exclusions already made when setting up the
      Bluesky account (Politics/Finance were deliberately skipped as
      high-controversy, low-fit for an earnest persona).
      `check_notifications.py` only prints notifications that pass.
- [x] Reply drafts go through the same draft-and-approve gate as original
      posts — done. `REPLY_SYSTEM_PROMPT` + `generate_reply()` (built on
      `generate_text()`) write the reply; `reply_review.py` (repo root)
      loops every notification that passes the content filter, drafts a
      reply for each, and gates posting behind a y/n per item — no
      exception, no auto-reply. `build_reply_ref()`
      (`pipeline/notifications.py`) constructs the root/parent
      `StrongRef`s Bluesky needs to thread the reply correctly. Verified
      in pieces (reply generation against real Groq calls, ref-building
      against synthetic data, the full script end to end with 0 real
      notifications) — the actual `send_post(reply_to=...)` call hasn't
      been exercised against a live incoming mention yet, since the
      account currently has 0 followers. First real mention will be the
      true end-to-end test.
- [x] **Juno's own memory file** — done, v1 scope. `data/memory.jsonl`
      stores one entry per reply (who she talked to, what it was about),
      written in her own first-person voice via `MEMORY_SYSTEM_PROMPT` +
      `generate_memory_entry()` (draft.py); `log_memory()` /
      `get_recent_memories()` (history.py) persist and read it back,
      mirroring `log_post()`/`get_recent_posts()`. `generate_draft()` now
      pulls recent memories into its prompt the same way it already
      pulls recent posts — this is the actual character-evolution
      mechanism: what she remembers from conversations can shape what
      she posts about next, not just narrative window-dressing. Scope
      cut for v1: automatic on every reply, no separate "is this
      memorable" judgment call (memory noise isn't a real problem yet at
      near-zero reply volume). "Running themes" / general
      self-observation entries beyond replies are a reasonable future
      addition, not built here.
- [ ] **Proactive engagement** — Juno browsing the platform and
      initiating comments on posts she wasn't tagged in. Fully scoped
      below; **not started**, explicitly gated behind reactive being
      *proven*: at least 5 real replies posted via `reply_review.py`,
      spanning at least 2 weeks of real operation, with no safety
      incidents (no harassment slipping past the content filter, no
      tone/factual mistake serious enough to need a takedown). That bar
      is clearly not met yet — reactive has 0 real mentions tested so
      far, since the account has 0 followers. Do not build this
      alongside reactive replies.
      - **Discovery:** `search_posts(q=..., limit=...)` (confirmed to
        exist on the installed `atproto` SDK) against a small fixed list
        of query terms drawn from Juno's declared Bluesky interests
        (Culture, Comedy, Music, Food, Nature) and her growing-up-arc
        content pillars — a plain constant list, not a dynamic topic
        model. Candidate home: `pipeline/notifications.py` (already
        holds Bluesky-specific read logic), or a new
        `pipeline/discovery.py` if that file gets crowded.
      - **Two-stage judgment**, same `generate_text()` pattern as
        `should_generate_image()`/`should_surface_notification()`:
        `should_engage_with_post()` (topical fit — does this genuinely
        connect to something Juno cares about, new
        `PROACTIVE_TOPIC_FIT_SYSTEM_PROMPT`) and
        `is_post_safe_to_engage()` (reuses `CONTENT_FILTER_SYSTEM_PROMPT`'s
        spirit but reworded for an arbitrary candidate post rather than a
        message sent to Juno, plus excludes Politics/Finance-adjacent
        content, matching the account's existing declared exclusions;
        new `PROACTIVE_SAFETY_SYSTEM_PROMPT`). Kept as two separate
        calls rather than merged, since they're different questions with
        different failure modes.
      - **Comment generation:** `generate_proactive_comment()`, built on
        `generate_text()` like `generate_reply()`, with a new
        `PROACTIVE_ENGAGEMENT_SYSTEM_PROMPT` — frames it as "noticed this
        and wanted to add a genuine related thought," not answering a
        direct question. Low-key, non-intrusive, same voice constraints
        as always.
      - **Rate/safety bounds** (code-level, not LLM-judged): a low cap on
        candidates per discovery run (start at 1); skip authors already
        engaged with recently (check `person` entries in
        `data/memory.jsonl`); skip high-engagement/already-viral posts
        (proxy for contentious, higher backlash risk — exact
        `search_posts()` metric field names to confirm when building);
        a simple, obvious kill switch to disable proactive discovery
        instantly.
      - **Execution model:** split discovery from review, since discovery
        needs to run on a schedule (unlike reactive, which triggers off
        an incoming notification) and the human-review gate blocks on
        `input()`, which can't run unattended in a cron job. A scheduled
        bash-wrapped script runs discovery → judgment → generation and
        writes surviving candidates to a new `data/pending_proactive.jsonl`
        — it never posts anything itself. A separate review step (CLI
        mirroring `reply_review.py`, or a new `review_ui.py` tab) shows
        each candidate's original post + Juno's proposed comment and
        gates posting behind the same explicit human approval as
        everywhere else — no exception.
      - **Memory reuse:** on approval + post, log via the existing
        `generate_memory_entry()`/`log_memory()`, same mechanism reactive
        replies already use.
      - **Autonomy reaffirmed:** discovery/drafting can run unattended;
        posting never can, matching how autonomy itself stays a
        deliberate, separate decision (see "Explicitly out of scope for
        now").

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
  itself. Worth revisiting sooner if Voice (below) ends up being a real
  priority: confirmed via the atproto SDK's own embed models
  (`atproto_client.models.app.bsky.embed.*` — images/video/external/
  record/gallery, no audio type) that Bluesky has no standalone audio
  embed, and X's posting is fundamentally the same (audio only rides
  inside video, not as its own post type). Instagram/Facebook are
  *assumed* to be more audio-native (Stories, Reels voiceover) but this
  is unverified — check for real before treating it as a plan, the same
  way the Bluesky assumption just turned out to be wrong.
- Full autonomy / unattended posting — draft-and-approve is the standing
  model; revisit later, deliberately.
- Monetization mechanics (sponsorships, affiliate, etc.) — not blocking the
  build, address once there's an audience.
- Voice (spoken posts, narration, eventually audio for video) — flagged as
  a future idea, not scoped yet. Confirmed neither Bluesky nor X support
  a standalone audio post (see Multi-platform note above), so this is
  gated on either Phase 4 video (audio riding inside a video post) or
  multi-platform expansion to something more audio-native — not a
  standalone feature on the current platform. Same cost-gating concern as
  Phase 4 video likely applies to the generation side (quality TTS APIs
  like ElevenLabs are mostly paid); revisit once there's an actual reason
  to build it, not preemptively.
  Options if/when this gets built, roughly cheapest-to-best quality:
  - Basic Python TTS (`pyttsx3`, wraps the OS's built-in speech engine —
    `espeak-ng` on Linux) — free, fully local, but genuinely robotic,
    closer to an old screen reader than a natural voice.
  - Open-source neural TTS (Piper, Coqui TTS/XTTS, Bark) — meaningfully
    more natural, and some are callable the same way Phase 2's image
    generation works: via `gradio_client` against a free-tier Hugging
    Face Space, reusing a pattern already proven out rather than
    learning a new one.
  - Paid APIs (ElevenLabs etc.) — best quality, but a real departure
    from the free/open-tooling principle, same as Phase 4 video.
