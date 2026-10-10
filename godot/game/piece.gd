extends Node2D
## One board piece. Display only: it never decides anything.
##
## The node position is the centre of the base disc. set_state() swaps ONE static texture:
##   res://assets/art/archer_<state>.png        (player)
##   res://assets/art/archer_<state>_enemy.png  (enemy; falls back to the player image tinted red)
## Without any image it draws a clearly labelled code placeholder.

const TARGET_HEIGHT: float = 80.0 ## on-screen height of the piece (idle image scaled to this)
const BASE_FROM_BOTTOM: float = 6.0 ## base-disc centre above the image's bottom edge, in screen px
const HOP_HEIGHT: float = 16.0
const HURT_TIME: float = 0.5
const RECOVER_TIME: float = 0.4
const ART_DIR: String = "res://assets/art/"
const STATES: Array[String] = ["idle", "draw", "hurt", "defeat", "win", "hop", "recover"]
const OPTIONAL_FALLBACK: Dictionary = {"hop": "idle", "recover": "idle"}
const ENEMY_TINT: Color = Color(1.0, 0.55, 0.5)

const COL_INK: Color = Color("#1B1410")
const COL_BIRCH: Color = Color("#E2B887")
const COL_PLAYER: Color = Color("#1F6F78")
const COL_ENEMY: Color = Color("#B23A2E")
const COL_HOOD: Color = Color("#24323F")
const COL_WALNUT: Color = Color("#5A3A22")

static var _tex_cache: Dictionary = {}

var unit_id: String = ""
var team: String = "player"
var facing: int = 1
var state: String = "idle"
var cell: Vector2i = Vector2i.ZERO
var texture_source: String = "placeholder" ## "player" | "enemy" | "player_tinted" | "placeholder"

var _sprite: Sprite2D
var _lift: float = 0.0
var _hopping: bool = false
var _hop_from: Vector2 = Vector2.ZERO
var _hop_to: Vector2 = Vector2.ZERO
var _hop_t: float = 0.0
var _hop_dur: float = 0.25
var _hurt_left: float = 0.0
var _recover_left: float = 0.0


func setup(id: String, team_name: String, start_facing: int, start_cell: Vector2i) -> void:
	unit_id = id
	team = team_name
	facing = start_facing
	cell = start_cell
	if _sprite == null:
		_sprite = Sprite2D.new()
		_sprite.centered = true
		add_child(_sprite)
	set_state("idle")


func set_facing(f: int) -> void:
	if f == 0 or f == facing:
		return
	facing = f
	_apply_visual()


func set_state(new_state: String) -> void:
	state = new_state
	if new_state != "hurt":
		_hurt_left = 0.0
	if new_state != "recover":
		_recover_left = 0.0
	_apply_visual()


func show_hurt() -> void:
	set_state("hurt")
	_hurt_left = HURT_TIME


func show_recover() -> void:
	if _find_texture("recover")[0] != null:
		set_state("recover")
		_recover_left = RECOVER_TIME
	else:
		set_state("idle")


func is_hopping() -> bool:
	return _hopping


func start_hop(from_pos: Vector2, to_pos: Vector2, duration: float) -> void:
	_hop_from = from_pos
	_hop_to = to_pos
	_hop_t = 0.0
	_hop_dur = maxf(duration, 0.001)
	_hopping = true
	position = from_pos
	if _find_texture("hop")[0] != null:
		set_state("hop")


func finish_hop() -> void:
	_hopping = false
	position = _hop_to
	_set_lift(0.0)
	if state == "hop":
		set_state("idle")


## Advanced by main with the (scaled) game clock, so pause stops it.
func tick(dt: float) -> void:
	if _hopping:
		_hop_t = minf(_hop_t + dt, _hop_dur)
		var k: float = _hop_t / _hop_dur
		position = _hop_from.lerp(_hop_to, k)
		_set_lift(HOP_HEIGHT * sin(PI * k))
	if _hurt_left > 0.0:
		_hurt_left -= dt
		if _hurt_left <= 0.0 and state == "hurt":
			set_state("idle")
	if _recover_left > 0.0:
		_recover_left -= dt
		if _recover_left <= 0.0 and state == "recover":
			set_state("idle")


func _set_lift(v: float) -> void:
	_lift = v
	_apply_visual()


# ---------------------------------------------------------------- textures

## Returns [Texture2D or null, source, modulate].
func _find_texture(state_name: String) -> Array:
	var tex: Texture2D = null
	if team == "enemy":
		tex = _load_tex(ART_DIR + "archer_%s_enemy.png" % state_name)
		if tex != null:
			return [tex, "enemy", Color.WHITE]
		tex = _load_tex(ART_DIR + "archer_%s.png" % state_name)
		if tex != null:
			return [tex, "player_tinted", ENEMY_TINT]
	else:
		tex = _load_tex(ART_DIR + "archer_%s.png" % state_name)
		if tex != null:
			return [tex, "player", Color.WHITE]
	return [null, "placeholder", Color.WHITE]


static func _load_tex(path: String) -> Texture2D:
	if _tex_cache.has(path):
		return _tex_cache[path]
	var tex: Texture2D = null
	if ResourceLoader.exists(path):
		var res: Resource = load(path)
		if res is Texture2D:
			tex = res as Texture2D
	_tex_cache[path] = tex
	return tex


func _apply_visual() -> void:
	if _sprite == null:
		return
	var found: Array = _find_texture(state)
	if found[0] == null and OPTIONAL_FALLBACK.has(state):
		found = _find_texture(OPTIONAL_FALLBACK[state])
	var tex: Texture2D = found[0]
	texture_source = found[1]
	if tex == null:
		_sprite.visible = false
		queue_redraw()
		return
	# One scale for every pose, taken from the idle image, so all states share the same pixel size.
	var ref: Texture2D = _find_texture("idle")[0]
	if ref == null:
		ref = tex
	var s: float = TARGET_HEIGHT / maxf(1.0, float(ref.get_height()))
	_sprite.texture = tex
	_sprite.visible = true
	_sprite.modulate = found[2]
	_sprite.scale = Vector2(s, s)
	_sprite.flip_h = facing < 0
	_sprite.position = Vector2(0.0, -tex.get_height() * s * 0.5 + BASE_FROM_BOTTOM - _lift)
	queue_redraw()


# ---------------------------------------------------------------- placeholder

func _draw() -> void:
	if _sprite != null and _sprite.visible:
		return
	var paint: Color = COL_PLAYER if team == "player" else COL_ENEMY
	var lean: float = 0.0
	match state:
		"hurt":
			lean = -0.32
		"defeat":
			lean = -1.45
	# Base disc stays on the board; the body leans/topples around it.
	draw_set_transform(Vector2(0.0, -_lift), 0.0, Vector2(facing, 1.0))
	_ellipse(Vector2.ZERO, Vector2(20.0, 6.0), COL_WALNUT)
	draw_set_transform(Vector2(0.0, -_lift - 4.0), lean * facing, Vector2(facing, 1.0))
	# quiver on the back
	draw_rect(Rect2(-19.0, -50.0, 7.0, 24.0), COL_WALNUT)
	draw_rect(Rect2(-19.0, -50.0, 7.0, 24.0), COL_INK, false, 2.0)
	# body
	draw_rect(Rect2(-12.0, -50.0, 24.0, 48.0), paint)
	draw_rect(Rect2(-12.0, -50.0, 24.0, 48.0), COL_INK, false, 2.5)
	# hood and ball head
	draw_circle(Vector2(-1.0, -60.0), 13.0, COL_HOOD)
	draw_circle(Vector2(2.0, -60.0), 9.5, COL_BIRCH)
	draw_arc(Vector2(-1.0, -60.0), 13.0, 0.0, TAU, 24, COL_INK, 2.0)
	draw_circle(Vector2(7.0, -61.0), 1.8, COL_INK)
	# bow
	match state:
		"draw":
			draw_arc(Vector2(10.0, -32.0), 22.0, -1.25, 1.25, 16, COL_WALNUT, 3.5)
			draw_polyline(PackedVector2Array([Vector2(16.5, -53.0), Vector2(-2.0, -32.0), Vector2(16.5, -11.0)]), COL_INK, 1.5)
		"win":
			draw_line(Vector2(6.0, -44.0), Vector2(18.0, -72.0), COL_INK, 3.0)
			draw_arc(Vector2(18.0, -78.0), 10.0, -2.6, 0.6, 12, COL_WALNUT, 3.0)
		_:
			draw_arc(Vector2(4.0, -32.0), 20.0, -1.2, 1.2, 16, COL_WALNUT, 3.5)
			draw_line(Vector2(11.2, -50.6), Vector2(11.2, -13.4), COL_INK, 1.2)
	# state label, unflipped, so the placeholder is obviously a placeholder
	draw_set_transform(Vector2(0.0, -_lift), 0.0, Vector2.ONE)
	var font: Font = ThemeDB.fallback_font
	var label: String = "[%s]" % state
	draw_rect(Rect2(-26.0, -96.0, 52.0, 13.0), Color(1, 1, 1, 0.7))
	draw_string(font, Vector2(-26.0, -86.0), label, HORIZONTAL_ALIGNMENT_CENTER, 52.0, 10, COL_INK)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


func _ellipse(center: Vector2, radii: Vector2, fill: Color) -> void:
	var pts: PackedVector2Array = PackedVector2Array()
	for i: int in 24:
		var a: float = TAU * float(i) / 24.0
		pts.append(center + Vector2(cos(a) * radii.x, sin(a) * radii.y))
	draw_colored_polygon(pts, fill)
	pts.append(pts[0])
	draw_polyline(pts, COL_INK, 2.0)
