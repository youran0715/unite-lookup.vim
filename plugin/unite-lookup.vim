au BufEnter * call unite#sources#lookup_file#buf_enter()
command! MruClean :call unite#sources#lookup_file#clean_mru()
