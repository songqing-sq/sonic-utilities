#!/usr/bin/env python3
"""Emit the click bash-completion script for a console-script name.

The legacy build (sonic-utilities-data/generate_completions.py) imports every
sonic_utilities entry point and asks click to source() its completion. That
needs the whole CLI package importable at build time; the emitted text is just
click's fixed bash template with the program name substituted, so generate it
directly instead.

Substitutions, matching click's BashComplete.source():
  function name  -> _<prog with - and . turned into _>_completion
  env var        -> _<PROG UPPERCASED, punctuation kept>_COMPLETE
  complete -F    -> the program name verbatim
"""

import re
import sys

_TEMPLATE = """_%(func)s_completion() {
    local IFS=$'\\n'
    local response

    response=$(env COMP_WORDS="${COMP_WORDS[*]}" COMP_CWORD=$COMP_CWORD _%(var)s_COMPLETE=bash_complete $1)

    for completion in $response; do
        IFS=',' read type value <<< "$completion"

        if [[ $type == 'dir' ]]; then
            COMPREPLY=()
            compopt -o dirnames
        elif [[ $type == 'file' ]]; then
            COMPREPLY=()
            compopt -o default
        elif [[ $type == 'plain' ]]; then
            COMPREPLY+=($value)
        fi
    done

    return 0
}

_%(func)s_completion_setup() {
    complete -o nosort -F _%(func)s_completion %(prog)s
}

_%(func)s_completion_setup;
"""


def main(argv):
    if len(argv) != 3:
        sys.stderr.write("usage: gen_completion.py <prog> <out>\n")
        return 2
    prog, out = argv[1], argv[2]
    func = re.sub(r"[-.]", "_", prog)
    with open(out, "w") as f:
        f.write(_TEMPLATE % {"func": func, "var": prog.upper(), "prog": prog})
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
