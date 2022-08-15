local wibox = require("wibox")
local awful = require("awful")
local gears = require("gears")
local beautiful = require("beautiful")
local markup_utils = require("utils.markup")

local function script_widget(name, buttons, timeout)
    base_widget = wibox.widget.textbox()
    base_widget.setup_my_foreground = "#FF0000"

    local widget = awful.widget.watch(
        linux_setup_status_scripts .. name,
        timeout,
        function(widget, stdout)
            text = markup_utils.wrap_span(stdout, widget.my_foreground, nil)
            widget.markup = text
        end,
        base_widget
    )

    widget.base_widget = base_widget
    widget.setup_my_foreground = function (widget, foreground) 
        widget.base_widget.my_foreground = foreground 
    end
    widget:setup_my_foreground(beautiful.fg_normal)

    handlers = {}
    for key, button in pairs(buttons) do
        handlers = gears.table.join(
            handlers,
            awful.button({ }, button, function() awful.spawn(command .. " " .. button) end)
        )
    end
    widget:buttons(handlers)
    return widget
end

local function time_widget()
    local widget = wibox.widget.textclock()
    widget.setup_my_foreground = function(widget, foreground)
        widget.format = markup_utils.wrap_span("%d-%m-%Y  %H:%M", foreground, nil)
    end
    return widget
end

return {
    script_widget = script_widget,
    time_widget = time_widget,
}
