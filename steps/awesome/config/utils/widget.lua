local wibox = require("wibox")
local awful = require("awful")
local gears = require("gears")
local beautiful = require("beautiful")
local markup_utils = require("utils.markup")
local widget_wrappers = require("utils.widget_wrappers")
local keygrabber = require("awful.keygrabber")

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

local _shutdown_popup_data = nil
local function shutdown_popup()
    -- Create the popup and all its data, if this is the first time we call it
    if _shutdown_popup_data == nil then
        local function create_button(text, callback)
            local widget = {
                widget = wibox.widget.textbox,
                text = text,
                forced_height = 100,
                forced_width = 100,
                align = "center",
                valign = "center",
            }
            widget = widget_wrappers.margin(widget, 10)
            widget = widget_wrappers.border(widget, gears.shape.rounded_rect, 3, beautiful.color_gray_light)
            widget.set_focused = function(self, value)
                if value then
                    self.shape_border_color = beautiful.color_theme
                else
                    self.shape_border_color = beautiful.color_gray_light
                end
            end
            widget.callback = callback
            return widget
        end

        local function create_main_widget(buttons)
            local widget = gears.table.join(
                {
                    layout = wibox.layout.fixed.horizontal,
                    spacing = 10,
                },
                _shutdown_popup_data.buttons
            )
            widget = widget_wrappers.margin(widget, 5)
            return widget
        end

        _shutdown_popup_data = {}
        _shutdown_popup_data.selection = 0
        _shutdown_popup_data.buttons = {
            create_button("Cancel",   function() end ),
            create_button("Shutdown", function() awful.spawn("shutdown now") end),
            create_button("Reboot",   function() awful.spawn("reboot")       end),
            create_button("Exit GUI", function() awful.spawn("pkill awesome")       end),
        }
        _shutdown_popup_data.refresh = function(self)
            for _, button in pairs(self.buttons) do
                button:set_focused(false)
            end
            self.buttons[self.selection]:set_focused(true)
        end

        _shutdown_popup_data.popup = awful.popup {
            widget = create_main_widget(_shutdown_popup_data.buttons),
            placement    = awful.placement.centered,
            shape        = gears.shape.rounded_rect,
            visible      = false,
            bg = beautiful.color_gray_dark
        }
    end

    -- By now the popup must have been used at least once
    _shutdown_popup_data.popup.visible = not _shutdown_popup_data.popup.visible

    -- Perform additional work if we just showed the popup
    if _shutdown_popup_data.popup.visible then
        -- Reset the selection
        _shutdown_popup_data.selection = 1
        _shutdown_popup_data:refresh()

        -- Intercept all keyboard input to navigate in the popup
        keygrabber.run(function(mod, key, event)
            if event ~= "press" then
                return
            end
            if key == "Left" then
                _shutdown_popup_data.selection = math.max(_shutdown_popup_data.selection - 1, 1)
                _shutdown_popup_data:refresh()
            elseif key == "Right" then
                _shutdown_popup_data.selection = math.min(_shutdown_popup_data.selection + 1, #_shutdown_popup_data.buttons)
                _shutdown_popup_data:refresh()
            elseif key == "Escape" then
                _shutdown_popup_data.popup.visible = false
                keygrabber.stop(grabber)
                return
            elseif key == "Return" or key == " " then
                _shutdown_popup_data.popup.visible = false
                _shutdown_popup_data.buttons[_shutdown_popup_data.selection].callback()
                keygrabber.stop(grabber)
                return
            end
        end)
    end
end

return {
    script_widget = script_widget,
    shutdown_popup = shutdown_popup,
}
