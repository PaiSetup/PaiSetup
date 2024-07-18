----------------------------------------------------------------------------------- Module imports
-- If LuaRocks is installed, make sure that packages installed through it are
-- found (e.g. lgi). If LuaRocks is not installed, do nothing.
pcall(require, "luarocks.loader")

-- Standard awesome library
local gears = require("gears")
local awful = require("awful")
local wibox = require("wibox")
local beautiful = require("beautiful")
local naughty = require("naughty")
local menubar = require("menubar")
local hotkeys_popup = require("awful.hotkeys_popup")
local dpi = require("beautiful.xresources").apply_dpi

-- Enable hotkeys help widget for VIM and other apps
require("awful.autofocus")

-- when client with a matching name is opened:
require("awful.hotkeys_popup.keys")

-- Custom utility functions
local widget_wrappers = require("widget.wrappers")
local markup_utils = require("utils.markup")
local utils = require("utils.utils")
local rules_utils = require("utils.rules")
local app_keybindings = require("utils.app_keybindings")

-- Custom widgets
local shutdown_popup = require("widget.shutdown_popup")
local script_widget = require("widget.script_widget")
local callback_widget = require("widget.callback_widget")
local tray_widget = require("widget.tray_widget")
local home_panel = require("widget.home_panel")
local taglist = require("widget.taglist")
local tasklist = require("widget.tasklist")
local layout_box = require("widget.layout_box")


----------------------------------------------------------------------------------- Error handling
-- Check if awesome encountered an error during startup and fell back to
-- another config (This code will only ever execute for the fallback config)
if awesome.startup_errors then
    naughty.notify({ preset = naughty.config.presets.critical,
                     title = "Oops, there were errors during startup!",
                     text = awesome.startup_errors })
end

-- Handle runtime errors after startup
do
    local in_error = false
    awesome.connect_signal("debug::error", function (err)
        -- Make sure we don't go into an endless error loop
        if in_error then return end
        in_error = true

        naughty.notify({ preset = naughty.config.presets.critical,
                         title = "Oops, an error happened!",
                         text = tostring(err) })
        in_error = false
    end)
end



----------------------------------------------------------------------------------- Variable definitions
-- Read some handy env variables
terminal = os.getenv("TERMINAL")
user = os.getenv("USER")
editor = os.getenv("EDITOR") or "nano"
editor_cmd = terminal .. " -e " .. editor
pai_setup = os.getenv("PAI_SETUP_ROOT")
pai_setup_steps = pai_setup .. "/steps/linux/"
pai_setup_status_scripts = pai_setup_steps .. "gui/scripts_statusbar/"
button_action = os.getenv("BUTTON_ACTION")
button_terminate = os.getenv("BUTTON_TERMINATE")
button_info = os.getenv("BUTTON_INFO")
button_scroll_up = os.getenv("BUTTON_SCROLL_UP")
button_scroll_down = os.getenv("BUTTON_SCROLL_DOWN")

-- Modkey is windows key
modkey = "Mod4"
altkey = "Mod1"



----------------------------------------------------------------------------------- Theme setup
beautiful.init(gears.filesystem.get_xdg_config_home() .. "/awesome/theme.lua")
beautiful.font = "DejaVu Sans 15"
beautiful.wallpaper = gears.filesystem.get_xdg_config_home() .. "/PaiSetup/wallpaper"



----------------------------------------------------------------------------------- Client layouts
awful.layout.layouts = {
    awful.layout.suit.tile,
    -- awful.layout.suit.floating,
    -- awful.layout.suit.tile.left,
    -- awful.layout.suit.tile.bottom,
    awful.layout.suit.tile.top,
    awful.layout.suit.fair,
    awful.layout.suit.fair.horizontal,
    -- awful.layout.suit.spiral,
    -- awful.layout.suit.spiral.dwindle,
    -- awful.layout.suit.max,
    -- awful.layout.suit.max.fullscreen,
    -- awful.layout.suit.magnifier,
    awful.layout.suit.corner.nw,
    -- awful.layout.suit.corner.ne,
    -- awful.layout.suit.corner.sw,
    -- awful.layout.suit.corner.se,
}



----------------------------------------------------------------------------------- Top bar

-- Definition of custom tags
local tags = {
    web = "",
    code = "",
    general = "",
    draw = "",
    video = "",
    home = "",
}
local default_tag_index = 3
function get_home_tag(screen)
    if screen == nil then
        screen = awful.screen.focused()
    end
    return awful.tag.find_by_name(screen, tags.home)
end

-- Preserve tags after restart
utils.enable_viewed_tag_preserving()

-- Re-set wallpaper when a screen's geometry changes (e.g. different resolution)
screen.connect_signal("property::geometry", utils.set_wallpaper)

-- Leaf widgets
local memory_widget = script_widget("memory.sh", {button_info}, 5)
local volume_widget = script_widget("volume.sh", {button_action, button_scroll_up, button_scroll_down}, 60)
local packages_widget = script_widget("packages.sh", {button_info, button_action}, 60, " ?")
local time_widget = script_widget("date.sh", {button_action}, 30)
local plex_widget = script_widget(pai_setup_steps .. "plex/status_bar_script.sh", {button_info, button_action}, 60)
local audio_switch_widget = script_widget("audio_switch.sh", {button_info, button_action, button_scroll_up, button_scroll_down}, 10)
local trash_widget = script_widget("trash.sh", {button_info, button_terminate, button_action}, 60)
local tray_widget = tray_widget()
local warnings_widget = script_widget("checks.py", {button_action, button_terminate, button_info}, 4, nil, "refresh:warnings")
local shutdown_popup_widget = callback_widget(function () shutdown_popup(pai_setup, terminal) end, "")
audio_switch_widget:add_widget_to_update(volume_widget)

-- Setup widgets for each screen
awful.screen.connect_for_each_screen(function(s)
    -- Wallpaper
    utils.set_wallpaper(s)

    -- Each screen has its own tag table.
    awful.tag({tags.web, tags.code, tags.general, tags.general, tags.general, tags.general, tags.draw, tags.video, tags.home }, s, awful.layout.layouts[1])

    -- Setup home tag and panel
    get_home_tag(s).is_home = true
    home_panel(tags.home, pai_setup, user, s)

    -- Create the bar
    s.mywibox = awful.wibar({ position = "top", screen = s, })

    -- Add widgets to the bar
    s.mywibox:setup {
        layout = wibox.layout.align.horizontal,
        -- Left widgets
        widget_wrappers.bg(taglist(s, modkey), beautiful.bg_normal),

        -- Middle widget
        widget_wrappers.center(tasklist(s)),

        -- Right widgets
        {
            layout = wibox.layout.fixed.horizontal,
            spacing = beautiful.widgets_group_margin,
            widget_wrappers.grp({memory_widget}),
            widget_wrappers.grp({
                volume_widget,
                audio_switch_widget,
            }),
            widget_wrappers.grp({packages_widget}),
            widget_wrappers.grp({time_widget}),
            widget_wrappers.grp({
                plex_widget,
                trash_widget,
                tray_widget,
                warnings_widget,
                shutdown_popup_widget,
            }),
            layout_box(s),
        },
    }
end)



----------------------------------------------------------------------------------- Extra theme setup (TODO, move this to theme.lua)
beautiful.taglist_squares_sel = utils.taglist_square_top_rect(beautiful.taglist_fg_focus)
beautiful.taglist_squares_unsel = utils.taglist_square_top_rect(beautiful.taglist_fg_empty)

menubar.utils.terminal = terminal -- Set the terminal for applications that require it
menubar.geometry = awful.screen.focused().mywibox:geometry()
beautiful.menubar_border_width = awful.screen.focused().mywibox.border_width



----------------------------------------------------------------------------------- Key/button bindings and rules



-- Global keys - they work everywhere
globalkeys = gears.table.join(
    --------------------------- Tag switching
    awful.key({ modkey          }, "Left",  awful.tag.viewprev,                          {description = "view previous", group = "Tag switching"}),
    awful.key({ modkey          }, "Right", awful.tag.viewnext,                          {description = "view next",     group = "Tag switching"}),
    awful.key({ altkey, "Shift" }, "Tab",   awful.tag.viewprev,                          {description = "view next",     group = "Tag switching"}),
    awful.key({ altkey          }, "Tab",   awful.tag.viewnext,                          {description = "view next",     group = "Tag switching"}),
    awful.key({ modkey          }, "Tab",   awful.tag.history.restore,                   {description = "go back",       group = "Tag switching"}),
    awful.key({ modkey          }, "d",     function () get_home_tag():view_only() end,  {description = "view desktop",  group = "Tag switching"}),

    ---------------------------- Per-tag
    gears.table.join(globalkeys, utils.get_per_tag_keys(modkey, "Per-tag")),

    --------------------------- Client switching
    awful.key({ modkey,         }, "j", function () awful.client.focus.byidx( 1) end, {description = "focus next by index",                group = "Client switching"}),
    awful.key({ modkey,         }, "k", function () awful.client.focus.byidx(-1) end, {description = "focus previous by index",            group = "Client switching"}),
    awful.key({ modkey, "Shift" }, "j", function () awful.client.swap.byidx(  1) end, {description = "swap with next client by index",     group = "Client switching"}),
    awful.key({ modkey, "Shift" }, "k", function () awful.client.swap.byidx( -1) end, {description = "swap with previous client by index", group = "Client switching"}),
    awful.key({ modkey,         }, "u", awful.client.urgent.jumpto,                   {description = "jump to urgent client",              group = "Client switching"}),

    --------------------------- Screen switching
    awful.key({ modkey, "Control" }, "j", function () awful.screen.focus_relative( 1) end,  {description = "focus the next screen",     group = "Screen switching"}),
    awful.key({ modkey, "Control" }, "k", function () awful.screen.focus_relative(-1) end,  {description = "focus the previous screen", group = "Screen switching"}),

    --------------------------- Awesome WM control`
    awful.key({ modkey, "Shift" }, "h",         hotkeys_popup.show_help,                             {description = "show help",           group = "AwesomeWM"}),
    awful.key({ modkey, "Shift" }, "BackSpace", function () shutdown_popup(pai_setup, terminal) end, {description = "show shutdown popup", group = "AwesomeWM"}),
    awful.key({ modkey          }, "r",         function () menubar.show()                      end, {description = "show the menubar",    group = "launcher"}),

    --------------------------- Layout control
    awful.key(           { modkey }, "l", function () awful.tag.incmwfact( 0.05)          end, {description = "increase master width factor", group = "layout"}),
    awful.key(           { modkey }, "h", function () awful.tag.incmwfact(-0.05)          end, {description = "decrease master width factor", group = "layout"}),
    utils.set_layout_key({ modkey }, "y", awful.layout.layouts[1]),
    utils.set_layout_key({ modkey }, "u", awful.layout.layouts[2]),
    utils.set_layout_key({ modkey }, "i", awful.layout.layouts[3]),
    utils.set_layout_key({ modkey }, "o", awful.layout.layouts[4]),
    utils.set_layout_key({ modkey }, "p", awful.layout.layouts[5]),
--  awful.key({ modkey, "Shift"   }, "h",     function () awful.tag.incnmaster( 1, nil, true) end, {description = "increase the number of master clients", group = "layout"}),
--  awful.key({ modkey, "Shift"   }, "l",     function () awful.tag.incnmaster(-1, nil, true) end, {description = "decrease the number of master clients", group = "layout"}),
--  awful.key({ modkey, "Control" }, "h",     function () awful.tag.incncol( 1, nil, true)    end, {description = "increase the number of columns", group = "layout"}),
--  awful.key({ modkey, "Control" }, "l",     function () awful.tag.incncol(-1, nil, true)    end, {description = "decrease the number of columns", group = "layout"}),
--  awful.key({ modkey,           }, "space", function () awful.layout.inc( 1)                end, {description = "select next", group = "layout"}),
--  awful.key({ modkey, "Shift"   }, "space", function () awful.layout.inc(-1)                end, {description = "select previous", group = "layout"}),

    --------------------------- App keybindings
    app_keybindings.get_keybindings(modkey)
)

-- Client keys and buttons - they work on a given client when it is focused. They do not work when there's no focused client.
clientkeys = gears.table.join(
    awful.key({ modkey          }, "f",        function (c) c.fullscreen = not c.fullscreen; c:raise() end, {description = "toggle fullscreen", group = "client"}),
    awful.key({ modkey, "Shift" }, "c",        function (c) c:kill()                                   end, {description = "close", group = "client"}),
    awful.key({ altkey          }, "F4",       function (c) c:kill()                                   end, {description = "close", group = "client"}),
    awful.key({ modkey          }, "Return",   function (c) c:swap(awful.client.getmaster())           end, {description = "move to master", group = "client"}),
    awful.key({ modkey          }, "KP_Enter", function (c) c:swap(awful.client.getmaster())           end, {description = "move to master", group = "client"})
)
clientbuttons = gears.table.join(
    awful.button({ }, 1, function (c)
        if not c.is_home_panel then
            c:emit_signal("request::activate", "mouse_click", {raise = true})
        end
    end),
    awful.button({ modkey }, 1, function (c)
        if not c.is_home_panel then
            c:emit_signal("request::activate", "mouse_click", {raise = true})
            c.floating = true
            c.maximized = false
            awful.mouse.client.move(c)
        end
    end),
    awful.button({ modkey }, 2, function (c)
        if not c.is_home_panel then
            c:emit_signal("request::activate", "mouse_click", {raise = true})
            c.floating = false
            c.maximized = false
        end
    end),
    awful.button({ modkey }, 3, function (c)
        if not c.is_home_panel then
            c:emit_signal("request::activate", "mouse_click", {raise = true})
            awful.mouse.client.resize(c)
        end
    end)
)

-- Setup all the rules
root.keys(globalkeys)
awful.rules.rules = gears.table.join(
    {
        rules_utils.get_default_rule(clientkeys, clientbuttons),
        rules_utils.get_floating_clients_rule(),
        rules_utils.get_non_floating_clients_rule(),
    },
    rules_utils.get_no_border_rules(),
    rules_utils.get_tag_mappings_rules(tags),
    awful.rules.rules
)



----------------------------------------------------------------------------------- Client signals (callbacks)

client.connect_signal("tagged", function (client, tag)
    -- Do not left moving clients to home panel tag. We need additional "client.managed" check,
    -- because when home panel clients (i.e. cava) are created, this signal is called before
    -- setting is_home_panel=True, so we have no way to check it.
    if tag.is_home and client.managed and not client.is_home_panel then
        local default_tag = client.screen.tags[default_tag_index]
        client:move_to_tag(default_tag)
    end
end)

client.connect_signal("manage", function (client)
    -- Prevent clients from being unreachable after screen count changes.
    if awesome.startup
      and not client.size_hints.user_position
      and not client.size_hints.program_position then
        awful.placement.no_offscreen(client)
    end

    -- Do not let creating new clients on home panel tag
    if client.first_tag.is_home and not client.is_home_panel then
        local default_tag = client.screen.tags[default_tag_index]
        client:move_to_tag(default_tag)
    end
    client.managed = true -- custom field, not a part of AwesomeWM
end)

-- Enable sloppy focus, so that focus follows mouse.
client.connect_signal("mouse::enter", function(c)
    c:emit_signal("request::activate", "mouse_enter", {raise = false})
end)

client.connect_signal("focus",   function(c) c.border_color = beautiful.border_focus  end)
client.connect_signal("unfocus", function(c) c.border_color = beautiful.border_normal end)
