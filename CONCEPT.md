# CONCEPT — Lane Tactics (working title)

*Version 1, written 2026-10-09, before any asset was generated. Later changes are added as dated revisions at the bottom; this version is not rewritten.*

## The game in two sentences

You command a small army of carved wooden pieces on a five-lane tabletop board, and you face an AI general who gives its orders at the same moment you give yours. Each turn you decide where every piece steps and what it strikes; then both plans play out together, and the first side to stand a piece on the enemy's back row wins.

Full rules: [RULES.md](RULES.md) (the single source of truth). How they were decided: [DESIGN-HISTORY.md](DESIGN-HISTORY.md).

## Core loop

| | |
|---|---|
| **Repeated action** | Plan a move for each piece (stay or step 1 square, 8 directions), watch the moves resolve, then pick a target square for each piece that can reach one. |
| **Decision each time** | Advance, hold or sidestep, and *when* to enter the enemy's reach: the side that strikes first alternates every turn. Which lane to push, which square to hit. |
| **Risk** | Pieces are few and fragile (two hits kill an archer). Stepping into range on the wrong turn means being shot first; holding back gives the enemy time to reach your back row. |

The asset slice proves this loop with one player archer against two enemy archers (see [CHANGE-BRIEF.md](CHANGE-BRIEF.md)).

## Design pillars

| Pillar | What it means | One visual or sound choice that honors it |
|---|---|---|
| **1. Read the board at a glance** | Team, unit type and state are clear in one look, even with the sound off. | Team paint covers the largest area of each piece, every piece has a thick dark outline, and teams also face opposite ways (player right, enemy left), so team survives without colour. |
| **2. Plans collide** | The tension is the reveal: two hidden plans meeting at once. | Music keeps a steady, patient pulse while you plan. Resolution is carried by sharp, single sound events that cut through it. |
| **3. Every piece has weight** | It should feel like moving real pieces on a real table. | Pieces hop square to square and land with a wooden *clack* (SFX-HOP). A defeated piece topples over instead of fading out. |
| **4. Fair, readable consequences** | When you lose a piece, you can see why and who did it. | The hurt pose leans away from the attacker. The targeted square is marked before the hit, and HP pips change at the same moment as the sound. |

## Art direction

**Painted wooden tabletop pieces on a linen game board, lit by a warm desk lamp.** Simple carved shapes (a cylinder body, a ball head, a disc base) are what image models reproduce most consistently, and they read as solid silhouettes at small size (pillars 1 and 3). The toy-like tabletop frame makes chess-like hopping and toppling feel natural rather than stiff (pillar 3).

Reference notes (words only):

- **Materials:** smooth birch and darker walnut wood, matte enamel paint in flat team colours, visible wood grain only on the base; woven linen board squares.
- **Lighting:** one warm lamp from the upper left, soft contact shadows under each base, a darker wooden table beyond the board edge.
- **Mood / era:** a hand-made strategy game from a grandparent's shelf: calm, tactile and a little worn, not glossy plastic or fantasy-epic.

## Audio direction

The sound should make the player feel **calm concentration while planning, and short, physical punctuation when plans collide**. The music is small and acoustic (plucked strings, soft wood percussion, a low drone), slow enough to think over. It is never heroic or busy, because the player is reading the board while it plays. Effects are dry, close and wooden: they sound like pieces on a table, not like a battlefield.

| Moment | Music | Effects |
|---|---|---|
| Title / planning | The loop plays steadily | none until you act |
| Move playback | Continues | SFX-HOP once per piece that lands in a new square |
| Combat | Continues | SFX-HIT when your arrow lands, SFX-HURT when you are hit |
| Pause | Ducks to a quieter level and resumes on unpause | none |
| Defeat | Fades out; silence carries the loss | the last SFX-HURT is the final sound |
| Win | Stops at once | SFX-WIN plays alone |
| Retry | Restarts from the top of the loop | — |

## Revisions

*(none yet)*
