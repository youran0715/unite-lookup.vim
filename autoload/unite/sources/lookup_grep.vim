let s:plugin_path = escape(expand('<sfile>:p:h'), '\')
execute 'py3file ' . s:plugin_path . '/lookup_grep.py'

let s:source_grep = {
    \   'name': 'look/grep',
    \   'description': 'candidates from grep',
    \   'max_candidates': 100,
    \   'hooks': {},
    \   'kind': 'file',
    \   'syntax': 'uniteSource__LookupFile',
    \   'is_volatile': 1,
\}

" define source
function! unite#sources#lookup_grep#define()
    return [s:source_grep]
endfunction

function! s:source_grep.gather_candidates(args, context)
    let s:rez = []
    let s:inputs = a:context["input"]

    execute 'python3 gather_candidates()'

    return s:rez
endfunction
