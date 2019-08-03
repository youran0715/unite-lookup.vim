au BufEnter * call unite#sources#lookup_file#buf_enter()
au VimEnter * call unite#sources#lookup_file#vim_enter()
au VimLeave * call unite#sources#lookup_file#vim_leave()
command! MruClean :call unite#sources#lookup_file#clean_mru()
