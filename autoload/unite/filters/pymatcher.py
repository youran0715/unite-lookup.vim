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

def Match(kw, rows, mode, limit):
    lowKw = kw.lower()
    regex = ''
    # Escape all of the characters as necessary
    escaped = [_escape.get(c, c) for c in lowKw]
    if len(lowKw) > 1:
        regex = ''.join([c + "[^" + c + "]*" for c in escaped[:-1]])

    regex += escaped[-1]

    regex = regex.lower()
    res = []
    rez = []
    prog = re.compile(regex)

    if mode == 'filename-only':
        res = [(filename_score(prog, line), line) for line in rows]
    else:
        res = [(path_score(prog, line), line) for line in rows]

    rez.extend([line for score, line in heapq.nlargest(limit, res) if score != 0])
    return rez

def UnitePyMatch():
    items = vim.eval('s:items')
    strInput = vim.eval('s:input')
    limit = int(vim.eval('s:limit'))
    mmode = vim.eval('s:mmode')

    rez = vim.eval('s:rez')

    strDir = ""
    strKws = ""
    kws = []
    kwsAndDirs = strInput.split(';')

    if len(kwsAndDirs) > 0:
        strKws = kwsAndDirs[0]

    if len(kwsAndDirs) > 1:
        strDir = kwsAndDirs[1]

    kws = strKws.split()
    rows = [line.lower() for line in items]
    for kw in kws:
        rows = Match(kw, rows, mmode, limit)

    rez = rows

    # Use double quoted vim strings and escape \
    vimrez = ['"' + line.replace('\\', '\\\\').replace('"', '\\"') + '"' for line in rez]

    vim.command('let s:rez = [%s]' % ','.join(vimrez))
