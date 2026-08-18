# AI Influencer (working title)

A virtual, AI-driven personality built for X (Twitter). A stylized/CGI "digital
being" with a consistent look and an evolving personality — posting text,
images, and eventually video — rather than a niche tips-and-tricks bot.

## Status

Scoping phase. No pipeline exists yet. See [ROADMAP.md](ROADMAP.md) for the
build plan and [docs/persona-brief.md](docs/persona-brief.md) for the
character concept we're defining first.

## Principles for this build

- **Draft-and-approve, not autonomous.** Nothing posts to X without a human
  looking at it first, at least until the pipeline has earned trust.
- **Side-project pace.** Favor cheap/free tools and incremental phases over a
  big-bang build. Every phase should produce something usable on its own.
- **Persona before pipeline.** The character's voice and identity get defined
  in a document before we write code that impersonates them — otherwise
  there's nothing for the LLM prompts or image prompts to be consistent with.

## Repo layout (so far)

```
docs/            scoping and design docs (persona bible, decisions, notes)
ROADMAP.md       phased build plan
README.md        this file
```

Code directories will be added as each phase actually starts (no point
scaffolding empty folders yet).
