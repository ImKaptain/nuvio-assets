# CLAUDE.md — nuvio-assets (stub)

Git repo of ~1,750 **generated images** (cards, hover gifs, backdrops, title logos), served raw from `raw.githubusercontent.com/ImKaptain/nuvio-assets/main/…` and GitHub Pages. Also contains `nuvio-share-hub/` (a copy of the public picker site).

This is the **asset store** for a larger 4-repo system. Images here are produced and pushed automatically by **Nuvio Studio v2** — they are not hand-curated.

➡️ **Full architecture, conventions, and safety notes:** `../nuvio-studio-v2/CLAUDE.md`

🗣️ **Talking to the user:** they're a vibecoder, not a developer. Focus on outcomes, skip the technical "how," use real-world analogies, and never dump code in chat. (Full rules in the doc above.)

Key things to know before editing here:
- The studio auto-commits/pushes assets via its `git.cjs`; on version promote it may **`git rm`** assets no longer referenced in the collection (destructive cleanup). Be careful pushing/committing manually.
- Folder layout (`Actors/`, `Directors/`, `Genres/`, `Streaming Services/`, `TitleLogos/`, …) and filenames are referenced by exact raw-URL paths in the collection JSON. Renaming a file breaks the live collection's artwork.
