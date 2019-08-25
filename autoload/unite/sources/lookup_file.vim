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
    let g:lookupfile_FollowLinks=v:true
endif

if !exists("g:lookupfile_IndexTimeLimit")
    let g:lookupfile_IndexTimeLimit=120
endif

let s:is_inited = 0
function! unite#sources#lookup_file#vim_enter()
    if !s:is_inited
        let s:cache_dir = s:get_cache_dir()
        execute 'python3 UnitePyLookupSetCacheDir()'
        execute 'python3 UnitePyLookupMruLoad()'
        let s:is_inited = 1
    endif
endfunction

function! unite#sources#lookup_file#vim_leave()
    execute 'python3 UnitePyLookupMruSave()'
endfunction

function! unite#sources#lookup_file#clean_mru()
    execute 'python3 UnitePyLookupMruClean()'
endfunction

function! unite#sources#lookup_file#buf_enter()
    let s:buf_path = bufname("%")
    if !filereadable(s:buf_path)
        return
    endif

    execute 'python3 UnitePyLookupMruAdd()'
endfunction

" define source
function! unite#sources#lookup_file#define()
    return [s:source_filemru]
endfunction

function! s:get_cache_dir()
    return expand($HOME) . "/.cache/vim/lookupfile/"
endfunction

let s:plugin_path = escape(expand('<sfile>:p:h'), '\')
execute 'py3file ' . s:plugin_path . '/lookup_vim.py'

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
    let a:context.ft = &ft
endfunction

function! s:source_filemru.gather_candidates(args, context)
    if a:context.is_redraw
        execute 'python3 UnitePyLookupMixRedraw()'
    endif

    let s:inputs = a:context['input']
    let s:ft = a:context.ft
    let s:rez = []

    execute 'python3 UnitePyLookupMixSearch()'

    return s:rez
endfunction

