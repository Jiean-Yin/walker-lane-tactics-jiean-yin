extends SceneTree
## Headless scene test: drives main.tscn with synthetic key presses and checks sounds == events.
## godot --headless --path godot --script res://tests/test_audio_events.gd

const Runner = preload("res://tests/route_runner.gd")
const Report = preload("res://tests/test_report.gd")
const RulesScript = preload("res://game/rules.gd")
const MainScene = preload("res://game/main.tscn")

const FAST: float = 40.0
const MAX_FRAMES: int = 200000
const SFX: Array[String] = ["SFX-HOP", "SFX-HIT", "SFX-HURT", "SFX-WIN"]

var rep: Report
var main: Variant
var audio: Variant
var spam_presses: int = 0
var echo_presses: int = 0
var echo_failures: Array[String] = []
var route_errors: Array[String] = []
var summary: Dictionary = {}


func _initialize() -> void:
	_run()


func _key(code: int, echo: bool = false) -> void:
	var ev: InputEventKey = InputEventKey.new()
	ev.keycode = code as Key
	ev.physical_keycode = code as Key
	ev.pressed = true
	ev.echo = echo
	root.push_input(ev)
	if echo:
		echo_presses += 1
	else:
		var up: InputEventKey = InputEventKey.new()
		up.keycode = code as Key
		up.physical_keycode = code as Key
		up.pressed = false
		root.push_input(up)


func _s() -> String:
	return main.state_name()


## Rapid repeated presses while a playback runs: all must be ignored.
func _spam() -> void:
	if _s() != "PLAY_MOVES" and _s() != "PLAY_ATTACKS":
		return
	for code: int in [KEY_ENTER, KEY_SPACE, KEY_RIGHT, KEY_UP, KEY_ENTER]:
		_key(code)
		spam_presses += 1
	_key(KEY_ENTER, true)


func _wait(cond: Callable, spam: bool = false) -> bool:
	for i: int in MAX_FRAMES:
		if cond.call():
			return true
		if spam and i % 2 == 0:
			_spam()
		await process_frame
	return false


func _counts() -> Dictionary:
	return (audio.play_counts as Dictionary).duplicate()


func _delta(before: Dictionary) -> Dictionary:
	var out: Dictionary = {}
	for id: String in SFX:
		out[id] = int(audio.play_counts[id]) - int(before[id])
	return out


## Plays a fixture through the real input path. Returns false if the scene did not follow it.
func _play_route(route: Dictionary, label: String, pause_check: bool = false) -> bool:
	var turns: Array = route["turns"]
	for i: int in turns.size():
		var step: Dictionary = turns[i]
		if not await _wait(func() -> bool: return _s() == "PLAN_MOVE"):
			route_errors.append("%s turn %d: never reached PLAN_MOVE (state %s)" % [label, i + 1, _s()])
			return false
		var turn_no: int = main.rules.turn
		# held keys (echo) at planning must not act
		_key(KEY_ENTER, true)
		_key(KEY_SPACE, true)
		_key(KEY_RIGHT, true)
		if _s() != "PLAN_MOVE" or main.planned_offset != Vector2i.ZERO:
			echo_failures.append("%s turn %d: echo acted in PLAN_MOVE" % [label, turn_no])
		var mv: Vector2i = Runner.move_of(step)
		if mv == Vector2i.ZERO:
			_key(KEY_SPACE)
		else:
			if mv.x == 1:
				_key(KEY_RIGHT)
			elif mv.x == -1:
				_key(KEY_LEFT)
			if mv.y == -1:
				_key(KEY_UP)
			elif mv.y == 1:
				_key(KEY_DOWN)
			_key(KEY_RIGHT, true) # held arrow: no extra step
			if main.planned_offset != mv:
				route_errors.append("%s turn %d: planned %s, wanted %s" % [label, turn_no, main.planned_offset, mv])
			_key(KEY_ENTER)
		if pause_check and i == 0:
			_key(KEY_P)
			var clock: float = main._clock
			var hops: int = int(audio.play_counts["SFX-HOP"])
			for f: int in 30:
				await process_frame
			rep.check("pause during move playback freezes the clock and the sounds",
				main.paused and main._clock == clock and int(audio.play_counts["SFX-HOP"]) == hops and _s() == "PLAY_MOVES")
			rep.check("music ducked by 12 dB while paused during playback",
				audio.music_state == "ducked" and is_equal_approx(audio.music_volume_db(), -12.0), audio.music_volume_db())
			_key(KEY_ESCAPE)
			rep.check("Esc unpauses; music back to full", not main.paused and audio.music_state == "playing"
				and is_equal_approx(audio.music_volume_db(), 0.0))
		_spam()
		var after_moves: Callable = func() -> bool:
			var s: String = _s()
			return s == "PLAN_ATTACK" or s == "WON" or s == "LOST" or (s == "PLAN_MOVE" and main.rules.turn > turn_no)
		if not await _wait(after_moves, true):
			route_errors.append("%s turn %d: stuck after moves (%s)" % [label, turn_no, _s()])
			return false
		var t: Variant = Runner.target_of(step)
		if _s() == "PLAN_ATTACK":
			_key(KEY_ENTER, true)
			if _s() != "PLAN_ATTACK":
				echo_failures.append("%s turn %d: echo acted in PLAN_ATTACK" % [label, turn_no])
			if t == null:
				_key(KEY_SPACE)
			else:
				var n: int = 0
				while main.selected_target() != t and n < 30:
					_key(KEY_RIGHT)
					n += 1
				if main.selected_target() != t:
					route_errors.append("%s turn %d: cannot select %s" % [label, turn_no, t])
					return false
				_key(KEY_ENTER)
			_spam()
			var after_attacks: Callable = func() -> bool:
				var s: String = _s()
				return s == "WON" or s == "LOST" or (s == "PLAN_MOVE" and main.rules.turn > turn_no)
			if not await _wait(after_attacks, true):
				route_errors.append("%s turn %d: stuck after attacks (%s)" % [label, turn_no, _s()])
				return false
		elif t != null:
			route_errors.append("%s turn %d: fixture has a target but attack planning was skipped" % [label, turn_no])
			return false
	return await _wait(func() -> bool: return _s() == "WON" or _s() == "LOST")


func _check_sounds(label: String, before: Dictionary, expect_win: int) -> Dictionary:
	var d: Dictionary = _delta(before)
	var expd: Dictionary = Runner.expected_sounds(main.event_log)
	var moved: int = 0
	for ev: Dictionary in main.event_log:
		if ev["type"] == "moved":
			moved += 1
	rep.check("%s: SFX-HOP triggers == moved events" % label, d["SFX-HOP"] == moved and moved > 0, "%d vs %d" % [d["SFX-HOP"], moved])
	rep.check("%s: SFX-HIT triggers == player shots that damaged an enemy" % label, d["SFX-HIT"] == expd["SFX-HIT"] and expd["SFX-HIT"] > 0,
		"%d vs %d" % [d["SFX-HIT"], expd["SFX-HIT"]])
	rep.check("%s: SFX-HIT triggers == damaged-on-enemy events (no friendly fire on this route)" % label,
		d["SFX-HIT"] == expd["damaged_enemy"], "%d vs %d" % [d["SFX-HIT"], expd["damaged_enemy"]])
	rep.check("%s: SFX-HURT triggers == damaged-on-player events" % label, d["SFX-HURT"] == expd["SFX-HURT"]
		and d["SFX-HURT"] == expd["damaged_player"] and expd["SFX-HURT"] > 0, "%d vs %d" % [d["SFX-HURT"], expd["damaged_player"]])
	rep.check("%s: SFX-WIN triggers == %d" % [label, expect_win], d["SFX-WIN"] == expect_win, d["SFX-WIN"])
	rep.check("%s: every event was played back exactly once, in order" % label, str(main.played_events) == str(main.event_log),
		"%d played / %d events" % [main.played_events.size(), main.event_log.size()])
	return d


func _run() -> void:
	rep = Report.new("test_audio_events")
	await process_frame
	main = MainScene.instantiate()
	main.time_scale = FAST
	root.add_child(main)
	await process_frame
	audio = main.audio
	var win: Dictionary = Runner.load_route("res://tests/fixtures/win_route.json")
	var lose: Dictionary = Runner.load_route("res://tests/fixtures/lose_route.json")
	var pure_win: Dictionary = Runner.play(win)
	var pure_lose: Dictionary = Runner.play(lose)

	# --- buses and title
	rep.check("buses Music and SFX exist (default_bus_layout.tres)", AudioServer.get_bus_index("Music") > 0 and AudioServer.get_bus_index("SFX") > 0,
		ProjectSettings.get_setting("audio/buses/default_bus_layout"))
	rep.check("one SFX player per id with polyphony 4", _polyphony_ok())
	rep.check("title: state TITLE, music playing, started once", _s() == "TITLE" and audio.music_state == "playing" and audio.music_starts == 1)
	_key(KEY_ENTER, true)
	rep.check("held (echo) Enter on the title does nothing", _s() == "TITLE")
	_key(KEY_M)
	var music_muted: bool = audio.is_bus_muted("Music")
	_key(KEY_M)
	rep.check("M toggles the Music bus only", music_muted and not audio.is_bus_muted("Music") and not audio.is_bus_muted("SFX"))
	_key(KEY_N)
	var sfx_muted: bool = audio.is_bus_muted("SFX")
	_key(KEY_N)
	rep.check("N toggles the SFX bus only", sfx_muted and not audio.is_bus_muted("SFX") and not audio.is_bus_muted("Music"))
	_key(KEY_ENTER)
	rep.check("Enter starts play; music continues (not restarted)", _s() == "PLAN_MOVE" and audio.music_starts == 1 and audio.music_state == "playing")

	# --- pause in planning
	_key(KEY_P)
	rep.check("P pauses: music ducked by 12 dB", main.paused and audio.music_state == "ducked" and is_equal_approx(audio.music_volume_db(), -12.0))
	_key(KEY_ENTER)
	_key(KEY_SPACE)
	rep.check("gameplay keys ignored while paused", _s() == "PLAN_MOVE" and main.event_log.is_empty())
	_key(KEY_P)
	rep.check("P unpauses: music back to 0 dB", not main.paused and audio.music_state == "playing" and is_equal_approx(audio.music_volume_db(), 0.0))

	# --- win route
	var before: Dictionary = _counts()
	var ignored_before: int = main.ignored_inputs
	var ok: bool = await _play_route(win, "win route", true)
	rep.check("win route: scene followed the fixture", ok and route_errors.is_empty(), route_errors)
	rep.check("win route: state WON, %s, turn %d" % [main.rules.reason, main.rules.turn],
		_s() == "WON" and main.rules.result == "won" and main.rules.turn == int(win["expected_turns"]))
	rep.check("win route: the result is not a tie (%s)" % main.rules.result_kind, main.rules.result_tie == false
		and main.rules.result_kind == win["expected_kind"] and main.last_result.get("tie", true) == false)
	rep.check("win card reads ENEMY DEFEATED", main.win_card_title() == "ENEMY DEFEATED", main.win_card_title())
	rep.check("win route: scene snapshot == pure rules replay (inputs added no orders)", main.rules.snapshot() == pure_win["snapshot"])
	rep.check("win route: scene events == pure rules events", str(main.event_log) == str(pure_win["events"]))
	var win_d: Dictionary = _check_sounds("win route", before, 1)
	summary["win_route_sounds"] = win_d
	rep.check("win route: rapid presses during playback were ignored", spam_presses > 0 and main.ignored_inputs - ignored_before >= spam_presses,
		"%d spam, %d ignored" % [spam_presses, main.ignored_inputs - ignored_before])
	rep.check("echo inputs never acted", echo_failures.is_empty() and main.ignored_echoes >= echo_presses, "%d echoes sent, %d ignored, %s" % [echo_presses, main.ignored_echoes, echo_failures])
	rep.check("win: music stopped at once (not faded)", audio.music_state == "stopped" and audio.music_history[-1] == "stopped" and audio.music_history[-2] != "fading", audio.music_history)
	var win_entry: Dictionary = _last_log("SFX-WIN")
	rep.check("win: SFX-WIN fired with the music already stopped (plays alone)", win_entry.get("music", "") == "stopped", win_entry)
	rep.check("win: player piece shows the win state", main.pieces["p1"].state == "win")
	var win_snapshot: Dictionary = main.rules.snapshot()
	var win_events: String = str(main.event_log)
	# held Enter / re-entering results must not re-fire SFX-WIN
	for k: int in 5:
		_key(KEY_ENTER, true)
	rep.check("held Enter on the win card does nothing", _s() == "WON" and not main.show_results and int(audio.play_counts["SFX-WIN"]) - int(before["SFX-WIN"]) == 1)
	await _wait(func() -> bool: return main._card_lock <= 0.0)
	_key(KEY_ENTER)
	rep.check("Enter shows the results card; SFX-WIN not re-fired", main.show_results and int(audio.play_counts["SFX-WIN"]) - int(before["SFX-WIN"]) == 1)
	_key(KEY_ENTER, true)
	_key(KEY_ENTER, true)
	rep.check("held Enter on results does nothing", main.show_results and _s() == "WON")
	var starts: int = audio.music_starts
	_key(KEY_ENTER)
	rep.check("Enter plays again: turn 1, music restarted from the beginning",
		_s() == "PLAN_MOVE" and main.rules.turn == 1 and audio.music_starts == starts + 1 and audio.music_state == "playing"
		and audio.last_music_start_pos == 0.0 and main.retries == 0)
	rep.check("play again does not fire SFX-WIN", int(audio.play_counts["SFX-WIN"]) - int(before["SFX-WIN"]) == 1)

	# --- lose route
	before = _counts()
	var fades: int = audio.music_fades
	ok = await _play_route(lose, "lose route")
	rep.check("lose route: scene followed the fixture", ok and route_errors.is_empty(), route_errors)
	rep.check("lose route: state LOST, '%s'" % main.rules.reason, _s() == "LOST" and main.rules.reason == lose["expected_reason"])
	rep.check("lose route: scene snapshot == pure rules replay", main.rules.snapshot() == pure_lose["snapshot"])
	var lose_d: Dictionary = _check_sounds("lose route", before, 0)
	summary["lose_route_sounds"] = lose_d
	rep.check("defeat: the last sound is SFX-HURT", (audio.play_log[-1] as Dictionary)["id"] == "SFX-HURT")
	rep.check("defeat: music fade started", audio.music_fades == fades + 1 and audio.music_history.has("fading"))
	await _wait(func() -> bool: return audio.music_state == "stopped")
	rep.check("defeat: music faded then stopped (silent on the card)", audio.music_history[-2] == "fading" and audio.music_history[-1] == "stopped"
		and audio.music_volume_db() <= -59.0, audio.music_history.slice(-3))
	rep.check("defeat: player piece toppled, hit enemy back to idle", main.pieces["p1"].state == "defeat" and main.pieces["e1"].state == "idle",
		[main.pieces["p1"].state, main.pieces["e1"].state])
	var lose_snapshot: Dictionary = main.rules.snapshot()
	_key(KEY_ENTER, true)
	rep.check("held Enter on the defeat card does nothing", not main.show_results and _s() == "LOST")
	starts = audio.music_starts
	_key(KEY_R)
	rep.check("R retries: turn 1, retry count 1, fresh board", _s() == "PLAN_MOVE" and main.retries == 1
		and main.rules.snapshot() == RulesScript.new().snapshot())
	rep.check("retry restarts the music from the beginning", audio.music_starts == starts + 1 and audio.music_state == "playing"
		and audio.last_music_start_pos == 0.0 and is_equal_approx(audio.music_volume_db(), 0.0))

	# --- muted runs: mute never changes state
	_key(KEY_M)
	_key(KEY_N)
	rep.check("both buses muted", audio.is_bus_muted("Music") and audio.is_bus_muted("SFX"))
	before = _counts()
	ok = await _play_route(win, "muted win route")
	rep.check("muted win route: same result and snapshot as unmuted", ok and main.rules.snapshot() == win_snapshot)
	rep.check("muted win route: same events as unmuted", str(main.event_log) == win_events)
	_check_sounds("muted win route", before, 1)
	await _wait(func() -> bool: return main._card_lock <= 0.0)
	_key(KEY_ENTER)
	_key(KEY_ENTER)
	before = _counts()
	ok = await _play_route(lose, "muted lose route")
	rep.check("muted lose route: same result and snapshot as unmuted", ok and main.rules.snapshot() == lose_snapshot)
	_check_sounds("muted lose route", before, 0)
	_key(KEY_M)
	_key(KEY_N)
	rep.check("buses unmuted again", not audio.is_bus_muted("Music") and not audio.is_bus_muted("SFX"))
	rep.check("no sound files present -> triggers counted without streams (placeholder audio)",
		_all_logged_have_file_flag(), "music stream: %s" % audio.has_music_stream())

	summary["play_counts_total"] = audio.play_counts
	summary["spam_presses"] = spam_presses
	summary["echo_presses"] = echo_presses
	summary["music_history"] = audio.music_history
	var code: int = rep.finish(summary)
	main.queue_free()
	await process_frame
	quit(code)


func _polyphony_ok() -> bool:
	for id: String in SFX:
		var p: AudioStreamPlayer = audio.get_node_or_null(id) as AudioStreamPlayer
		if p == null or p.max_polyphony != 4 or p.bus != &"SFX":
			return false
	return true


func _last_log(id: String) -> Dictionary:
	for i: int in range(audio.play_log.size() - 1, -1, -1):
		if audio.play_log[i]["id"] == id:
			return audio.play_log[i]
	return {}


## Every logged trigger records whether a stream existed; with no assets, all must be false and still counted.
func _all_logged_have_file_flag() -> bool:
	for e: Dictionary in audio.play_log:
		if not e.has("file"):
			return false
		if bool(e["file"]) != audio.has_stream(String(e["id"])):
			return false
	return audio.play_log.size() > 0
