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
local widget_wrappers = require("utils.widget_wrappers")
local widget_utils = require("utils.widget")
local markup_utils = require("utils.markup")
local utils = require("utils.utils")
local rules_utils = require("utils.rules")
local app_keybindings = require("utils.app_keybindings")



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
editor = os.getenv("EDITOR") or "nano"
editor_cmd = terminal .. " -e " .. editor
linux_setup = os.getenv("LINUX_SETUP_ROOT")
linux_setup_status_scripts = linux_setup .. "/steps/gui/statusbar/"
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
beautiful.wallpaper = gears.filesystem.get_xdg_config_home() .. "/LinuxSetup/wallpaper"



----------------------------------------------------------------------------------- Client layouts
awful.layout.layouts = {
    awful.layout.suit.tile,
    awful.layout.suit.floating,
    awful.layout.suit.tile.left,
    awful.layout.suit.tile.bottom,
    awful.layout.suit.tile.top,
    awful.layout.suit.fair,
    awful.layout.suit.fair.horizontal,
    awful.layout.suit.spiral,
    awful.layout.suit.spiral.dwindle,
    awful.layout.suit.max,
    awful.layout.suit.max.fullscreen,
    awful.layout.suit.magnifier,
    awful.layout.suit.corner.nw,
    -- awful.layout.suit.corner.ne,
    -- awful.layout.suit.corner.sw,
    -- awful.layout.suit.corner.se,
}

----------------------------------------------------------------------------------- Top bar

-- Preserve tags after restart
utils.enable_viewed_tag_preserving()

local taglist_buttons = gears.table.join(
    awful.button({ },        1, function(t) t:view_only()                                        end),
    awful.button({ modkey }, 1, function(t) if client.focus then client.focus:move_to_tag(t) end end),
    awful.button({ },        3, awful.tag.viewtoggle),
    awful.button({ modkey }, 3, function(t) if client.focus then client.focus:toggle_tag(t)  end end),
    awful.button({ },        4, function(t) awful.tag.viewnext(t.screen)                         end),
    awful.button({ },        5, function(t) awful.tag.viewprev(t.screen)                         end)
)

-- Re-set wallpaper when a screen's geometry changes (e.g. different resolution)
screen.connect_signal("property::geometry", utils.set_wallpaper)

-- Leaf widgets
local memory_widget = widget_utils.script_widget("memory.sh", {button_info}, 5)
local uptime_widget = widget_utils.script_widget("uptime.sh", {}, 60)
local volume_widget = widget_utils.script_widget("volume.sh", {button_action, button_scroll_up, button_scroll_down}, 60)
local packages_widget = widget_utils.script_widget("packages.sh", {button_info, button_action}, 60)
local time_widget = widget_utils.script_widget("date.sh", {button_action}, 30)
local warnings_widget = widget_utils.script_widget("warnings.sh", {button_info}, 4)
local tray_widget = widget_utils.tray_widget()
local screen_capture_widget = widget_utils.script_widget("screen_capture.sh", {button_info, button_action}, 10)
local pomodoro_widget = widget_utils.script_widget("pomodoro.sh", {button_info, button_action}, 10)
local audio_switch_widget = widget_utils.script_widget("audio_switch.sh", {button_info, button_action}, 10)

local tags = {
    web = "",
    code = "",
    draw = "",
    video = "",
    music = "",
}

-- Setup widgets for each screen
awful.screen.connect_for_each_screen(function(s)
    -- Wallpaper
    utils.set_wallpaper(s)

    -- Each screen has its own tag table.
    awful.tag({tags.web, tags.code, "", "", "", "", tags.draw, tags.video, tags.music }, s, awful.layout.layouts[1])

    -- Create an imagebox widget which will contain an icon indicating which layout we're using.
    s.mylayoutbox = awful.widget.layoutbox(s)
    s.mylayoutbox:buttons(gears.table.join(
        awful.button({ }, 1, function () awful.layout.inc( 1) end),
        awful.button({ }, 3, function () awful.layout.inc(-1) end),
        awful.button({ }, 4, function () awful.layout.inc( 1) end),
        awful.button({ }, 5, function () awful.layout.inc(-1) end)
    ))

    -- Create a taglist widget
    s.mytaglist = awful.widget.taglist {
        screen  = s,
        filter  = awful.widget.taglist.filter.all,
        buttons = taglist_buttons,
        widget_template =
        {
            {
                {
                    {
                        id     = 'text_role',
                        widget = wibox.widget.textbox,
                    },
                    layout = wibox.layout.fixed.horizontal,
                },
                left  = 10,
                right = 10,
                widget = wibox.container.margin
            },
            id     = 'background_role',
            widget = wibox.container.background,
        },
    }

    -- Create a tasklist widget
    s.mytasklist = awful.widget.tasklist {
        screen  = s,
        filter  = awful.widget.tasklist.filter.focused,
        buttons = tasklist_buttons,
        widget_template = {
            widget = wibox.container.background,
            id = "background_role",
            forced_width = dpi(300),
            forced_height = beautiful.wibar_height,
            widget_wrappers.margin({
                layout = wibox.layout.align.horizontal,
                {
                    id     = 'icon_role',
                    widget = wibox.widget.imagebox,
                },
                {
                    id     = 'text_role',
                    widget = wibox.widget.textbox,
                },
            }, dpi(4)),
        },
    }

    -- Create the wibox
    s.mywibox = awful.wibar({ position = "top", screen = s, })

    -- Add widgets to the wibox
    s.mywibox:setup {
        layout = wibox.layout.align.horizontal,
        -- Left widgets
        {
            layout = wibox.layout.fixed.horizontal,
            {
                widget = wibox.container.background,
                bg     = beautiful.bg_normal,
                shape  = gears.shape.rounded_rect,
                s.mytaglist,
            }
          },

        -- Middle widget
        {
            widget = wibox.container.place,
            halign  = center,
            s.mytasklist,
        },

        -- Right widgets
        {
            layout = wibox.layout.fixed.horizontal,
            spacing = beautiful.widgets_group_margin,
            widget_wrappers.grp({memory_widget}),
            widget_wrappers.grp({uptime_widget}),
            widget_wrappers.grp({volume_widget}),
            widget_wrappers.grp({packages_widget}),
            widget_wrappers.grp({time_widget}),
            widget_wrappers.grp({
                screen_capture_widget,
                pomodoro_widget,
                audio_switch_widget,
                tray_widget,
                warnings_widget,
            }),
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
    awful.key({ modkey          }, "Left",  awful.tag.viewprev,        {description = "view previous", group = "Tag switching"}),
    awful.key({ modkey          }, "Right", awful.tag.viewnext,        {description = "view next",     group = "Tag switching"}),
    awful.key({ altkey, "Shift" }, "Tab",   awful.tag.viewprev,        {description = "view next",     group = "Tag switching"}),
    awful.key({ altkey          }, "Tab",   awful.tag.viewnext,        {description = "view next",     group = "Tag switching"}),
    awful.key({ modkey          }, "Tab",   awful.tag.history.restore, {description = "go back",       group = "Tag switching"}),

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

    --------------------------- Program launching
    awful.key({ modkey }, "r",                   function () menubar.show()               end, {description = "show the menubar",  group = "launcher"}),
    awful.key({ modkey, "Shift"   }, "Return",   function () awful.spawn(terminal)        end, {description = "open a terminal",   group = "launcher"}),
    awful.key({ modkey, "Shift"   }, "KP_Enter", function () awful.spawn(terminal)        end, {description = "open a terminal",   group = "launcher"}),
    awful.key({ modkey, "Shift"   }, "s",        function () awful.spawn("flameshot gui") end, {description = "make a screenshot", group = "launcher"}),

    --------------------------- Awesome WM control
    awful.key({ modkey, "Shift" }, "h",         hotkeys_popup.show_help,                                  {description = "show help",           group = "AwesomeWM"}),
    awful.key({ modkey, "Shift" }, "q",         awesome.restart,                                          {description = "reload awesome",      group = "AwesomeWM"}),
    awful.key({ modkey, "Shift" }, "w",         function () utils.set_random_wallpaper(linux_setup) end,  {description = "change wallpaper",    group = "AwesomeWM"}),
    awful.key({ modkey, "Shift" }, "BackSpace", widget_utils.shutdown_popup,                              {description = "show shutdown popup", group = "AwesomeWM"}),

    --------------------------- Layout control
    awful.key({ modkey,           }, "l",     function () awful.tag.incmwfact( 0.05)          end, {description = "increase master width factor", group = "layout"}),
    awful.key({ modkey,           }, "h",     function () awful.tag.incmwfact(-0.05)          end, {description = "decrease master width factor", group = "layout"}),
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
        c:emit_signal("request::activate", "mouse_click", {raise = true})
    end),
    awful.button({ modkey }, 1, function (c)
        c:emit_signal("request::activate", "mouse_click", {raise = true})
        c.floating = true
        awful.mouse.client.move(c)
    end),
    awful.button({ modkey }, 2, function (c)
        c:emit_signal("request::activate", "mouse_click", {raise = true})
        c.floating = false
    end),
    awful.button({ modkey }, 3, function (c)
        c:emit_signal("request::activate", "mouse_click", {raise = true})
        awful.mouse.client.resize(c)
    end)
)

-- Setup all the rules
root.keys(globalkeys)
awful.rules.rules = gears.table.join(
    {
        rules_utils.get_default_rule(clientkeys, clientbuttons),
        rules_utils.get_floating_clients_rule(),
    },
    rules_utils.get_no_border_rules(),
    rules_utils.get_tag_mappings_rules(tags)
)



----------------------------------------------------------------------------------- Client signals (callbacks)
client.connect_signal("manage", function (c)
    -- Set the windows at the slave,
    -- i.e. put it at the end of others instead of setting it master.
    -- if not awesome.startup then awful.client.setslave(c) end

    if awesome.startup
      and not c.size_hints.user_position
      and not c.size_hints.program_position then
        -- Prevent clients from being unreachable after screen count changes.
        awful.placement.no_offscreen(c)
    end
end)

-- Enable sloppy focus, so that focus follows mouse.
client.connect_signal("mouse::enter", function(c)
    c:emit_signal("request::activate", "mouse_enter", {raise = false})
end)

client.connect_signal("focus",   function(c) c.border_color = beautiful.border_focus  end)
client.connect_signal("unfocus", function(c) c.border_color = beautiful.border_normal end)
