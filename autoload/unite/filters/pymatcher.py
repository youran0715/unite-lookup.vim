import vim, re
import heapq
import platform;

_escape = dict((c , "\\" + c) for c in ['^','$','.','{','}','(',')','[',']','\\','/','+'])

def UnitePyMatch():
    items = vim.eval('s:items')
    astr = vim.eval('s:input')
    lowAstr = astr.lower()
    limit = int(vim.eval('s:limit'))
    mmode = vim.eval('s:mmode')

    rez = vim.eval('s:rez')

    regex = ''
    # Escape all of the characters as necessary
    escaped = [_escape.get(c, c) for c in lowAstr]

    # If the string is longer that one character, append a mismatch
    # expression to each character (except the last).
    if len(lowAstr) > 1:
        regex = ''.join([c + "[^" + c + "]*" for c in escaped[:-1]])

    # Append the last character in the string to the regex
    regex += escaped[-1]
    # because this IGNORECASE flag is extremely expensive we are converting everything to lower case
    # see https://github.com/FelikZ/ctrlp-py-matcher/issues/29
    regex = regex.lower()

    res = []
    prog = re.compile(regex)

    def filename_score(line):
        # get filename via reverse find to improve performance
        slashPos = line.rfind('/')
        if platform.system() == "Windows":
            slashPos = line.rfind('\\')

        if slashPos != -1:
            line = line[slashPos + 1:]

        lineLower = line.lower()
        result = prog.search(lineLower)
        if result:
            score = result.end() - result.start() + 1
            score = score + ( len(lineLower) + 1 ) / 100.0
            score = score + ( len(line) + 1 ) / 1000.0
            return 1000.0 / score

        return 0

    def path_score(line):
        lineLower = line.lower()
        result = prog.search(lineLower)
        if result:
            score = result.end() - result.start() + 1
            score = score + ( len(lineLower) + 1 ) / 100.0
            return 1000.0 / score

        return 0

    if mmode == 'filename-only':
        res = [(filename_score(line), line) for line in items]
    else:
        res = [(path_score(line), line) for line in items]

    rez.extend([line for score, line in heapq.nlargest(limit, res) if score != 0])

    # Use double quoted vim strings and escape \
    vimrez = ['"' + line.replace('\\', '\\\\').replace('"', '\\"') + '"' for line in rez]

    vim.command('let s:rez = [%s]' % ','.join(vimrez))
