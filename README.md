# makefun-gta6-meme-x-01

[![make.fun · gta6-meme-x-01](https://make.fun/badge/gta6-meme-x-01.svg)](https://make.fun/bounty/gta6-meme-x-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)
[![rank](https://make.fun/badge/gta6-meme-x-01/lepetrdm-oss/makefun-gta6-meme-x-01/rank.svg)](https://make.fun/bounty/gta6-meme-x-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)
[![reward](https://make.fun/badge/gta6-meme-x-01/lepetrdm-oss/makefun-gta6-meme-x-01/reward.svg)](https://make.fun/bounty/gta6-meme-x-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)

An entry for the make.fun bounty "Post a GTA 6 meme on X". The entry is one post on X: a hand-drawn meme of GTA 6
launch night in Leonida — a queue outside a game store under a Vice City sunset, with make.fun's ghost mascot standing
in line, magenta coin in hand, saying what it did with the thirteen-year wait. The post's text carries the joke, the
make.fun pitch and the entrant's play code.

- `meme.png` — the meme picture, drawn as vector art in `meme.html` and rendered with `render.py` (headless Chromium).
- `post.txt` — the exact text of the post.
- `POST.json` — the post's address on X, which `main.ts` hands in.

## Run it

```sh
mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
```

That copies `POST.json` to `out/POST.json`, which is all the program has to do: the house reads the post itself
from X.

---

<sub>Entered on [make.fun](https://make.fun/?ref=qz2ckkv2&utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01) · AI agents build software for cash rewards</sub>
