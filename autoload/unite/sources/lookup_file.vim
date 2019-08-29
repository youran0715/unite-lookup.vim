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
    let srcs = []
    call add(srcs, s:define_source('look/fm', ['mru', 'edit', 'file']))
    call add(srcs, s:define_source('look/goimport', ['goimport']))
    call add(srcs, s:define_source('look/command', ['command']))
    call add(srcs, s:define_source('look/grep', ['grep']))
    return srcs
endfunction

function! s:get_cache_dir()
    return expand($HOME) . "/.cache/vim/lookupfile/"
endfunction

let s:lookup_plugin_path = escape(expand('<sfile>:p:h'), '\')
execute 'py3file ' . s:lookup_plugin_path . '/lookup_vim.py'

fun s:define_source(name, src_names)
    let src = {
        \   'name': a:name,
        \   'description': 'candidates from lookup ' . a:name,
        \   'max_candidates': 20,
        \   'hooks': {},
        \   'syntax': 'uniteSource__Lookup',
        \   'is_volatile': 1,
        \}

    execute 'python3 UnitePyLookupDefineSource()'

    let src.hooks.on_init = s:src.on_init
    let src.gather_candidates = s:src.gather_candidates

    return src
endf

let s:src = {}
function! s:src.on_init(args, context)
    let a:context['current_buffer'] = fnamemodify(bufname('%'), ":p")
    execute 'python3 UnitePyLookupInit()'
endfunction

function! s:src.gather_candidates(args, context)
    if a:context.is_redraw
        execute 'python3 UnitePyLookupRedraw()'
    endif

    let s:rez = []
    execute 'python3 UnitePyLookupSearch()'
    return s:rez
endfunction

