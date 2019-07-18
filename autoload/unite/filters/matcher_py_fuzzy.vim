let s:save_cpo = &cpo
set cpo&vim

let s:plugin_path = escape(expand('<sfile>:p:h'), '\')

if has('python3')
  execute 'py3file ' . s:plugin_path . '/pymatcher.py'
else
  execute 'pyfile ' . s:plugin_path . '/pymatcher.py'
endif

function! unite#filters#matcher_py_fuzzy#clearcache(key) abort "{{{
    let s:key = a:key
    execute 'python3 ClearCache()'
endfunction "}}}

function! unite#filters#matcher_py_fuzzy#setcandidates(key, items) abort "{{{
    let s:key = a:key
    let s:items = a:items

    execute 'python3 SetCandidates()'
endfunction "}}}

function! unite#filters#matcher_py_fuzzy#loadcandidates(key, path) abort "{{{
    let s:key = a:key
    let s:path = a:path

    execute 'python3 LoadCandidates()'
endfunction "}}}

function! unite#filters#matcher_py_fuzzy#matcher(context, limit) abort "{{{
    let s:input = a:context.input
    let s:mmode = a:context.mmode
    let s:limit = a:limit
    let s:key = a:context.cache_type

    let s:rez = []
    let s:rows = []
    execute 'python' . (has('python3') ? '3' : '') . ' UnitePyMatch()'

    return s:rez
endfunction "}}}

let &cpo = s:save_cpo
unlet s:save_cpo
