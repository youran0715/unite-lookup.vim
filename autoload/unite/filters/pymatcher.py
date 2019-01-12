import vim, re
import heapq
import platform;

_escape = dict((c , "\\" + c) for c in ['^','$','.','{','}','(',')','[',']','\\','/','+'])

def filename_score(reprog, line):
    # get filename via reverse find to improve performance
    slashPos = line.rfind('/')
    if platform.system() == "Windows":
        slashPos = line.rfind('\\')

    if slashPos != -1:
        line = line[slashPos + 1:]

    result = reprog.search(line)
    if result:
        score = result.start() * 2
        score = score + result.end() - result.start() + 1
        score = score + ( len(line) + 1 ) / 100.0
        score = score + ( len(line) + 1 ) / 1000.0
        return 1000.0 / score

    return 0

def path_score(reprog, line):
    result = reprog.search(line)
    if result:
        score = result.end() - result.start() + 1
        score = score + ( len(line) + 1 ) / 100.0
        return 1000.0 / score

    return 0

def dir_score(reprog, line):
    result = reprog.search(os.path.dirname(line))
    if result:
        score = result.end() - result.start() + 1
        score = score + ( len(line) + 1 ) / 100.0
        return 1000.0 / score

    return 0

def get_regex_prog(kw):
    lowKw = kw.lower()
    regex = ''
    # Escape all of the characters as necessary
    escaped = [_escape.get(c, c) for c in lowKw]
    if len(lowKw) > 1:
        regex = ''.join([c + "[^" + c + "]*" for c in escaped[:-1]])

    regex += escaped[-1]

    regex = regex.lower()
    return re.compile(regex)

def Match(opts, rows, limit):
    res = []
    rez = []

    for row in rows:
        line = row.lower()
        scoreTotal = 0.0
        for kw, prog, mode in opts:
            score = 0.0

            if mode == 'filename-only':
                score = filename_score(prog, line)
            elif mode == 'dir':
                score = dir_score(prog, line)
            else:
                score = path_score(prog, line)

            if score == 0:
                scoreTotal = 0
                break
            else:
                scoreTotal+=score

        if scoreTotal != 0:
            res.append((scoreTotal, row))

    rez.extend([line for score, line in heapq.nlargest(limit, res) if score != 0])
    return rez

def UnitePyMatch():
    items = vim.eval('s:items')
    strInput = vim.eval('s:input')
    limit = int(vim.eval('s:limit'))
    mmode = vim.eval('s:mmode')

    # rows = [line.lower() for line in items]
    rows = items

    kwsAndDirs = strInput.split(';')
    strKws = kwsAndDirs[0] if len(kwsAndDirs) > 0 else ""
    strDir = kwsAndDirs[1] if len(kwsAndDirs) > 1 else ""

    opts = [(kw, get_regex_prog(kw), mmode) for kw in strKws.split() if kw != ""]

    if strDir != "":
        opts.append((strDir, get_regex_prog(strDir), 'dir'))

    if len(opts) > 0:
        rows = Match(opts, rows, limit)

    if len(rows) > limit:
        rows = rows[:limit]

    # Use double quoted vim strings and escape \
    vimrez = ['"' + line.replace('\\', '\\\\').replace('"', '\\"') + '"' for line in rows]
    vim.command('let s:rez = [%s]' % ','.join(vimrez))
