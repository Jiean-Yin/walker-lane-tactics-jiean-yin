extends SceneTree
## Headless rules tests: godot --headless --path godot --script res://tests/test_rules.gd

const RulesScript = preload("res://game/rules.gd")
const Runner = preload("res://tests/route_runner.gd")
const Report = preload("res://tests/test_report.gd")

var rep: Report


func _initialize() -> void:
	rep = Report.new("test_rules")
	_run()
	var win: Dictionary = Runner.load_route("res://tests/fixtures/win_route.json")
	quit(rep.finish({"win_route": win.get("turns", [])}))


func _mk(units: Array, turn: int = 1) -> RulesScript:
	var r: RulesScript = RulesScript.new()
	r.setup(units, turn)
	return r


func _types(events: Array) -> Array[String]:
	var out: Array[String] = []
	for e: Dictionary in events:
		out.append(String(e["type"]))
	return out


func _count(events: Array, type: String, field: String = "", value: Variant = null) -> int:
	var n: int = 0
	for e: Dictionary in events:
		if e["type"] == type and (field == "" or e.get(field) == value):
			n += 1
	return n


func _run() -> void:
	# --- setup
	var r: RulesScript = RulesScript.new()
	var p: Dictionary = r.get_unit("p1")
	rep.check("setup: player archer at col 0 lane 4, hp 4, facing right",
		p["col"] == 0 and p["lane"] == 4 and p["hp"] == 4 and p["facing"] == 1, p)
	var e1: Dictionary = r.get_unit("e1")
	rep.check("setup: exactly one enemy archer, at col 7 lane 3 (shown lane 4), hp 4, facing left",
		r.units.size() == 2 and r.alive_units("enemy").size() == 1 and e1["col"] == 7 and e1["lane"] == 3
		and e1["hp"] == 4 and e1["facing"] == -1, r.units)
	rep.check("setup: default config (HP 4, damage 3, all living units hold attack slots, enemy marches)",
		r.config["player_hp"] == 4 and r.config["enemy_hp"] == 4 and r.config["player_damage"] == 3
		and r.config["enemy_damage"] == 3 and r.config["attack_order_mode"] == "all_living" and (r.config["enemy_ai"] as Dictionary).is_empty(), r.config)
	rep.check("setup: turn 1, player strikes first", r.turn == 1 and r.first_side() == "player")

	# --- legal moves
	var corner: Array[Vector2i] = r.legal_moves("p1")
	rep.check("legal moves from corner (0,4): stay + 3 on-board neighbours", corner.size() == 4
		and corner.has(Vector2i(0, 4)) and corner.has(Vector2i(1, 4)) and corner.has(Vector2i(0, 3)) and corner.has(Vector2i(1, 3)), corner)
	var mid: RulesScript = _mk([{"id": "p1", "team": "player", "col": 3, "lane": 2}, {"id": "e1", "team": "enemy", "col": 7, "lane": 0}])
	var mm: Array[Vector2i] = mid.legal_moves("p1")
	var all8: bool = mm.size() == 9
	for dl: int in [-1, 0, 1]:
		for dc: int in [-1, 0, 1]:
			all8 = all8 and mm.has(Vector2i(3 + dc, 2 + dl))
	rep.check("legal moves in open board: stay + all 8 directions", all8, mm)
	var off: RulesScript = RulesScript.new()
	var off_ev: Array[Dictionary] = off.resolve_moves({"p1": Vector2i(-1, 1)})
	rep.check("off-board order is treated as stay", off.get_unit("p1")["col"] == 0 and off.get_unit("p1")["lane"] == 4
		and _count(off_ev, "moved", "unit", "p1") == 0)
	var bad: RulesScript = RulesScript.new()
	bad.resolve_moves({"p1": Vector2i(2, 0)})
	rep.check("order longer than 1 square is treated as stay", bad.get_unit("p1")["col"] == 0)

	# --- archer range
	var rc: Array[Vector2i] = mid.range_cells("p1")
	var ring_ok: bool = rc.size() == 24 and not rc.has(Vector2i(3, 2))
	for c: Vector2i in rc:
		ring_ok = ring_ok and RulesScript.distance(c, Vector2i(3, 2)) >= 1 and RulesScript.distance(c, Vector2i(3, 2)) <= 2
	rep.check("archer range = 24 squares of the 5x5, own square excluded", ring_ok, rc.size())
	rep.check("range clipped at the corner (0,4): 8 squares", r.range_cells("p1").size() == 8, r.range_cells("p1").size())
	rep.check("valid targets: empty squares excluded (no enemy in reach)", mid.valid_targets("p1").is_empty())
	var tgt: RulesScript = _mk([
		{"id": "p1", "team": "player", "col": 3, "lane": 2},
		{"id": "p2", "team": "player", "col": 4, "lane": 2},
		{"id": "e1", "team": "enemy", "col": 5, "lane": 4},
		{"id": "e2", "team": "enemy", "col": 3, "lane": 2},
		{"id": "e3", "team": "enemy", "col": 6, "lane": 2},
	])
	var vt: Array[Vector2i] = tgt.valid_targets("p1")
	rep.check("valid targets: enemy squares in range only (not own square, not ally square, not out of range)",
		vt == [Vector2i(5, 4)], vt)
	var e_vt: Array[Vector2i] = tgt.valid_targets("e3")
	rep.check("enemy valid targets hold a player unit", e_vt == [Vector2i(4, 2)], e_vt)

	# --- friendly fire
	var ff: RulesScript = _mk([
		{"id": "p1", "team": "player", "col": 3, "lane": 2},
		{"id": "e1", "team": "enemy", "col": 3, "lane": 2},
		{"id": "e2", "team": "enemy", "col": 5, "lane": 2},
	], 2)
	ff.resolve_moves({})
	rep.check("enemy beside the player stays (in range) and the squaremate does not count as in range",
		ff.get_unit("e2")["col"] == 5 and ff.get_unit("e1")["col"] == 2, [ff.get_unit("e1"), ff.get_unit("e2")])
	# reset to an exact shared square for the shot
	ff = _mk([
		{"id": "p1", "team": "player", "col": 3, "lane": 2},
		{"id": "e1", "team": "enemy", "col": 3, "lane": 2},
		{"id": "e2", "team": "enemy", "col": 5, "lane": 2},
	], 2)
	ff.phase = "attack"
	var ffe: Array[Dictionary] = ff.resolve_attacks({})
	rep.check("friendly fire: one arrow damages every unit in the square (player and enemy squaremate)",
		_count(ffe, "attack") == 1 and _count(ffe, "damaged") == 2 and ff.get_unit("p1")["hp"] == 1 and ff.get_unit("e1")["hp"] == 1, _types(ffe))
	var keys: Dictionary = {}
	for e: Dictionary in ffe:
		if e["type"] == "damaged":
			keys[e["attack"]] = true
	rep.check("friendly fire: both damaged events share one attack key", keys.size() == 1)
	rep.check("squaremate enemy cannot shoot its own square", _count(ffe, "attack", "unit", "e1") == 0)

	# --- attack order
	var ao: RulesScript = _mk([
		{"id": "p1", "team": "player", "col": 2, "lane": 2},
		{"id": "p2", "team": "player", "col": 3, "lane": 4},
		{"id": "e1", "team": "enemy", "col": 5, "lane": 3},
		{"id": "e2", "team": "enemy", "col": 4, "lane": 0},
		{"id": "e3", "team": "enemy", "col": 4, "lane": 1},
	], 1)
	var o1: Array[String] = ao.attack_order()
	rep.check("attack order turn 1: player first, alternate, front to back then top lane first",
		o1 == ["p2", "e2", "p1", "e3", "e1"], o1)
	ao.turn = 2
	var o2: Array[String] = ao.attack_order()
	rep.check("attack order turn 2: enemy first", o2 == ["e2", "p2", "e3", "p1", "e1"], o2)
	ao.turn = 3
	rep.check("first side switches every turn (turn 3 = player)", ao.first_side() == "player" and ao.attack_order()[0] == "p2")

	# --- killed before its turn / attack_cancelled
	var kb: RulesScript = _mk([
		{"id": "p1", "team": "player", "col": 3, "lane": 2, "hp": 3},
		{"id": "e1", "team": "enemy", "col": 4, "lane": 1},
		{"id": "e2", "team": "enemy", "col": 5, "lane": 2},
	], 2)
	kb.phase = "attack"
	var kbe: Array[Dictionary] = kb.resolve_attacks({"p1": Vector2i(5, 2)})
	rep.check("killed before its turn: the player does not attack", _count(kbe, "attack", "unit", "p1") == 0
		and _count(kbe, "killed", "unit", "p1") == 1 and kb.get_unit("e2")["hp"] == 4, _types(kbe))
	rep.check("attack_cancelled when the target square has no enemy left", _count(kbe, "attack_cancelled", "unit", "e2") == 1, _types(kbe))
	var kbr: Dictionary = kb.end_turn()
	rep.check("loss by elimination of the player names the shooter's lane",
		kbr["result"] == "lost" and kbr["kind"] == "shot" and kbr["reason"] == "shot by the enemy archer in lane 2", kbr)
	var kills: RulesScript = _mk([
		{"id": "p1", "team": "player", "col": 3, "lane": 2},
		{"id": "e1", "team": "enemy", "col": 5, "lane": 2, "hp": 3},
	], 1)
	kills.phase = "attack"
	var ke: Array[Dictionary] = kills.resolve_attacks({"p1": Vector2i(5, 2)})
	rep.check("player striking first kills a 3-HP enemy before it shoots", _types(ke) == ["attack", "damaged", "killed"], _types(ke))
	rep.check("damaged event carries by, amount 3 and hp_after", ke[1]["by"] == "p1" and ke[1]["amount"] == 3 and ke[1]["hp_after"] == 0, ke[1])
	var kr: Dictionary = kills.end_turn()
	rep.check("win by elimination", kr["result"] == "won" and kr["kind"] == "elimination" and kr["reason"] == "enemy defeated" and not kr["tie"], kr)
	var kills2: RulesScript = _mk([
		{"id": "p1", "team": "player", "col": 3, "lane": 2},
		{"id": "e1", "team": "enemy", "col": 5, "lane": 2, "hp": 3},
		{"id": "e2", "team": "enemy", "col": 7, "lane": 0, "hp": 0},
	], 1)
	kills2.phase = "attack"
	kills2.resolve_attacks({"p1": Vector2i(5, 2)})
	var kr2: Dictionary = kills2.end_turn()
	rep.check("elimination text with two enemies", kr2["result"] == "won" and kr2["reason"] == "both enemies defeated", kr2)
	var invalid: RulesScript = _mk([
		{"id": "p1", "team": "player", "col": 0, "lane": 4},
		{"id": "e1", "team": "enemy", "col": 7, "lane": 0},
	], 1)
	invalid.phase = "attack"
	rep.check("invalid player target is ignored", invalid.resolve_attacks({"p1": Vector2i(7, 0)}).is_empty())

	# --- win / loss checks
	var br: RulesScript = _mk([
		{"id": "p1", "team": "player", "col": 6, "lane": 4},
		{"id": "e1", "team": "enemy", "col": 6, "lane": 0},
	], 5)
	br.resolve_moves({"p1": Vector2i(1, 0)})
	br.resolve_attacks({})
	var brr: Dictionary = br.end_turn()
	rep.check("win by reaching the enemy back row", brr["result"] == "won" and brr["kind"] == "back_row" and brr["reason"] == "back row reached", brr)
	var lb: RulesScript = _mk([
		{"id": "p1", "team": "player", "col": 5, "lane": 4},
		{"id": "e1", "team": "enemy", "col": 1, "lane": 0},
	], 5)
	lb.resolve_moves({})
	lb.resolve_attacks({})
	var lbr: Dictionary = lb.end_turn()
	rep.check("loss when an enemy stands in column 0", lbr["result"] == "lost" and lbr["kind"] == "enemy_back_row"
		and lbr["reason"] == "an enemy archer reached your back row in lane 1", lbr)
	var both: RulesScript = _mk([
		{"id": "p1", "team": "player", "col": 6, "lane": 4},
		{"id": "e1", "team": "enemy", "col": 1, "lane": 0},
	], 5)
	both.resolve_moves({"p1": Vector2i(1, 0)})
	both.resolve_attacks({})
	var bothr: Dictionary = both.end_turn()
	rep.check("both lose on the same turn => the player wins", bothr["result"] == "won" and bothr["kind"] == "back_row", bothr)
	var none: RulesScript = RulesScript.new()
	none.resolve_moves({})
	none.resolve_attacks({})
	var noner: Dictionary = none.end_turn()
	rep.check("no result -> next turn, phase move", noner["result"] == "none" and none.turn == 2 and none.phase == "move", noner)
	var tl: RulesScript = _mk([
		{"id": "p1", "team": "player", "col": 0, "lane": 4},
		{"id": "e1", "team": "enemy", "col": 6, "lane": 0},
		{"id": "e2", "team": "enemy", "col": 6, "lane": 1},
	], 20)
	tl.resolve_moves({})
	tl.resolve_attacks({})
	var tlr: Dictionary = tl.end_turn()
	rep.check("turn limit 20: fewer units loses", tlr["result"] == "lost" and tlr["kind"] == "turn_limit", tlr)
	print("(the next ERROR line is expected: an out-of-order call is rejected)")
	var oo: RulesScript = RulesScript.new()
	var oo_ev: Array[Dictionary] = oo.resolve_attacks({})
	rep.check("calling steps out of order does nothing", oo_ev.is_empty() and oo.phase == "move")

	# --- enemy AI
	var ai: RulesScript = _mk([
		{"id": "p1", "team": "player", "col": 3, "lane": 4},
		{"id": "e1", "team": "enemy", "col": 5, "lane": 3},
		{"id": "e2", "team": "enemy", "col": 5, "lane": 1},
	], 1)
	var orders: Dictionary = ai.enemy_orders()
	rep.check("enemy AI: player in range -> stay; out of range -> 1 column toward col 0 in its lane",
		orders["e1"] == Vector2i.ZERO and orders["e2"] == Vector2i(-1, 0), orders)
	var ai2: RulesScript = _mk([
		{"id": "p1", "team": "player", "col": 2, "lane": 4},
		{"id": "e1", "team": "enemy", "col": 5, "lane": 3},
	], 1)
	ai2.resolve_moves({"p1": Vector2i(1, 0)})
	rep.check("enemy AI decides from positions at the start of planning (simultaneous moves)",
		ai2.get_unit("e1")["col"] == 4 and ai2.get_unit("p1")["col"] == 3)
	ai2.phase = "attack"
	rep.check("enemy attack AI targets the player's square", ai2.enemy_targets() == {"e1": Vector2i(3, 4)}, ai2.enemy_targets())
	var fresh: RulesScript = RulesScript.new()
	var mev: Array[Dictionary] = fresh.resolve_moves({})
	rep.check("turn 1 with player staying: one moved event (the enemy), none for the player",
		mev.size() == 1 and _count(mev, "moved", "unit", "p1") == 0 and mev[0]["unit"] == "e1"
		and mev[0]["from"] == Vector2i(7, 3) and mev[0]["to"] == Vector2i(6, 3), mev)

	# --- routes
	var win: Dictionary = Runner.load_route("res://tests/fixtures/win_route.json")
	var w1: Dictionary = Runner.play(win)
	rep.check("win route fixture: every target valid", w1["ok"], w1["error"])
	rep.check("win route fixture: result won (%s) on turn %d" % [w1["result"].get("reason", ""), w1["snapshot"]["turn"]],
		w1["result"]["result"] == "won" and w1["result"]["kind"] == win["expected_kind"] and w1["snapshot"]["turn"] == int(win["expected_turns"])
		and w1["result"]["reason"] == win["expected_reason"], w1["result"])
	rep.check("win route fixture: the win is NOT a tie (no help from 'ties go to the player')",
		w1["result"]["tie"] == false and w1["snapshot"]["result_kind"] == "elimination", w1["result"])
	var w2: Dictionary = Runner.play(win)
	rep.check("determinism: same orders => same snapshot", w1["snapshot"] == w2["snapshot"])
	rep.check("determinism: same orders => same event list", str(w1["events"]) == str(w2["events"]))
	var lose: Dictionary = Runner.load_route("res://tests/fixtures/lose_route.json")
	var l1: Dictionary = Runner.play(lose)
	rep.check("lose route fixture: result lost, '%s'" % l1["result"].get("reason", ""),
		l1["ok"] and l1["result"]["result"] == "lost" and l1["result"]["reason"] == lose["expected_reason"]
		and l1["snapshot"]["turn"] == int(lose["expected_turns"]), l1["result"])
	var naive_ok: bool = true
	for st: Dictionary in lose["turns"]:
		naive_ok = naive_ok and Runner.move_of(st) == Vector2i(1, 0)
	rep.check("lose route is the naive plan: straight forward (+1,0) in lane 5 every turn, shooting when possible", naive_ok)
	var ws: Dictionary = Runner.expected_sounds(w1["events"])
	rep.check("win route exercises hops, hits and hurts", ws["SFX-HOP"] > 0 and ws["SFX-HIT"] == 2 and ws["SFX-HURT"] == 1, ws)
	var ls: Dictionary = Runner.expected_sounds(l1["events"])
	rep.check("lose route exercises hits and hurts", ls["SFX-HIT"] == 1 and ls["SFX-HURT"] == 2, ls)
	# a naive 'stay forever' plan does not win (sanity: the slice needs the timing)
	var stay: RulesScript = RulesScript.new()
	var guard: int = 0
	while stay.result == "none" and guard < 30:
		stay.resolve_moves({})
		var vts: Array[Vector2i] = stay.valid_targets("p1")
		stay.resolve_attacks({"p1": vts[0]} if not vts.is_empty() else {})
		stay.end_turn()
		guard += 1
	rep.check("staying in the back row and always shooting loses (shot on turn 6)",
		stay.result == "lost" and stay.result_kind == "shot" and stay.turn == 6, stay.reason)
	# --- variant configs stay selectable (V0: the earlier two-enemy setup)
	var v0: RulesScript = RulesScript.new()
	v0.reset({"units": RulesScript.TWO_ENEMY_UNITS})
	rep.check("V0 config: two enemies at col 7 lanes 1 and 3", v0.alive_units("enemy").size() == 2
		and v0.get_unit("e1")["lane"] == 1 and v0.get_unit("e2")["lane"] == 3)
	var v0_route: Dictionary = {"turns": [
		{"move": [1, -1], "target": null}, {"move": [1, 0], "target": null}, {"move": [1, 1], "target": [4, 3]},
		{"move": [1, 0], "target": [4, 3]}, {"move": [1, -1], "target": null}, {"move": [1, -1], "target": null},
		{"move": [1, -1], "target": null}]}
	var v0r: Dictionary = Runner.play(v0_route, v0)
	rep.check("V0 config: the old turn-7 route still wins, and only on the tie", v0r["ok"] and v0r["result"]["result"] == "won"
		and v0r["result"]["tie"] == true and v0r["snapshot"]["turn"] == 7, v0r["result"])
	var v0b: RulesScript = RulesScript.new()
	v0b.reset({"units": RulesScript.TWO_ENEMY_UNITS, "attack_order_mode": "with_target"})
	var v0br: Dictionary = Runner.play(v0_route, v0b)
	rep.check("V0b config (order slots only for units with a target): the same route loses", v0br["result"]["result"] == "lost", v0br["result"])
