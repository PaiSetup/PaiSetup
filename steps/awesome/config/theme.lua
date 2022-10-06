----------------------------------------------------------------------------------- Module imports
local theme_assets = require("beautiful.theme_assets")
local xresources = require("beautiful.xresources")
local dpi = xresources.apply_dpi
local gfs = require("gears.filesystem")
local gears = require("gears")
local themes_path = gfs.get_themes_dir()

local theme = {}
local linux_setup = os.getenv("LINUX_SETUP_ROOT")



----------------------------------------------------------------------------------- Load XResources
xrdb = xresources.get_current_theme()
color_theme = xrdb.color1
color_gray_light = xrdb.color2
color_gray_dark = xrdb.color3
color_font = xrdb.color4
color_urgent = "00ff00" -- I don't know where I'll see this color. Make it something flashy, so I'll notice
color_minimze = "00ffff" -- I don't know where I'll see this color. Make it something flashy, so I'll notice



----------------------------------------------------------------------------------- Custom values for our setup (used in rc.lua or its sub-scripts)
theme.widgets_padding = dpi(3)
theme.widgets_margin = dpi(4)
theme.widgets_group_margin = dpi(6)
theme.client_border_width = dpi(1)
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
theme.tasklist_align = "center" -- this aligns the 'text_role' widget



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
-- theme.notification_font 	Notifications font.
theme.notification_bg 	= "#222222"
theme.notification_fg = color_gray_light
theme.notification_border_width = 1
theme.notification_border_color = theme.border_focus
theme.notification_shape 	= gears.shape.rounded_rect
theme.notification_max_width = dpi(500)
theme.notification_icon_size = dpi(90)



----------------------------------------------------------------------------------- Wibar
theme.wibar_border_width = dpi(10)
theme.wibar_bg = "#00000000"
theme.wibar_height = dpi(30)



----------------------------------------------------------------------------------- Layout icons
local icons_dir = linux_setup .. "/steps/awesome/config/icons_colorized/"
theme.layout_fairh = icons_dir.."fairh.png"
theme.layout_fairv = icons_dir.."fairv.png"
theme.layout_floating  = icons_dir.."floating.png"
theme.layout_magnifier = icons_dir.."magnifier.png"
theme.layout_max = icons_dir.."max.png"
theme.layout_fullscreen = icons_dir.."fullscreen.png"
theme.layout_tilebottom = icons_dir.."tilebottom.png"
theme.layout_tileleft   = icons_dir.."tileleft.png"
theme.layout_tile = icons_dir.."tile.png"
theme.layout_tiletop = icons_dir.."tiletop.png"
theme.layout_spiral  = icons_dir.."spiral.png"
theme.layout_dwindle = icons_dir.."dwindle.png"
theme.layout_cornernw = icons_dir.."cornernw.png"
theme.layout_cornerne = icons_dir.."cornerne.png"
theme.layout_cornersw = icons_dir.."cornersw.png"
theme.layout_cornerse = icons_dir.."cornerse.png"



----------------------------------------------------------------------------------- Other icons
theme.arch_logo = icons_dir.."arch.png"


----------------------------------------------------------------------------------- Rest
-- Define the icon theme for application icons. If not set then the icons
-- from /usr/share/icons and /usr/share/icons/hicolor will be used.
theme.icon_theme = nil

theme.rounded = dpi(15)
return theme
