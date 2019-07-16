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

    let items = a:items

    " echo a:context

    if s:input == ""
        let s:cache={}
        " echo "clear cache"
        return a:items[:a:limit - 1]
    else
        let cache_key_pre = a:context['cache_type'] . "_" . s:input[:-2]
        " 判断前面输入的是否有缓存
        if has_key(s:cache, cache_key_pre)
            " echo "load cache " . cache_key_pre
            let items = s:cache[cache_key_pre]
        endif
    endif

    let s:rez = []
    let s:rows = []
    let s:items = items
    execute 'python' . (has('python3') ? '3' : '') . ' UnitePyMatch()'

    let cache_key_now = a:context['cache_type'] . "_" . s:input
    let s:cache[cache_key_now] = s:rows

    return s:rez
endfunction

let &cpo = s:save_cpo
unlet s:save_cpo
