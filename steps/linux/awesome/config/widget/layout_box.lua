
local awful = require("awful")
local widget_wrappers = require("widget.wrappers")
local beautiful = require("beautiful")
local gears = require("gears")
local dpi = require("beautiful.xresources").apply_dpi

return function(screen)
    local widget = awful.widget.layoutbox(screen)
    widget:buttons(gears.table.join(
        awful.button({ }, 1, function () awful.layout.inc( 1) end),
        awful.button({ }, 3, function () awful.layout.inc(-1) end),
        awful.button({ }, 4, function () awful.layout.inc(-1) end),
        awful.button({ }, 5, function () awful.layout.inc( 1) end)
    ))
    widget = widget_wrappers.margin(widget, dpi(3))
    widget = widget_wrappers.bg(widget, beautiful.color_gray_light)
    return widget
end
