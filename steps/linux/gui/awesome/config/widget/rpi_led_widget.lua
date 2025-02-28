local wibox = require("wibox")
local awful = require("awful")
local gears = require("gears")
local beautiful = require("beautiful")
local markup_utils = require("utils.markup")
local widget_wrappers = require("widget.wrappers")
local create_toggle_button = require("widget.toggle_button")
local dpi = require("beautiful.xresources").apply_dpi

local pai_setup = nil
local rpi_led_state = {}
rpi_led_state.enabled_sections = 0
rpi_led_state.brightness = 0
rpi_led_state.query_rpi_led = function(self)
    command = pai_setup .. "/steps/linux/rpi_led/client/query_rpi_led.py --brightness --sections"
    awful.spawn.easy_async_with_shell(command, function(stdout)
        matcher = stdout:gmatch("[^\r\n]+")
        rpi_led_state.brightness = matcher()
        rpi_led_state.enabled_sections = tonumber(matcher())

        awesome.emit_signal("rpi_led::queried_state")
    end)
end
rpi_led_state.update_rpi_led = function(self)
    executable = pai_setup .. "/steps/linux/rpi_led/client/update_rpi_led.py"
    arg_section = " -s " .. tostring(self.enabled_sections)
    arg_brightness = " -b " .. tostring(self.brightness)
    command =  executable .. arg_section .. arg_brightness
    awful.spawn.easy_async_with_shell(command, function() end)
end
rpi_led_state.set_section = function(self, value, index)
    local mask = 1 << (index - 1)
    if value then
        self.enabled_sections = self.enabled_sections | mask
    else
        self.enabled_sections = self.enabled_sections & (~mask)
    end
    self:update_rpi_led()
end
rpi_led_state.is_section_enabled = function(self, index)
    local mask = 1 << (index - 1)
    return (self.enabled_sections & mask) ~= 0
end
rpi_led_state.set_brightness = function(self, value)
    self.brightness = value / 100
    self:update_rpi_led()
end
rpi_led_state.get_brightness = function(self)
    return self.brightness * 100
end

local function create_section_button(icon, index)
    local function callback(widget, value, index)
        if widget.send_to_rpi then
            rpi_led_state:set_section(value, index)
        end
    end

    local widget = create_toggle_button(
        icon,
        beautiful.color_theme,
        beautiful.color_gray_dark,
        true,
        callback,
        index
    )
    widget.send_to_rpi = true

    awesome.connect_signal("rpi_led::queried_state", function()
        widget.send_to_rpi = false
        widget:set_is_clicked(rpi_led_state:is_section_enabled(index))
        widget.send_to_rpi = true
    end)

    return widget
end

local function create_brightness_slider()
    local widget = wibox.widget.slider()
    widget.bar_shape = gears.shape.rounded_rect
    widget.bar_height = dpi(10)
    widget.bar_color = beautiful.color_gray_dark
    widget.handle_color = beautiful.color_theme
    widget.handle_shape = gears.shape.circle
    widget.handle_width = dpi(25)
    widget.value = rpi_led_state:get_brightness()
    widget.send_to_rpi = true

    widget:connect_signal("property::value", function()
        if widget.send_to_rpi then
            rpi_led_state:set_brightness(widget.value)
        end
    end)

    awesome.connect_signal("rpi_led::queried_state", function()
        widget.send_to_rpi = false
        widget.value = rpi_led_state:get_brightness()
        widget.send_to_rpi = true
    end)

    return widget
end

local function create_popup(screen)
    -- Some size constants
    local window_width = dpi(200)
    local window_height = dpi(110)
    local button_spacing = dpi(10)

    local layout_line0 = wibox.layout.fixed.horizontal()
    layout_line0.spacing = button_spacing
    icon_speakers=""    -- U+F8DE - PaiIconGlyphs
    icon_monitor=""     -- U+F108 - FontAwesome
    layout_line0:add(create_section_button(icon_speakers, 1))
    layout_line0:add(create_section_button(icon_monitor, 2))
    layout_line0:add(create_section_button(icon_speakers, 3))

    local layout_line1 = wibox.layout.fixed.horizontal()
    layout_line1:add(create_brightness_slider())

    local root_layout = wibox.layout.fixed.vertical()
    root_layout:add(layout_line0)
    root_layout:add(layout_line1)

    local widget = wibox {
        width = window_width,
        height = window_height,
        x = (screen.geometry.width - window_width),
        y = beautiful.wibar_height + 2 * beautiful.wibar_border_width + beautiful.useless_gap,
        bg = "#00000000",
        ontop = true
    }
    widget:setup(widget_wrappers.bg(widget_wrappers.margin(root_layout, root_layout.spacing), beautiful.color_gray_light))
    return widget
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

return function(screen, pai_setup_root)
    pai_setup = pai_setup_root

    popup = create_popup(screen)
    button = create_button(popup)

    rpi_led_state:query_rpi_led()
    return button
end
