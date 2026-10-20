# Lane Tactics — Rules Draft

Oct 9, 2026 · @Stark

Two armies fight across a 5-lane board. Both sides plan in secret at the same time, then the turn plays out. Get one soldier into the enemy's back row and keep it alive to the end of a turn to win. "Lane Tactics" is a working title, and every number is a placeholder for playtesting.

*Additions agreed on 2026-10-19 (goblin enemies, minimum damage, the shielder half-health rule, mountains, night levels, Mend, the giant) are marked with that date. How they were decided: DESIGN-HISTORY.md section 8. Where they sit in the game: GDD.md.*

## Board and army

The board has 5 horizontal lanes, like Plants vs Zombies. The player's army starts on the left and the AI's on the right. Each side's **back row** is the 5 squares along its own edge.

- A square holds at most 2 units: two allies, two enemies, or one of each.
- Before the match, each side gets a fixed pool of soldiers and chooses how many archers, riders and shielders it has.
- At the start of every turn, each side receives a set number of new soldiers. The player picks their types from what is left in the pool and places each one on a free square of their own back row.
- The AI follows the same rules.

## Turn sequence

Every turn runs the same eight steps. Both sides plan at the same time and cannot see each other's orders.

1. **Reinforce:** both sides place their new soldiers on their own back row.
2. **Plan moves:** both sides give every unit a move order. A unit with no order stays. The player may also order one Mend (see Mend).
3. **Riders' first step:** every rider on both sides takes its first step.
4. **Main move:** all other units move, and riders take their second step.
5. **Plan attacks:** both sides choose a target square for every unit that has one in reach.
6. **Combat:** melee and archer attacks resolve together, one unit at a time, in attack order.
7. **Settle contested moves:** surviving units that were waiting to enter a full square move in. A Mend ordered on the previous turn heals its unit now.
8. **Win check:** see Win and loss.

## Movement

Each unit either stays or moves 1 square in any of the 8 directions: forward, sideways, back or diagonal. Squares off the board are not options.

- **Riders** take 2 steps, and both are planned in step 2 of the turn. The second step is cancelled if, after the first step, an enemy is in or next to the rider's square.
- **Passing through:** units can move through each other, and two enemies can swap squares. They usually end up next to each other and fight.

### Contested squares

A square is contested when more units try to enter it than it has room for.

1. Units that stayed in the square keep their spots.
2. Every unit trying to enter waits in its starting square and fights from there. An arrow or shadow on the target square shows the attempt.
3. After combat, the surviving waiting units enter in attack order until the square is full. The rest stay where they are.

A waiting unit still holds its starting square. Because of that, the check repeats until no square is over its limit.

If a rider's first step is contested, it does not take a second step. If its second step is contested, it gets no charge bonus.

## Combat

Combat is one phase after movement. Units attack one at a time, and each attack lands together with its strike back.

### Targeting

- **Melee units** (riders and shielders) target their own square or one of the 8 around it.
- **Archers** target any of the 24 squares within two steps (the full 5 × 5 around them), not their own square (see Units).
- The chosen square must hold at least one enemy. If a unit has only one valid target, it is selected automatically. A unit with no valid target does not attack.
- **Melee** hits every enemy in the target square and never hits allies.
- **Arrows** hit every unit in the target square, allies included. The one exception is shielder protection (see Units).

### Attack order

- The two sides alternate, one unit at a time. Which side goes first switches every turn.
- Within a side, units go front to back (closest to the enemy first), then top lane to bottom.
- During attack planning, an order number appears over every unit.
- A unit killed before its turn does not attack. If its target square has no enemies left when its turn comes, the attack is cancelled.
- A unit with no valid target keeps its place in the attack order and skips its attack. *(Added 2026-10-12 after the asset-slice search; see CHANGE-BRIEF.md revision R1.)*

### Strike back

Riders and shielders strike back every time an adjacent enemy hits them. Units in the same square count as adjacent.

- **Against melee:** the attack and the strike back land at the same moment. A defender killed by the hit still strikes back.
- **Against an adjacent archer:** the arrow lands first. The defender strikes back only if it survives.
- At half health or below, measured after the hit, the strike back does reduced damage.
- Archers never strike back. Nobody strikes back against arrows from two squares away or against their own side.

### Rider charge

If a rider's two steps go in the same direction, it gets bonus damage when attacking one of the 3 squares in that direction. Those squares are shown in red (see Units).

### Minimum damage *(2026-10-19)*

Every hit deals at least 1 damage after all reductions (shielder halving, a mountain, reduced strike back), so no unit is ever immune. The one exception is the shielder's squaremate while the shielder is above half health: it takes 0 from arrows, because that is a block, not a reduced hit (see Shielder protection under Units).

## Units

The three types are meant to counter each other: shielders block arrows, riders break through shielder lines, and archers punish riders.

| Unit | Movement | Attack | Strikes back | Role |
| --- | --- | --- | --- | --- |
| Archer | 1 square | Any of the 24 squares within two steps; hits every unit in the square | Never | Ranged damage, fragile |
| Rider | 2 steps, first step before other units | Adjacent; charge bonus after 2 steps in the same direction | Yes | Fast flanker |
| Shielder | 1 square | Adjacent, low damage | Yes | High health; blocks arrows for the allied unit in its square |

**Shielder protection.** An arrow into a shielder's square does half damage (round down) to the shielder. Its allied squaremate takes 0 while the shielder is above half health. Once the shielder is at or below half health, measured before the arrow lands, the squaremate takes half (round down, at least 1). *(Half-health rule added 2026-10-19.)*

**The enemy's pieces *(2026-10-19)*.** The AI's army is goblins: the **goblin archer**, the **wolf rider** (a goblin on a wolf) and the **goblin shielder** (a goblin with a shield). Each follows exactly the same rules and numbers as the matching type above.

**Archer range.** A is the archer and X is a square it can target. It cannot target its own square.

```text
X X X X X
X X X X X
X X A X X
X X X X X
X X X X X
```

**Rider charge squares.** R is the rider after two steps in the same direction. The X squares get the charge bonus and are shown in red.

```text
Straight →     Diagonal ↗
· · X          · X X
· R X          · R X
· · X          · · ·
```

## Mountains *(2026-10-19)*

Some levels have mountain squares. Both sides see where the mountains are from the start, even at night, and both sides get the same bonuses. Mountains are placed in mirror pairs, so neither side starts closer to one.

- **Entering a mountain ends that unit's move.** A rider whose first step enters a mountain takes no further step and gets no charge bonus.
- **Archer** standing on a mountain: one more ring of range, so any of the 48 squares within three steps (still not its own square).
- **Rider** that starts the turn on a mountain: one more step in its first move, so two steps in step 3 and its usual step in step 4, three in all. Every step after the first is cancelled if an enemy is in or next to the rider's square. If all three steps go in the same direction, the charge bonus is +3 instead of +2.
- **Shielder** standing on a mountain: takes 1 less damage from every hit (never below 1, see Minimum damage).
- **Sight at night:** a unit on a mountain sees one square further (see Night levels).

## Night levels *(2026-10-19)*

**Mist.** At night the board starts dark. A square is revealed once it is within 2 squares of any square one of your units has stood on, at the end of any step (3 squares when that square is a mountain). A revealed square stays revealed for the rest of the level, and you see everything on it as it happens. Mountains are always shown.

**Enemy states.** Each enemy starts **sleeping** (it stays where it is) or **patrolling** (it walks a fixed route, one step per turn). Patrolling enemies show their next step as an arrow while they stand on a revealed square. A blocked patroller stays and tries the same step next turn. Once **alarmed**, an enemy plays normally.

**Danger zones.** The attack range of every enemy is shown in red on revealed squares, even when the enemy itself is hidden in the mist. For a patrolling enemy, the zone shown is where it will stand after its next step, because that is the position the alarm check uses.

**Alarm.**

1. After the main move (step 4), a sleeping or patrolling enemy becomes alarmed if one of your units is inside its attack range. It is also alarmed when one of your units attacks it.
2. An enemy alarmed this turn does not attack this turn. It plays normally from the next turn.
3. At the end of each turn, before the win check, every alarmed enemy alarms the patrolling enemies within 2 squares of it and the sleeping enemies within 1 square. The alarm spreads one step per turn: an enemy alarmed by this spread passes it on at the end of the next turn.
4. Any enemy that attacks one of your units reveals its own square.

The AI always sees the whole board.

## Mend *(2026-10-19, player only)*

- During step 2 (Plan moves), the player may order Mend on one friendly unit. One Mend per turn, never on a unit whose Mend is still pending.
- At the end of that turn the unit glows, as a reminder.
- In step 7 of the next turn, after combat, it heals +3 HP (never above its maximum) if it is still alive. If it dies first, the use is spent.
- 2 uses per level, available from Episode 2 (see GDD.md).
- The AI never uses Mend and does not react to the glow. This is a deliberate advantage for the human player.

## The giant: the boss level *(2026-10-19; numbers and some details later)*

- **Arrival:** the giant enters as an enemy reinforcement on a later turn, on a free square of the enemy back row. That gives the player time to gather and push up the lanes first.
- **Size:** the giant and the goblin archer on its shoulder are two units that fill one square, so no other unit can enter it, share it or pass through it. The goblin attacks like a goblin archer and dies when the giant dies.
- **Movement:** every turn, at the start of step 4 (before the other units' main move), the giant moves 1 square straight along its lane toward the player's back row. Nothing can block it or contest its square. Units ordered into its new square stay where they are.
- **Push:** just before it moves, the giant hits every unit in the square in front of it, from either side. Each survivor is pushed one square back along the lane. Pushed units enter that square in attack order while there is room. A unit that does not fit, because the square is full or off the board, is destroyed at once. A pushed unit's own move this turn is cancelled.
- **Unstoppable:** the giant can only be killed. It reaches the player's back row 7 turns after it arrives, unless it dies first.
- **Win and loss:** in the boss level the player wins only by eliminating every enemy, the giant included. Reaching the enemy back row does not win, and there is no turn limit. The player still loses if any enemy, the giant included, reaches the player's back row, or by elimination.

## Win and loss

The win check runs at the end of each turn, after combat and contested moves. A side loses in any of these cases:

- **Back row:** an enemy unit is standing in its back row.
- **Elimination:** it has no soldiers left, either on the board or in reserve. This loss is immediate.
- **Turn limit:** the limit is reached and it has fewer soldiers left than the other side.

If both sides lose on the same turn, the player wins. This is a deliberate advantage for the player against the AI, to revisit if two-player mode is ever added.

The boss level replaces these win conditions with its own (see The giant).

## Numbers to tune

These are first guesses so a paper test can start. Playtesting will replace them.

| Number | First guess | Notes |
| --- | --- | --- |
| Board length | 8 columns | 5 lanes × 8 columns |
| Soldier pool per side | 12 | Split among the three types before the match |
| Reinforcements per turn | 2 | Whole pool is on the board by turn 6 |
| Health: archer / rider / shielder | 4 / 6 / 10 |  |
| Damage: archer / rider / shielder | 3 / 3 / 2 |  |
| Rider charge bonus | +2 damage | Only on the 3 charge squares |
| Strike-back damage | Full; half when at or below half health | Round down |
| Shielder arrow protection | Squaremate takes 0 (half once the shielder is at or below half health); shielder takes half | Half-health rule 2026-10-19 |
| Turn limit | 20 turns |  |
| Minimum damage per hit | 1 | 2026-10-19 |
| Mountain: archer range | +1 ring (within 3 steps) | 2026-10-19 |
| Mountain: rider first move | +1 step | Starting the turn on a mountain |
| Mountain: rider charge bonus | +3 instead of +2 | All three steps in one direction |
| Mountain: shielder damage taken | −1 per hit | Never below 1 |
| Night sight | 2 squares, 3 from a mountain | Revealed squares stay revealed |
| Alarm spread | Patrolling within 2, sleeping within 1 | One step per turn |
| Mend | +3 HP, 2 uses per level | Lands after the next turn's combat |
| Giant: speed | 1 square per turn | Agreed 2026-10-19 |
| Giant: arrival turn, HP, push damage | Later | |

## Deferred and open

**Deferred to later milestones**

- **Watch command for archers:** the archer stays and automatically fires at the first enemy entering its range. An archer with no target switches to Watch.
- Two human players. Mend and the "player wins ties" rule would both need revisiting.
- **The giant, still to settle:** arrival turn, HP, push damage, how its shield works, and whether its shoulder goblin can be hit on its own (see The giant).

**Assumptions to confirm**

- [x] The player's side is the left.
- [x] Within a side, attack order runs front to back, then top lane to bottom.
- [x] Reinforcements with no free back-row square wait in reserve until the next turn.
- [x] A shielder takes half damage from arrows itself and fully protects its squaremate.
- [x] Elimination and turn-limit ties also go to the player.

**Assumptions to confirm (2026-10-19)**

- [x] The shielder's squaremate takes 0 from arrows while the shielder is above half health, and half (at least 1) once it is at or below half health. *(Changed by the user.)*
- [x] "Each woken enemy wakes woken others within 2 squares" means alarmed enemies alarm **patrolling** enemies within 2 squares (patrollers are awake but not yet alarmed).
- [x] The alarm spreads one step per turn, not all at once.
- [x] Night sight is 2 squares (3 from a mountain), and a rider's middle square counts as a square it has stood on.
- [x] Danger zones appear only on squares that are already revealed, including the zones of enemies hidden in the mist.
- [x] A patroller's danger zone is shown at its position after its next step.
- [x] No torches: an enemy is seen only on revealed squares, but any enemy that attacks you reveals its square.
- [x] A Mend is spent if its unit dies before the heal lands.

**Assumptions to confirm (the shielder and the giant, 2026-10-19)**

- [x] The shielder's half-health check is made before the arrow lands. All units in the square are hit at the same moment.
- [x] The giant's push hits and pushes units of either side, its own goblins included.
- [x] The giant moves at the start of step 4, before the other units' main move, so a rider's early first step (step 3) can still dodge it.
- [x] A pushed unit's own move is cancelled, and pushed units enter the square behind in attack order.
- [x] Riders and shielders strike back against the push hit, as against any hit from an adjacent enemy.
- [x] In the boss level the player cannot win by reaching the enemy back row (elimination only), but still loses if the giant or any enemy reaches the player's back row.
