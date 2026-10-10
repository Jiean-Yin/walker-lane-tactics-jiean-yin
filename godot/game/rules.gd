class_name Rules
extends RefCounted
## Lane Tactics asset-slice rules: pure data, deterministic, no nodes, no audio.
##
## Board: 8 columns (0 = player back row, 7 = enemy back row) x 5 lanes (0 = top).
## A turn is: resolve_moves() -> resolve_attacks() -> end_turn().
## Every call returns plain events; the scene only plays them back.

const COLS: int = 8
const LANES: int = 5
const MAX_PER_SQUARE: int = 2
const ARCHER_HP: int = 4
const ARCHER_DAMAGE: int = 3
const ARCHER_MIN_RANGE: int = 1
const ARCHER_MAX_RANGE: int = 2
const TURN_LIMIT: int = 20
const PLAYER: String = "player"
const ENEMY: String = "enemy"
const PLAYER_BACK_COL: int = 0
const ENEMY_BACK_COL: int = COLS - 1

## "move" -> "attack" -> "end" -> ("move" of the next turn | "over")
var phase: String = "move"
var turn: int = 1
var result: String = "none"
var result_kind: String = ""
var reason: String = ""
var hits_landed: int = 0
var units: Array[Dictionary] = []

var _attack_serial: int = 0
var _last_player_killer: String = ""


func _init() -> void:
	reset()


## Slice start: player archer at col 0 lane 4; enemy archers at col 7 lanes 1 and 3.
func reset() -> void:
	setup([
		{"id": "p1", "team": PLAYER, "col": 0, "lane": 4},
		{"id": "e1", "team": ENEMY, "col": 7, "lane": 1},
		{"id": "e2", "team": ENEMY, "col": 7, "lane": 3},
	], 1)


## Custom setup (used by tests). Each entry needs id, team, col, lane; hp and facing are optional.
func setup(unit_list: Array, start_turn: int = 1) -> void:
	units.clear()
	for entry: Dictionary in unit_list:
		var team: String = entry["team"]
		units.append({
			"id": String(entry["id"]),
			"team": team,
			"col": int(entry["col"]),
			"lane": int(entry["lane"]),
			"hp": int(entry.get("hp", ARCHER_HP)),
			"facing": int(entry.get("facing", 1 if team == PLAYER else -1)),
		})
	turn = start_turn
	phase = "move"
	result = "none"
	result_kind = ""
	reason = ""
	hits_landed = 0
	_attack_serial = 0
	_last_player_killer = ""


# ---------------------------------------------------------------- queries

static func cell_of(u: Dictionary) -> Vector2i:
	return Vector2i(int(u["col"]), int(u["lane"]))


static func on_board(c: Vector2i) -> bool:
	return c.x >= 0 and c.x < COLS and c.y >= 0 and c.y < LANES


static func distance(a: Vector2i, b: Vector2i) -> int:
	return maxi(absi(a.x - b.x), absi(a.y - b.y))


## Archer reach: the 24 squares of the 5x5 around it (Chebyshev 1..2), never its own square.
static func in_range(from: Vector2i, to: Vector2i) -> bool:
	var d: int = distance(from, to)
	return d >= ARCHER_MIN_RANGE and d <= ARCHER_MAX_RANGE


static func other_team(team: String) -> String:
	return ENEMY if team == PLAYER else PLAYER


func get_unit(id: String) -> Dictionary:
	for u: Dictionary in units:
		if u["id"] == id:
			return u
	return {}


func is_alive(id: String) -> bool:
	var u: Dictionary = get_unit(id)
	return not u.is_empty() and int(u["hp"]) > 0


func alive_units(team: String = "") -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for u: Dictionary in units:
		if int(u["hp"]) > 0 and (team == "" or u["team"] == team):
			out.append(u)
	return out


func units_at(c: Vector2i, include_dead: bool = false) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for u: Dictionary in units:
		if (include_dead or int(u["hp"]) > 0) and cell_of(u) == c:
			out.append(u)
	return out


## The side that strikes first: the player on turn 1, then it alternates.
func first_side() -> String:
	return PLAYER if turn % 2 == 1 else ENEMY


## Destination squares for a unit: its own square (stay) plus the on-board squares of the 8 around it.
func legal_moves(unit_id: String) -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	var u: Dictionary = get_unit(unit_id)
	if u.is_empty() or int(u["hp"]) <= 0:
		return out
	var here: Vector2i = cell_of(u)
	for dl: int in [-1, 0, 1]:
		for dc: int in [-1, 0, 1]:
			var c: Vector2i = here + Vector2i(dc, dl)
			if on_board(c):
				out.append(c)
	return out


## On-board squares an archer can reach from where it stands (24 in open board).
func range_cells(unit_id: String) -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	var u: Dictionary = get_unit(unit_id)
	if u.is_empty():
		return out
	var here: Vector2i = cell_of(u)
	for dl: int in range(-ARCHER_MAX_RANGE, ARCHER_MAX_RANGE + 1):
		for dc: int in range(-ARCHER_MAX_RANGE, ARCHER_MAX_RANGE + 1):
			var c: Vector2i = here + Vector2i(dc, dl)
			if on_board(c) and in_range(here, c):
				out.append(c)
	return out


## Range squares that hold at least one living enemy of the unit, top lane first then left to right.
func valid_targets(unit_id: String) -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	var u: Dictionary = get_unit(unit_id)
	if u.is_empty() or int(u["hp"]) <= 0:
		return out
	var foe: String = other_team(u["team"])
	for c: Vector2i in range_cells(unit_id):
		for v: Dictionary in units_at(c):
			if v["team"] == foe:
				out.append(c)
				break
	return out


## Enemy move AI, decided from positions at the start of planning:
## a player unit in range -> stay; otherwise step 1 column toward column 0 in its own lane.
func enemy_orders() -> Dictionary:
	var orders: Dictionary = {}
	var players: Array[Dictionary] = alive_units(PLAYER)
	for e: Dictionary in alive_units(ENEMY):
		var sees_player: bool = false
		for p: Dictionary in players:
			if in_range(cell_of(e), cell_of(p)):
				sees_player = true
				break
		var step: Vector2i = Vector2i.ZERO if sees_player else Vector2i(-1, 0)
		if not on_board(cell_of(e) + step):
			step = Vector2i.ZERO
		orders[e["id"]] = step
	return orders


## Enemy attack AI: shoot the player's square if it is a valid target.
func enemy_targets() -> Dictionary:
	var targets: Dictionary = {}
	for e: Dictionary in alive_units(ENEMY):
		var options: Array[Vector2i] = valid_targets(e["id"])
		for p: Dictionary in alive_units(PLAYER):
			if options.has(cell_of(p)):
				targets[e["id"]] = cell_of(p)
				break
	return targets


## Combat order over every living unit: sides alternate one unit at a time, starting with first_side();
## within a side front to back (closest to the enemy first), then top lane to bottom.
## A unit with no target still holds its place in the order (it simply does not attack).
func attack_order() -> Array[String]:
	var players: Array[Dictionary] = alive_units(PLAYER)
	var enemies: Array[Dictionary] = alive_units(ENEMY)
	players.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		if a["col"] != b["col"]:
			return int(a["col"]) > int(b["col"])
		if a["lane"] != b["lane"]:
			return int(a["lane"]) < int(b["lane"])
		return String(a["id"]) < String(b["id"]))
	enemies.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		if a["col"] != b["col"]:
			return int(a["col"]) < int(b["col"])
		if a["lane"] != b["lane"]:
			return int(a["lane"]) < int(b["lane"])
		return String(a["id"]) < String(b["id"]))
	var sides: Array = [players, enemies] if first_side() == PLAYER else [enemies, players]
	var out: Array[String] = []
	var n: int = maxi(players.size(), enemies.size())
	for i: int in n:
		for side: Array in sides:
			if i < side.size():
				out.append(String(side[i]["id"]))
	return out


# ---------------------------------------------------------------- turn steps

## Simultaneous moves. player_orders: unit id -> Vector2i offset (each axis in -1..1).
## Illegal or missing orders mean "stay". Enemy orders come from enemy_orders().
## Returns one {type:"moved"} event per unit whose square changed.
func resolve_moves(player_orders: Dictionary) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	if phase != "move":
		push_error("Rules.resolve_moves called in phase '%s'" % phase)
		return events
	var orders: Dictionary = enemy_orders()
	for id: Variant in player_orders:
		var u: Dictionary = get_unit(String(id))
		if u.is_empty() or u["team"] != PLAYER or int(u["hp"]) <= 0:
			continue
		if typeof(player_orders[id]) != TYPE_VECTOR2I:
			continue
		var off: Vector2i = player_orders[id]
		if absi(off.x) <= 1 and absi(off.y) <= 1 and on_board(cell_of(u) + off):
			orders[u["id"]] = off
	var movers: Array[Dictionary] = alive_units()
	var dest: Dictionary = {}
	for u: Dictionary in movers:
		dest[u["id"]] = cell_of(u) + (orders.get(u["id"], Vector2i.ZERO) as Vector2i)
	# Square capacity: a unit entering an over-full square stays where it was.
	# (Cannot happen in the slice; kept so the data stays valid.)
	var changed: bool = true
	while changed:
		changed = false
		var counts: Dictionary = {}
		for id: Variant in dest:
			counts[dest[id]] = int(counts.get(dest[id], 0)) + 1
		for u: Dictionary in movers:
			var d: Vector2i = dest[u["id"]]
			if int(counts[d]) > MAX_PER_SQUARE and d != cell_of(u):
				dest[u["id"]] = cell_of(u)
				changed = true
	for u: Dictionary in movers:
		var from: Vector2i = cell_of(u)
		var to: Vector2i = dest[u["id"]]
		if to == from:
			continue
		if to.x != from.x:
			u["facing"] = 1 if to.x > from.x else -1
		u["col"] = to.x
		u["lane"] = to.y
		events.append({"type": "moved", "unit": u["id"], "team": u["team"], "from": from, "to": to})
	phase = "attack"
	return events


## Combat. player_targets: unit id -> Vector2i target square (must be in valid_targets()).
## Events: attack {unit, target}; damaged {unit, by, amount, hp_after} for EVERY unit in the square
## (friendly fire included); killed; attack_cancelled when the square has no enemy left.
## All events of one shot share the same "attack" key.
func resolve_attacks(player_targets: Dictionary) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	if phase != "attack":
		push_error("Rules.resolve_attacks called in phase '%s'" % phase)
		return events
	var targets: Dictionary = enemy_targets()
	for id: Variant in player_targets:
		var u: Dictionary = get_unit(String(id))
		if u.is_empty() or u["team"] != PLAYER or int(u["hp"]) <= 0:
			continue
		if typeof(player_targets[id]) != TYPE_VECTOR2I:
			continue # null = hold fire
		var t: Vector2i = player_targets[id]
		if valid_targets(u["id"]).has(t):
			targets[u["id"]] = t
	for id: String in attack_order():
		var u: Dictionary = get_unit(id)
		if int(u["hp"]) <= 0:
			continue # killed before its turn: no attack
		if not targets.has(id):
			continue
		var target: Vector2i = targets[id]
		_attack_serial += 1
		var key: String = "%d:%d" % [turn, _attack_serial]
		if target.x != int(u["col"]):
			u["facing"] = 1 if target.x > int(u["col"]) else -1
		var foe: String = other_team(u["team"])
		var has_foe: bool = false
		for v: Dictionary in units_at(target):
			if v["team"] == foe:
				has_foe = true
		if not has_foe:
			events.append({"type": "attack_cancelled", "unit": id, "team": u["team"], "target": target, "attack": key})
			continue
		events.append({"type": "attack", "unit": id, "team": u["team"], "target": target, "attack": key})
		for v: Dictionary in units_at(target):
			v["hp"] = maxi(0, int(v["hp"]) - ARCHER_DAMAGE)
			events.append({"type": "damaged", "unit": v["id"], "team": v["team"], "by": id, "by_team": u["team"],
				"amount": ARCHER_DAMAGE, "hp_after": v["hp"], "attack": key})
			if u["team"] == PLAYER and v["team"] == ENEMY:
				hits_landed += 1
			if int(v["hp"]) == 0:
				events.append({"type": "killed", "unit": v["id"], "team": v["team"], "by": id, "by_team": u["team"], "attack": key})
				if v["team"] == PLAYER:
					_last_player_killer = id
	phase = "end"
	return events


## Win check at the end of the turn. Returns {result: "none"|"won"|"lost", kind, reason, turn}.
## If both sides lose on the same turn, the player wins.
func end_turn() -> Dictionary:
	if phase != "end":
		push_error("Rules.end_turn called in phase '%s'" % phase)
		return {"result": result, "kind": result_kind, "reason": reason, "turn": turn}
	var players: Array[Dictionary] = alive_units(PLAYER)
	var enemies: Array[Dictionary] = alive_units(ENEMY)
	var enemy_in_player_back: Dictionary = {}
	for e: Dictionary in enemies:
		if int(e["col"]) == PLAYER_BACK_COL:
			enemy_in_player_back = e
			break
	var player_in_enemy_back: bool = false
	for p: Dictionary in players:
		if int(p["col"]) == ENEMY_BACK_COL:
			player_in_enemy_back = true
	var player_lost: bool = players.is_empty() or not enemy_in_player_back.is_empty()
	var enemy_lost: bool = enemies.is_empty() or player_in_enemy_back
	if enemy_lost:
		result = "won"
		if enemies.is_empty():
			result_kind = "elimination"
			reason = "both enemies defeated"
		else:
			result_kind = "back_row"
			reason = "back row reached"
		if player_lost:
			reason += " (both sides lost this turn; ties go to the player)"
	elif player_lost:
		result = "lost"
		if players.is_empty():
			result_kind = "shot"
			var killer: Dictionary = get_unit(_last_player_killer)
			var lane_shown: int = int(killer.get("lane", 0)) + 1
			reason = "shot by the enemy archer in lane %d" % lane_shown
		else:
			result_kind = "enemy_back_row"
			reason = "an enemy archer reached your back row in lane %d" % (int(enemy_in_player_back["lane"]) + 1)
	elif turn >= TURN_LIMIT:
		result_kind = "turn_limit"
		if players.size() < enemies.size():
			result = "lost"
			reason = "turn limit reached with fewer pieces"
		else:
			result = "won"
			reason = "turn limit reached; you hold as many pieces or more (ties go to you)"
	if result == "none":
		turn += 1
		phase = "move"
	else:
		phase = "over"
	return {"result": result, "kind": result_kind, "reason": reason, "turn": turn}


## Plain-data copy of the whole state, for test comparison.
func snapshot() -> Dictionary:
	var us: Array = []
	for u: Dictionary in units:
		us.append({"id": u["id"], "team": u["team"], "col": u["col"], "lane": u["lane"], "hp": u["hp"], "facing": u["facing"]})
	return {
		"turn": turn,
		"phase": phase,
		"result": result,
		"result_kind": result_kind,
		"reason": reason,
		"hits_landed": hits_landed,
		"units": us,
	}
