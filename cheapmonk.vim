function! StartWriting(delay) abort
    let s:thisBuf = bufname('%')
    let s:write_channel = ch_open('localhost:8766')
    call ch_sendexpr(s:write_channel,"%%write_signal%%")
    let s:writeTimer = timer_start(a:delay,'Write',{'repeat' : -1})
endfunction

function! StopWriting() abort
    call timer_stop(s:writeTimer)
    call ch_close(s:write_channel)
endfunction

function! Write(timer_id) abort
    let l:thatBuf = bufname('%')
    call SavePreviousFile()
    if l:thatBuf ==# s:thisBuf
        execute "write"
        let l:addendum = GetAdditions(s:thisBuf)
        let l:status = ch_status(s:write_channel)
        if l:status ==# "open"
            call ch_sendexpr(s:write_channel, l:addendum) 
        endif
    endif
endfunction

function! GetAdditions(thisFile) abort
    let l:returnVal = ""
python3 << EOF
import difflib, vim
fname = vim.eval("a:thisFile")
f1 = open('.tmp', 'r+')
f2 = open(str(fname), 'r+')
s1 = f1.readlines()
s2 = f2.readlines()
for line in difflib.unified_diff(s1,s2, fromfile = '.tmp', tofile = str(fname)):
    if(line[0] == '+' and not line[1] == '+'):
        vim.command("let l:returnVal = \"" + line[1:line.index('\n')] + "\"")
        break
EOF
    return l:returnVal
endfunction

function! SavePreviousFile() abort
    let l:thisFileName = @%
python3 << EOF

import vim, shutil

fileName = vim.eval("l:thisFileName")
shutil.copyfile(fileName,".tmp")
EOF
endfunction

function! StartReading() abort
    let s:read_channel = ch_open('localhost:8765')
    call ch_sendexpr(s:read_channel,"%%read_signal%%")
endfunction

function! StopReading() abort
    call ch_close(s:read_channel)
endfunction
