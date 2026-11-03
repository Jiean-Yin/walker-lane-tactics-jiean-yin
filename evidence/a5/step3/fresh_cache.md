# Fresh cache check (2026-11-02, Claude)

The course asks to delete `godot/.godot`, reimport and run `test_materials`. The editor was open in the working
folder, so the check ran in a fresh clone of commit `222d690` instead (a clone has no `.godot` cache):

1. `git clone` into a short path outside the repository (a clone into a deep folder failed: a film-QC file name
   under `youtube/` is longer than the Windows path limit; see Known limitations).
2. `"$GODOT" --headless --path godot --import` - exit 0.
3. `./scripts/run-test.sh test_materials.gd 60` - **148/148, exit 0, no SHADER ERROR**
   (`fresh_cache_test_materials_60fps.log`).

**Import files rewritten by the fresh import:** 24 (every `.import` in the project). `git diff --ignore-cr-at-eol` on
them is empty: git checked them out with CRLF line endings (`core.autocrlf=true`) and Godot wrote them back with LF.
No import setting changed. The clone was deleted afterwards.
