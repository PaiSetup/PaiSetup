vim.opt.tabstop = 4
vim.opt.softtabstop = 4
vim.opt.shiftwidth  = 4
vim.opt.expandtab = true

vim.opt.showcmd = true
vim.opt.showmode = true


local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
    vim.fn.system({
        "git",
        "clone",
        "--filter=blob:none",
        "https://github.com/folke/lazy.nvim.git",
        "--branch=stable", -- latest stable release
        lazypath,
    })
end
vim.opt.rtp:prepend(lazypath)
require("lazy").setup(
-- Plugins
{
    --"folke/which-key.nvim",
    --{ "folke/neoconf.nvim", cmd = "Neoconf" },
    --"folke/neodev.nvim",
    'ThePrimeagen/vim-be-good',
    'nvim-tree/nvim-tree.lua',
    'nvim-tree/nvim-web-devicons',
},

-- Opts
nil
)

-- Nvim-tree setup

vim.g.loaded_netrw = 1
vim.g.loaded_netrwPlugin = 1
require('nvim-tree').setup({
    git = {
        enable = true,
        ignore = false,
        timeout = 500,
    },
})
vim.keymap.set('n', '<c-n>', ':NvimTreeFindFileToggle<CR>')
--vim.keymap.set('n', '<c-n>', ':NvimTreeFocus<CR>')


require('nvim-web-devicons').setup()
