let SessionLoad = 1
if &cp | set nocp | endif
let s:cpo_save=&cpo
set cpo&vim
inoremap <C-U> u
nmap Q gq
xmap Q gq
omap Q gq
vmap gx <Plug>NetrwBrowseXVis
nmap gx <Plug>NetrwBrowseX
vnoremap <silent> <Plug>NetrwBrowseXVis :call netrw#BrowseXVis()<NL>nnoremap <silent> <Plug>NetrwBrowseX :call netrw#BrowseX(expand((exists("g:netrw_gx")? g:netrw_gx : '<cfile>')),netrw#CheckIfRemote())<NL>inoremap  u
inoremap  u
let &cpo=s:cpo_save
unlet s:cpo_save
set autoindent
set background=dark
set display=truncate
set expandtab
set fileencodings=ucs-bom,utf-8,default,latin1
set helplang=en
set hidden
set incsearch
set langnoremap
set nolangremap
set nomodeline
set mouse=a
set nrformats=bin,hex
set path=.,/usr/include,,,**
set printoptions=paper:a4
set ruler
set runtimepath=~/.vim,/var/lib/vim/addons,/etc/vim,/usr/share/vim/vimfiles,/usr/share/vim/vim91,/usr/share/vim/vim91/pack/dist/opt/netrw,/usr/share/vim/vimfiles/after,/etc/vim/after,/var/lib/vim/addons/after,~/.vim/after
set scrolloff=5
set sessionoptions=blank,buffers,folds,help,options,tabpages,winsize,terminal
set shiftwidth=4
set shortmess=filnxtToO
set showcmd
set softtabstop=4
set suffixes=.bak,~,.swp,.o,.info,.aux,.log,.dvi,.bbl,.blg,.brf,.cb,.ind,.idx,.ilg,.inx,.out,.toc
set tabstop=4
set tags=./tags;,tags
set ttimeout
set ttimeoutlen=100
set wildignore=*.pyc
let s:so_save = &g:so | let s:siso_save = &g:siso | setg so=0 siso=0 | setl so=-1 siso=-1
let v:this_session=expand("<sfile>:p")
silent only
silent tabonly
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
if &shortmess =~ 'A'
  set shortmess=aoOA
else
  set shortmess=aoO
endif
badd +23 ~/projects/raspberrypi/balloon_mission/README.md
badd +1 ~/projects/raspberrypi/balloon_mission/main.py
badd +1 ~/projects/raspberrypi/balloon_mission/scripts/check_services.sh
badd +1 ~/projects/raspberrypi/balloon_mission/scripts/copy_services.sh
badd +1 ~/projects/raspberrypi/balloon_mission/scripts/git_pull.sh
badd +1 ~/projects/raspberrypi/balloon_mission/scripts/kill_udp_servers.sh
badd +1 ~/projects/raspberrypi/balloon_mission/scripts/open_vim.sh
badd +1 ~/projects/raspberrypi/balloon_mission/scripts/optimizations
badd +1 ~/projects/raspberrypi/balloon_mission/scripts/run_services.sh
badd +1 ~/projects/raspberrypi/balloon_mission/scripts/run_udp_servers.sh
badd +1 ~/projects/raspberrypi/balloon_mission/scripts/start_udp_servers.sh
badd +1 ~/projects/raspberrypi/balloon_mission/scripts/start_udp_servers_backup.sh
badd +1 ~/projects/raspberrypi/balloon_mission/systemd/README.txt
badd +1 ~/projects/raspberrypi/balloon_mission/systemd/balloon-main.service
badd +1 ~/projects/raspberrypi/balloon_mission/systemd/balloon-udp-chopper.service
badd +1 ~/projects/raspberrypi/balloon_mission/systemd/balloon-udp-gyro.service
badd +1 ~/projects/raspberrypi/balloon_mission/systemd/balloon-udp-pressure.service
badd +1 ~/projects/raspberrypi/balloon_mission/systemd/balloon-udp-receiver.service
badd +1 ~/projects/raspberrypi/balloon_mission/systemd/balloon-udp-spectrometer.service
badd +1 ~/projects/raspberrypi/balloon_mission/systemd/balloon-udp-telemetry.service
badd +1 ~/projects/raspberrypi/balloon_mission/systemd/balloon-udp-temperature.service
badd +1 ~/projects/raspberrypi/balloon_mission/systemd/balloon-udp@.service
badd +1 ~/projects/raspberrypi/balloon_mission/systemd/todo.txt
badd +1 ~/projects/raspberrypi/balloon_mission/docs/analysis.md
badd +1 ~/projects/raspberrypi/balloon_mission/docs/cheat_sheet.txt
badd +1 ~/projects/raspberrypi/balloon_mission/docs/hardware
badd +1 ~/projects/raspberrypi/balloon_mission/docs/lose\ notes.txt
badd +1 ~/projects/raspberrypi/balloon_mission/docs/measurement
badd +1 ~/projects/raspberrypi/balloon_mission/docs/python\ test\ ideas.txt
badd +1 ~/projects/raspberrypi/balloon_mission/docs/systemd
badd +1 ~/projects/raspberrypi/balloon_mission/docs/systemd_diagnostics
badd +1 ~/projects/raspberrypi/balloon_mission/docs/todo
badd +1 ~/projects/raspberrypi/balloon_mission/docs/todo.md
badd +1 ~/projects/raspberrypi/balloon_mission/docs/udp.md
badd +1 ~/projects/raspberrypi/balloon_mission/docs/uv_pip.md
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/__init__.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/__init__.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/add_to_noise_temperature_folder_viewer.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/background_analysis.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/background_analysis_utils.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/cold_load_temperature_over_time.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/cold_load_temperature_viewer.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/gyro_analysis.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/hot_cold_folder_analysis.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/hot_cold_folder_analysis_v1.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/hot_cold_folder_viewer.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/hot_cold_folder_viewer_v1.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/hot_cold_folder_viewer_v2.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/hot_cold_folder_viewer_v3.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/hot_cold_folder_viewer_v4.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/hot_cold_folder_viewer_v5.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/noise_temperature_all_dumbs_over_time.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/noise_temperature_all_dumbs_over_time_v1.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/noise_temperature_average_over_time.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/noise_temperature_frequency_scan.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/noise_temperature_over_time_v1.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/pressure_analysis.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/single_spec_file_viewer.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/spec_analysis_index_range_old.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/spec_analysis_simple_old.py
badd +272 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/spec_analysis_utils.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/spec_analysis_utils_v1.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/spec_analysis_utils_v3_trash.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/spec_folder_to_csv_converter.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/spec_folder_viewer.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/spec_folder_viewer_v1.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/spec_folder_viewer_v2.0.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/spec_to_csv_converter.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/spec_viewer.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/t_format_converter.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/telemetry_analysis.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/temperature_analysis.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/y_factor_all_dumps_over_time.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/y_factor_all_dumps_over_time_v1.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/y_factor_all_dumps_over_time_v2.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/y_factor_average_over_time.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/devices/__init__.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/devices/chopper_control.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/devices/gyro_sensor.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/devices/led_control.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/devices/led_control_old.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/devices/led_simple.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/devices/pressure_sensor.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/devices/receiver_control.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/devices/spectrometer_backend.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/devices/spectrometer_control.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/devices/telemetry_sensor.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/devices/temperature_sensor.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/devices/temperature_sensor_v1.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/udp/__init__.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/udp/chopper_udp_server.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/udp/gyro_udp_server.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/udp/led_udp_server.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/udp/pressure_udp_server.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/udp/receiver_udp_server.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/udp/spectrometer_udp_server.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/udp/spectrometer_udp_server_backup.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/udp/telemetry_udp_server.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/udp/temperature_udp_server.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/udp/temperature_udp_server_v1.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/udp/udp_utility.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/utility/__init__.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/utility/analysis_utility.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/utility/parser_utility.py
badd +1 ~/projects/raspberrypi/balloon_mission/src/balloon/utility/verbose_utils.py
badd +1 ~/projects/raspberrypi/balloon_mission/config/README.md
badd +1 ~/projects/raspberrypi/balloon_mission/Untitled
badd +64 ~/projects/raspberrypi/balloon_mission/Session.vim
badd +1 ~/dotfiles/vimrc
badd +0 ~/projects/raspberrypi/balloon_mission/\!/bin/bash
argglobal
%argdel
set stal=2
tabnew +setlocal\ bufhidden=wipe
tabrewind
edit ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/spec_analysis_utils.py
let s:save_splitbelow = &splitbelow
let s:save_splitright = &splitright
set splitbelow splitright
wincmd _ | wincmd |
split
1wincmd k
wincmd _ | wincmd |
vsplit
1wincmd h
wincmd w
wincmd w
let &splitbelow = s:save_splitbelow
let &splitright = s:save_splitright
wincmd t
let s:save_winminheight = &winminheight
let s:save_winminwidth = &winminwidth
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
exe '1resize ' . ((&lines * 38 + 35) / 70)
exe 'vert 1resize ' . ((&columns * 140 + 140) / 280)
exe '2resize ' . ((&lines * 38 + 35) / 70)
exe 'vert 2resize ' . ((&columns * 139 + 140) / 280)
exe '3resize ' . ((&lines * 28 + 35) / 70)
argglobal
balt ~/projects/raspberrypi/balloon_mission/Session.vim
setlocal keymap=
setlocal noarabic
setlocal autoindent
setlocal backupcopy=
setlocal balloonexpr=
setlocal nobinary
setlocal nobreakindent
setlocal breakindentopt=
setlocal bufhidden=
setlocal buflisted
setlocal buftype=
setlocal nocindent
setlocal cinkeys=0{,0},0),0],:,!^F,o,O,e
setlocal cinoptions=
setlocal cinscopedecls=public,protected,private
setlocal cinwords=if,else,while,do,for,switch
setlocal colorcolumn=
setlocal comments=b:#,fb:-
setlocal commentstring=#\ %s
setlocal complete=.,w,b,u,t,i
setlocal completefunc=
setlocal completeopt=
setlocal concealcursor=
setlocal conceallevel=0
setlocal nocopyindent
setlocal cryptmethod=
setlocal nocursorbind
setlocal nocursorcolumn
setlocal nocursorline
setlocal cursorlineopt=both
setlocal define=^\\s*\\(\\(async\\s\\+\\)\\?def\\|class\\)
setlocal dictionary=
setlocal nodiff
setlocal equalprg=
setlocal errorformat=
setlocal eventignorewin=
setlocal expandtab
if &filetype != 'python'
setlocal filetype=python
endif
setlocal fillchars=
setlocal findfunc=
setlocal fixendofline
setlocal foldcolumn=0
setlocal foldenable
setlocal foldexpr=0
setlocal foldignore=#
setlocal foldlevel=0
setlocal foldmarker={{{,}}}
set foldmethod=indent
setlocal foldmethod=indent
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldtext=foldtext()
setlocal formatexpr=
setlocal formatlistpat=^\\s*\\d\\+[\\]:.)}\\t\ ]\\s*
setlocal formatoptions=tcq
setlocal formatprg=
setlocal grepprg=
setlocal iminsert=0
setlocal imsearch=-1
setlocal include=^\\s*\\(from\\|import\\)
setlocal includeexpr=substitute(substitute(substitute(v:fname,b:grandparent_match,b:grandparent_sub,''),b:parent_match,b:parent_sub,''),b:child_match,b:child_sub,'g')
setlocal indentexpr=python#GetIndent(v:lnum)
setlocal indentkeys=0{,0},0),0],:,!^F,o,O,e,<:>,=elif,=except
setlocal noinfercase
setlocal iskeyword=@,48-57,_,192-255
setlocal keywordprg=python3\ -m\ pydoc
setlocal nolinebreak
setlocal nolisp
setlocal lispoptions=
setlocal lispwords=
setlocal nolist
setlocal listchars=
setlocal makeencoding=
setlocal makeprg=
setlocal matchpairs=(:),{:},[:]
setlocal nomodeline
setlocal modifiable
setlocal nrformats=bin,hex
set number
setlocal number
setlocal numberwidth=4
setlocal omnifunc=python3complete#Complete
setlocal path=
setlocal nopreserveindent
setlocal nopreviewwindow
setlocal quoteescape=\\
setlocal noreadonly
set relativenumber
setlocal relativenumber
setlocal norightleft
setlocal rightleftcmd=search
setlocal noscrollbind
setlocal scrolloff=-1
setlocal shiftwidth=4
setlocal noshortname
setlocal showbreak=
setlocal sidescrolloff=-1
setlocal signcolumn=auto
setlocal nosmartindent
setlocal nosmoothscroll
setlocal softtabstop=4
setlocal nospell
setlocal spellcapcheck=[.?!]\\_[\\])'\"\	\ ]\\+
setlocal spellfile=
setlocal spelllang=en
setlocal spelloptions=
setlocal statusline=
setlocal suffixesadd=.py
setlocal swapfile
setlocal synmaxcol=3000
if &syntax != 'python'
setlocal syntax=python
endif
setlocal tabstop=4
setlocal tagcase=
setlocal tagfunc=
setlocal tags=
setlocal termwinkey=
setlocal termwinscroll=10000
setlocal termwinsize=
setlocal textwidth=0
setlocal thesaurus=
setlocal thesaurusfunc=
setlocal noundofile
setlocal undolevels=-123456
setlocal varsofttabstop=
setlocal vartabstop=
setlocal virtualedit=
setlocal wincolor=
setlocal nowinfixbuf
setlocal nowinfixheight
setlocal nowinfixwidth
setlocal wrap
setlocal wrapmargin=0
let s:l = 14 - ((5 * winheight(0) + 19) / 38)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 14
normal! 045|
wincmd w
argglobal
if bufexists(fnamemodify("~/projects/raspberrypi/balloon_mission/src/balloon/analysis/hot_cold_folder_viewer.py", ":p")) | buffer ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/hot_cold_folder_viewer.py | else | edit ~/projects/raspberrypi/balloon_mission/src/balloon/analysis/hot_cold_folder_viewer.py | endif
balt ~/projects/raspberrypi/balloon_mission/README.md
setlocal keymap=
setlocal noarabic
setlocal autoindent
setlocal backupcopy=
setlocal balloonexpr=
setlocal nobinary
setlocal nobreakindent
setlocal breakindentopt=
setlocal bufhidden=
setlocal buflisted
setlocal buftype=
setlocal nocindent
setlocal cinkeys=0{,0},0),0],:,!^F,o,O,e
setlocal cinoptions=
setlocal cinscopedecls=public,protected,private
setlocal cinwords=if,else,while,do,for,switch
setlocal colorcolumn=
setlocal comments=b:#,fb:-
setlocal commentstring=#\ %s
setlocal complete=.,w,b,u,t,i
setlocal completefunc=
setlocal completeopt=
setlocal concealcursor=
setlocal conceallevel=0
setlocal nocopyindent
setlocal cryptmethod=
setlocal nocursorbind
setlocal nocursorcolumn
setlocal nocursorline
setlocal cursorlineopt=both
setlocal define=^\\s*\\(\\(async\\s\\+\\)\\?def\\|class\\)
setlocal dictionary=
setlocal nodiff
setlocal equalprg=
setlocal errorformat=
setlocal eventignorewin=
setlocal expandtab
if &filetype != 'python'
setlocal filetype=python
endif
setlocal fillchars=
setlocal findfunc=
setlocal fixendofline
setlocal foldcolumn=0
setlocal foldenable
setlocal foldexpr=0
setlocal foldignore=#
setlocal foldlevel=0
setlocal foldmarker={{{,}}}
set foldmethod=indent
setlocal foldmethod=indent
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldtext=foldtext()
setlocal formatexpr=
setlocal formatlistpat=^\\s*\\d\\+[\\]:.)}\\t\ ]\\s*
setlocal formatoptions=tcq
setlocal formatprg=
setlocal grepprg=
setlocal iminsert=0
setlocal imsearch=-1
setlocal include=^\\s*\\(from\\|import\\)
setlocal includeexpr=substitute(substitute(substitute(v:fname,b:grandparent_match,b:grandparent_sub,''),b:parent_match,b:parent_sub,''),b:child_match,b:child_sub,'g')
setlocal indentexpr=python#GetIndent(v:lnum)
setlocal indentkeys=0{,0},0),0],:,!^F,o,O,e,<:>,=elif,=except
setlocal noinfercase
setlocal iskeyword=@,48-57,_,192-255
setlocal keywordprg=python3\ -m\ pydoc
setlocal nolinebreak
setlocal nolisp
setlocal lispoptions=
setlocal lispwords=
setlocal nolist
setlocal listchars=
setlocal makeencoding=
setlocal makeprg=
setlocal matchpairs=(:),{:},[:]
setlocal nomodeline
setlocal modifiable
setlocal nrformats=bin,hex
set number
setlocal number
setlocal numberwidth=4
setlocal omnifunc=python3complete#Complete
setlocal path=
setlocal nopreserveindent
setlocal nopreviewwindow
setlocal quoteescape=\\
setlocal noreadonly
set relativenumber
setlocal relativenumber
setlocal norightleft
setlocal rightleftcmd=search
setlocal noscrollbind
setlocal scrolloff=-1
setlocal shiftwidth=4
setlocal noshortname
setlocal showbreak=
setlocal sidescrolloff=-1
setlocal signcolumn=auto
setlocal nosmartindent
setlocal nosmoothscroll
setlocal softtabstop=4
setlocal nospell
setlocal spellcapcheck=[.?!]\\_[\\])'\"\	\ ]\\+
setlocal spellfile=
setlocal spelllang=en
setlocal spelloptions=
setlocal statusline=
setlocal suffixesadd=.py
setlocal swapfile
setlocal synmaxcol=3000
if &syntax != 'python'
setlocal syntax=python
endif
setlocal tabstop=4
setlocal tagcase=
setlocal tagfunc=
setlocal tags=
setlocal termwinkey=
setlocal termwinscroll=10000
setlocal termwinsize=
setlocal textwidth=0
setlocal thesaurus=
setlocal thesaurusfunc=
setlocal noundofile
setlocal undolevels=-123456
setlocal varsofttabstop=
setlocal vartabstop=
setlocal virtualedit=
setlocal wincolor=
setlocal nowinfixbuf
setlocal nowinfixheight
setlocal nowinfixwidth
setlocal wrap
setlocal wrapmargin=0
let s:l = 31 - ((5 * winheight(0) + 19) / 38)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 31
normal! 0
wincmd w
argglobal
terminal ++curwin ++cols=280 ++rows=28 
let s:term_buf_113 = bufnr()
balt ~/projects/raspberrypi/balloon_mission/README.md
setlocal keymap=
setlocal noarabic
setlocal autoindent
setlocal backupcopy=
setlocal balloonexpr=
setlocal nobinary
setlocal nobreakindent
setlocal breakindentopt=
setlocal bufhidden=
setlocal buflisted
setlocal buftype=terminal
setlocal nocindent
setlocal cinkeys=0{,0},0),0],:,0#,!^F,o,O,e
setlocal cinoptions=
setlocal cinscopedecls=public,protected,private
setlocal cinwords=if,else,while,do,for,switch
setlocal colorcolumn=
setlocal comments=s1:/*,mb:*,ex:*/,://,b:#,:%,:XCOMM,n:>,fb:-
setlocal commentstring=/*%s*/
setlocal complete=.,w,b,u,t,i
setlocal completefunc=
setlocal completeopt=
setlocal concealcursor=
setlocal conceallevel=0
setlocal nocopyindent
setlocal cryptmethod=
setlocal nocursorbind
setlocal nocursorcolumn
setlocal nocursorline
setlocal cursorlineopt=both
setlocal define=
setlocal dictionary=
setlocal nodiff
setlocal equalprg=
setlocal errorformat=
setlocal eventignorewin=
setlocal expandtab
if &filetype != ''
setlocal filetype=
endif
setlocal fillchars=
setlocal findfunc=
setlocal fixendofline
setlocal foldcolumn=0
setlocal foldenable
setlocal foldexpr=0
setlocal foldignore=#
setlocal foldlevel=0
setlocal foldmarker={{{,}}}
set foldmethod=indent
setlocal foldmethod=manual
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldtext=foldtext()
setlocal formatexpr=
setlocal formatlistpat=^\\s*\\d\\+[\\]:.)}\\t\ ]\\s*
setlocal formatoptions=tcq
setlocal formatprg=
setlocal grepprg=
setlocal iminsert=0
setlocal imsearch=-1
setlocal include=
setlocal includeexpr=
setlocal indentexpr=
setlocal indentkeys=0{,0},0),0],:,0#,!^F,o,O,e
setlocal noinfercase
setlocal iskeyword=@,48-57,_,192-255
setlocal keywordprg=
setlocal nolinebreak
setlocal nolisp
setlocal lispoptions=
setlocal lispwords=
setlocal nolist
setlocal listchars=
setlocal makeencoding=
setlocal makeprg=
setlocal matchpairs=(:),{:},[:]
setlocal modeline
setlocal nomodifiable
setlocal nrformats=bin,octal,hex
set number
setlocal number
setlocal numberwidth=4
setlocal omnifunc=
setlocal path=
setlocal nopreserveindent
setlocal nopreviewwindow
setlocal quoteescape=\\
setlocal noreadonly
set relativenumber
setlocal norelativenumber
setlocal norightleft
setlocal rightleftcmd=search
setlocal noscrollbind
setlocal scrolloff=-1
setlocal shiftwidth=4
setlocal noshortname
setlocal showbreak=
setlocal sidescrolloff=-1
setlocal signcolumn=auto
setlocal nosmartindent
setlocal nosmoothscroll
setlocal softtabstop=4
setlocal nospell
setlocal spellcapcheck=[.?!]\\_[\\])'\"\	\ ]\\+
setlocal spellfile=
setlocal spelllang=en
setlocal spelloptions=
setlocal statusline=
setlocal suffixesadd=
setlocal swapfile
setlocal synmaxcol=3000
if &syntax != ''
setlocal syntax=
endif
setlocal tabstop=4
setlocal tagcase=
setlocal tagfunc=
setlocal tags=
setlocal termwinkey=
setlocal termwinscroll=10000
setlocal termwinsize=
setlocal textwidth=0
setlocal thesaurus=
setlocal thesaurusfunc=
setlocal noundofile
setlocal undolevels=-123456
setlocal varsofttabstop=
setlocal vartabstop=
setlocal virtualedit=
setlocal wincolor=
setlocal nowinfixbuf
setlocal nowinfixheight
setlocal nowinfixwidth
setlocal wrap
setlocal wrapmargin=0
let s:l = 1 - ((0 * winheight(0) + 14) / 28)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 1
normal! 0
wincmd w
exe '1resize ' . ((&lines * 38 + 35) / 70)
exe 'vert 1resize ' . ((&columns * 140 + 140) / 280)
exe '2resize ' . ((&lines * 38 + 35) / 70)
exe 'vert 2resize ' . ((&columns * 139 + 140) / 280)
exe '3resize ' . ((&lines * 28 + 35) / 70)
tabnext
edit ~/dotfiles/vimrc
argglobal
balt ~/projects/raspberrypi/balloon_mission/\!/bin/bash
xnoremap <buffer> <silent> [" :exe "normal! gv"|call search('\%(^\s*".*\n\)\%(^\s*"\)\@!', "bW")
nnoremap <buffer> <silent> [" :call search('\%(^\s*".*\n\)\%(^\s*"\)\@!', "bW")
xnoremap <buffer> <silent> [] m':exe "normal! gv"|call search('^\s*end\(f\%[unction]\|\(export\s\+\)\?def\)\>', "bW")
nnoremap <buffer> <silent> [] m':call search('^\s*end\(f\%[unction]\|\(export\s\+\)\?def\)\>', "bW")
xnoremap <buffer> <silent> [[ m':exe "normal! gv"|call search('^\s*\(fu\%[nction]\|\(export\s\+\)\?def\)\>', "bW")
nnoremap <buffer> <silent> [[ m':call search('^\s*\(fu\%[nction]\|\(export\s\+\)\?def\)\>', "bW")
xnoremap <buffer> <silent> ]" :exe "normal! gv"|call search('\%(^\s*".*\n\)\@<!\%(^\s*"\)', "W")
nnoremap <buffer> <silent> ]" :call search('\%(^\s*".*\n\)\@<!\%(^\s*"\)', "W")
xnoremap <buffer> <silent> ][ m':exe "normal! gv"|call search('^\s*end\(f\%[unction]\|\(export\s\+\)\?def\)\>', "W")
nnoremap <buffer> <silent> ][ m':call search('^\s*end\(f\%[unction]\|\(export\s\+\)\?def\)\>', "W")
xnoremap <buffer> <silent> ]] m':exe "normal! gv"|call search('^\s*\(fu\%[nction]\|\(export\s\+\)\?def\)\>', "W")
nnoremap <buffer> <silent> ]] m':call search('^\s*\(fu\%[nction]\|\(export\s\+\)\?def\)\>', "W")
setlocal keymap=
setlocal noarabic
setlocal autoindent
setlocal backupcopy=
setlocal balloonexpr=
setlocal nobinary
setlocal nobreakindent
setlocal breakindentopt=
setlocal bufhidden=
setlocal buflisted
setlocal buftype=
setlocal nocindent
setlocal cinkeys=0{,0},0),0],:,0#,!^F,o,O,e
setlocal cinoptions=
setlocal cinscopedecls=public,protected,private
setlocal cinwords=if,else,while,do,for,switch
setlocal colorcolumn=
setlocal comments=sO:#\ -,mO:#\ \ ,eO:##,:#\\\ ,:#,sO:\"\ -,mO:\"\ \ ,eO:\"\",:\"\\\ ,:\"
setlocal commentstring=\"%s
setlocal complete=.,w,b,u,t,i
setlocal completefunc=
setlocal completeopt=
setlocal concealcursor=
setlocal conceallevel=0
setlocal nocopyindent
setlocal cryptmethod=
setlocal nocursorbind
setlocal nocursorcolumn
setlocal nocursorline
setlocal cursorlineopt=both
setlocal define=\\v^\\s*export\\s*(def|const|var|final)
setlocal dictionary=
setlocal nodiff
setlocal equalprg=
setlocal errorformat=
setlocal eventignorewin=
setlocal expandtab
if &filetype != 'vim'
setlocal filetype=vim
endif
setlocal fillchars=
setlocal findfunc=
setlocal fixendofline
setlocal foldcolumn=0
setlocal foldenable
setlocal foldexpr=0
setlocal foldignore=#
setlocal foldlevel=0
setlocal foldmarker={{{,}}}
set foldmethod=indent
setlocal foldmethod=indent
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldtext=foldtext()
setlocal formatexpr=
setlocal formatlistpat=^\\s*\\d\\+[\\]:.)}\\t\ ]\\s*
setlocal formatoptions=croql
setlocal formatprg=
setlocal grepprg=
setlocal iminsert=0
setlocal imsearch=-1
setlocal include=\\v^\\s*import\\s*(autoload)?
setlocal includeexpr=
setlocal indentexpr=g:VimIndent()
setlocal indentkeys=0{,0},0),0],!^F,o,O,e,=endif,=enddef,=endfu,=endfor,=endwh,=endtry,=endclass,=endinterface,=endenum,=},=else,=cat,=finall,=END,0\\,0=\"\\\ ,0=#\\\ 
setlocal noinfercase
setlocal iskeyword=@,48-57,_,192-255,#
setlocal keywordprg=:VimKeywordPrg
setlocal nolinebreak
setlocal nolisp
setlocal lispoptions=
setlocal lispwords=
setlocal nolist
setlocal listchars=
setlocal makeencoding=
setlocal makeprg=
setlocal matchpairs=(:),{:},[:]
setlocal nomodeline
setlocal modifiable
setlocal nrformats=bin,hex
set number
setlocal number
setlocal numberwidth=4
setlocal omnifunc=
setlocal path=
setlocal nopreserveindent
setlocal nopreviewwindow
setlocal quoteescape=\\
setlocal noreadonly
set relativenumber
setlocal relativenumber
setlocal norightleft
setlocal rightleftcmd=search
setlocal noscrollbind
setlocal scrolloff=-1
setlocal shiftwidth=4
setlocal noshortname
setlocal showbreak=
setlocal sidescrolloff=-1
setlocal signcolumn=auto
setlocal nosmartindent
setlocal nosmoothscroll
setlocal softtabstop=4
setlocal nospell
setlocal spellcapcheck=[.?!]\\_[\\])'\"\	\ ]\\+
setlocal spellfile=
setlocal spelllang=en
setlocal spelloptions=
setlocal statusline=
setlocal suffixesadd=
setlocal swapfile
setlocal synmaxcol=3000
if &syntax != 'vim'
setlocal syntax=vim
endif
setlocal tabstop=4
setlocal tagcase=
setlocal tagfunc=
setlocal tags=
setlocal termwinkey=
setlocal termwinscroll=10000
setlocal termwinsize=
setlocal textwidth=78
setlocal thesaurus=
setlocal thesaurusfunc=
setlocal noundofile
setlocal undolevels=-123456
setlocal varsofttabstop=
setlocal vartabstop=
setlocal virtualedit=
setlocal wincolor=
setlocal nowinfixbuf
setlocal nowinfixheight
setlocal nowinfixwidth
setlocal wrap
setlocal wrapmargin=0
let s:l = 11 - ((10 * winheight(0) + 34) / 68)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 11
normal! 0
tabnext 1
set stal=1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20
set shortmess=filnxtToO
let &winminheight = s:save_winminheight
let &winminwidth = s:save_winminwidth
let s:sx = expand("<sfile>:p:r")."x.vim"
if filereadable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &g:so = s:so_save | let &g:siso = s:siso_save
nohlsearch
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
