local wibox = require("wibox")
local awful = require("awful")
local gears = require("gears")
local beautiful = require("beautiful")
local markup_utils = require("utils.markup")

local function script_widget(name, buttons, timeout)
    local command = linux_setup_status_scripts .. name

    -- Create the base widget for our watch widget, so we can insert some additional
    -- fields. This additional state is needed to implement alternating foreground colors.
    -- Textbox widget doesn't have fgColor field on itself
    base_widget = wibox.widget.textbox()
    base_widget.my_foreground = "#FF0000"

    -- Create the watch widget and supply our preparated base_widget. It must contain the
    -- extra foreground color field, which we use in update callback function.
    local widget, timer = awful.widget.watch(
        command,
        timeout,
        function(widget, stdout)
            text = markup_utils.wrap_span(stdout, widget.my_foreground, nil)
            widget.markup = text
        end,
        base_widget
    )

    -- Add additional fields to the watch widget, so our logic for setting foreground colors
    -- can access base_widget's color.
    widget.base_widget = base_widget
    widget.setup_my_foreground = function (widget, foreground) 
        widget.base_widget.my_foreground = foreground 
    end
    widget:setup_my_foreground(beautiful.fg_normal)

    -- Refresh the widget after interaction with one of selected buttons. The sleep is needed
    -- for some reason to display up to date information.
    widget:connect_signal("button::press",  function(_, _, _, pressed_button)
        for _, button in pairs(buttons) do
            if button == tostring(pressed_button) then
                os.execute("sleep 0.05") -- TODO it seems only audio_switch needs this. volume.sh feels less responsive because of this
                timer:emit_signal("timeout")
            end
        end
    end)

    -- Register mouse button handlers only for the buttons that were selected. The rest will be
    -- ignored.
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

return {
    script_widget = script_widget,
}
