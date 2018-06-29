if !exists("g:lookup_file_max_candidates")
    let g:lookup_file_max_candidates = 100
endif
if !exists("g:lookup_file_min_input")
    let g:lookup_file_min_input = 3
endif
if !exists("g:lookup_file_mru_max")
    let g:lookup_file_mru_max = 30
endif

" define source
function! unite#sources#lookup_file#define()
    return [s:source_file, s:source_buf, s:source_filebuf, s:source_mru, s:source_filemru]
endfunction

let g:lookupfile_ignore_dirs = ['.git', '.svn', '.hg', '.vimproject',
            \'build-*', 'target', 'vendor', 'uploads']
let g:lookupfile_ignore_fts = ['.o', '.dll', '.lib', '.a', '.so', '.exe', '.dep', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pyc','.jar', '.log']
" let g:lookupfile_ignore_fts = ['.pyc']
let g:lookupfile_ignore_pattern = '\.o$\|\.dep$\|moc.*\.cpp$\|\.vimproject\|.log$\|\.png$\|\.ico$\|\.jpg$\|\.pyc$\|\.jar$'
let g:lookupfile_cmd_find = 'find'

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

function! s:system(cmd)
	" echoerr a:cmd
	call vimproc#system(a:cmd)
    "call system(a:cmd)
endfunction

function! s:get_mrulist(current_buffer)
    let filepath = s:get_cache_path_mrulist()

    if !filereadable(filepath)
        return []
    endif

    let mrulist = []
    for line in readfile(filepath)
        if filereadable(line) && a:current_buffer != line
            call add(mrulist, line)
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

let s:proj_buf_list = []

function! s:find_buf(buf)
    let buf_path = fnamemodify(a:buf, ":p")

    let idx = 0
    for buf in s:proj_buf_list

        if fnamemodify(buf, ":p") == buf_path
            return idx
        endif

        let idx = idx + 1
    endfor

    return -1
endfunction

function! s:del_buf(buf_path)
    if !filereadable(a:buf_path)
        return
    endif

    let buf_idx = s:find_buf(a:buf_path)
    if buf_idx != -1
        call remove(s:proj_buf_list, buf_idx)
    endif
endfunction

function! s:add_buf(buf_path)
    if !filereadable(a:buf_path)
        return
    endif

    call s:del_buf(a:buf_path)
    call insert(s:proj_buf_list, a:buf_path)
endfunction

function! s:get_buflist(current_buffer)
    let buf_list = []

    let current_buffer = fnamemodify(a:current_buffer, ":p")
    for buf in s:proj_buf_list
        let buf = fnamemodify(buf, ":p")
        if buflisted(buf) && buf != current_buffer
        " if buflisted(buf) 
            call add(buf_list, fnamemodify(buf, ":p"))
        endif
    endfor

    return buf_list
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

    let mrus = mrus[:g:lookup_file_mru_max]

    call writefile(mrus, mrupath)
endfunction

function! unite#sources#lookup_file#clean_mru()
    let filepath = s:get_cache_path_mrulist()
    call delete(filepath)
endfunction

function! unite#sources#lookup_file#buf_enter()
    if s:is_init_buf == 0
        call s:buflist_init()
    endif

    call s:buffer_clear()

    let buf_name = bufname("%")

    call s:add_buf(fnamemodify(buf_name, ":p"))
    call s:add_mru(fnamemodify(buf_name, ":p"))
endfunction

function! s:buffer_clear()
    let buf_list = []
    let buf_idx = 0

    for buf in s:proj_buf_list
        if buflisted(buf) != 0
            call add(buf_list, buf)
        endif
    endfor

    let s:proj_buf_list = buf_list
endfunction

let s:is_init_buf = 0
function! s:buflist_init()
    let buf_nr = bufnr("$")

    let s:is_init_buf = 1

    let buf_idx = 0
    while buf_idx <= buf_nr
        " echomsg "add buf". buf_idx
        call s:add_buf(bufname(buf_idx))

        let buf_idx = buf_idx + 1
    endwhile

    if len(s:proj_buf_list) <= 3
        let s:is_init_buf = 0
    endif

endfunction

function! s:get_cache_path_filelist()
    return s:get_cache_dir() . 'filelist2'
endfunction

function! s:get_cache_path_mrulist()
    return s:get_cache_dir() . 'mrulist'
endfunction

function! s:refresh_filelist()
	if g:is_os_windows
		return s:refresh_filelist_windows()
	else
		return s:refresh_filelist_unix()
	endif
endfunction

function! s:refresh_filelist_windows()
    let path = s:get_cache_path_filelist()
	
	" call s:system("echo '!_TAG_FILE_SORTED	2	/2=foldcase/' > " . path)
	" let cmd = "for /r ./ %i in (*) do @echo %~nxi	%i	1 >> " . path
	
	let cmd = "for /r ./ %i in (*) do @echo %i> " . path
	call s:system(cmd)

    let ignore_dirs = copy(g:lookupfile_ignore_dirs)
    if exists("g:ignore_dirs")
        call extend(ignore_dirs, g:ignore_dirs)
    endif
    let ignore_fts = copy(g:lookupfile_ignore_fts)
    if exists("g:ignore_fts")
        call extend(ignore_fts, g:ignore_fts)
    endif

    let files_all = readfile(path)
    let files = []
    for file_path in files_all
        let is_ignore = 0
        for ignore_dir in ignore_dirs
            if file_path =~ ignore_dir . '\\'
                let is_ignore = 1
                break
            endif
        endfor

        if is_ignore == 0 
            for ignore_ft in ignore_fts
                if file_path =~ ignore_ft . "$"
                    " let is_ignore = 1
                    break
                endif
            endfor
        endif

        if is_ignore == 0 
            call add(files, file_path)
        endif
    endfor
    call writefile(files, path)
endfunction

function! s:refresh_filelist_unix()
    let path = s:get_cache_path_filelist()

    call s:system("echo '!_TAG_FILE_SORTED	2	/2=foldcase/' > " . path)

    let cmd = 'find ' . escape(fnamemodify("./", ":p"), ' \')

    let ignore_dirs = copy(g:lookupfile_ignore_dirs)
    if exists("g:ignore_dirs")
        call extend(ignore_dirs, g:ignore_dirs)
    endif
    let ignore_fts = copy(g:lookupfile_ignore_fts)
    if exists("g:ignore_fts")
        call extend(ignore_fts, g:ignore_fts)
    endif

    let ignore_dir_cnt = len(ignore_dirs)
    if ignore_dir_cnt > 0
        if ignore_dir_cnt > 1
            let cmd = cmd . ' \( '
        endif

        let ignore_dir_idx = 0
        for ignore_dir in ignore_dirs
            let cmd = cmd . ' -name "' . ignore_dir . '"'

            let ignore_dir_idx = ignore_dir_idx + 1
            if ignore_dir_idx < ignore_dir_cnt
                let cmd = cmd . ' -o '
            endif
        endfor

        for ignore_tp in ignore_fts 
            let cmd = cmd . ' -o -name "*' . ignore_tp . '"'
        endfor

        if ignore_dir_cnt > 1
            let cmd = cmd . ' \) '
        endif

        let cmd = cmd . ' -prune -o'

        " find . \( -name '*.svn*' -prune  -o ! -name '*.html' \)
    endif

    let cmd = cmd . ' -type f -printf "%p\n" > ' . path
    " let cmd = cmd . ' -type f -printf "%f\t%p\t1\n" >> ' . path

    " echomsg cmd

    call s:system(cmd)
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


" source buffer
let s:source_buf = {
    \   'name': 'look/b',
    \   'description': 'candidates from lookup buffer',
    \   'max_candidates': 30,
    \   'hooks': {},
    \   'default_kind' : 'file',
    \   'default_action' : {'*' : 'open'},
    \   'syntax': 'uniteSource__LookupBuf',
    \   'is_volatile': 1,
\}

" source buffer
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

" source file & buffer
let s:source_filebuf = {
    \   'name': 'look/fb',
    \   'description': 'candidates from lookup file and buffer',
    \   'max_candidates': 50,
    \   'hooks': {},
    \   'default_kind' : 'file',
    \   'default_action' : {'*' : 'open'},
    \   'syntax': 'uniteSource__LookupFile',
    \   'is_volatile': 1,
\}


" source file & buffer
let s:source_filemru = {
    \   'name': 'look/fm',
    \   'description': 'candidates from lookup file and mru',
    \   'max_candidates': 50,
    \   'hooks': {},
    \   'syntax': 'uniteSource__LookupFile',
    \   'is_volatile': 1,
\}

function! s:reset_context(args, context)
    let input = a:context.input
    let pattern = ':'
    let arr = split(input, ':\zs')
    " if len(arr) > 1
    "     echoerr arr[0]
    " endif
    let preType = ""
    for key in arr 
        let keyInput = key
        let lastChar = key[len(key) - 1]
        if lastChar =~ pattern
            if len(key) >= 2 
                let keyInput = key[0:len(key) - 2]
            else
                let keyInput = ""
            endif
        endif

        if preType == ""
            let a:context.input = keyInput
        elseif preType == ":"
            let a:context.lineno = keyInput
        endif

        if lastChar =~ pattern
            let preType = lastChar
        else
            let preType = ""
        endif
    endfor
endfunction

function! s:load_tags(args, context)
    let a:context.tags = &tags
    let &tags = eval(string(s:get_cache_path_filelist()))
endfunction

function! s:resume_tags(args, context)
    let &tags = a:context.tags
endfunction

function! s:source_file.hooks.on_init(args, context)
    let a:context.exclude_buffer = 0
    let a:context.exclude_mru  = 0
    let a:context.current_buffer = fnamemodify(bufname('%'), ":p")
    call s:load_tags(a:args, a:context)
endfunction

function! s:source_file.hooks.on_close(args, context)
    call unite#filters#matcher_py_fuzzy#clean(a:context)
    call s:resume_tags(a:args, a:context)
endfunction

function! s:source_filebuf.hooks.on_init(args, context)
    let a:context.exclude_buffer = 1
    let a:context.exclude_mru  = 0
    let a:context.current_buffer = bufname('%')
    call s:load_tags(a:args, a:context)
endfunction

function! s:source_filebuf.hooks.on_close(args, context)
    call unite#filters#matcher_py_fuzzy#clean(a:context)
    call s:resume_tags(a:args, a:context)
endfunction

function! s:source_filemru.hooks.on_init(args, context)
    let a:context.exclude_buffer = 0
    let a:context.exclude_mru  = 1
    let a:context.current_buffer = fnamemodify(bufname('%'), ":p")
    call s:update_mru_map()
    call s:load_tags(a:args, a:context)
endfunction

function! s:source_filemru.hooks.on_close(args, context)
    call unite#filters#matcher_py_fuzzy#clean(a:context)
    call s:resume_tags(a:args, a:context)
    call s:clean_mru_map()
endfunction

function! s:source_file.gather_candidates(args, context)
    let a:context.mmode = "filename-only"
    return s:gather_candidates_file(a:args, a:context)
endfunction

function! s:source_buf.hooks.on_init(args, context)
    let a:context.current_buffer = bufname('%')
endfunction

function! s:source_buf.gather_candidates(args, context)
    let a:context.mmode = "filename-only"
    return s:gather_candidates_buf(a:args, a:context)
endfunction

function! s:source_mru.gather_candidates(args, context)
    let a:context.mmode = "filename-only"
    return s:gather_candidates_mru(a:args, a:context)
endfunction

function! s:source_mru.hooks.on_init(args, context)
    let a:context.current_buffer = bufname('%')
endfunction

function! s:source_filebuf.gather_candidates(args, context)
    let a:context.mmode = "filename-only"

    let candidates_buffer = s:gather_candidates_buf(a:args, a:context)
    let candidates_file   = s:gather_candidates_file(a:args, a:context)
    let candidates_curr = s:gather_candidates_current_buf(a:args, a:context)

    let result = extend(candidates_buffer, candidates_curr)
    let result = extend(result, candidates_file)

    return result
endfunction

function! s:source_filemru.gather_candidates(args, context)
    let a:context.mmode = "filename-only"

    if len(a:context.input) < 3 
        let candidates_mru  = s:gather_candidates_mru(a:args, a:context)
        let candidates_file = s:gather_candidates_file(a:args, a:context)
        let candidates_curr = s:gather_candidates_current_buf(a:args, a:context)

        let result = extend(candidates_mru, candidates_curr)
        let result = extend(result, candidates_file)

        return result
    else
        return s:gather_candidates_file(a:args, a:context)
    endif
endfunction

let s:cached_result = []

function! s:gather_candidates_file(args, context)
    if a:context.is_redraw || !filereadable(s:get_cache_path_filelist())
        call s:refresh_filelist()
        let s:cached_result = []
    endif

    let refresh = 0
    if empty(s:cached_result) 
        let s:cached_result = readfile(s:get_cache_path_filelist())
        let refresh = 1
    endif

    let context = a:context
    let context.source_name = "lookup/file"

    let inputs = split(a:context.input, ';')

    let input = a:context.input
    if len(inputs) > 0 
        let input = inputs[0]
    endif

    let input_dir = ""
    if len(inputs) > 1 
        let input_dir = inputs[1]
        echo input_dir
    endif

    let a:context.input = input
    let match_result = unite#filters#matcher_py_fuzzy#matcher(a:context, s:cached_result, refresh)

    let result = []

    if len(input) < 3 
        let tag_idx = 0
        while tag_idx < len(match_result)
            let file = match_result[tag_idx]
            if   (a:context.exclude_buffer && buflisted(file))
            \ || (a:context.exclude_mru && s:mrulisted(file))
                let tag_idx = tag_idx + 1
                continue
            endif

            call add(result, file)

            let tag_idx = tag_idx + 1
        endwhile
    else
        let result = match_result
    endif

    " 需要过滤目录
    if input_dir != "" 
        let result_cp = result
        let result = []
        let fuzzy_input = unite#sources#lookup_file#get_fuzzy_pattern(input_dir)
        let tag_idx = 0
        while tag_idx < len(match_result)
            let file = match_result[tag_idx]
            let dir = fnamemodify(file, ":.:h")
            if dir =~ fuzzy_input
                call add(result, file)
            endif
            
            let tag_idx = tag_idx + 1
        endwhile
    endif

    return map(result, "{
          \ 'word': v:val,
          \ 'abbr': printf('%s', fnamemodify(v:val, ':.')),
          \ 'kind' : 'file',
          \ 'group': 'file',
          \ 'action__path': v:val,
          \ }")
endfunction

function! s:gather_candidates_buf(args, context)
    if s:is_init_buf == 0
        " echomsg "init buffer"
        call s:buflist_init()
    endif

    let context = a:context
    let context.source_name = "lookup/buf"

    let buffers = s:get_buflist(a:context.current_buffer)
    let buffers_filter = unite#filters#matcher_py_fuzzy#matcher(context, buffers, 1)

    return map(buffers_filter, "{
          \ 'word': fnamemodify(v:val, ':t'),
          \ 'abbr': printf('%s', fnamemodify(v:val, ':p:.')),
          \ 'kind'  : 'buffer',
          \ 'group' : 'buffer',
          \ 'action__path': v:val,
          \ 'action__buffer_nr':bufnr(v:val),
          \ }")
endfunction

function! s:gather_candidates_mru(args, context)
    let context = a:context
    let context.source_name = "lookup/mru"

    let buffers = s:get_mrulist(a:context.current_buffer)
    let buffers_filter = unite#filters#matcher_py_fuzzy#matcher(context, buffers, 1)

    let result = map(buffers_filter, "{
          \ 'word': fnamemodify(v:val, ':t'),
          \ 'abbr': printf('%s', fnamemodify(v:val, ':p:.')),
          \ 'kind'  : 'file',
          \ 'group' : 'file',
          \ 'action__path': v:val,
          \ }")
    return result
endfunction

function! s:gather_candidates_current_buf(args, context)
    let buf = a:context.current_buffer
    let buffers_filter = []

    if !buflisted(buf) 
        return []
    endif

    let pattern_input = unite#sources#lookup_file#get_fuzzy_pattern(a:context.input)
    if fnamemodify(buf, ':t') !~ pattern_input
        return []
    endif

    call add(buffers_filter, fnamemodify(buf, ":p"))

    let result = map(buffers_filter, "{
          \ 'word': fnamemodify(v:val, ':t'),
          \ 'abbr': printf('[E] %s', fnamemodify(v:val, ':p:.')),
          \ 'kind'  : 'buffer',
          \ 'group' : 'buffer',
          \ 'action__path': v:val,
          \ 'action__buffer_nr':bufnr(v:val),
          \ }")
    return s:sort_result(result, a:context.input)
endfunction

function s:sort_result(result, input)
    if len(a:result) == 0
        return []
    endif

    return unite#filters#sorter_selecta#_sort(a:result, a:input)
endfunction

function! unite#sources#lookup_file#get_fuzzy_pattern(pattern)
    " return '\c' . a:pattern
    let pattern_len = strlen(a:pattern)
    let fuzzy_pattern = '\c'
    let pattern_idx = 0

    while pattern_idx < pattern_len
        let char = a:pattern[pattern_idx]

        if char =~ '[a-zA-Z_]'
            let fuzzy_pattern = fuzzy_pattern . char . '.*'
        else
            let fuzzy_pattern = fuzzy_pattern . char
        endif

        let pattern_idx = pattern_idx + 1
    endwhile

    return fuzzy_pattern
endfunction
