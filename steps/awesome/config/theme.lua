----------------------------------------------------------------------------------- Module imports
local theme_assets = require("beautiful.theme_assets")
local xresources = require("beautiful.xresources")
local dpi = xresources.apply_dpi
local gfs = require("gears.filesystem")
local gears = require("gears")
local themes_path = gfs.get_themes_dir()

local theme = {}



----------------------------------------------------------------------------------- Load XResources
xrdb = xresources.get_current_theme()
color_theme = xrdb.color1
color_gray_light = xrdb.color2
color_gray_dark = xrdb.color3
color_font = xrdb.color4
color_urgent = "00ff00" -- I don't know where I'll see this color. Make it something flashy, so I'll notice
color_minimze = "00ffff" -- I don't know where I'll see this color. Make it something flashy, so I'll notice



----------------------------------------------------------------------------------- Custom values for our setup (used in rc.lua or its sub-scripts)
theme.widgets_padding = 3
theme.widgets_margin = 4
theme.widgets_group_margin = 6
theme.bg_normal2 = color_gray_dark
theme.color_theme = color_theme
theme.color_gray_light = color_gray_light
theme.color_gray_dark = color_gray_dark



----------------------------------------------------------------------------------- General config
theme.font          = "sans 8"

theme.fg_normal     = color_font
theme.fg_focus      = color_font
theme.fg_urgent     = color_urgent
theme.fg_minimize   = color_minimze

theme.bg_normal     = color_gray_light
theme.bg_focus      = color_gray_dark
theme.bg_urgent     = color_gray_light
theme.bg_minimize   = color_gray_light
theme.bg_systray    = color_gray_light

theme.useless_gap   = dpi(5)
theme.border_width  = dpi(0)
theme.border_normal = "#000000"
theme.border_focus  = color_theme
theme.border_marked = "#000000"



----------------------------------------------------------------------------------- Tasklist
theme.tasklist_fg_normal   = color_theme
theme.tasklist_fg_focus    = color_theme
theme.tasklist_fg_urgent   = color_theme
theme.tasklist_fg_minimize = color_theme
theme.tasklist_bg_normal   = color_gray_light
theme.tasklist_bg_focus    = color_gray_light
theme.tasklist_bg_urgent   = color_gray_light
theme.tasklist_bg_minimize = color_gray_light
theme.tasklist_shape = gears.shape.rounded_rect
theme.tasklist_disable_icon = false



----------------------------------------------------------------------------------- Taglist
theme.taglist_fg_empty = color_theme
theme.taglist_fg_focus = color_gray_light
theme.taglist_fg_occupied = theme.taglist_fg_empty
theme.taglist_bg_empty = color_gray_light
theme.taglist_bg_occupied = theme.taglist_bg_empty
theme.taglist_bg_focus = color_theme
theme.taglist_bg_volatile = color_urgent
theme.taglist_bg_urgent = color_urgent
theme.taglist_shape = gears.shape.rounded_rect



----------------------------------------------------------------------------------- Hotkeys popup
theme.hotkeys_bg = theme.bg_normal
theme.hotkeys_fg = theme.fg_normal
theme.hotkeys_shape = gears.shape.rounded_rect
theme.hotkeys_modifiers_fg = color_theme
theme.hotkeys_label_fg = color_font
theme.hotkeys_group_margin = dpi(30)



----------------------------------------------------------------------------------- Notifications
-- TODO
-- Variables set for theming notifications:
-- notification_font
-- notification_[bg|fg]
-- notification_[width|height|margin]
-- notification_[border_color|border_width|shape|opacity]



----------------------------------------------------------------------------------- Wibar
theme.wibar_border_width = dpi(10)
theme.wibar_bg = "#00000000"
theme.wibar_height = dpi(30)



----------------------------------------------------------------------------------- Layout icons
theme.layout_fairh = themes_path.."default/layouts/fairhw.png"
theme.layout_fairv = themes_path.."default/layouts/fairvw.png"
theme.layout_floating  = themes_path.."default/layouts/floatingw.png"
theme.layout_magnifier = themes_path.."default/layouts/magnifierw.png"
theme.layout_max = themes_path.."default/layouts/maxw.png"
theme.layout_fullscreen = themes_path.."default/layouts/fullscreenw.png"
theme.layout_tilebottom = themes_path.."default/layouts/tilebottomw.png"
theme.layout_tileleft   = themes_path.."default/layouts/tileleftw.png"
theme.layout_tile = themes_path.."default/layouts/tilew.png"
theme.layout_tiletop = themes_path.."default/layouts/tiletopw.png"
theme.layout_spiral  = themes_path.."default/layouts/spiralw.png"
theme.layout_dwindle = themes_path.."default/layouts/dwindlew.png"
theme.layout_cornernw = themes_path.."default/layouts/cornernww.png"
theme.layout_cornerne = themes_path.."default/layouts/cornernew.png"
theme.layout_cornersw = themes_path.."default/layouts/cornersww.png"
theme.layout_cornerse = themes_path.."default/layouts/cornersew.png"



----------------------------------------------------------------------------------- Rest
-- Define the icon theme for application icons. If not set then the icons
-- from /usr/share/icons and /usr/share/icons/hicolor will be used.
theme.icon_theme = nil

theme.rounded = dpi(15)
return theme
