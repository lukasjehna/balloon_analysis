let SessionLoad = 1
let s:so_save = &g:so | let s:siso_save = &g:siso | setg so=0 siso=0 | setl so=-1 siso=-1
let v:this_session=expand("<sfile>:p")
doautoall SessionLoadPre
silent only
silent tabonly
cd ~/projects/raspberrypi/balloon_analysis
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
let s:shortmess_save = &shortmess
set shortmess+=aoO
badd +1 config/\*
badd +1 docs/analysis.md
badd +1 docs/todo.md
badd +1 docs/uv_pip.md
badd +1 pyproject.toml
badd +1 src/balloon_analysis/spec_folder_viewer_v2.0.py
badd +1 src/balloon_analysis/noise_temperature_all_dumbs_over_time.py
badd +1 src/balloon_analysis/pressure_analysis.py
badd +1 src/balloon_analysis/t_format_converter.py
badd +1 src/balloon_analysis/background_analysis_utils.py
badd +1 src/balloon_analysis/hot_cold_folder_viewer_v1.py
badd +1 src/balloon_analysis/background_analysis.py
badd +1 src/balloon_analysis/telemetry_analysis.py
badd +1 src/balloon_analysis/noise_temperature_frequency_scan.py
badd +1 src/balloon_analysis/y_factor_all_dumps_over_time_v2.py
badd +1 src/balloon_analysis/y_factor_all_dumps_over_time.py
badd +1 src/balloon_analysis/gyro_analysis.py
badd +1 src/balloon_analysis/spec_viewer.py
badd +1 src/balloon_analysis/single_spec_file_viewer.py
badd +1 src/balloon_analysis/spec_folder_to_csv_converter.py
badd +1 src/balloon_analysis/add_to_noise_temperature_folder_viewer.py
badd +1 src/balloon_analysis/spec_analysis_utils_v3_trash.py
badd +1 src/balloon_analysis/hot_cold_folder_viewer.py
badd +1 src/balloon_analysis/hot_cold_folder_analysis.py
badd +1 src/balloon_analysis/spec_to_csv_converter.py
badd +1 src/balloon_analysis/noise_temperature_all_dumbs_over_time_v1.py
badd +1 src/balloon_analysis/y_factor_all_dumps_over_time_v1.py
badd +1 src/balloon_analysis/hot_cold_folder_viewer_v4.py
badd +1 src/balloon_analysis/y_factor_average_over_time.py
badd +1 src/balloon_analysis/hot_cold_folder_analysis_v1.py
badd +1 src/balloon_analysis/cold_load_temperature_over_time.py
badd +1 src/balloon_analysis/hot_cold_folder_viewer_v2.py
badd +1 src/balloon_analysis/spec_analysis_utils_v1.py
badd +1 src/balloon_analysis/noise_temperature_average_over_time.py
badd +1 src/balloon_analysis/spec_analysis_utils.py
badd +1 src/balloon_analysis/spec_folder_viewer_v1.py
badd +1 src/balloon_analysis/noise_temperature_over_time_v1.py
badd +1 src/balloon_analysis/cold_load_temperature_viewer.py
badd +1 src/balloon_analysis/temperature_analysis.py
badd +1 src/balloon_analysis/spec_analysis_index_range_old.py
badd +1 src/balloon_analysis/hot_cold_folder_viewer_v5.py
badd +1 src/balloon_analysis/hot_cold_folder_viewer_v3.py
badd +1 src/balloon_analysis/spec_analysis_simple_old.py
badd +1 src/balloon_analysis/spec_folder_viewer.py
badd +1 src/balloon_analysis/utility/parser_utility.py
badd +1 src/balloon_analysis/utility/analysis_utility.py
badd +1 src/balloon_analysis/utility/verbose_utils.py
badd +1 term://~/projects/raspberrypi/balloon_analysis//321:/bin/bash
badd +19 README.md
badd +3 scripts/create_vim_session.sh
argglobal
%argdel
$argadd config/\*
$argadd docs/analysis.md
$argadd docs/todo.md
$argadd docs/uv_pip.md
$argadd pyproject.toml
$argadd src/balloon_analysis/spec_folder_viewer_v2.0.py
$argadd src/balloon_analysis/noise_temperature_all_dumbs_over_time.py
$argadd src/balloon_analysis/pressure_analysis.py
$argadd src/balloon_analysis/t_format_converter.py
$argadd src/balloon_analysis/background_analysis_utils.py
$argadd src/balloon_analysis/hot_cold_folder_viewer_v1.py
$argadd src/balloon_analysis/background_analysis.py
$argadd src/balloon_analysis/telemetry_analysis.py
$argadd src/balloon_analysis/noise_temperature_frequency_scan.py
$argadd src/balloon_analysis/y_factor_all_dumps_over_time_v2.py
$argadd src/balloon_analysis/y_factor_all_dumps_over_time.py
$argadd src/balloon_analysis/gyro_analysis.py
$argadd src/balloon_analysis/spec_viewer.py
$argadd src/balloon_analysis/single_spec_file_viewer.py
$argadd src/balloon_analysis/spec_folder_to_csv_converter.py
$argadd src/balloon_analysis/add_to_noise_temperature_folder_viewer.py
$argadd src/balloon_analysis/spec_analysis_utils_v3_trash.py
$argadd src/balloon_analysis/hot_cold_folder_viewer.py
$argadd src/balloon_analysis/hot_cold_folder_analysis.py
$argadd src/balloon_analysis/spec_to_csv_converter.py
$argadd src/balloon_analysis/noise_temperature_all_dumbs_over_time_v1.py
$argadd src/balloon_analysis/y_factor_all_dumps_over_time_v1.py
$argadd src/balloon_analysis/hot_cold_folder_viewer_v4.py
$argadd src/balloon_analysis/y_factor_average_over_time.py
$argadd src/balloon_analysis/hot_cold_folder_analysis_v1.py
$argadd src/balloon_analysis/cold_load_temperature_over_time.py
$argadd src/balloon_analysis/hot_cold_folder_viewer_v2.py
$argadd src/balloon_analysis/spec_analysis_utils_v1.py
$argadd src/balloon_analysis/noise_temperature_average_over_time.py
$argadd src/balloon_analysis/spec_analysis_utils.py
$argadd src/balloon_analysis/spec_folder_viewer_v1.py
$argadd src/balloon_analysis/noise_temperature_over_time_v1.py
$argadd src/balloon_analysis/cold_load_temperature_viewer.py
$argadd src/balloon_analysis/temperature_analysis.py
$argadd src/balloon_analysis/spec_analysis_index_range_old.py
$argadd src/balloon_analysis/hot_cold_folder_viewer_v5.py
$argadd src/balloon_analysis/hot_cold_folder_viewer_v3.py
$argadd src/balloon_analysis/spec_analysis_simple_old.py
$argadd src/balloon_analysis/spec_folder_viewer.py
$argadd src/balloon_analysis/utility/parser_utility.py
$argadd src/balloon_analysis/utility/analysis_utility.py
$argadd src/balloon_analysis/utility/verbose_utils.py
set stal=2
tabnew +setlocal\ bufhidden=wipe
tabrewind
edit src/balloon_analysis/hot_cold_folder_viewer.py
let s:save_splitbelow = &splitbelow
let s:save_splitright = &splitright
set splitbelow splitright
wincmd _ | wincmd |
split
1wincmd k
wincmd _ | wincmd |
vsplit
wincmd _ | wincmd |
vsplit
2wincmd h
wincmd w
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
exe '1resize ' . ((&lines * 40 + 35) / 70)
exe 'vert 1resize ' . ((&columns * 93 + 140) / 280)
exe '2resize ' . ((&lines * 40 + 35) / 70)
exe 'vert 2resize ' . ((&columns * 93 + 140) / 280)
exe '3resize ' . ((&lines * 40 + 35) / 70)
exe 'vert 3resize ' . ((&columns * 92 + 140) / 280)
exe '4resize ' . ((&lines * 26 + 35) / 70)
argglobal
if bufexists(fnamemodify("src/balloon_analysis/hot_cold_folder_viewer.py", ":p")) | buffer src/balloon_analysis/hot_cold_folder_viewer.py | else | edit src/balloon_analysis/hot_cold_folder_viewer.py | endif
if &buftype ==# 'terminal'
  silent file src/balloon_analysis/hot_cold_folder_viewer.py
endif
balt scripts/create_vim_session.sh
setlocal foldmethod=manual
setlocal foldexpr=0
setlocal foldmarker={{{,}}}
setlocal foldignore=#
setlocal foldlevel=0
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldenable
silent! normal! zE
let &fdl = &fdl
let s:l = 1 - ((0 * winheight(0) + 20) / 40)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 1
normal! 0
wincmd w
argglobal
if bufexists(fnamemodify("src/balloon_analysis/spec_analysis_utils.py", ":p")) | buffer src/balloon_analysis/spec_analysis_utils.py | else | edit src/balloon_analysis/spec_analysis_utils.py | endif
if &buftype ==# 'terminal'
  silent file src/balloon_analysis/spec_analysis_utils.py
endif
balt src/balloon_analysis/utility/analysis_utility.py
setlocal foldmethod=manual
setlocal foldexpr=0
setlocal foldmarker={{{,}}}
setlocal foldignore=#
setlocal foldlevel=0
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldenable
silent! normal! zE
let &fdl = &fdl
let s:l = 12 - ((11 * winheight(0) + 20) / 40)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 12
normal! 0
wincmd w
argglobal
if bufexists(fnamemodify("src/balloon_analysis/utility/analysis_utility.py", ":p")) | buffer src/balloon_analysis/utility/analysis_utility.py | else | edit src/balloon_analysis/utility/analysis_utility.py | endif
if &buftype ==# 'terminal'
  silent file src/balloon_analysis/utility/analysis_utility.py
endif
balt README.md
setlocal foldmethod=manual
setlocal foldexpr=0
setlocal foldmarker={{{,}}}
setlocal foldignore=#
setlocal foldlevel=0
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldenable
silent! normal! zE
let &fdl = &fdl
let s:l = 1 - ((0 * winheight(0) + 20) / 40)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 1
normal! 0
wincmd w
argglobal
if bufexists(fnamemodify("term://~/projects/raspberrypi/balloon_analysis//321:/bin/bash", ":p")) | buffer term://~/projects/raspberrypi/balloon_analysis//321:/bin/bash | else | edit term://~/projects/raspberrypi/balloon_analysis//321:/bin/bash | endif
if &buftype ==# 'terminal'
  silent file term://~/projects/raspberrypi/balloon_analysis//321:/bin/bash
endif
balt config/\*
setlocal foldmethod=manual
setlocal foldexpr=0
setlocal foldmarker={{{,}}}
setlocal foldignore=#
setlocal foldlevel=0
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldenable
let s:l = 27 - ((25 * winheight(0) + 13) / 26)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 27
normal! 063|
wincmd w
2wincmd w
exe '1resize ' . ((&lines * 40 + 35) / 70)
exe 'vert 1resize ' . ((&columns * 93 + 140) / 280)
exe '2resize ' . ((&lines * 40 + 35) / 70)
exe 'vert 2resize ' . ((&columns * 93 + 140) / 280)
exe '3resize ' . ((&lines * 40 + 35) / 70)
exe 'vert 3resize ' . ((&columns * 92 + 140) / 280)
exe '4resize ' . ((&lines * 26 + 35) / 70)
tabnext
argglobal
enew
balt scripts/create_vim_session.sh
setlocal foldmethod=manual
setlocal foldexpr=0
setlocal foldmarker={{{,}}}
setlocal foldignore=#
setlocal foldlevel=0
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldenable
tabnext 1
set stal=1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0 && getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20
let &shortmess = s:shortmess_save
let &winminheight = s:save_winminheight
let &winminwidth = s:save_winminwidth
let s:sx = expand("<sfile>:p:r")."x.vim"
if filereadable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &g:so = s:so_save | let &g:siso = s:siso_save
set hlsearch
nohlsearch
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
