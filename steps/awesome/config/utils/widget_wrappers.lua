local wibox = require("wibox")
local beautiful = require("beautiful")
local gears = require("gears")

local function margin(arg, value)
    return {
        margins = value,
        widget = wibox.container.margin,
        arg,
    }
end

local function horizontal_margin(arg, value)
    return {
        layout = wibox.container.margin,
        left = value,
        right = value,
        arg,
    }
end

local function border(arg, shape, width, color)
    return {
        layout = wibox.container.background,
        shape = shape,
        shape_border_width = width,
        shape_border_color = color,
        arg,
    }
end

local function bg(arg, color)
    return {
        layout = wibox.container.background,
        bg = color,
        shape = gears.shape.rounded_rect,
        shape_border_width = beautiful.border_width,
        shape_border_color = "#000000",
        arg,
    }
end

local function min_width(arg, width)
    return {
        widget = wibox.container.constraint,
        arg,
        strategy = 'min',
        width = width,
    }
end

local function max_width(arg, width)
    return {
        widget = wibox.container.constraint,
        arg,
        strategy = 'max',
        width = width,
    }
end

local function width_between(arg, min, max)
    return min_width(max_width(arg, max), min)
end

local alternating_counter = 0
local function grp(arg)
    if alternating_counter % 2 == 0 then
        fg_color = beautiful.color_theme
        bg_color = beautiful.color_gray_light
    else
        fg_color = beautiful.color_gray_light
        bg_color = beautiful.color_theme
    end
    alternating_counter = alternating_counter + 1

    for index, widget in pairs(arg) do
        widget:setup_my_foreground(fg_color)
    end

    arg.layout = wibox.layout.fixed.horizontal
    arg.spacing = beautiful.widgets_margin
    return bg(horizontal_margin(arg, beautiful.widgets_padding), bg_color)
end

return {
    margin = margin,
    horizontal_margin = horizontal_margin,
    bg = bg,
    min_width = min_width,
    max_width = max_width,
    width_between = width_between,
    border = border,
    grp = grp,
}
