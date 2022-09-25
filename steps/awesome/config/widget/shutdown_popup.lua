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
            create_button("", "Exit GUI",            function() awful.spawn("pkill awesome")  end),
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