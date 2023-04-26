local wibox = require("wibox")
local awful = require("awful")
local gears = require("gears")
local beautiful = require("beautiful")
local markup_utils = require("utils.markup")
local widget_wrappers = require("widget.wrappers")
local keygrabber = require("awful.keygrabber")
local dpi = require("beautiful.xresources").apply_dpi

local _shutdown_popup_data = nil
return function (linux_setup_root, terminal)
    -- Create the popup and all its data, if this is the first time we call it
    if _shutdown_popup_data == nil then
        buttons_count = 0
        local function create_button(icon, caption, callback)
            buttons_count = buttons_count + 1

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
            widget.is_focused = false
            widget.index = buttons_count
            widget.set_focused = function(self, value)
                self.is_focused = value
                if value then
                    self.bg = beautiful.color_theme
                else
                    self.bg = beautiful.color_gray_light
                end
            end
            widget.callback = callback
            widget.caption = caption
            widget:buttons(awful.button({ }, 1, function ()
                if widget.is_focused then
                    widget.callback()
                    _shutdown_popup_data:close()
                else
                    _shutdown_popup_data:select(widget.index)
                end
            end))

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

        -- Prepare popup data
        _shutdown_popup_data = {}

        -- Prepare fields of popup data
        _shutdown_popup_data.selection = 0
        _shutdown_popup_data.selected_caption = create_selected_caption()
        _shutdown_popup_data.buttons = {
            create_button("", "Cancel",              function()                               end),
            create_button("", "Shutdown",            function() awful.spawn("shutdown now")   end),
            create_button("", "Update and shutdown", function()
                update_command = terminal .. " sh -c '$LINUX_SETUP_ROOT/steps/gui/update_packages.sh 0'"
                time_before_shutdown = 3 -- not really needed, but it doesn't hurt
                awful.spawn.easy_async_with_shell(update_command, function()
                    gears.timer.start_new(time_before_shutdown, function() awful.spawn("shutdown now") end)
                end)
            end),
            create_button("", "Reboot",              function() awful.spawn("reboot")         end),
            create_button("", "Reboot to Windows",   function()
                update_command = terminal .. " sh -c '$LINUX_SETUP_ROOT/steps/gui/reboot_to_windows.sh'"
                awful.spawn(update_command)
            end),
            create_button("", "Exit GUI",            function() awful.spawn("pkill awesome")  end),
        }
        _shutdown_popup_data.popup = awful.popup {
            widget    = create_main_widget(_shutdown_popup_data.buttons),
            ontop     = true,
            placement = awful.placement.centered,
            shape     = gears.shape.rounded_rect,
            visible   = false,
            bg        = beautiful.color_gray_dark
        }

        -- Prepare methods of popup data
        _shutdown_popup_data.keygrabber_callback = function(self, mod, key, event)
            if event ~= "press" then
                return
            end
            if key == "Left" then
                if _shutdown_popup_data.selection == 1 then
                    _shutdown_popup_data:select(#_shutdown_popup_data.buttons)
                else
                    _shutdown_popup_data:select(_shutdown_popup_data.selection - 1)
                end
            elseif key == "Right" then
                if _shutdown_popup_data.selection == #_shutdown_popup_data.buttons then
                    _shutdown_popup_data:select(1)
                else
                    _shutdown_popup_data:select(_shutdown_popup_data.selection + 1)
                end
            elseif key == "Escape" then
                _shutdown_popup_data:close()
                return
            elseif key == "Return" or key == " " then
                _shutdown_popup_data.buttons[_shutdown_popup_data.selection].callback()
                _shutdown_popup_data:close()
                return
            end
        end
        _shutdown_popup_data.open = function(self)
            self.popup.visible = true
            self:select(1)
            keygrabber.run(function(mod, key, event)
                _shutdown_popup_data:keygrabber_callback(mod, key, event)
            end)
        end
        _shutdown_popup_data.close = function(self)
            self.popup.visible = false
            keygrabber.stop(grabber)
        end
        _shutdown_popup_data.toggle_open = function(self)
            if self.popup.visible then
                self:close()
            else
                self:open()
            end
        end
        _shutdown_popup_data.select = function(self, index)
            self.selection = index
            for _, button in pairs(self.buttons) do
                button:set_focused(false)
            end
            self.buttons[self.selection]:set_focused(true)
            self.selected_caption.text = self.buttons[self.selection].caption
        end
    end

    -- Initialize popup
    _shutdown_popup_data:toggle_open()
end
