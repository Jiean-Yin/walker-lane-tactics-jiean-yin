extends RefCounted
## Shared test helpers: load a route fixture and replay it through Rules alone (no scene, no audio).

const RulesScript = preload("res://game/rules.gd")


static func load_route(path: String) -> Dictionary:
	var text: String = FileAccess.get_file_as_string(path)
	var data: Variant = JSON.parse_string(text)
	if typeof(data) != TYPE_DICTIONARY:
		push_error("cannot parse route fixture %s" % path)
		return {}
	return data


static func move_of(step: Dictionary) -> Vector2i:
	var m: Array = step["move"]
	return Vector2i(int(m[0]), int(m[1]))


static func target_of(step: Dictionary) -> Variant:
	if step["target"] == null:
		return null
	var t: Array = step["target"]
	return Vector2i(int(t[0]), int(t[1]))


## Replays the route on a fresh Rules. Returns {result: Dictionary, events: Array, snapshot: Dictionary,
## turns_played: int, ok: bool, error: String}.
static func play(route: Dictionary, rules: RulesScript = null) -> Dictionary:
	if rules == null:
		rules = RulesScript.new()
	var events: Array = []
	var res: Dictionary = {"result": "none"}
	var played: int = 0
	var error: String = ""
	for step: Dictionary in route["turns"]:
		if rules.result != "none":
			error = "route continues after the game ended"
			break
		events.append_array(rules.resolve_moves({"p1": move_of(step)}))
		var t: Variant = target_of(step)
		var orders: Dictionary = {}
		if t != null:
			if not rules.valid_targets("p1").has(t):
				error = "turn %d: target %s is not valid" % [rules.turn, str(t)]
			orders["p1"] = t
		events.append_array(rules.resolve_attacks(orders))
		res = rules.end_turn()
		played += 1
	return {"result": res, "events": events, "snapshot": rules.snapshot(), "turns_played": played,
		"ok": error == "", "error": error}


## Expected sound triggers for an event list, per the CHANGE-BRIEF map (at most one sound per shot).
static func expected_sounds(events: Array) -> Dictionary:
	var hop: int = 0
	var hit_keys: Dictionary = {}
	var hurt_keys: Dictionary = {}
	var damaged_enemy: int = 0
	var damaged_player: int = 0
	for ev: Dictionary in events:
		match String(ev["type"]):
			"moved":
				hop += 1
			"damaged":
				if ev["team"] == "player":
					damaged_player += 1
					hurt_keys[ev["attack"]] = true
				elif ev["team"] == "enemy":
					damaged_enemy += 1
					if ev["by_team"] == "player" and not hurt_keys.has(ev["attack"]):
						hit_keys[ev["attack"]] = true
	return {"SFX-HOP": hop, "SFX-HIT": hit_keys.size(), "SFX-HURT": hurt_keys.size(),
		"damaged_enemy": damaged_enemy, "damaged_player": damaged_player}
