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
        score = result.end() - result.start() + 1
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
    result = reprog.search(line)
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

def Match(kws, rows, mode, limit):
    progs = [ get_regex_prog(kw) for kw in kws ]

    res = []
    rez = []

    for row in rows:
        scoreTotal = 0.0
        for prog in progs:
            score = filename_score(prog, row) if mode == 'filename-only' else path_score(prog, row)

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

    rez = vim.eval('s:rez')

    kwsAndDirs = strInput.split(';')
    strKws = kwsAndDirs[0] if len(kwsAndDirs) > 0 else ""
    strDir = kwsAndDirs[1] if len(kwsAndDirs) > 1 else ""

    kws = [kw for kw in strKws.split() if kw != ""]
    rows = [line.lower() for line in items]

    if strDir != "":
        progDir = get_regex_prog(strDir)
        rows = [ row for row in rows if progDir.search(os.path.dirname(row))]

    rez = Match(kws, rows, mmode, limit)

    # Use double quoted vim strings and escape \
    vimrez = ['"' + line.replace('\\', '\\\\').replace('"', '\\"') + '"' for line in rez]

    vim.command('let s:rez = [%s]' % ','.join(vimrez))
