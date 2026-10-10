# Lane Tactics — design history

How the game and its rules were decided, Sep 29 – Oct 9, 2026, in a conversation between the user and Claude. Each decision records who proposed it, which is useful raw material for the Frictional log. **User** = the user's own idea. **Claude → accepted** = Claude proposed it and the user accepted. **Changed by user** = the user overrode Claude's proposal.

## 1. Choosing a genre (Sep 29)

- Claude reviewed the Assignment 1 submission and laid out genre options: silhouette platformer, point-and-click adventure, rhythm game, deckbuilder, arcade/survivor-like, top-down action, and horror.
- The key constraint Claude raised: image models are bad at drawing the same character the same way across many frames. Genres that need many matching animation frames (walk cycles, 4- or 8-direction sprites) are the riskiest for generated art.
- Given the user's taste (Outer Wilds, Sekiro, Elden Ring), Claude suggested two options: a 2D atmospheric exploration game (safest fit) or a silhouette duel game (more ambitious).

## 2. Real-time Clash Royale-style idea (Sep 29)

- **User:** a simple Clash Royale-like game where the player deploys soldiers from the bottom of the screen, and can also order existing soldiers to hold or move.
- Claude's estimate: 40–60 hours for a first playable scene.
- Claude's concerns:
  - Commanding units one by one turns the game into a small RTS (10–15 hours alone, plus a lot of tuning for feel).
  - A top-down view where units walk in every direction is the worst case for consistent generated art.
- Claude's alternatives: army-wide commands (like Stick War: Legacy), rally points (like Kingdom Rush), or a side view.

## 3. Switch to turn-based (Sep 29) — user

- **User:** turn-based play, top-down view, Plants vs Zombies-style lanes, chess-like movement, a fixed army whose mix the player chooses, reinforcements every turn, an order for every soldier, a 2-unit limit per square, melee resolving before archers, and a win by reaching or damaging the enemy's end.
- Claude's analysis: turn-based play largely removes the art-consistency problem, because units hop between squares and need no walk cycles. It also makes the rules testable as plain data. New risks: giving every unit an order is tedious, simultaneous moves create edge cases, players need previews of what will happen, and balance.
- 5 lanes vs 3: **Claude → accepted** 5. Three lanes are no easier to code, and with these ranges every unit would reach the whole board width, so lanes would stop mattering.
- Claude's estimate: 60–95 hours for the full rule set, or 30–40 hours for a reduced first scene.

## 4. Rules, round 1 (Oct 6)

| Topic | Decision | Source |
| --- | --- | --- |
| Turn order | Both sides give orders at the same time | User |
| Reinforcement count | Tune in testing | User |
| Reinforcement types | Player picks from the remaining pool | Claude → accepted |
| Riders | Only riders move 2 squares; every rider's first step resolves before other units move; the second step is cancelled if an enemy is in or next to the rider's square | User |
| Melee | Attacks own square or one adjacent square, and strikes back when hit | User |
| Rider charge | Extra damage after two complete steps | User (refined in round 2) |
| Archers | Never strike back; choose a target manually after movement | User |
| Archer auto-fire ("Watch") | User idea; Claude recommended building manual targeting first and adding Watch later | Claude → accepted |
| Archer range | "Two steps away" | User (exact shape settled later) |
| Reaching the back row | One enemy getting through is an instant loss | User |
| Shared squares | Friendly and enemy units can share a square | Claude → accepted |
| No order given | The unit stays | Claude → accepted |

## 5. Rules, round 2 (Oct 9)

| Topic | Decision | Source |
| --- | --- | --- |
| Combat structure | Melee and archer attacks happen in one phase | User (Claude had them as two phases) |
| Resolution | Attacks resolve one at a time; each attack and its strike back land together | User |
| Archer strike back | An archer attacking an adjacent square is struck back after its arrow lands | User |
| Archer targets | Cannot choose a square with no enemy; friendly fire allowed | User |
| Contested squares | Show the attempt (arrow or shadow); survivors move in after combat | User idea; Claude formalized the details |
| Swaps | Units may pass through each other | Changed by user (Claude proposed both units stay put) |
| Sideways moves | Allowed (all 8 directions) | User |
| Charge bonus | Both steps in the same direction; applies only to the 3 squares in that direction, marked red | User |
| Strike back | On every hit, reduced at half health or below | User (Claude proposed once per turn) |
| Back row | The whole back row; an enemy standing there at the end of the turn causes a loss | User |
| Base health | Dropped | Follows from the back-row rule |
| Elimination | Running out of all soldiers is an immediate loss | User (Claude proposed a turn limit) |
| Turn limit | Kept as well: the side with fewer soldiers left loses | Claude → accepted |

## 6. Rules, round 3 (Oct 9)

| Topic | Decision | Source |
| --- | --- | --- |
| Lane direction | Horizontal | User |
| Attack order | Sides alternate one unit at a time; the side going first switches each turn | Claude → accepted (Claude flagged that strict left-to-right order would favor one side) |
| Within-side order | Front to back, then top lane to bottom | Claude assumption, confirmed by user |
| Who enters a contested square first | Survivors, in attack order | User |
| Archer's own square | Cannot be targeted | User |
| Target gone before the unit's turn | Attack cancelled; later, archers will switch to Watch instead | Claude → accepted, with user's addition |
| Both sides lose on the same turn | The player wins (deliberate player advantage against the AI) | Changed by user (Claude proposed a draw on equal counts) |
| Shielders | High health, low damage, block arrows for the allied unit in their square, take half arrow damage themselves | Claude → accepted |

## 7. Rules draft written, plus a later correction (Oct 9)

- Claude wrote `RULES.md` (originally a Claude Docs page). All five open assumptions were ticked as confirmed by the user.
- **Correction from the user (doc comment):** Claude had drawn the archer range as a star shape with 16 squares. The user corrected it: archers reach all 24 squares in the 5 × 5 area except their own square.
- The numbers table holds Claude's first guesses for the paper test. None are agreed values.

## Open for the Frictional log

These entries still need the user's own "Expected" and "Learned / still unsure" lines:

- Why the real-time idea was dropped for turn-based.
- How the contested-square "shadow" rule came about.
- The archer-range misunderstanding (star shape vs full 5 × 5).
