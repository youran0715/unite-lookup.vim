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

let s:is_inited = 0
function! unite#sources#lookup_file#vim_enter()
    if !s:is_inited
        let s:file_path = s:get_cache_path_mrulist()
        if filereadable(s:file_path)
            execute 'python3 UnitePyLoadMrus()'
        endif
        let s:is_inited = 1
    endif
endfunction

function! unite#sources#lookup_file#vim_leave()
    let s:file_path = s:get_cache_path_mrulist()
    execute 'python3 UnitePySaveMrus()'
endfunction

function! unite#sources#lookup_file#buf_enter()
    let s:buf_path = bufname("%")
    if !filereadable(s:buf_path)
        return
    endif

    execute 'python3 UnitePyAddMru()'
endfunction

" define source
function! unite#sources#lookup_file#define()
    return [s:source_filemru]
endfunction

function! s:get_cache_dir()
	set shellslash
    let cache_dir = expand($HOME) . "/.cache/vim/lookupfile/"

	let cwd = substitute(getcwd(), '/', '_', 'g')
	let cwd = substitute(cwd, ':', '_', 'g')
	let dir = cache_dir . cwd . '/'

    if !isdirectory(dir)
        call mkdir(dir, "p")
    endif

	if g:is_os_windows
		set noshellslash
	endif

    return dir
endfunction

function! s:get_cache_path_filelist()
    return s:get_cache_dir() . 'filelist5'
endfunction

function! s:get_cache_path_mrulist()
    return s:get_cache_dir() . 'mrulist5'
endfunction

let s:plugin_path = escape(expand('<sfile>:p:h'), '\')
execute 'py3file ' . s:plugin_path . '/lookup_file.py'

function! s:refresh_filelist()
    let s:file_list=[]
    let s:file_path = s:get_cache_path_filelist()

    let s:dir_path= escape(fnamemodify("./", ":p"), ' \')

    let s:dir_path= fnamemodify("./", ":p")
    execute 'python3 UnitePyGetFileList()'
endfunction

" source file & mru
let s:source_filemru = {
    \   'name': 'look/fm',
    \   'description': 'candidates from lookup file and mru',
    \   'max_candidates': 50,
    \   'hooks': {},
    \   'kind': 'file',
    \   'syntax': 'uniteSource__LookupFile',
    \   'is_volatile': 1,
\}

function! s:source_filemru.hooks.on_init(args, context)
    let a:context.exclude_mru  = 1
    let a:context.current_buffer = fnamemodify(bufname('%'), ":p")
    if a:context.is_redraw
        " call unite#filters#matcher_py_fuzzy#clearcache(s:cache_key)
    endif
endfunction

function! s:load_filelist()
    let s:file_path = s:get_cache_path_filelist()
    execute 'python3 UnitePyLoad()'
endfunction

let s:is_load_file = 0
function! s:source_filemru.gather_candidates(args, context)
    if a:context.is_redraw || !filereadable(s:get_cache_path_filelist())
        call s:refresh_filelist()
        let s:is_load_file = 0
    endif

    if s:is_load_file == 0
        call s:load_filelist()
        let s:is_load_file = 1
    endif

    let s:inputs = a:context['input']
    let s:rez = []
    execute 'python3 UnitePyGetResult()'

    return s:rez
endfunction

