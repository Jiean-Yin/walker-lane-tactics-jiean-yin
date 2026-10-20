# Lane Tactics — design history

How the game and its rules were decided, Sep 29 – Oct 9, 2026, in a conversation between the user and Claude (section 8: Oct 19, with Claude Code in this repository). Each decision records who proposed it, which is useful raw material for the Frictional log. **User** = the user's own idea. **Claude → accepted** = Claude proposed it and the user accepted. **Changed by user** = the user overrode Claude's proposal.

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

## 8. Campaign additions (Oct 19)

Worked out while drafting GDD.md, in this repository. The rules are in RULES.md, marked 2026-10-19.

| Topic | Decision | Source |
| --- | --- | --- |
| Story | Outline: a human commander holds back a goblin invasion that gets harder, fights them in the mountains, strikes back with a night raid, and faces an unstoppable giant as the goblins' last effort | User |
| Story text | Briefings, level lines and closing lines for each episode in GDD.md §6, drafted from the outline | Claude, from the user's outline (for the user to edit) |
| Enemy army | Monsters: goblin archers, wolf riders, and a shield unit | User |
| Enemy rules | Same rules and numbers as the matching player type | Claude → accepted |
| Enemy art | Carved and painted wooden monsters, like the player's pieces | Claude → accepted |
| Enemy shield unit | A goblin holding a shield, so all three enemy types share one goblin look | Changed by user (the user's first idea and Claude's sketch had a shield giant) |
| Environments as the challenge | Levels get harder through terrain and night, not only through bigger armies | User |
| Mountains | Archers shoot further, riders get one more first-move step and a bigger charge, shielders take less damage, units see further | User |
| Mountain details | Entering a mountain ends the move; the rider's extra step counts when it starts the turn there; +1 ring, +3 charge, −1 damage for shielders, +1 sight; mirror pairs | Claude → accepted |
| Minimum damage | Every hit deals at least 1 damage, in any circumstance | User (after Claude flagged that an archer and shielder on a mountain would be immune to arrows) |
| Night: mist | Civilization-style exploration: squares stay revealed once your units have been near them; mountains are always known; enemy ranges are shown on revealed squares | Changed by user (Claude proposed a sight radius around current units only, with torches on woken enemies) |
| Night: enemies | Enemies sleep or patrol a fixed route until alarmed; patrol routes are shown with arrows | User |
| Night: alarm trigger | A unit of yours inside an enemy's attack range after moves, or attacking it; a newly alarmed enemy attacks from the next turn; the AI sees the whole board | Claude → accepted |
| Night: alarm spread | Each alarmed enemy alarms patrolling enemies within 2 squares and sleeping enemies within 1 square at the end of the turn | User (Claude proposed one radius for all) |
| Boss | A giant, chosen over a Walking Fortress | Changed by user (Claude recommended the Fortress) |
| Boss arrival | Arrives as an enemy reinforcement in a later turn, giving the player time to gather | User |
| Boss design | Carries a shield and a goblin archer on its shoulder, which dies with the giant; the other details are left for later | User |
| Giant: movement | 1 square per turn along its lane; it cannot be blocked and can only be killed | User |
| Giant: push | Before moving, it hits every unit in the square in front and pushes it one square back; a unit with no room behind it is destroyed | User |
| Giant: push details | Either side is pushed; the push happens at the start of step 4; a pushed unit's move is cancelled; pushed units enter in attack order; strike back applies | Claude → accepted |
| Boss level: win and loss | Win only by eliminating every enemy; no turn limit; losing on the back row still applies | User (win condition); Claude → accepted (back-row loss kept, back-row win off) |
| Shielder at half health | Once the shielder is at or below half health, its squaremate takes half arrow damage (at least 1) instead of 0 | Changed by user (Claude proposed the squaremate always takes 0) |
| Night: questions 2–8 | The alarm reading, one-step spread, sight 2, danger zones only on revealed squares, the post-step patrol zone, no torches, a Mend spent on death | Claude → accepted |
| Heal ability | One heal for a friendly unit, with limited uses or a one-turn delay | User |
| Heal name | Mend, because "Reinforcement" already means the new soldiers each turn | Claude → accepted |
| Heal limits | Both the delay and the limit: it lands after the next turn's combat; 2 uses per level; +3 HP | Claude → accepted |
| Heal and the AI | Player only: the AI neither uses Mend nor reacts to it | Changed by user (Claude proposed the AI gets it too) |
| Levels | Four episodes (Open Field, The Hills, Night Raid, The Giant); Mend from Episode 2 | Claude → accepted, built on the user's environment and boss ideas |
| Presentation | The game stays 2D; the 3D diorama stays a later option | Claude → accepted |

## Open for the Frictional log

These entries still need the user's own "Expected" and "Learned / still unsure" lines:

- Why the real-time idea was dropped for turn-based.
- How the contested-square "shadow" rule came about.
- The archer-range misunderstanding (star shape vs full 5 × 5).
- The shield giant becoming a goblin shielder, for a consistent look (Oct 19).
- Civilization-style mist instead of Claude's sight-radius-and-torches proposal (Oct 19).
- Keeping Mend for the human player only (Oct 19).
