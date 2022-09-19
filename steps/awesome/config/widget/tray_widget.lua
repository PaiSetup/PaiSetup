local wibox = require("wibox")
local awful = require("awful")
local gears = require("gears")
local beautiful = require("beautiful")
local markup_utils = require("utils.markup")
local widget_wrappers = require("utils.widget_wrappers")
local keygrabber = require("awful.keygrabber")
local dpi = require("beautiful.xresources").apply_dpi

local _tray_popup_data = nil
return function()
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
