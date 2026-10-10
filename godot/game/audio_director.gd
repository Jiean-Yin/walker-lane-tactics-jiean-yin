extends Node
## AudioDirector: turns rules events (already resolved) into sounds. It never touches game state.
##
## Event-to-sound map (CHANGE-BRIEF):
##   SFX-HOP  - one per "moved" event, called by playback as each piece lands
##   SFX-HIT  - "damaged" where the target is an enemy and the attacker is the player
##   SFX-HURT - "damaged" where the target is the player
##   SFX-WIN  - only on the transition into WON
## Guards: at most one sound per shot (events of one shot share an "attack" key), SFX-WIN is
## armed once per session. A missing file means silence, but the trigger is still counted.

const PLAYER: String = "player"
const ENEMY: String = "enemy"
const SFX_IDS: Array[String] = ["SFX-HOP", "SFX-HIT", "SFX-HURT", "SFX-WIN"]
const SFX_FILES: Dictionary = {
	"SFX-HOP": "res://assets/sfx/sfx_hop",
	"SFX-HIT": "res://assets/sfx/sfx_hit",
	"SFX-HURT": "res://assets/sfx/sfx_hurt",
	"SFX-WIN": "res://assets/sfx/sfx_win",
}
const MUSIC_FILE: String = "res://assets/music/mus_loop"
const MUSIC_BUS: String = "Music"
const SFX_BUS: String = "SFX"
const FULL_DB: float = 0.0
const DUCK_DB: float = -12.0
const SILENT_DB: float = -60.0
const FADE_TIME: float = 0.5
const MAX_POLYPHONY: int = 4

## Public counters for tests.
var play_counts: Dictionary = {}
var play_log: Array = [] # {id, t (seconds since start), ...}
var guarded_skips: int = 0 # second damaged event of one shot: no extra sound
## "playing" | "ducked" | "fading" | "stopped"
var music_state: String = "stopped"
var music_history: Array[String] = []
var music_starts: int = 0
var music_fades: int = 0
var last_music_start_pos: float = -1.0
## Scaled like the game clock so tests can run fast; does not affect rules.
var time_scale: float = 1.0

var _sfx_players: Dictionary = {}
var _music: AudioStreamPlayer
var _fade_left: float = 0.0
var _fade_from: float = FULL_DB
var _sounded_attacks: Dictionary = {}
var _win_armed: bool = true
var _paused: bool = false


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_ensure_buses()
	for id: String in SFX_IDS:
		play_counts[id] = 0
		var p: AudioStreamPlayer = AudioStreamPlayer.new()
		p.name = id
		p.bus = SFX_BUS
		p.max_polyphony = MAX_POLYPHONY
		p.stream = _load_stream(SFX_FILES[id])
		add_child(p)
		_sfx_players[id] = p
	_music = AudioStreamPlayer.new()
	_music.name = "MusicPlayer"
	_music.bus = MUSIC_BUS
	_music.process_mode = Node.PROCESS_MODE_ALWAYS
	var stream: AudioStream = _load_stream(MUSIC_FILE)
	if stream is AudioStreamOggVorbis:
		(stream as AudioStreamOggVorbis).loop = true
	elif stream is AudioStreamWAV:
		var wav: AudioStreamWAV = stream as AudioStreamWAV
		wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
		wav.loop_begin = 0
		wav.loop_end = int(wav.get_length() * wav.mix_rate)
	_music.stream = stream
	add_child(_music)


func _process(delta: float) -> void:
	if music_state != "fading":
		return
	_fade_left -= delta * time_scale
	if _fade_left <= 0.0:
		_music.volume_db = SILENT_DB
		_music.stop()
		_set_music_state("stopped")
	else:
		var k: float = 1.0 - _fade_left / FADE_TIME
		_music.volume_db = lerpf(_fade_from, SILENT_DB, k)


# ---------------------------------------------------------------- sfx

func has_stream(id: String) -> bool:
	return (_sfx_players[id] as AudioStreamPlayer).stream != null


func has_music_stream() -> bool:
	return _music != null and _music.stream != null


## Feed one rules event at the moment playback shows it.
func on_event(ev: Dictionary) -> void:
	match String(ev.get("type", "")):
		"moved":
			_trigger("SFX-HOP", ev)
		"damaged":
			var key: String = String(ev.get("attack", ""))
			if _sounded_attacks.has(key):
				guarded_skips += 1
				return
			if ev["team"] == PLAYER:
				_sounded_attacks[key] = true
				_trigger("SFX-HURT", ev)
			elif ev["team"] == ENEMY and ev.get("by_team", "") == PLAYER:
				_sounded_attacks[key] = true
				_trigger("SFX-HIT", ev)


func _trigger(id: String, ev: Dictionary = {}) -> void:
	play_counts[id] = int(play_counts[id]) + 1
	play_log.append({"id": id, "t": Time.get_ticks_msec() / 1000.0, "unit": ev.get("unit", ""), "attack": ev.get("attack", ""),
		"music": music_state, "file": has_stream(id)})
	var p: AudioStreamPlayer = _sfx_players[id]
	if p.stream != null:
		p.play()


## New session (start, retry, play again): restart music from the top and re-arm the guards.
func new_session() -> void:
	_sounded_attacks.clear()
	_win_armed = true
	start_music()


# ---------------------------------------------------------------- music

func start_music() -> void:
	_fade_left = 0.0
	_music.stop()
	_music.volume_db = DUCK_DB if _paused else FULL_DB
	if _music.stream != null:
		_music.play(0.0)
	music_starts += 1
	last_music_start_pos = 0.0
	_set_music_state("ducked" if _paused else "playing")


func set_paused(paused: bool) -> void:
	_paused = paused
	if music_state == "playing" or music_state == "ducked":
		_music.volume_db = DUCK_DB if paused else FULL_DB
		_set_music_state("ducked" if paused else "playing")


## Defeat: fade out over 0.5 s and stay silent.
func on_lost() -> void:
	if music_state == "playing" or music_state == "ducked":
		_fade_from = _music.volume_db
		_fade_left = FADE_TIME
		music_fades += 1
		_set_music_state("fading")


## Win: stop the music at once, then SFX-WIN plays alone (once per session).
func on_won() -> void:
	_fade_left = 0.0
	_music.stop()
	_set_music_state("stopped")
	if _win_armed:
		_win_armed = false
		_trigger("SFX-WIN")


func music_volume_db() -> float:
	return _music.volume_db


func music_player() -> AudioStreamPlayer:
	return _music


func _set_music_state(s: String) -> void:
	if music_state != s:
		music_history.append(s)
	music_state = s


# ---------------------------------------------------------------- buses

func toggle_music_mute() -> bool:
	return _toggle_bus(MUSIC_BUS)


func toggle_sfx_mute() -> bool:
	return _toggle_bus(SFX_BUS)


func is_bus_muted(bus_name: String) -> bool:
	var idx: int = AudioServer.get_bus_index(bus_name)
	return idx >= 0 and AudioServer.is_bus_mute(idx)


func _toggle_bus(bus_name: String) -> bool:
	var idx: int = AudioServer.get_bus_index(bus_name)
	if idx < 0:
		return false
	AudioServer.set_bus_mute(idx, not AudioServer.is_bus_mute(idx))
	return AudioServer.is_bus_mute(idx)


## default_bus_layout.tres provides Music and SFX; create them only if the layout was not loaded.
func _ensure_buses() -> void:
	for bus_name: String in [MUSIC_BUS, SFX_BUS]:
		if AudioServer.get_bus_index(bus_name) == -1:
			AudioServer.add_bus()
			var idx: int = AudioServer.bus_count - 1
			AudioServer.set_bus_name(idx, bus_name)
			AudioServer.set_bus_send(idx, &"Master")


static func _load_stream(base: String) -> AudioStream:
	for ext: String in [".ogg", ".wav"]:
		var path: String = base + ext
		if ResourceLoader.exists(path):
			var res: Resource = load(path)
			if res is AudioStream:
				return res as AudioStream
	return null
