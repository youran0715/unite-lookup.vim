
function! unite#filters#matcher_none#define()
  return s:matcher
endfunction

let s:matcher = {
      \ 'name' : 'matcher_none',
      \ 'description' : 'none matcher',
      \}

function! s:matcher.pattern(input) "{{{
  let [head, input] = unite#filters#matcher_fuzzy#get_fuzzy_input(
        \ unite#util#escape_match(a:input))
  return substitute(head . substitute(input,
        \ '\([[:alnum:]_/-]\|\\\.\)\ze.', '\0.\\{-}', 'g'), '\*\*', '*', 'g')
endfunction"}}}

function! s:matcher.filter(candidates, context)
    return a:candidates
endfunction
