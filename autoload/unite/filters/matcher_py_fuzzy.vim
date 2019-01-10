let s:save_cpo = &cpo
set cpo&vim

let s:plugin_path = escape(expand('<sfile>:p:h'), '\')

if has('python3')
  execute 'py3file ' . s:plugin_path . '/pymatcher.py'
else
  execute 'pyfile ' . s:plugin_path . '/pymatcher.py'
endif

let s:cache = {}

function! s:get_input_key(input)
    return "input:" . a:input
endfunction

function! unite#filters#matcher_py_fuzzy#matcher(context, items, limit) abort "{{{
    let s:input = a:context.input
    let s:mmode = a:context.mmode
    let s:limit = a:limit

    if s:input == ""
        return a:items
    endif

    let s:rez = []
    let s:items = a:items
    execute 'python' . (has('python3') ? '3' : '') . ' UnitePyMatch()'

    return s:rez
endfunction

let &cpo = s:save_cpo
unlet s:save_cpo
