#!/usr/bin/env bash
# scripts/redact-paths.sh <file>...
# Rewrites files in place so they can be committed: this checkout's absolute path becomes <repo>
# and the home folder becomes <home>, in forward-slash, backslash and JSON-escaped (\\) forms.
# Nothing personal is written here: both paths are read at run time.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
R_UNIX="$root"
R_WIN="$(cd "$root" && pwd -W 2>/dev/null || pwd)"
H_UNIX="$HOME"
H_WIN="$(cd "$HOME" && pwd -W 2>/dev/null || pwd)"
export R_UNIX R_WIN H_UNIX H_WIN
perl -pi -e '
  for my $pair ([$ENV{R_WIN}, "<repo>"], [$ENV{R_UNIX}, "<repo>"], [$ENV{H_WIN}, "<home>"], [$ENV{H_UNIX}, "<home>"]) {
    my ($from, $to) = @$pair;
    next unless length $from;
    (my $back = $from) =~ s{/}{\\}g;
    (my $json = $from) =~ s{/}{\\\\}g;
    for my $form ($json, $back, $from) { s/\Q$form\E/$to/gi; }
  }' "$@"
