# Lane Tactics — Rules Draft

Oct 9, 2026 · @Stark

Two armies fight across a 5-lane board. Both sides plan in secret at the same time, then the turn plays out. Get one soldier into the enemy's back row and keep it alive to the end of a turn to win. "Lane Tactics" is a working title, and every number is a placeholder for playtesting.

## Board and army

The board has 5 horizontal lanes, like Plants vs Zombies. The player's army starts on the left and the AI's on the right. Each side's **back row** is the 5 squares along its own edge.

- A square holds at most 2 units: two allies, two enemies, or one of each.
- Before the match, each side gets a fixed pool of soldiers and chooses how many archers, riders and shielders it has.
- At the start of every turn, each side receives a set number of new soldiers. The player picks their types from what is left in the pool and places each one on a free square of their own back row.
- The AI follows the same rules.

## Turn sequence

Every turn runs the same eight steps. Both sides plan at the same time and cannot see each other's orders.

1. **Reinforce:** both sides place their new soldiers on their own back row.
2. **Plan moves:** both sides give every unit a move order. A unit with no order stays.
3. **Riders' first step:** every rider on both sides takes its first step.
4. **Main move:** all other units move, and riders take their second step.
5. **Plan attacks:** both sides choose a target square for every unit that has one in reach.
6. **Combat:** melee and archer attacks resolve together, one unit at a time, in attack order.
7. **Settle contested moves:** surviving units that were waiting to enter a full square move in.
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

### Strike back

Riders and shielders strike back every time an adjacent enemy hits them. Units in the same square count as adjacent.

- **Against melee:** the attack and the strike back land at the same moment. A defender killed by the hit still strikes back.
- **Against an adjacent archer:** the arrow lands first. The defender strikes back only if it survives.
- At half health or below, measured after the hit, the strike back does reduced damage.
- Archers never strike back. Nobody strikes back against arrows from two squares away or against their own side.

### Rider charge

If a rider's two steps go in the same direction, it gets bonus damage when attacking one of the 3 squares in that direction. Those squares are shown in red (see Units).

## Units

The three types are meant to counter each other: shielders block arrows, riders break through shielder lines, and archers punish riders.

| Unit | Movement | Attack | Strikes back | Role |
| --- | --- | --- | --- | --- |
| Archer | 1 square | Any of the 24 squares within two steps; hits every unit in the square | Never | Ranged damage, fragile |
| Rider | 2 steps, first step before other units | Adjacent; charge bonus after 2 steps in the same direction | Yes | Fast flanker |
| Shielder | 1 square | Adjacent, low damage | Yes | High health; blocks arrows for the allied unit in its square |

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

## Win and loss

The win check runs at the end of each turn, after combat and contested moves. A side loses in any of these cases:

- **Back row:** an enemy unit is standing in its back row.
- **Elimination:** it has no soldiers left, either on the board or in reserve. This loss is immediate.
- **Turn limit:** the limit is reached and it has fewer soldiers left than the other side.

If both sides lose on the same turn, the player wins. This is a deliberate advantage for the player against the AI, to revisit if two-player mode is ever added.

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
| Shielder arrow protection | Squaremate takes 0; shielder takes half |  |
| Turn limit | 20 turns |  |

## Deferred and open

**Deferred to later milestones**

- **Watch command for archers:** the archer stays and automatically fires at the first enemy entering its range. An archer with no target switches to Watch.
- Two human players.

**Assumptions to confirm**

- [x] The player's side is the left.
- [x] Within a side, attack order runs front to back, then top lane to bottom.
- [x] Reinforcements with no free back-row square wait in reserve until the next turn.
- [x] A shielder takes half damage from arrows itself and fully protects its squaremate.
- [x] Elimination and turn-limit ties also go to the player.
