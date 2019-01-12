if !exists("g:lookup_file_max_candidates")
    let g:lookup_file_max_candidates = 100
endif
if !exists("g:lookup_file_min_input")
    let g:lookup_file_min_input = 3
endif
if !exists("g:lookup_file_mru_max")
    let g:lookup_file_mru_max = 50
endif

if !exists("g:lookupfile_WildIgnore")
    let g:lookupfile_WildIgnore= {
        \ 'file': ['*.sw?','~$*','*.bak','*.exe','*.o','*.so','*.py[co]'],
        \ "dir" : [".git", ".svn", ".hg", "node_modules"]
        \}
endif

if !exists("g:lookupfile_FollowLinks")
    let g:lookupfile_FollowLinks=1
endif

if !exists("g:lookupfile_IndexTimeLimit")
    let g:lookupfile_IndexTimeLimit=120
endif

function! unite#sources#lookup_file#buf_enter()
    call s:add_mru(fnamemodify(bufname("%"), ":p"))
endfunction

" define source
function! unite#sources#lookup_file#define()
    return [s:source_file, s:source_mru, s:source_filemru]
endfunction

function! s:get_cache_dir()
	set shellslash
    let cache_dir = expand($HOME) . "/.cache/vim/"

    if !isdirectory(cache_dir)
        call mkdir(cache_dir)
    endif

	let cwd = substitute(getcwd(), '/', '_', 'g')
	let cwd = substitute(cwd, ':', '_', 'g')
	let dir = cache_dir . cwd . '/'

    if !isdirectory(dir)
        call mkdir(dir)
    endif

	if g:is_os_windows
		set noshellslash
	endif

    return dir
endfunction

function! s:get_mrulist(current_buffer)
    let filepath = s:get_cache_path_mrulist()

    if !filereadable(filepath)
        return []
    endif

    let mrulist = []
    for line in readfile(filepath)
        if filereadable(line) && a:current_buffer != line
            call add(mrulist, fnamemodify(line, ":."))
        endif
    endfor

    return mrulist
endfun

let s:mru_map = {}
function! s:update_mru_map()
    let filepath = s:get_cache_path_mrulist()
    if !filereadable(filepath)
        return
    endif

    let s:mru_map = {}
    for line in readfile(filepath)
        let s:mru_map[line] = 1
    endfor
endfun

function! s:clean_mru_map()
    let s:mru_map = {}
endfunction

function! s:mrulisted(file)
    return has_key(s:mru_map, a:file)
endfunction

function! s:add_mru(path)
    let mrus = []
    if !filereadable(a:path)
        return
    endif

    let path = fnamemodify(a:path, ":p:.")
    if path[0] == '.' || path[0] == '/'
        return
    endif

    call add(mrus, a:path)

    let mrupath = s:get_cache_path_mrulist()
    if filereadable(mrupath)
        for line in readfile(mrupath)
            if line != a:path
                call add(mrus, line)
            endif
        endfor
    endif

    if len(mrus) > g:lookup_file_mru_max
        let mrus = mrus[:g:lookup_file_mru_max - 1]
    endif

    call writefile(mrus, mrupath)
endfunction

function! unite#sources#lookup_file#clean_mru()
    let filepath = s:get_cache_path_mrulist()
    call delete(filepath)
endfunction

function! s:get_cache_path_filelist()
    return s:get_cache_dir() . 'filelist2'
endfunction

function! s:get_cache_path_mrulist()
    return s:get_cache_dir() . 'mrulist'
endfunction

let s:plugin_path = escape(expand('<sfile>:p:h'), '\')

if has('python3')
  execute 'py3file ' . s:plugin_path . '/fileexpl.py'
else
  execute 'pyfile ' . s:plugin_path . '/fileexpl.py'
endif

function! s:refresh_filelist()
    let s:file_list=[]
    let s:file_path = s:get_cache_path_filelist()
    call writefile(s:file_list, s:file_path)

    let s:dir_path= escape(fnamemodify("./", ":p"), ' \')

    let s:dir_path= fnamemodify("./", ":p")
    execute 'python' . (has('python3') ? '3' : '') . ' UnitePyGetFileList()'
endfunction

" source file
let s:source_file = {
    \   'name': 'look/f',
    \   'description': 'candidates from lookup file',
    \   'max_candidates': g:lookup_file_max_candidates,
    \   'hooks': {},
    \   'default_kind' : 'file',
    \   'default_action' : {'*' : 'open'},
    \   'syntax': 'uniteSource__LookupFile',
    \   'is_volatile': 1,
\}

" source mru
let s:source_mru = {
    \   'name': 'look/mru',
    \   'description': 'candidates from lookup mru',
    \   'max_candidates': 30,
    \   'hooks': {},
    \   'default_kind' : 'file',
    \   'default_action' : {'*' : 'open'},
    \   'syntax': 'uniteSource__LookupMru',
    \   'is_volatile': 1,
\}

" source file & mru
let s:source_filemru = {
    \   'name': 'look/fm',
    \   'description': 'candidates from lookup file and mru',
    \   'max_candidates': 50,
    \   'hooks': {},
    \   'syntax': 'uniteSource__LookupFile',
    \   'is_volatile': 1,
\}

function! s:source_file.hooks.on_init(args, context)
    let a:context.exclude_mru  = 0
    let a:context.current_buffer = fnamemodify(bufname('%'), ":p")
endfunction

function! s:source_file.hooks.on_close(args, context)
endfunction

function! s:source_filemru.hooks.on_init(args, context)
    let a:context.exclude_mru  = 1
    let a:context.current_buffer = fnamemodify(bufname('%'), ":p")
    call s:update_mru_map()
endfunction

function! s:source_filemru.hooks.on_close(args, context)
    call s:clean_mru_map()
endfunction

function! s:source_file.gather_candidates(args, context)
    let a:context.mmode = "filename-only"
    return s:gather_candidates_file(a:args, a:context)
endfunction

function! s:source_mru.gather_candidates(args, context)
    let a:context.mmode = "filename-only"
    return s:gather_candidates_mru(a:args, a:context)
endfunction

function! s:source_mru.hooks.on_init(args, context)
    let a:context.current_buffer = bufname('%')
endfunction

function! s:gather_candidates_current_buf(args, context)
    let buf = a:context.current_buffer

    if !buflisted(buf) | return [] | endif

    let files = [fnamemodify(buf, ":p:.")]
    return s:map_result(s:get_result(a:context, files), '[E]')
endfunction

function! s:source_filemru.gather_candidates(args, context)
    let a:context.mmode = "filename-only"

    let candidates_mru  = s:gather_candidates_mru(a:args, a:context)
    let candidates_curr = s:gather_candidates_current_buf(a:args, a:context)
    let candidates_file = s:gather_candidates_file(a:args, a:context)

    let result = extend(candidates_mru, candidates_curr)
    let result = extend(result, candidates_file)

    return result
endfunction

let s:cached_result = []
function! s:gather_candidates_file(args, context)
    if a:context.is_redraw || !filereadable(s:get_cache_path_filelist())
        call s:refresh_filelist()
        let s:cached_result = []
    endif

    if empty(s:cached_result)
        let s:cached_result = readfile(s:get_cache_path_filelist())
    endif

    let match_result = s:get_result(a:context, s:cached_result)

    let result = []

    let tag_idx = 0
    while tag_idx < len(match_result)
        let file = fnamemodify(match_result[tag_idx], ":p")
        " let file = match_result[tag_idx]
        if (a:context.exclude_mru && s:mrulisted(file))
            let tag_idx = tag_idx + 1
            continue
        endif

        call add(result, file)

        let tag_idx = tag_idx + 1
    endwhile

    return s:map_result(result, '')
endfunction

function! s:gather_candidates_mru(args, context)
    return s:map_result(s:get_result(a:context, s:get_mrulist(a:context.current_buffer)), '[M]')
endfunction

fun s:get_result(context, items)
    return unite#filters#matcher_py_fuzzy#matcher(a:context, a:items, g:lookup_file_max_candidates)
endf

fun s:map_result(rows, abbr)
    return map(a:rows, "{
      \ 'word': fnamemodify(v:val, ':t'),
      \ 'abbr': printf('%s %s', a:abbr, fnamemodify(v:val, ':.')),
      \ 'kind'  : 'file',
      \ 'group' : 'file',
      \ 'action__path': v:val,
      \ }")
endf

