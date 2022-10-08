""""""""""""""""""""""""""""""
" vim-plug
""""""""""""""""""""""""""""""
call plug#begin('~/.config/nvim/site/autoload/')
Plug 'arcticicestudio/nord-vim'     " カラースキーム
Plug 'tomtom/tcomment_vim'          " コメント切り替え
Plug 'terryma/vim-multiple-cursors' " 複数カーソル
Plug 'tpope/vim-fugitive'           " VimからGitを使用する
Plug 'ryanoasis/vim-devicons'       " ファイルタイプアイコン
Plug 'easymotion/vim-easymotion'    " easymotion
Plug 'haya14busa/incsearch.vim'     " easymotion
Plug 'haya14busa/incsearch-easymotion.vim' " easymotion
call plug#end()

""""""""""""""""""""""""""""""
"" color scheme
""""""""""""""""""""""""""""""
syntax enable
set background=dark
colorscheme nord

""""""""""""""""""""""""""""""
"" general
""""""""""""""""""""""""""""""
set encoding=utf-8
scriptencoding utf-8
set nrformats-=octal      " 0始まりの数字の増減操作の時8進数として操作しない
set nohidden              " hiddenバッファを積極的には使わない
set whichwrap=b,s,[,],<,> " 行頭、行末で左右に移動した時の動き
set wildmenu              " wildmenuを利用する。
set mouse=a               " すべてのモードでマウスを利用する
set conceallevel=0        " 一切concealしない。
set backspace=indent,eol,start
"" タブと空白
set expandtab             " Tab文字を挿入するとき、代わりに空白を使う。
set shiftwidth=4          " インデントの幅
set softtabstop=-1        " マイナスなら 'shiftwidth' の値が使われる。
set tabstop=4             " 画面上でTab文字が占める幅
set list                  " タブ文字、改行を表示する。
set listchars=tab:»-,trail:-,extends:»,precedes:«,nbsp:%
"" 表示設定
set number                " 行番号を表示
set synmaxcol=300         " 構文解析を行う桁数の最大値
set hls                   " 検索語をハイライト
set showmatch             " 括弧の対応を表示する
set matchtime=1           " showmatchのカーソル移動時間。単位は0.1秒。
set showcmd               " 入力中のコマンド・選択中の領域の大きさを表示する。
set cursorline            " カーソル行をハイライトする
set colorcolumn=80        " 80文字目をハイライトする
"" 特定のコマンドを実行する時に自動でquickfixウィンドウを開く
au QuickfixCmdPost make,grep,grepadd,vimgrep,helpg copen
"" escキーの遅延対策
set ttimeoutlen=10
"" カーソルの形状
if has('vim_starting')
    " 挿入モード時に点滅の縦棒タイプのカーソル
    let &t_SI .= "\e[5 q"
    " ノーマルモード時に点滅のブロックタイプのカーソル
    let &t_EI .= "\e[1 q"
    " 置換モード時に点滅の下線タイプのカーソル
    let &t_SR .= "\e[3 q"
endif
autocmd VimEnter * silent exec "! echo -ne '\e[1 q'"
autocmd VimLeave * silent exec "! echo -ne '\e[5 q'"

""""""""""""""""""""""""""""""
"" key mapping
""""""""""""""""""""""""""""""
inoremap jj <esc>
nnoremap <silent> j j:noh<CR>

""""""""""""""""""""""""""""""
"" user defined command
""""""""""""""""""""""""""""""
" 行末のスペースを削除する。
if !exists(":TrimSpaces")
  command TrimSpaces %s/\s\+$//
endif
" 日付時刻を挿入する
if !exists(":InsertTime")
  command InsertTime put! =strftime(\"%Y-%m-%d %H:%M:%S\")
endif
" if !exists(":InsertTimeWithUnderbar")
"   command InsertTimeWithUnderbar put! =strftime(\"%Y_%m%d_%H%M_%S\")
" endif

""""""""""""""""""""""""""""""
"" statusline, tabline
""""""""""""""""""""""""""""""
" statusline設定
let g:WebDevIconsUnicodeByteOrderMarkerDefaultSymbol = '  w/BOM'
function GitBranchIcon()
    return FugitiveHead() != ''  ? '' : ''
endfunction
set statusline=
set statusline+=%f
set statusline+=%m
set statusline+=\ %{GitBranchIcon()}
set statusline+=\ %{FugitiveHead()}
set statusline+=%=
set statusline+=\ %{WebDevIconsGetFileTypeSymbol()}
set statusline+=\ %{&filetype}
set statusline+=\ %{&fileencoding?&fileencoding:&encoding}
set statusline+=%{WebDevIconsGetFileFormatSymbol()}
set statusline+=\ %{&fileformat}
set statusline+=\ %p%%
set statusline+=\ \ %l\ %c
set laststatus=2 " ステータスラインを常に表示

" tabline設定
function! MyTabLine()
  let s = ''
  for i in range(tabpagenr('$'))
    let tabnr = i + 1 " range() starts at 0
    let winnr = tabpagewinnr(tabnr)
    let buflist = tabpagebuflist(tabnr)
    let bufnr = buflist[winnr - 1]
    let bufname = fnamemodify(bufname(bufnr), ':t')
    let s .= '%' . tabnr . 'T'
    let s .= (tabnr == tabpagenr() ? '%#TabLineSel#' : '%#TabLine#')
    let s .= ' ' . tabnr
    let n = tabpagewinnr(tabnr,'$')
    if n > 1 | let s .= ':' . n | endif
    let s .= empty(bufname) ? ' [No Name] ' : ' ' . bufname . ' '
    let bufmodified = getbufvar(bufnr, "&mod")
    if bufmodified | let s .= '+ ' | endif
  endfor
  let s .= '%#TabLineFill#'
  return s
endfunction
set tabline=%!MyTabLine()

""""""""""""""""""""""""""""""
"" leader
""""""""""""""""""""""""""""""
let mapleader = "\<Space>"
nnoremap <Leader>w :w<CR>
vmap <Leader>y "+y
vmap <Leader>d "+d
nmap <Leader>p "+p
nmap <Leader>P "+P
vmap <Leader>p "+p
vmap <Leader>P "+P
set notimeout
set ttimeout

""""""""""""""""""""""""""""""
"" incsearch-easymotion
""""""""""""""""""""""""""""""
" You can use other keymappings like <C-l> instead of <CR> if you want to
" use these mappings as default search and sometimes want to move cursor with
" EasyMotion.
function! s:incsearch_config(...) abort
  return incsearch#util#deepextend(deepcopy({
  \   'modules': [incsearch#config#easymotion#module({'overwin': 1})],
  \   'keymap': {
  \     "\<CR>": '<Over>(easymotion)'
  \   },
  \   'is_expr': 0
  \ }), get(a:, 1, {}))
endfunction

noremap <silent><expr> /  incsearch#go(<SID>incsearch_config())
noremap <silent><expr> ?  incsearch#go(<SID>incsearch_config({'command': '?'}))
noremap <silent><expr> g/ incsearch#go(<SID>incsearch_config({'is_stay': 1}))

