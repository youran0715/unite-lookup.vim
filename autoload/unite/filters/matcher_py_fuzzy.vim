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

function! unite#filters#matcher_py_fuzzy#clean(context) abort "{{{
    let source_name = a:context.source_name
    if has_key(s:cache, source_name) 
        let s:cache[source_name] = {}
    endif
endfunction "}}}

function! unite#filters#matcher_py_fuzzy#matcher(context, items, refresh) abort "{{{
    let s:input = a:context.input
    let s:mmode = a:context.mmode
    let source_name = a:context.source_name

    if !has_key(s:cache, source_name) || a:refresh
        let s:cache[source_name] = {}
    endif

    if !has_key(s:cache[source_name], "result") || a:refresh
        let s:cache[source_name].result = {}
    endif

    let s:rez = []
    if s:input == "" 
        let s:rez = deepcopy(a:items)
    else 
        let input_key = s:get_input_key(s:input)
        if has_key(s:cache[source_name].result, input_key) 
            return deepcopy(s:cache[source_name].result[input_key])
        endif

        let previous_input = strpart(s:input, 0, len(s:input) - 1)
        let p_input_key = s:get_input_key(previous_input)

        if has_key(s:cache[source_name].result, p_input_key) 
            let s:items = deepcopy(s:cache[source_name].result[p_input_key])
        else
            let s:items = a:items
        endif

        execute 'python' . (has('python3') ? '3' : '') . ' UnitePyMatch()'
    endif

    let s:cache[source_name].result[s:get_input_key(s:input)] = deepcopy(s:rez)

    return s:rez
endfunction

let &cpo = s:save_cpo
unlet s:save_cpo
