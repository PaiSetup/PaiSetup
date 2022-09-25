local widget_wrappers = require("widget.wrappers")
local awful = require("awful")
local dpi = require("beautiful.xresources").apply_dpi
local wibox = require("wibox")
local beautiful = require("beautiful")

return function(screen)
    return awful.widget.tasklist {
        screen  = screen,
        filter  = awful.widget.tasklist.filter.focused,
        widget_template = {
            widget = wibox.container.background,
            id = "background_role",
            forced_height = beautiful.wibar_height,
            widget_wrappers.horizontal_margin({
                layout = wibox.layout.fixed.horizontal,
                widget_wrappers.horizontal_margin({
                    id     = 'icon_role',
                    widget = wibox.widget.imagebox,
                }, dpi(6)),
                widget_wrappers.width_between({
                    widget = wibox.widget.textbox,
                    id     = 'text_role',
                    align  = 'center',
                }, dpi(500), dpi(850))
            }, dpi(10)),
        },
    }
end
