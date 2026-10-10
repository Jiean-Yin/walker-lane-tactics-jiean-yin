extends Node2D
## Lane Tactics asset slice: scene controller.
##
## Each step asks Rules for the result FIRST, then plays the returned event list back once
## (visuals + AudioDirector). Playback and sound never decide game state.
## Pause is implemented without get_tree().paused: the controller stops its own clock.

const RulesScript = preload("res://game/rules.gd")
const PieceScript = preload("res://game/piece.gd")
const DrawLayerScript = preload("res://game/draw_layer.gd")
const AudioDirectorScript = preload("res://game/audio_director.gd")

enum State { TITLE, PLAN_MOVE, PLAY_MOVES, PLAN_ATTACK, PLAY_ATTACKS, WON, LOST }
const STATE_NAMES: Array[String] = ["TITLE", "PLAN_MOVE", "PLAY_MOVES", "PLAN_ATTACK", "PLAY_ATTACKS", "WON", "LOST"]
const PHASE_LABELS: Array[String] = ["", "PLAN MOVE", "MOVES", "PLAN ATTACK", "COMBAT", "VICTORY", "DEFEAT"]

const PLAYER_ID: String = "p1"
const VIEW: Vector2 = Vector2(1280, 720)
const SQUARE: Vector2 = Vector2(128, 96)
const BOARD_ORIGIN: Vector2 = Vector2(128, 170)
const BASE_Y: float = 80.0 ## base-disc centre below the square's top edge
const SLOT_OFFSET: float = 32.0
const SLOT_SIZE: Vector2 = Vector2(64, 96)
const BASE_DISC: Vector2 = Vector2(40, 12)

const HOP_TIME: float = 0.25
const HOP_STAGGER: float = 0.12
const MOVE_TAIL: float = 0.3
const DRAW_LEAD: float = 0.2
const ARROW_TIME: float = 0.35
const ARROW_ARC: float = 40.0
const ATTACK_RECOVER: float = 0.25
const ATTACK_GAP: float = 0.25
const CANCEL_TIME: float = 0.6
const ATTACK_TAIL: float = 0.35
const FLOAT_TIME: float = 0.9
const CARD_LOCK: float = 0.5
const MESSAGE_TIME: float = 1.4

const COL_TABLE: Color = Color("#6B4A2E")
const COL_SQ_A: Color = Color("#D8C7A0")
const COL_SQ_B: Color = Color("#CDB98E")
const COL_INK: Color = Color("#1B1410")
const COL_TEAL: Color = Color("#1F6F78")
const COL_RED: Color = Color("#B23A2E")
const COL_YELLOW: Color = Color("#F2C14E")
const COL_TARGET: Color = Color("#E0453A")
const COL_CARD: Color = Color("#F3E9D2")
const COL_HUD_TEXT: Color = Color("#F3E9D2")

const ACTION_ORDER: Array[String] = ["lt_confirm", "lt_left", "lt_right", "lt_up", "lt_down", "lt_stay",
	"lt_retry", "lt_pause", "lt_music", "lt_sfx", "lt_debug"]
const ACTION_KEYS: Dictionary = {
	"lt_confirm": [KEY_ENTER, KEY_KP_ENTER],
	"lt_left": [KEY_LEFT, KEY_A],
	"lt_right": [KEY_RIGHT, KEY_D],
	"lt_up": [KEY_UP, KEY_W],
	"lt_down": [KEY_DOWN, KEY_S],
	"lt_stay": [KEY_SPACE],
	"lt_retry": [KEY_R],
	"lt_pause": [KEY_P, KEY_ESCAPE],
	"lt_music": [KEY_M],
	"lt_sfx": [KEY_N],
	"lt_debug": [KEY_F3],
}
const DIRS: Dictionary = {
	"lt_left": Vector2i(-1, 0), "lt_right": Vector2i(1, 0), "lt_up": Vector2i(0, -1), "lt_down": Vector2i(0, 1),
}

static var _tex_cache: Dictionary = {}

## Playback speed multiplier (tests use it to run fast). Never changes rules.
var time_scale: float = 1.0
var rules: RulesScript
var audio: AudioDirectorScript
var state: State = State.TITLE
var paused: bool = false
var debug_footprints: bool = false
var show_results: bool = false
var retries: int = 0
var event_log: Array[Dictionary] = [] ## every rules event of this session
var played_events: Array[Dictionary] = [] ## events whose moment has been shown by playback
var ignored_inputs: int = 0
var ignored_echoes: int = 0
var last_result: Dictionary = {}
var planned_offset: Vector2i = Vector2i.ZERO
var legal_cells: Array[Vector2i] = []
var targets: Array[Vector2i] = []
var target_index: int = -1
var has_marked_target: bool = false
var marked_target: Vector2i = Vector2i.ZERO
var display_hp: Dictionary = {}
var pieces: Dictionary = {} ## unit id -> piece

var _board_layer: Node2D
var _pieces_root: Node2D
var _fx_layer: Node2D
var _hud_layer: Node2D
var _cues: Array[Dictionary] = []
var _clock: float = 0.0
var _floaters: Array[Dictionary] = []
var _arrows: Array[Dictionary] = []
var _message: String = ""
var _message_left: float = 0.0
var _card_lock: float = 0.0
var _time: float = 0.0


func _ready() -> void:
	_ensure_actions()
	rules = RulesScript.new()
	audio = get_node_or_null("AudioDirector") as AudioDirectorScript
	if audio == null:
		audio = AudioDirectorScript.new()
		audio.name = "AudioDirector"
		add_child(audio)
	_board_layer = _make_layer(_draw_board, 0)
	_board_layer.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
	_pieces_root = Node2D.new()
	_pieces_root.name = "Pieces"
	_pieces_root.y_sort_enabled = true
	_pieces_root.z_index = 1
	add_child(_pieces_root)
	_fx_layer = _make_layer(_draw_fx, 2)
	_hud_layer = _make_layer(_draw_hud, 3)
	_build_pieces()
	state = State.TITLE
	audio.new_session() # MUS-LOOP starts on the title and continues into play


func _make_layer(fn: Callable, z: int) -> Node2D:
	var n: Node2D = DrawLayerScript.new()
	n.draw_fn = fn
	n.z_index = z
	add_child(n)
	return n


static func _ensure_actions() -> void:
	for action: String in ACTION_ORDER:
		if InputMap.has_action(action):
			continue
		InputMap.add_action(action)
		for code: int in ACTION_KEYS[action]:
			var ev: InputEventKey = InputEventKey.new()
			ev.physical_keycode = code as Key
			InputMap.action_add_event(action, ev)


func state_name() -> String:
	return STATE_NAMES[state]


func selected_target() -> Variant:
	if target_index >= 0 and target_index < targets.size():
		return targets[target_index]
	return null


# ---------------------------------------------------------------- clock

func _process(delta: float) -> void:
	var dt: float = delta * time_scale
	audio.time_scale = time_scale
	_time += delta
	if not paused:
		_clock += dt
		_run_cues()
		for p: PieceScript in pieces.values():
			p.tick(dt)
		_tick_fx(dt)
		if _message_left > 0.0:
			_message_left -= dt
		if _card_lock > 0.0:
			_card_lock -= dt
	_board_layer.queue_redraw()
	_fx_layer.queue_redraw()
	_hud_layer.queue_redraw()


func _schedule(t: float, fn: Callable) -> void:
	var i: int = _cues.size()
	while i > 0 and float(_cues[i - 1]["t"]) > t:
		i -= 1
	_cues.insert(i, {"t": t, "fn": fn})


func _clear_cues() -> void:
	_cues.clear()
	_clock = 0.0


func _run_cues() -> void:
	while not _cues.is_empty() and float(_cues[0]["t"]) <= _clock:
		var c: Dictionary = _cues.pop_front()
		(c["fn"] as Callable).call()


func _tick_fx(dt: float) -> void:
	for f: Dictionary in _floaters:
		f["t"] = float(f["t"]) + dt
	_floaters = _floaters.filter(func(f: Dictionary) -> bool: return float(f["t"]) < FLOAT_TIME)
	for a: Dictionary in _arrows:
		a["t"] = float(a["t"]) + dt
	_arrows = _arrows.filter(func(a: Dictionary) -> bool: return float(a["t"]) < ARROW_TIME)


# ---------------------------------------------------------------- input

func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey):
		return
	var k: InputEventKey = event as InputEventKey
	if not k.pressed:
		return
	if k.is_echo():
		ignored_echoes += 1 # held keys never act
		get_viewport().set_input_as_handled()
		return
	var action: String = _action_for(k)
	if action == "":
		return
	get_viewport().set_input_as_handled()
	_handle_action(action, k)


func _action_for(event: InputEvent) -> String:
	for action: String in ACTION_ORDER:
		if event.is_action(action):
			return action
	return ""


func _handle_action(action: String, k: InputEventKey) -> void:
	match action:
		"lt_music":
			audio.toggle_music_mute()
			return
		"lt_sfx":
			audio.toggle_sfx_mute()
			return
		"lt_debug":
			debug_footprints = not debug_footprints
			return
	if state == State.TITLE:
		if action == "lt_confirm":
			_start_play()
		else:
			ignored_inputs += 1
		return
	if action == "lt_pause":
		if _in_play():
			_set_paused(not paused)
		elif show_results and (k.keycode == KEY_ESCAPE or k.physical_keycode == KEY_ESCAPE):
			get_tree().quit()
		else:
			ignored_inputs += 1
		return
	if paused:
		ignored_inputs += 1
		return
	if action == "lt_retry":
		_restart(true)
		return
	match state:
		State.PLAN_MOVE:
			if DIRS.has(action):
				_adjust_move(DIRS[action])
			elif action == "lt_confirm":
				_confirm_move(planned_offset)
			elif action == "lt_stay":
				_confirm_move(Vector2i.ZERO)
		State.PLAN_ATTACK:
			if action == "lt_left" or action == "lt_up":
				_cycle_target(-1)
			elif action == "lt_right" or action == "lt_down":
				_cycle_target(1)
			elif action == "lt_confirm":
				_confirm_attack(selected_target())
			elif action == "lt_stay":
				_confirm_attack(null)
		State.WON, State.LOST:
			if action != "lt_confirm" or _card_lock > 0.0:
				ignored_inputs += 1
			elif not show_results:
				show_results = true
			else:
				_restart(false)
		_:
			ignored_inputs += 1 # playback: gameplay input is ignored


func _in_play() -> bool:
	return state in [State.PLAN_MOVE, State.PLAY_MOVES, State.PLAN_ATTACK, State.PLAY_ATTACKS]


func _set_paused(p: bool) -> void:
	paused = p
	audio.set_paused(p)


# ---------------------------------------------------------------- session

func _start_play() -> void:
	rules.reset()
	event_log.clear()
	played_events.clear()
	_build_pieces()
	_begin_plan_move()


## Retry (R) or play again (Enter on results): full reset to turn 1, music from the top.
func _restart(is_retry: bool) -> void:
	if is_retry:
		retries += 1
	else:
		retries = 0
	_clear_cues()
	_arrows.clear()
	_floaters.clear()
	_set_paused(false)
	show_results = false
	has_marked_target = false
	_message_left = 0.0
	last_result = {}
	rules.reset()
	event_log.clear()
	played_events.clear()
	_build_pieces()
	for p: PieceScript in pieces.values():
		p.show_recover()
	audio.new_session()
	_begin_plan_move()


func _build_pieces() -> void:
	for p: Node in _pieces_root.get_children():
		p.queue_free()
		_pieces_root.remove_child(p)
	pieces.clear()
	display_hp.clear()
	var cells: Dictionary = {}
	for u: Dictionary in rules.units:
		cells[u["id"]] = RulesScript.cell_of(u)
	for u: Dictionary in rules.units:
		var p: PieceScript = PieceScript.new()
		p.name = String(u["id"])
		_pieces_root.add_child(p)
		p.setup(u["id"], u["team"], int(u["facing"]), RulesScript.cell_of(u))
		p.position = _slot_pos(u["id"], cells)
		pieces[u["id"]] = p
		display_hp[u["id"]] = int(u["hp"])


# ---------------------------------------------------------------- move phase

func _begin_plan_move() -> void:
	state = State.PLAN_MOVE
	planned_offset = Vector2i.ZERO
	legal_cells = rules.legal_moves(PLAYER_ID)
	targets.clear()
	target_index = -1


func _adjust_move(d: Vector2i) -> void:
	var nxt: Vector2i = Vector2i(clampi(planned_offset.x + d.x, -1, 1), clampi(planned_offset.y + d.y, -1, 1))
	var here: Vector2i = RulesScript.cell_of(rules.get_unit(PLAYER_ID))
	if RulesScript.on_board(here + nxt):
		planned_offset = nxt


func _confirm_move(offset: Vector2i) -> void:
	_message_left = 0.0 # a transient message lasts until the next decision
	var events: Array[Dictionary] = rules.resolve_moves({PLAYER_ID: offset})
	event_log.append_array(events)
	_play_moves(events)


func _play_moves(events: Array[Dictionary]) -> void:
	_clear_cues()
	state = State.PLAY_MOVES
	var final_cells: Dictionary = {}
	for id: String in pieces:
		final_cells[id] = (pieces[id] as PieceScript).cell
	for ev: Dictionary in events:
		final_cells[ev["unit"]] = ev["to"]
	var i: int = 0
	for ev: Dictionary in events:
		var start: float = HOP_STAGGER * i
		_schedule(start, _cue_hop_start.bind(ev, final_cells))
		_schedule(start + HOP_TIME, _cue_hop_land.bind(ev))
		i += 1
	var end: float = (HOP_STAGGER * (i - 1) + HOP_TIME if i > 0 else 0.0) + MOVE_TAIL
	_schedule(end, _after_moves)


func _cue_hop_start(ev: Dictionary, final_cells: Dictionary) -> void:
	var p: PieceScript = pieces[ev["unit"]]
	var from: Vector2i = ev["from"]
	var to: Vector2i = ev["to"]
	if to.x != from.x:
		p.set_facing(1 if to.x > from.x else -1)
	p.start_hop(p.position, _slot_pos(ev["unit"], final_cells), HOP_TIME)


func _cue_hop_land(ev: Dictionary) -> void:
	var p: PieceScript = pieces[ev["unit"]]
	p.cell = ev["to"]
	p.finish_hop()
	played_events.append(ev)
	audio.on_event(ev) # SFX-HOP as the piece lands
	_relayout()


func _relayout() -> void:
	var cells: Dictionary = {}
	for id: String in pieces:
		cells[id] = (pieces[id] as PieceScript).cell
	for id: String in pieces:
		var p: PieceScript = pieces[id]
		if not p.is_hopping():
			p.position = _slot_pos(id, cells)


func _after_moves() -> void:
	targets = rules.valid_targets(PLAYER_ID)
	if targets.is_empty():
		_show_message("no target in range")
		_confirm_attack(null)
		return
	state = State.PLAN_ATTACK
	_message_left = 0.0
	target_index = 0 # preselected; with a single target it is the only choice


# ---------------------------------------------------------------- attack phase

func _cycle_target(step: int) -> void:
	if targets.is_empty():
		return
	target_index = posmod(target_index + step, targets.size())


func _confirm_attack(target: Variant) -> void:
	var orders: Dictionary = {}
	has_marked_target = target != null
	if target != null:
		marked_target = target
		orders[PLAYER_ID] = target
	var events: Array[Dictionary] = rules.resolve_attacks(orders)
	event_log.append_array(events)
	_play_attacks(events)


func _play_attacks(events: Array[Dictionary]) -> void:
	_clear_cues()
	state = State.PLAY_ATTACKS
	targets.clear()
	target_index = -1
	var groups: Array[Dictionary] = []
	for ev: Dictionary in events:
		if ev["type"] == "attack" or ev["type"] == "attack_cancelled":
			groups.append({"head": ev, "hits": []})
		elif not groups.is_empty():
			(groups[-1]["hits"] as Array).append(ev)
	var t: float = 0.0
	for g: Dictionary in groups:
		var head: Dictionary = g["head"]
		if head["type"] == "attack":
			_schedule(t, _cue_draw.bind(head))
			_schedule(t + DRAW_LEAD, _cue_arrow.bind(head))
			_schedule(t + DRAW_LEAD + ARROW_TIME, _cue_impact.bind(head, g["hits"]))
			_schedule(t + DRAW_LEAD + ARROW_TIME + ATTACK_RECOVER, _cue_attacker_idle.bind(head))
			t += DRAW_LEAD + ARROW_TIME + ATTACK_RECOVER + ATTACK_GAP
		else:
			_schedule(t, _cue_cancel.bind(head))
			t += CANCEL_TIME
	_schedule(t + ATTACK_TAIL, _after_attacks)


func _cue_draw(head: Dictionary) -> void:
	var p: PieceScript = pieces[head["unit"]]
	var target: Vector2i = head["target"]
	if target.x != p.cell.x:
		p.set_facing(1 if target.x > p.cell.x else -1)
	p.set_state("draw")
	played_events.append(head)


func _cue_arrow(head: Dictionary) -> void:
	var p: PieceScript = pieces[head["unit"]]
	var target: Vector2i = head["target"]
	var from: Vector2 = p.position + Vector2(14.0 * p.facing, -36.0)
	var to: Vector2 = _cell_rect(target).get_center() + Vector2(0.0, 2.0)
	_arrows.append({"from": from, "to": to, "t": 0.0})


func _cue_impact(head: Dictionary, hits: Array) -> void:
	if head["team"] == RulesScript.PLAYER:
		has_marked_target = false # the marked square stays visible until this hit
	for ev: Dictionary in hits:
		played_events.append(ev)
		var p: PieceScript = pieces[ev["unit"]]
		match String(ev["type"]):
			"damaged":
				display_hp[ev["unit"]] = int(ev["hp_after"])
				audio.on_event(ev) # SFX-HIT / SFX-HURT at the same moment as the pips change
				_floaters.append({"pos": p.position + Vector2(0.0, -92.0), "text": "-%d" % int(ev["amount"]),
					"color": COL_TARGET, "t": 0.0})
				if int(ev["hp_after"]) > 0:
					p.show_hurt()
			"killed":
				p.set_state("defeat")


func _cue_attacker_idle(head: Dictionary) -> void:
	var p: PieceScript = pieces[head["unit"]]
	if p.state == "draw":
		p.set_state("idle")


func _cue_cancel(head: Dictionary) -> void:
	played_events.append(head)
	if head["team"] == RulesScript.PLAYER:
		has_marked_target = false
	var p: PieceScript = pieces[head["unit"]]
	_floaters.append({"pos": p.position + Vector2(0.0, -92.0), "text": "no target", "color": COL_HUD_TEXT, "t": 0.0})


func _after_attacks() -> void:
	has_marked_target = false
	last_result = rules.end_turn()
	match String(last_result["result"]):
		"won":
			_enter_won()
		"lost":
			_enter_lost()
		_:
			_begin_plan_move()


func _enter_won() -> void:
	if state == State.WON:
		return
	state = State.WON
	show_results = false
	_message_left = 0.0
	_card_lock = CARD_LOCK
	var p: PieceScript = pieces.get(PLAYER_ID)
	if p != null and rules.is_alive(PLAYER_ID):
		p.set_state("win")
	audio.on_won() # music stops at once, SFX-WIN plays alone (only on this transition)


func _enter_lost() -> void:
	if state == State.LOST:
		return
	state = State.LOST
	show_results = false
	_message_left = 0.0
	_card_lock = CARD_LOCK
	audio.on_lost() # music fades over 0.5 s


func _show_message(text: String) -> void:
	_message = text
	_message_left = MESSAGE_TIME


# ---------------------------------------------------------------- geometry

func _cell_rect(c: Vector2i) -> Rect2:
	return Rect2(BOARD_ORIGIN + Vector2(c.x * SQUARE.x, c.y * SQUARE.y), SQUARE)


## Base-disc position for a unit given everyone's cells: one unit centred, two in left/right slots.
func _slot_pos(id: String, cells: Dictionary) -> Vector2:
	var c: Vector2i = cells[id]
	var group: Array[String] = []
	for other: String in cells:
		if cells[other] == c:
			group.append(other)
	group.sort_custom(func(a: String, b: String) -> bool:
		var ta: int = 0 if _team_of(a) == RulesScript.PLAYER else 1
		var tb: int = 0 if _team_of(b) == RulesScript.PLAYER else 1
		if ta != tb:
			return ta < tb
		return a < b)
	var n: int = group.size()
	var i: int = group.find(id)
	var off: float = 0.0
	if n == 2:
		off = -SLOT_OFFSET if i == 0 else SLOT_OFFSET
	elif n > 2:
		off = lerpf(-40.0, 40.0, float(i) / float(n - 1))
	var r: Rect2 = _cell_rect(c)
	return Vector2(r.position.x + SQUARE.x * 0.5 + off, r.position.y + BASE_Y)


func _team_of(id: String) -> String:
	return String(rules.get_unit(id).get("team", ""))


static func _tex(path: String) -> Texture2D:
	if _tex_cache.has(path):
		return _tex_cache[path]
	var tex: Texture2D = null
	if ResourceLoader.exists(path):
		var res: Resource = load(path)
		if res is Texture2D:
			tex = res as Texture2D
	_tex_cache[path] = tex
	return tex


# ---------------------------------------------------------------- drawing: board

func _draw_board(ci: CanvasItem) -> void:
	var table: Texture2D = _tex("res://assets/art/env_table.png")
	if table != null:
		var ts: Vector2 = table.get_size()
		var s: float = maxf(VIEW.x / ts.x, VIEW.y / ts.y)
		var size: Vector2 = ts * s
		ci.draw_texture_rect(table, Rect2((VIEW - size) * 0.5, size), false)
	else:
		ci.draw_rect(Rect2(Vector2.ZERO, VIEW), COL_TABLE)
	var board: Rect2 = Rect2(BOARD_ORIGIN, SQUARE * Vector2(RulesScript.COLS, RulesScript.LANES))
	ci.draw_rect(Rect2(board.position + Vector2(6, 8), board.size), Color(0, 0, 0, 0.35))
	var linen: Texture2D = _tex("res://assets/art/env_linen.png")
	for c: int in RulesScript.COLS:
		for l: int in RulesScript.LANES:
			var r: Rect2 = _cell_rect(Vector2i(c, l))
			ci.draw_rect(r, COL_SQ_A if (c + l) % 2 == 0 else COL_SQ_B)
			if linen != null:
				ci.draw_texture_rect(linen, r, true, Color(1, 1, 1, 0.45))
			if c == RulesScript.PLAYER_BACK_COL:
				ci.draw_rect(r, Color(COL_TEAL, 0.12))
			elif c == RulesScript.ENEMY_BACK_COL:
				ci.draw_rect(r, Color(COL_RED, 0.12))
	for c: int in range(1, RulesScript.COLS):
		var x: float = BOARD_ORIGIN.x + c * SQUARE.x
		ci.draw_line(Vector2(x, board.position.y), Vector2(x, board.end.y), Color(COL_INK, 0.3), 1.0)
	for l: int in range(1, RulesScript.LANES):
		var y: float = BOARD_ORIGIN.y + l * SQUARE.y
		ci.draw_line(Vector2(board.position.x, y), Vector2(board.end.x, y), Color(COL_INK, 0.3), 1.0)
	ci.draw_rect(board, Color("#3A2616"), false, 3.0)
	var font: Font = ThemeDB.fallback_font
	for l: int in RulesScript.LANES:
		var y: float = BOARD_ORIGIN.y + l * SQUARE.y + SQUARE.y * 0.5 + 7.0
		ci.draw_string(font, Vector2(BOARD_ORIGIN.x - 52.0, y), "%d" % (l + 1), HORIZONTAL_ALIGNMENT_CENTER, 40.0, 20, COL_HUD_TEXT)
	ci.draw_string(font, Vector2(BOARD_ORIGIN.x - 62.0, BOARD_ORIGIN.y - 8.0), "lane", HORIZONTAL_ALIGNMENT_CENTER, 60.0, 14, COL_HUD_TEXT)
	_draw_markers(ci)


func _draw_markers(ci: CanvasItem) -> void:
	if state == State.PLAN_MOVE and rules.is_alive(PLAYER_ID):
		var here: Vector2i = RulesScript.cell_of(rules.get_unit(PLAYER_ID))
		for c: Vector2i in legal_cells:
			ci.draw_rect(_cell_rect(c).grow(-5.0), Color(COL_YELLOW, 0.85), false, 2.0)
		var dest: Vector2i = here + planned_offset
		var dr: Rect2 = _cell_rect(dest).grow(-5.0)
		ci.draw_rect(dr, Color(COL_YELLOW, 0.2))
		ci.draw_rect(dr, COL_YELLOW, false, 4.0)
		if planned_offset != Vector2i.ZERO:
			_draw_arrow_shape(ci, _cell_rect(here).get_center(), _cell_rect(dest).get_center(), COL_YELLOW, 6.0)
	elif state == State.PLAN_ATTACK:
		for c: Vector2i in targets:
			ci.draw_rect(_cell_rect(c).grow(-5.0), Color(COL_TARGET, 0.7), false, 2.0)
		var sel: Variant = selected_target()
		if sel != null:
			_draw_target_mark(ci, sel)
	elif state == State.PLAY_ATTACKS and has_marked_target:
		_draw_target_mark(ci, marked_target)


func _draw_target_mark(ci: CanvasItem, c: Vector2i) -> void:
	var r: Rect2 = _cell_rect(c).grow(-4.0)
	ci.draw_rect(r, Color(COL_TARGET, 0.3))
	ci.draw_rect(r, COL_TARGET, false, 4.0)
	var m: Vector2 = r.get_center()
	ci.draw_arc(m, 22.0, 0.0, TAU, 24, COL_TARGET, 3.0)
	ci.draw_line(m + Vector2(-30, 0), m + Vector2(30, 0), COL_TARGET, 2.0)
	ci.draw_line(m + Vector2(0, -30), m + Vector2(0, 30), COL_TARGET, 2.0)


func _draw_arrow_shape(ci: CanvasItem, from: Vector2, to: Vector2, color: Color, width: float) -> void:
	var dir: Vector2 = (to - from).normalized()
	var tip: Vector2 = to - dir * 18.0
	ci.draw_line(from + dir * 18.0, tip - dir * 10.0, color, width)
	var side: Vector2 = Vector2(-dir.y, dir.x)
	ci.draw_colored_polygon(PackedVector2Array([tip + dir * 6.0, tip - dir * 14.0 + side * 12.0, tip - dir * 14.0 - side * 12.0]), color)


# ---------------------------------------------------------------- drawing: effects

func _draw_fx(ci: CanvasItem) -> void:
	var font: Font = ThemeDB.fallback_font
	# small HP pips under every living piece
	for id: String in pieces:
		var p: PieceScript = pieces[id]
		var hp: int = int(display_hp.get(id, 0))
		if hp <= 0:
			continue
		var team_col: Color = COL_TEAL if p.team == RulesScript.PLAYER else COL_RED
		for i: int in RulesScript.ARCHER_HP:
			var pos: Vector2 = p.position + Vector2(-13.5 + i * 9.0, 13.0)
			ci.draw_circle(pos, 3.5, team_col if i < hp else Color(COL_INK, 0.25))
	# attack order numbers during attack planning
	if state == State.PLAN_ATTACK:
		var order: Array[String] = rules.attack_order()
		for i: int in order.size():
			var p: PieceScript = pieces[order[i]]
			var pos: Vector2 = p.position + Vector2(0.0, -108.0)
			ci.draw_circle(pos, 11.0, COL_INK)
			ci.draw_string(font, pos + Vector2(-11.0, 6.0), "%d" % (i + 1), HORIZONTAL_ALIGNMENT_CENTER, 22.0, 16, COL_HUD_TEXT)
	# arrows in flight
	for a: Dictionary in _arrows:
		var s: float = clampf(float(a["t"]) / ARROW_TIME, 0.0, 1.0)
		var from: Vector2 = a["from"]
		var to: Vector2 = a["to"]
		var pos: Vector2 = from.lerp(to, s) + Vector2(0.0, -ARROW_ARC * 4.0 * s * (1.0 - s))
		var vel: Vector2 = (to - from) + Vector2(0.0, -ARROW_ARC * 4.0 * (1.0 - 2.0 * s))
		var dir: Vector2 = vel.normalized()
		var side: Vector2 = Vector2(-dir.y, dir.x)
		ci.draw_line(pos - dir * 30.0, pos, Color("#5A3A22"), 3.0)
		ci.draw_colored_polygon(PackedVector2Array([pos + dir * 8.0, pos + side * 4.5, pos - side * 4.5]), COL_INK)
		ci.draw_line(pos - dir * 30.0, pos - dir * 36.0 + side * 5.0, COL_CARD, 2.0)
		ci.draw_line(pos - dir * 30.0, pos - dir * 36.0 - side * 5.0, COL_CARD, 2.0)
	# floating numbers
	for f: Dictionary in _floaters:
		var k: float = float(f["t"]) / FLOAT_TIME
		var pos: Vector2 = (f["pos"] as Vector2) + Vector2(-60.0, -30.0 * k)
		var col: Color = f["color"]
		ci.draw_string_outline(font, pos, String(f["text"]), HORIZONTAL_ALIGNMENT_CENTER, 120.0, 28, 6, Color(COL_INK, 1.0 - k))
		ci.draw_string(font, pos, String(f["text"]), HORIZONTAL_ALIGNMENT_CENTER, 120.0, 28, Color(col, 1.0 - k))
	# F3: footprint slots (display only)
	if debug_footprints:
		for id: String in pieces:
			var p: PieceScript = pieces[id]
			var slot: Rect2 = Rect2(Vector2(p.position.x - SLOT_SIZE.x * 0.5, p.position.y - BASE_Y), SLOT_SIZE)
			ci.draw_rect(slot, Color(1, 0, 0, 0.9), false, 2.0)
			var pts: PackedVector2Array = PackedVector2Array()
			for i: int in 25:
				var ang: float = TAU * float(i) / 24.0
				pts.append(p.position + Vector2(cos(ang) * BASE_DISC.x * 0.5, sin(ang) * BASE_DISC.y * 0.5))
			ci.draw_polyline(pts, Color(0.1, 0.3, 1.0), 2.0)
		ci.draw_string(font, Vector2(BOARD_ORIGIN.x, BOARD_ORIGIN.y + 5 * SQUARE.y + 22.0), "F3 footprints: red = 64x96 slot, blue = 40x12 base disc (display only)", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, COL_HUD_TEXT)


# ---------------------------------------------------------------- drawing: HUD and cards

func _text(ci: CanvasItem, cx: float, y: float, text: String, size: int, color: Color) -> void:
	ci.draw_string(ThemeDB.fallback_font, Vector2(cx - 600.0, y), text, HORIZONTAL_ALIGNMENT_CENTER, 1200.0, size, color)


func _draw_hud(ci: CanvasItem) -> void:
	var font: Font = ThemeDB.fallback_font
	if state == State.TITLE:
		ci.draw_rect(Rect2(Vector2.ZERO, VIEW), Color(0.05, 0.035, 0.02, 0.72))
		_text(ci, 640, 250, "LANE TACTICS", 80, COL_CARD)
		_text(ci, 640, 292, "asset slice: one archer against two", 22, Color(COL_CARD, 0.8))
		var blink: float = 0.55 + 0.45 * sin(_time * 4.0)
		_text(ci, 640, 370, "press Enter", 34, Color(COL_YELLOW, blink))
		var lines: Array[String] = [
			"Arrows / WASD: choose a square or a target    Space: stay / hold fire    Enter: confirm",
			"R: retry    P / Esc: pause    M: music on/off    N: sound on/off    F3: footprints",
			"Reach the red back row, or defeat both enemies. Who strikes first alternates each turn.",
		]
		for i: int in lines.size():
			_text(ci, 640, 450 + i * 32, lines[i], 18, COL_CARD)
		return
	ci.draw_rect(Rect2(0, 0, VIEW.x, 150), Color(0.06, 0.045, 0.03, 0.62))
	ci.draw_string(font, Vector2(40, 34), "LANE TACTICS · asset slice", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(COL_HUD_TEXT, 0.7))
	ci.draw_string(font, Vector2(40, 78), "TURN %d / %d" % [rules.turn, RulesScript.TURN_LIMIT], HORIZONTAL_ALIGNMENT_LEFT, -1, 34, COL_HUD_TEXT)
	ci.draw_string(font, Vector2(40, 116), PHASE_LABELS[state], HORIZONTAL_ALIGNMENT_LEFT, -1, 24, COL_YELLOW)
	# player HP pips
	ci.draw_string(font, Vector2(380, 66), "HP", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, COL_HUD_TEXT)
	var hp: int = int(display_hp.get(PLAYER_ID, 0))
	for i: int in RulesScript.ARCHER_HP:
		var c: Vector2 = Vector2(432 + i * 32, 58)
		if i < hp:
			ci.draw_circle(c, 11.0, Color("#3FA7B2"))
		ci.draw_arc(c, 11.0, 0.0, TAU, 24, COL_HUD_TEXT, 2.0)
	var first_you: bool = rules.first_side() == RulesScript.PLAYER
	ci.draw_string(font, Vector2(380, 112), "strikes first this turn:", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, COL_HUD_TEXT)
	ci.draw_string(font, Vector2(610, 112), "YOU" if first_you else "ENEMY", HORIZONTAL_ALIGNMENT_LEFT, -1, 22,
		Color("#7FD1D9") if first_you else Color("#F08A7E"))
	var music_on: bool = not audio.is_bus_muted(AudioDirectorScript.MUSIC_BUS)
	var sfx_on: bool = not audio.is_bus_muted(AudioDirectorScript.SFX_BUS)
	ci.draw_string(font, Vector2(930, 50), "music (M): %s" % ("on" if music_on else "MUTED"), HORIZONTAL_ALIGNMENT_LEFT, -1, 18, COL_HUD_TEXT)
	ci.draw_string(font, Vector2(930, 78), "sound (N): %s" % ("on" if sfx_on else "MUTED"), HORIZONTAL_ALIGNMENT_LEFT, -1, 18, COL_HUD_TEXT)
	ci.draw_string(font, Vector2(930, 106), "retries: %d" % retries, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, COL_HUD_TEXT)
	ci.draw_string(font, Vector2(930, 132), "F3: footprints %s" % ("on" if debug_footprints else "off"), HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(COL_HUD_TEXT, 0.6))
	# message and hint line below the board
	if _message_left > 0.0:
		_text(ci, 640, 680, _message, 22, COL_YELLOW)
	_text(ci, 640, 708, _hint(), 16, COL_HUD_TEXT)
	if paused:
		ci.draw_rect(Rect2(Vector2.ZERO, VIEW), Color(0, 0, 0, 0.55))
		_text(ci, 640, 340, "PAUSED", 64, COL_CARD)
		_text(ci, 640, 392, "P / Esc: resume    M: music    N: sound", 22, COL_CARD)
	if state == State.WON or state == State.LOST:
		_draw_card(ci)


func _hint() -> String:
	match state:
		State.PLAN_MOVE:
			return "Arrows / WASD: choose a square    Space: stay    Enter: confirm the move"
		State.PLAN_ATTACK:
			return "Arrows / WASD: next target    Enter: shoot the marked square    Space: hold fire"
		State.PLAY_MOVES:
			return "moves play out together..."
		State.PLAY_ATTACKS:
			return "combat: one shot at a time, sides alternate"
	return ""


func _draw_card(ci: CanvasItem) -> void:
	var won: bool = state == State.WON
	var r: Rect2 = Rect2(330, 230, 620, 270)
	ci.draw_rect(Rect2(Vector2.ZERO, VIEW), Color(0, 0, 0, 0.25))
	ci.draw_rect(Rect2(r.position + Vector2(6, 8), r.size), Color(0, 0, 0, 0.4))
	ci.draw_rect(r, COL_CARD)
	ci.draw_rect(r, COL_INK, false, 3.0)
	var accent: Color = COL_TEAL if won else COL_RED
	var reason: String = String(last_result.get("reason", ""))
	if show_results:
		_text(ci, 640, 300, "VICTORY" if won else "DEFEAT", 56, accent)
		_text(ci, 640, 352, "turns: %d" % rules.turn, 24, COL_INK)
		_text(ci, 640, 386, "hits landed: %d" % rules.hits_landed, 24, COL_INK)
		_text(ci, 640, 420, "retries: %d" % retries, 24, COL_INK)
		_text(ci, 640, 474, "Enter: play again    R: retry    Esc: quit", 18, COL_INK)
	elif won:
		var title: String = "BOTH ENEMIES DEFEATED" if String(last_result.get("kind", "")) == "elimination" else "BACK ROW REACHED"
		_text(ci, 640, 304, title, 44, accent)
		var extra: String = ""
		var paren: int = reason.find("(")
		if paren >= 0:
			extra = reason.substr(paren + 1).trim_suffix(")")
		_text(ci, 640, 352, extra if extra != "" else "your archer stands on the enemy back row" if String(last_result.get("kind", "")) == "back_row" else reason, 20, COL_INK)
		_text(ci, 640, 420, "Enter: results    R: retry    M: music    N: sound", 18, COL_INK)
	else:
		_text(ci, 640, 300, "DEFEAT", 56, accent)
		_text(ci, 640, 352, reason.capitalize() if reason == "" else reason[0].to_upper() + reason.substr(1), 24, COL_INK)
		_text(ci, 640, 420, "R retry · M music · N sound", 22, COL_INK)
		_text(ci, 640, 466, "Enter: results", 18, COL_INK)
