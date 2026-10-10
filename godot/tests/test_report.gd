extends RefCounted
## Collects PASS/FAIL checks and writes a timestamped JSON report to <repo>/evidence/.

var name: String = ""
var checks: Array[Dictionary] = []
var started_unix: int = 0


func _init(report_name: String) -> void:
	name = report_name
	started_unix = int(Time.get_unix_time_from_system())


func check(label: String, ok: bool, detail: Variant = "") -> bool:
	checks.append({"check": label, "pass": ok, "detail": str(detail)})
	print("%s  %s%s" % ["PASS" if ok else "FAIL", label, "" if str(detail) == "" else "  (" + str(detail) + ")"])
	return ok


func passed() -> int:
	var n: int = 0
	for c: Dictionary in checks:
		if c["pass"]:
			n += 1
	return n


func all_passed() -> bool:
	return passed() == checks.size() and not checks.is_empty()


## Writes the report and returns the exit code (0 only if every check passed).
func finish(extra: Dictionary = {}) -> int:
	var dir: String = ProjectSettings.globalize_path("res://").path_join("../evidence").simplify_path()
	DirAccess.make_dir_recursive_absolute(dir)
	var path: String = dir.path_join("%s-%d.json" % [name, started_unix])
	var data: Dictionary = {
		"report": name,
		"unix_time": started_unix,
		"engine": Engine.get_version_info().get("string", ""),
		"passed": passed(),
		"total": checks.size(),
		"all_passed": all_passed(),
		"checks": checks,
	}
	data.merge(extra)
	var f: FileAccess = FileAccess.open(path, FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(data, "\t"))
		f.close()
	print("SUMMARY %s: %d/%d passed -> %s" % [name, passed(), checks.size(), path])
	return 0 if all_passed() else 1
