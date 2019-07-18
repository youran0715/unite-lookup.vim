# import vim
import re
import heapq
import platform;

_escape = dict((c , "\\" + c) for c in ['^','$','.','{','}','(',')','[',']','\\','/','+'])


def filename_score(reprog, path, slash):
    # get filename via reverse find to improve performance
    slashPos = path.rfind(slash)
    filename = path[slashPos + 1:] if slashPos != -1 else path

    result = reprog.search(filename)
    if result:
        score = result.start() * 2
        score = score + result.end() - result.start() + 1
        score = score + ( len(filename) + 1 ) / 100.0
        score = score + ( len(path) + 1 ) / 1000.0
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

def contain_upper(kw):
    prog = re.compile('[A-Z]+')
    return prog.search(kw)

def is_search_lower(kw):
    return False if contain_upper(kw) else True

def get_regex_prog(kw, isregex, islower):
    searchkw = kw.lower() if islower else kw

    regex = ''
    # Escape all of the characters as necessary
    escaped = [_escape.get(c, c) for c in searchkw]

    if isregex:
        if len(searchkw) > 1:
            regex = ''.join([c + "[^" + c + "]*" for c in escaped[:-1]])
        regex += escaped[-1]
    else:
        regex = ''.join(escaped)

    return re.compile(regex)

def Match(opts, rows, islower):
    res = []

    slash = '/' if platform.system() != "Windows" else '\\'

    for row in rows:
        line = row.lower() if islower else row
        scoreTotal = 0.0
        for kw, prog, mode in opts:
            score = 0.0

            if mode == 'filename-only':
                score = filename_score(prog, line, slash)
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

    return res

def GetFilterRows(rowsWithScore):
    rez = []
    rez.extend([line for score, line in rowsWithScore])
    return rez

def Sort(rowsWithScore, limit):
    rez = []
    rez.extend([line for score, line in heapq.nlargest(limit, rowsWithScore) if score != 0])
    return rez

def vimecho(msg):
    vim.eval("echo " + msg)

candidates = {}
def setCandidates(key, items):
    candidates[key] = items

def loadCandidates(key, path):
    items = []
    setCandidates(key, items)

def SetCandidates():
    key = vim.eval('s:key')
    items = vim.eval('s:items')

    setCandidates(key, items)

def LoadCandidates():
    key = vim.eval('s:key')
    path = vim.eval('s:path')

    loadCandidates(key, path)

candidatesCache = {}
resultCache = {}
def ClearCache():
    candidatesCache = {}
    resultCache = {}

def getCacheKey(key, inputs):
    return key + "@" + inputs

def setCandidatesToCache(key, inputs, items):
    candidatesCache[getCacheKey(key, inputs)] = items

def getCandidatesFromCache(key, inputs):
    return candidatesCache.get(getCacheKey(key, inputs), [])

def setResultToCache(key, inputs, items):
    resultCache[getCacheKey(key, inputs)] = items

def getCandidates(key, inputs):
    items = []
    if len(inputs) == 0: #没有输入 返回全部候选集
        return candidates.get(key, [])

    # 判断是否已经有缓存
    cacheKey = getCacheKey(key, inputs)
    if cacheKey in candidatesCache:
        return candidatesCache.get(cacheKey, [])

    if len(inputs) == 0: # 只输入了1个字符 又没有缓存
                         # 返回全部候选集
        return candidates.get(key, [])

    # 判断去掉最后一个字符的是否在缓存中
    cacheKey = getCacheKey(key, inputs[:-1])
    if cacheKey in candidatesCache:
        return candidatesCache.get(cacheKey, [])

    # 没有缓存，前面的输入也没有缓存，返回全部
    return candidates.get(key, [])

def uniteMatch(key, inputs, limit, mmode):
    isregex = True
    smartcase = True

    cacheKey = getCacheKey(key, inputs)
    if cacheKey in resultCache:
        return resultCache.get(cacheKey, [])

    items = getCandidates(key, inputs)

    rows = items
    rowsFilter = items

    kwsAndDirs = inputs.split(';')
    strKws = kwsAndDirs[0] if len(kwsAndDirs) > 0 else ""
    strDir = kwsAndDirs[1] if len(kwsAndDirs) > 1 else ""

    islower = is_search_lower(inputs)

    opts = [(kw, get_regex_prog(kw, isregex, islower), mmode) for kw in strKws.split() if kw != ""]

    if strDir != "":
        opts.append((strDir, get_regex_prog(strDir, isregex, islower), 'dir'))

    if len(opts) > 0:
        rowsWithScore = Match(opts, rows, islower)
        rowsFilter = GetFilterRows(rowsWithScore)
        setCandidatesToCache(key, inputs, rowsFilter)

        rows = Sort(rowsWithScore, limit)
        setResultToCache(key, inputs, rows)

    if len(rows) > limit:
        rows = rows[:limit]

    return rows

def UnitePyMatch():
    # items = vim.eval('s:items')
    inputs = vim.eval('s:input')
    limit = int(vim.eval('s:limit'))
    mmode = vim.eval('s:mmode')
    key = vim.eval('s:key')
    isregex = True
    # isregex = False
    smartcase = True

    rows = uniteMatch(key, inputs, limit, mmode)

    vimrez = ['"' + line.replace('\\', '\\\\').replace('"', '\\"') + '"' for line in rows]
    vim.command('let s:rez = [%s]' % ','.join(vimrez))

def main():
    items = ["aaa", "bbb", "ccc", "abc", "aba", "abababa", "acbacb"]
    key = "test"
    setCandidates(key, items)
    res = uniteMatch(key, "a", 10, "filename-only")
    print(res)
    res = uniteMatch(key, "ab", 10, "filename-only")
    print(res)
    res = uniteMatch(key, "abc", 10, "filename-only")
    print(res)

# if __name__ == "__main__":
    # main()
