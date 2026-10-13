extends SceneTree
## Exhaustive analysis of rule variants (analysis only; the slice defaults are not changed).
## godot --headless --path godot --script res://tests/analyze_variants.gd
##
## Search: breadth-first by turn over every player order (9 moves, then hold fire or any valid
## target), merging identical board states and carrying the number of order sequences that reach
## each one. Enemy orders are the deterministic AI, so every complete player order sequence ends
## in exactly one result. Counts are floats (exact below 2^53).

const RulesScript = preload("res://game/rules.gd")

const MOVES: Array[Vector2i] = [
	Vector2i(-1, -1), Vector2i(0, -1), Vector2i(1, -1),
	Vector2i(-1, 0), Vector2i(0, 0), Vector2i(1, 0),
	Vector2i(-1, 1), Vector2i(0, 1), Vector2i(1, 1),
]

const TWO: Array[Dictionary] = RulesScript.TWO_ENEMY_UNITS

## V4 is the slice default since 2026-10-12; the others are selected through Rules config.
var VARIANTS: Array[Dictionary] = [
	{"id": "V0", "label": "earlier setup: player HP 4, 2 marching enemies (lanes 2 & 4), order slots = all living units", "cfg": {"units": TWO}},
	{"id": "V0b", "label": "V0 but attack-order slots only for units that have a target", "cfg": {"units": TWO, "attack_order_mode": "with_target"}},
	{"id": "V1", "label": "V0 with player HP 6", "cfg": {"units": TWO, "player_hp": 6}},
	{"id": "V2", "label": "V0 with player HP 7", "cfg": {"units": TWO, "player_hp": 7}},
	{"id": "V3", "label": "V0 with enemy damage 2 (player HP 4)", "cfg": {"units": TWO, "enemy_damage": 2}},
	{"id": "V4", "label": "SLICE DEFAULT: one marching enemy only (lane 4)", "cfg": {}},
	{"id": "V5", "label": "V0 but the lane-2 enemy guards col 7; lane-4 enemy marches", "cfg": {"units": TWO, "enemy_ai": {"e1": "guard"}}},
	{"id": "V6", "label": "V0 but both enemies guard col 7", "cfg": {"units": TWO, "enemy_ai": {"e1": "guard", "e2": "guard"}}},
]


func _initialize() -> void:
	var t0: int = Time.get_ticks_msec()
	var results: Array[Dictionary] = []
	for v: Dictionary in VARIANTS:
		var a: Dictionary = analyze(v["cfg"])
		a["id"] = v["id"]
		a["label"] = v["label"]
		a["naive_forward_lane5"] = naive(v["cfg"], Vector2i(1, 0))
		a["stay_and_shoot"] = naive(v["cfg"], Vector2i.ZERO)
		a["real_timing_decision"] = a["clean_win_possible"] and a["naive_forward_lane5"]["result"] == "lost" \
			and a["stay_and_shoot"]["result"] == "lost"
		results.append(a)
		print_row(a)
		for cat: String in a["example_routes"]:
			var ex: Dictionary = a["example_routes"][cat]
			print("     example %s (turn %d): %s" % [cat, ex["turn"], JSON.stringify(ex["route"])])
	var unix: int = int(Time.get_unix_time_from_system())
	var dir: String = ProjectSettings.globalize_path("res://").path_join("../evidence").simplify_path()
	DirAccess.make_dir_recursive_absolute(dir)
	var path: String = dir.path_join("analyze_variants-%d.json" % unix)
	var f: FileAccess = FileAccess.open(path, FileAccess.WRITE)
	f.store_string(JSON.stringify({
		"report": "analyze_variants",
		"unix_time": unix,
		"engine": Engine.get_version_info().get("string", ""),
		"method": "BFS by turn over all player orders (9 moves x [hold fire + each valid target]); identical states merged with sequence counts; enemy orders from the AI. 'tie' = won only because ties go to the player (both lost the same turn, or equal pieces at the turn limit). Naive routes shoot the first valid target (top lane first).",
		"seconds": (Time.get_ticks_msec() - t0) / 1000.0,
		"variants": results,
	}, "\t"))
	f.close()
	print("wrote ", path)
	quit(0)


func _make(units: Array, turn: int, cfg: Dictionary) -> RulesScript:
	var r: RulesScript = RulesScript.new()
	r.setup(units, turn, cfg)
	return r


static func _units_of(r: RulesScript) -> Array:
	var out: Array = []
	for u: Dictionary in r.units:
		out.append({"id": u["id"], "team": u["team"], "col": u["col"], "lane": u["lane"], "hp": u["hp"]})
	return out


static func _key(r: RulesScript) -> String:
	var parts: PackedStringArray = PackedStringArray()
	for u: Dictionary in r.units:
		parts.append("%d,%d,%d" % [u["col"], u["lane"], u["hp"]])
	return "|".join(parts)


static func _category(r: RulesScript, res: Dictionary) -> String:
	if bool(res["tie"]):
		return "tie_turn_limit" if String(res["kind"]) == "turn_limit" else "tie_same_turn"
	match String(res["kind"]):
		"back_row":
			return "back_row"
		"elimination":
			return "elimination"
	return "turn_limit_more"


func analyze(cfg: Dictionary) -> Dictionary:
	var r0: RulesScript = RulesScript.new()
	r0.reset(cfg)
	var frontier: Dictionary = {_key(r0): {"units": _units_of(r0), "count": 1.0, "route": []}}
	var wins: Dictionary = {"back_row": 0.0, "elimination": 0.0, "tie_same_turn": 0.0, "tie_turn_limit": 0.0, "turn_limit_more": 0.0}
	var examples: Dictionary = {}
	var losses: float = 0.0
	var earliest_win: int = -1
	var earliest_clean: int = -1
	var max_states: int = 1
	var expansions: int = 0
	for turn: int in range(1, RulesScript.TURN_LIMIT + 1):
		var nf: Dictionary = {}
		for k: String in frontier:
			var entry: Dictionary = frontier[k]
			var cnt: float = entry["count"]
			for mv: Vector2i in MOVES:
				var base: RulesScript = _make(entry["units"], turn, cfg)
				var here: Vector2i = RulesScript.cell_of(base.get_unit("p1"))
				if not RulesScript.on_board(here + mv):
					continue
				base.resolve_moves({"p1": mv})
				var moved: Array = _units_of(base)
				var options: Array = [null]
				options.append_array(base.valid_targets("p1"))
				for t: Variant in options:
					expansions += 1
					var r: RulesScript = _make(moved, turn, cfg)
					r.phase = "attack"
					r.resolve_attacks({"p1": t} if t != null else {})
					var res: Dictionary = r.end_turn()
					var step: Array = [mv.x, mv.y, null if t == null else [t.x, t.y]]
					if res["result"] == "won":
						var cat: String = _category(r, res)
						wins[cat] = float(wins[cat]) + cnt
						if earliest_win < 0:
							earliest_win = turn
						if not cat.begins_with("tie") and earliest_clean < 0:
							earliest_clean = turn
						if not examples.has(cat):
							var route: Array = (entry["route"] as Array).duplicate()
							route.append(step)
							examples[cat] = {"turn": turn, "route": route, "reason": res["reason"]}
					elif res["result"] == "lost":
						losses += cnt
					else:
						var nk: String = _key(r)
						if nf.has(nk):
							nf[nk]["count"] = float(nf[nk]["count"]) + cnt
						else:
							var route2: Array = (entry["route"] as Array).duplicate()
							route2.append(step)
							nf[nk] = {"units": _units_of(r), "count": cnt, "route": route2}
		frontier = nf
		max_states = maxi(max_states, frontier.size())
		if frontier.is_empty():
			break
	var total_wins: float = 0.0
	for c: String in wins:
		total_wins += float(wins[c])
	var clean: float = float(wins["back_row"]) + float(wins["elimination"]) + float(wins["turn_limit_more"])
	return {
		"clean_win_possible": clean > 0.0,
		"winning_sequences": total_wins,
		"wins_by_kind": wins,
		"losing_sequences": losses,
		"total_sequences": total_wins + losses,
		"win_fraction": total_wins / maxf(1.0, total_wins + losses),
		"earliest_win_turn": earliest_win,
		"earliest_clean_win_turn": earliest_clean,
		"example_routes": examples,
		"max_states_per_turn": max_states,
		"expansions": expansions,
		"counts_exact": total_wins + losses < 9007199254740992.0,
	}


## A fixed policy: every turn move by `step` (stay if off-board) and shoot the first valid target.
func naive(cfg: Dictionary, step: Vector2i) -> Dictionary:
	var r: RulesScript = RulesScript.new()
	r.reset(cfg)
	var res: Dictionary = {"result": "none"}
	while r.result == "none":
		var here: Vector2i = RulesScript.cell_of(r.get_unit("p1"))
		r.resolve_moves({"p1": step if RulesScript.on_board(here + step) else Vector2i.ZERO})
		var vt: Array[Vector2i] = r.valid_targets("p1")
		r.resolve_attacks({"p1": vt[0]} if not vt.is_empty() else {})
		res = r.end_turn()
	return {"result": res["result"], "kind": res["kind"], "tie": res["tie"], "turn": res["turn"], "reason": res["reason"]}


func print_row(a: Dictionary) -> void:
	var w: Dictionary = a["wins_by_kind"]
	print("%-4s clean=%-5s wins=%d (back_row %d, elim %d, tie-same-turn %d, tie-turn-limit %d) / %d seqs  earliest=%d clean_earliest=%d  forward=%s(%s,t%d)  stay=%s(%s,t%d)  timing=%s" % [
		a["id"], a["clean_win_possible"], int(a["winning_sequences"]), int(w["back_row"]), int(w["elimination"]),
		int(w["tie_same_turn"]), int(w["tie_turn_limit"]), int(a["total_sequences"]), a["earliest_win_turn"], a["earliest_clean_win_turn"],
		a["naive_forward_lane5"]["result"], a["naive_forward_lane5"]["kind"], a["naive_forward_lane5"]["turn"],
		a["stay_and_shoot"]["result"], a["stay_and_shoot"]["kind"], a["stay_and_shoot"]["turn"], a["real_timing_decision"]])
