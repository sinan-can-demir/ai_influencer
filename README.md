# AI Influencer (working title)

A virtual, AI-driven personality — "Juno," a stylized/CGI "digital being"
with a consistent visual identity and an evolving, openly-AI personality —
posting text and images (video planned later), rather than a niche
tips-and-tricks bot. Full character concept in
[docs/persona-brief.md](docs/persona-brief.md).

## Status

Live and running, currently on Bluesky ([@junogrows.bsky.social](https://bsky.app/profile/junogrows.bsky.social)) —
X/Twitter is the eventual real target, added once the pipeline is fully
proven out here first. Built in phases; see [ROADMAP.md](ROADMAP.md) for
the full plan and detailed build history.

**Working today:**
- Draft generation grounded in a persona system prompt + recent post/reply
  history (Groq, `openai/gpt-oss-120b`).
- Identity-conditioned image generation from a curated reference set
  (Hugging Face, free tier).
- A human-in-the-loop review UI (Streamlit) — generate, edit, and either
  post immediately, reject, or approve for scheduled posting.
- A cron-driven scheduled poster that drains an approved-drafts queue on
  a fixed schedule — nothing in it was ever auto-generated or
  auto-approved, only auto-*timed*.
- Reactive engagement: filtered mentions/replies, drafted replies (same
  human-approval gate), a persona memory file, follow-back judgment, and
  topic-based follow discovery.

**Not yet built:** proactive engagement (commenting on posts Juno wasn't
tagged in) is fully designed but deliberately gated behind reactive
engagement being proven safe over real time — see ROADMAP.md's Phase 5.
X/Threads integration is scoped but not started.

## Principles for this build

- **Draft-and-approve, not autonomous.** No post — original, reply, or
  scheduled — ever leaves human review before its content is decided.
  Scheduling only ever affects *when* an already-approved draft posts,
  never *whether* it does.
- **Side-project pace.** Favor cheap/free tools and incremental phases
  over a big-bang build. Every phase produces something usable on its
  own.
- **Persona before pipeline.** The character's voice and identity are
  defined in a document before any code that impersonates them, so
  there's something concrete for LLM/image prompts to stay consistent
  with.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in the values below
```

`.env` needs:

| Variable | Used for |
|---|---|
| `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD` | Posting/reading via the AT Protocol. Use an app password scoped without DM access, not the real account password. |
| `GROQ_API_KEY` | Text generation (drafts, replies, judgment calls) — Groq's free tier. |
| `HF_API_TOKEN` | Image generation — Hugging Face, needs the "Inference Providers" permission on a fine-grained token. |

## Running it

- `streamlit run review_ui.py` — the main daily tool. Generate a draft,
  edit it, and post immediately, reject it, or approve it for scheduled
  posting.
- `python scheduled_poster.py` — posts the oldest approved-but-unposted
  draft, if any. Meant to run on a schedule (see the cron entry
  documented in ROADMAP.md), not typically invoked by hand. Run with
  `--dry-run` to see what it *would* post without any live side effect.
- `python reply_review.py` — drafts replies to filtered mentions/replies,
  gated behind a per-item approval prompt.
- `python check_notifications.py` — read-only, prints filtered
  notifications without drafting anything.
- `python follow_back.py` / `python discover_follows.py` — judge and
  follow accounts automatically (no per-item approval — following
  generates no public content, so it doesn't carry the same stakes as
  posting/replying).

## Repo layout

```
pipeline/            core logic: persona prompts, generation, image
                     pipeline, JSONL logging, the approved-post queue,
                     notification/reply helpers
driver.py            CLI alternative to review_ui.py
review_ui.py         Streamlit review UI (main daily tool)
scheduled_poster.py  posts the oldest approved queue entry; cron-driven
reply_review.py      drafts + gates replies to real mentions
check_notifications.py   read-only notification visibility
follow_accounts.py   one-off manual follow list
follow_back.py       automatic judged follow-backs
discover_follows.py  topic-based automatic follow discovery
data/                JSONL logs: posts, images, follows, approved queue,
                     persona memory (real audit trail, not secrets —
                     tracked in git)
assets/reference/    Juno's bootstrap identity reference images
assets/generated/    every image actually generated for a post
docs/persona-brief.md   the character bible
ROADMAP.md           phased build plan + detailed decision history
```
