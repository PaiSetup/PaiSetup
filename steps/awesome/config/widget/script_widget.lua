local wibox = require("wibox")
local awful = require("awful")
local gears = require("gears")
local beautiful = require("beautiful")
local markup_utils = require("utils.markup")
local widget_wrappers = require("widget.wrappers")
local keygrabber = require("awful.keygrabber")
local dpi = require("beautiful.xresources").apply_dpi

return function (name, buttons, timeout, initial_text)
    local command = linux_setup_status_scripts .. name

    -- Create the base widget for our watch widget, so we can insert some additional
    -- fields. This additional state is needed to implement alternating foreground colors.
    -- Textbox widget doesn't have fgColor field on itself
    base_widget = wibox.widget.textbox()
    base_widget.my_foreground = "#FF0000"
    if initial_text ~= nil then
        base_widget.my_text = initial_text
    else
        base_widget.my_text = ""
    end
    base_widget.refresh = function(self, text)
        self.markup = markup_utils.wrap_span(self.my_text, self.my_foreground, nil)
    end

    -- Create the watch widget and supply our preparated base_widget. It must contain the
    -- extra foreground color field, which we use in update callback function.
    local widget, timer = awful.widget.watch(
        command,
        timeout,
        function (widget, stdout)
            widget.my_text = stdout
            widget:refresh()

            for index, widget_to_update in pairs(widget.widgets_to_update) do
                widget_to_update:run_script()
            end
        end,
        base_widget
    )

    -- Add additional fields to the watch widget, so our logic for setting foreground colors
    -- can access base_widget's color.
    widget.base_widget = base_widget
    widget.setup_my_foreground = function (widget, foreground)
        widget.base_widget.my_foreground = foreground
        widget.base_widget:refresh()
    end

    -- Register mouse button handlers only for the buttons that were selected. The rest will be
    -- ignored.
    local handlers = {}
    for key, button in pairs(buttons) do
        local handler = awful.button({ }, button, function()
            awful.spawn.easy_async_with_shell(command .. " " .. button, function()
                timer:emit_signal("timeout")
            end)
        end)
        handlers = gears.table.join(handlers, handler)
    end
    widget:buttons(handlers)

    -- Create a function to manually rerun the underlying script and update widget's view.
    widget.run_script = function(self)
        awful.spawn.easy_async_with_shell(command, function()
            timer:emit_signal("timeout")
        end)
    end

    -- Prepare an array of other script widgets that should be updated whenever this one is
    -- done executing.
    widget.widgets_to_update = {}
    widget.add_widget_to_update = function(self, widget_to_update)
        self.widgets_to_update[#self.widgets_to_update+1] = widget_to_update
    end

    -- Finally return the widget
    return widget
end
