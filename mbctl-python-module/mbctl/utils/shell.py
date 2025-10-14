import re

# code from Python shlex.py
_find_unsafe = re.compile(r'[^\w@%+=:,./-]', re.ASCII).search

def quote(s):
    """Return a shell-escaped version of the string *s*."""
    if not s:
        return "''"
    if _find_unsafe(s) is None:
        return s

    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    return "'" + s.replace("'", "'\"'\"'") + "'"

def args_list_to_command(args_list: list[str] | str) -> str:
    if isinstance(args_list, list):
        return " ".join(quote(arg) for arg in args_list)
    return args_list