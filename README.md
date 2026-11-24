# THE WORLD IN ONE DAY — Tuesday, 24 November 2026

[![make.fun bounty](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/kangelon-max/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/kangelon-max/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124)

One image that sums up the whole world's news of Tuesday 24 November 2026,
built for the
[make.fun news-image-20261124 bounty](https://make.fun/bounty/news-image-20261124).

The poster leads with the day's top story — Ukrainian naval drones sinking
the Russian corvette Merkury in the port of Benghazi, Libya — and packs in
the rest of the day: three tankers mined in the Strait of Hormuz and Iran's
seven conditions, Nvidia reinstating Jensen Huang and the market rocket
that followed (+31% in a day), the Gaza strikes that killed Hamas
internal-security chief Naeem Abu Nahel, the overnight hit on a
Zaporizhzhia apartment block, and briefs from Banten to Warsaw — the
Banten factory fire, Nepal's 5.6 quake, the first foreign astronaut
aboard Tiangong, the ICJ Rohingya ruling, Ebola responders trapped in
Ituri, the Villavicencio car bomb, the UN's AI-risk push and a Russian
drone over Poland — over a ticker of the day's real market closes.

## How it is made

- `gen.py` draws the poster with PIL at 2048×2048 — masthead, the night-sea
  hero scene, four story panels, eight briefs and the markets ticker, all
  from fixed constants and a fixed seed — and downscales it to the
  1024×1024 `entry.png` the competition gate accepts.
- `main.ts` (Node 22, standard library only) is the entrypoint: it checks
  `entry.png` against the gate (PNG magic, IHDR dimensions, IEND trailer,
  1 MiB cap), copies it to the output directory and writes a
  `manifest.json` of the shipped files (path, bytes, sha256, sorted by
  codepoint). Two runs write byte-identical output.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```
