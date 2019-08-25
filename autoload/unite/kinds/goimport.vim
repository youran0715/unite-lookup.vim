let s:save_cpo = &cpo
set cpo&vim

let &cpo = s:save_cpo
unlet s:save_cpo

function! s:cmd_for(name) abort
    if exists('g:unite_source_go_import_' . a:name . '_cmd')
        return g:unite_source_go_import_{a:name}_cmd
    endif

    let camelized = toupper(a:name[0]) . a:name[1:]

    if exists(':' . camelized)
        let g:unite_source_go_import_{a:name}_cmd = camelized
        return camelized
    else
        " For vim-go
        let name = a:name =~# '^go' ? a:name[2:] : a:name
        let camelized = 'Go' . toupper(name[0]) . name[1:]

        if exists(':' . camelized)
            let g:unite_source_go_import_{a:name}_cmd = camelized
            return camelized
        endif
    endif

    return ''
endfunction

function! unite#kinds#goimport#define() abort "{{{
  return s:kind
endfunction"}}}

let s:kind = {
      \ 'name' : 'goimport',
      \ 'default_action' : 'import',
      \ 'action_table': {},
      \}

let s:kind.action_table.import = {
            \ 'description' : 'Import Go package(s)',
            \ 'is_selectable' : 1,
            \ }

function! s:kind.action_table.import.func(candidates) abort
    let cmd = s:cmd_for('import')
    if cmd ==# '' | return | endif

    for candidate in a:candidates
        execute cmd candidate.word
    endfor
endfunction

let s:kind.action_table.import_as = {
            \ 'description' : 'Import Go package with local name',
            \ 'is_selectable' : 0,
            \ }

function! s:kind.action_table.import_as.func(candidate) abort
    let local_name = input('Enter local name: ')
    if local_name ==# ''
        echo 'Canceled.'
        return
    endif

    let cmd = s:cmd_for('importAs')
    if cmd ==# '' | return | endif

    execute cmd local_name a:candidate.word
endfunction

let s:kind.action_table.drop = {
            \ 'description' : 'Drop Go package(s)',
            \ 'is_selectable' : 1,
            \ }

function! s:kind.action_table.drop.func(candidates) abort
    let cmd = s:cmd_for('drop')
    if cmd ==# '' | return | endif

    for candidate in a:candidates
        execute cmd candidate.word
    endfor
endfunction

let s:kind.action_table.godoc = {
            \ 'description' : 'Show documentation for the package',
            \ 'is_selectable' : 0,
            \ }

function! s:kind.action_table.godoc.func(candidate) abort
    let cmd = s:cmd_for('godoc')
    if cmd ==# '' | return | endif
    execute cmd a:candidate.word
endfunction

let s:kind.action_table.godoc_browser = {
            \ 'description' : 'Show documentation for the package with browser',
            \ 'is_selectable' : 1,
            \ }

function! s:kind.action_table.godoc_browser.func(candidates) abort
    if exists(':OpenBrowser')
        for c in a:candidates
            execute 'OpenBrowser' 'https://godoc.org/' . c.word
        endfor
        return
    endif

    let cmdline = ''
    if has('win32') || has('win64')
        let cmdline = '!start "https://godoc.org/%s"'
    elseif (has('mac') || has('macunix') || has('gui_macvim')) && executable('sw_vers')
        let cmdline = 'open "https://godoc.org/%s"'
    elseif executable('xdg-open')
        let cmdline = 'xdg-open "https://godoc.org/%s"'
    endif

    if cmdline ==# ''
        echohl ErrorMsg | echomsg 'No command was found to open a browser' | echohl None
        return
    endif

    for c in a:candidates
        let output = system(printf(cmdline, c.word))
        if v:shell_error
            echohl ErrorMsg | echomsg 'Error on opening a browser: ' . output | echohl None
            return
        endif
    endfor
endfunction

let s:kind.action_table.preview = {
            \ 'description' : 'Preview the package with godoc',
            \ 'is_quit' : 0,
            \ }

function! s:kind.action_table.preview.func(candidate) abort
    let cmd = s:cmd_for('godoc')
    if cmd ==# '' | return | endif
    let b = bufnr('%')

    execute cmd a:candidate.word
    setlocal previewwindow
    let bufnr = bufnr('%')

    let w = bufwinnr(b)
    execute w . 'wincmd w'

    if !buflisted(bufnr)
        call unite#add_previewed_buffer_list(bufnr)
    endif
endfunction

" vim: foldmethod=marker
