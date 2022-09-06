local wibox = require("wibox")
local awful = require("awful")
local gears = require("gears")
local beautiful = require("beautiful")
local markup_utils = require("utils.markup")
local widget_wrappers = require("utils.widget_wrappers")
local keygrabber = require("awful.keygrabber")
local dpi = require("beautiful.xresources").apply_dpi

local function script_widget(name, buttons, timeout, initial_text)
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
    return widget
end

local _shutdown_popup_data = nil
local function shutdown_popup()
    -- Create the popup and all its data, if this is the first time we call it
    if _shutdown_popup_data == nil then
        local function create_button(icon, caption, callback)
            local widget = {
                widget = wibox.widget.textbox,
                text = icon,
                forced_height = dpi(100),
                forced_width = dpi(100),
                align = "center",
                valign = "center",
                font = "sans 50",
            }
            widget = widget_wrappers.margin(widget, dpi(10))
            widget = widget_wrappers.border(widget, gears.shape.rounded_rect, dpi(3), beautiful.color_gray_light)
            widget = wibox.widget(widget)
            widget.set_focused = function(self, value)
                if value then
                    self.bg = beautiful.color_theme
                else
                    self.bg = beautiful.color_gray_light
                end
            end
            widget.callback = callback
            widget.caption = caption
            return widget
        end

        local function create_selected_caption()
            local widget = wibox.widget.textbox()
            widget.align = "center"
            widget.valign = "center"
            widget.font = "sans 20"
            return widget
        end

        local function create_main_widget(buttons)
            local widget = {
                layout = wibox.layout.fixed.vertical,
                spacing = dpi(10),
                gears.table.join(
                    {
                        layout = wibox.layout.fixed.horizontal,
                        spacing = dpi(10),
                    },
                    _shutdown_popup_data.buttons
                ),
                _shutdown_popup_data.selected_caption
            }
            widget = widget_wrappers.margin(widget, dpi(5))
            return widget
        end

        _shutdown_popup_data = {}
        _shutdown_popup_data.selection = 0
        _shutdown_popup_data.buttons = {
            create_button("", "Cancel",   function()                               end),
            create_button("", "Shutdown", function() awful.spawn("shutdown now")   end),
            create_button("", "Reboot",   function() awful.spawn("reboot")         end),
            create_button("", "Exit GUI", function() awful.spawn("pkill awesome")  end),
        }
        _shutdown_popup_data.selected_caption = create_selected_caption()
        _shutdown_popup_data.refresh = function(self)
            for _, button in pairs(self.buttons) do
                button:set_focused(false)
            end
            self.buttons[self.selection]:set_focused(true)
            self.selected_caption.text = self.buttons[self.selection].caption
        end

        _shutdown_popup_data.popup = awful.popup {
            widget    = create_main_widget(_shutdown_popup_data.buttons),
            ontop     = true,
            placement = awful.placement.centered,
            shape     = gears.shape.rounded_rect,
            visible   = false,
            bg        = beautiful.color_gray_dark
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

local naughty = require("naughty")

local _tray_popup_data = nil
local function tray_widget()
    local function create_popup()
        if _tray_popup_data == nil then
            -- Some constants
            local margins = {
                top = beautiful.wibar_height + 2 * beautiful.wibar_border_width,
                right = beautiful.wibar_border_width,
            }
            local width = dpi(40)
            local height = width * 4 -- I cannot make this change height based on the number of apps, so we just hardcode space for 4 apps :()

            -- Create main widget - the systray
            _tray_popup_data = {}
            _tray_popup_data.main_widget = wibox.widget.systray()
            _tray_popup_data.main_widget.forced_width = width
            _tray_popup_data.main_widget.forced_height = height
            _tray_popup_data.main_widget:set_horizontal(false)

            -- Create popup instance, initially hidden
            _tray_popup_data.popup = awful.popup {
                widget    = _tray_popup_data.main_widget,
                ontop     = true,
                placement = function(c) return awful.placement.top_right(c, { margins = margins }) end,
                shape     = gears.shape.rounded_rect,
                visible   = false,
                minimum_width = width,
                maxmimum_width = width,
                minimum_height = width,
                maximum_height = height,
                hide_on_right_click = false,
            }
        end
        return _tray_popup_data.popup
    end

    local function create_button(widget_to_show)
        local widget = wibox.widget.textbox()
        widget.is_clicked = false
        widget.refresh = function (self)
            local icon = ""
            if self.is_clicked then
                icon = ""
            end
            self.markup = markup_utils.wrap_span(icon, self.my_foreground, nil)
            widget_to_show.visible = self.is_clicked
        end
        widget.setup_my_foreground = function (self, foreground)
            self.my_foreground = foreground
            self:refresh()
        end

        widget:connect_signal("button::press", function (self, lx, ly, button, mods, metadata)
            if button == 1 then
                self.is_clicked = not self.is_clicked
                self:refresh()
            end
        end)

        widget:setup_my_foreground("#FF0000")

        return widget
    end

    popup = create_popup()
    button = create_button(popup)
    popup:connect_signal("button::press", function (self, lx, ly, button_id, mods, metadata)
        if button_id == 1 or button_id == 3 then
            button:emit_signal("button::press", lx, ly, 1, mods, metadata)
        end
    end)
    return button
end

return {
    script_widget = script_widget,
    shutdown_popup = shutdown_popup,
    tray_widget = tray_widget,
}
