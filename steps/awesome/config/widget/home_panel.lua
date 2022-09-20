local wibox = require("wibox")
local awful = require("awful")
local gears = require("gears")
local beautiful = require("beautiful")
local markup_utils = require("utils.markup")
local widget_wrappers = require("utils.widget_wrappers")
local keygrabber = require("awful.keygrabber")
local dpi = require("beautiful.xresources").apply_dpi

local naughty = require("naughty")


-- Global constants
local tile_size = dpi(200)

local function wrap_widget(widget, rowspan, colspan)
    widget = widget_wrappers.sized_bg(widget, beautiful.color_gray_light, colspan * tile_size, rowspan * tile_size)
    widget = wibox.widget(widget)
    return widget
end

local function create_disk_usage_widget(mount_point)
    local mount_point_caption = wibox.widget.textbox()
    mount_point_caption.text = mount_point
    mount_point_caption.align = 'center'
    mount_point_caption.font = "sans " .. tostring(tile_size * 0.08)

    local chart = wibox.container.arcchart(mount_point_caption)
    chart.thickness = tile_size * 0.1
    chart.bg = beautiful.color_gray_dark
    chart.colors = { beautiful.color_theme }
    chart.min_value = 0
    chart.max_value = 100
    chart.forced_width = tile_size * 0.8
    chart.forced_height = tile_size * 0.8

    local caption = wibox.widget.textbox()
    caption.text = ""
    caption.font = "sans " .. tostring(tile_size * 0.07)

    local widget = wibox.widget {
        layout  = wibox.layout.fixed.horizontal,
        spacing = tile_size * 0.1,
        chart,
        caption,
    }

    local command = "bash -c 'df " .. mount_point .. " --output=used,size,pcent -h | tail +2'"
    widget = awful.widget.watch(command, 5, function (_, stdout)
            matcher = stdout:gmatch("%S+")
            used = matcher()
            size = matcher()
            percent = matcher()
            if percent ~= nil then
                chart.value = tonumber(string.sub(percent, 1, -2))
                caption.text = used .. " of " .. size .. " used (" .. percent .. ")"
            else
                chart.value = 0
                caption.text = "ERROR: " .. mount_point .. " is invalid"
            end
        end,
        widget
    )

    widget = widget_wrappers.margin(widget, tile_size * 0.04)
    return wrap_widget(widget, 1, 2)
end

local function create_xd(text)
    local widget = wibox.widget.textbox()
    widget.text = text
    widget.align = 'center'
    widget.font = "sans " .. tostring(tile_size * 0.08)
    return wrap_widget(widget, 1, 1)
end

local function create_calendar()
    local bold = function(t) return '<b>' .. t .. '</b>' end
    local styles = {
        month = {
            padding      = 5,
            bg_color     = beautiful.color_gray_light,
            border_width = 2,
        },
        weeknumber = {
            fg_color = beautiful.color_gray_light,
            bg_color = beautiful.color_theme,
            markup = bold,
        },
        focus = {
            fg_color = beautiful.color_gray_light,
            bg_color = beautiful.color_theme,
            shape = gears.shape.rounded_rect,
            markup = bold,
        },
        header = {
            fg_color = beautiful.color_theme,
            bg_color = beautiful.color_gray_light,
            markup = bold,
        },
        weekday = {
            fg_color = beautiful.color_gray_light,
            bg_color = beautiful.color_theme,
            markup = bold,
        },
        default = {
            fg_color = beautiful.color_theme,
            bg_color = beautiful.color_gray_light,
            shape = gears.shape.rect,
        }
    }
    local function decorate_cell(widget, flag, date)
        if flag=='monthheader' and not styles.monthheader then
            flag = 'header'
        end
        local props = styles[flag] or styles.default
        if props.markup and widget.get_text and widget.set_markup then
            widget:set_markup(props.markup(widget:get_text()))
        end
        widget.align = 'center'
        widget.valign = 'center'

        local ret = wibox.widget {
            widget,
            shape              = props.shape    or styles.default.shape,
            fg                 = props.fg_color or styles.default.fg_color,
            bg                 = props.bg_color or styles.default.bg_color,
            widget             = wibox.container.background,
        }
        return ret
    end


    local widget = wibox.widget.calendar.month(os.date('*t'))
    widget.spacing = 0
    widget.week_numbers = true
    widget.fn_embed = decorate_cell
    widget = widget_wrappers.margin(widget, tile_size * 0.04)
    return wrap_widget(widget, 1, 1)
end

return function(visible_tag, screen)
    -- Some size constants
    local rows = 3
    local columns = 3
    local spacing = tile_size * 0.1
    local grid_width = columns * tile_size + (columns - 1) * spacing
    local grid_height = rows * tile_size + (rows - 1) * spacing
    local window_width = grid_width + 2 * spacing -- There are margins
    local window_height = grid_height + 2 * spacing -- There are margins

    -- Setup the grid layout with widgets
    local root_layout = wibox.layout.grid()
    root_layout.forced_num_rows = rows
    root_layout.forced_num_cols = columns
    root_layout.min_cols_size = tile_size
    root_layout.min_rows_size = tile_size
    root_layout.spacing = spacing
    root_layout.expand = false
    root_layout.homogeneous = true
    root_layout.forced_height = grid_height
    root_layout.forced_width = grid_width
    root_layout:add_widget_at(create_disk_usage_widget("/dev/sdb1"),   1, 1,   1, 2)
    root_layout:add_widget_at(create_disk_usage_widget("/"),           2, 1,   1, 2)
    root_layout:add_widget_at(create_xd('1'),                          3, 1,   1, 1)
    root_layout:add_widget_at(create_calendar(),                          3, 2,   1, 1)

    -- Setup window and embed the grid layout in it
    local widget = wibox {
        width = window_width,
        height = window_height,
        x = (screen.geometry.width - window_width) / 2,
        y = (screen.geometry.height - window_height) / 2,
        bg = "#00000000",
        screen = screen,
    }
    widget:setup(widget_wrappers.bg(widget_wrappers.margin(root_layout, spacing), beautiful.color_gray_dark))

    -- Setup visibility
    widget.refresh_visibility = function(self)
        self.visible = visible_tag == awful.tag.selected(1).name
    end
    widget:refresh_visibility()
    screen:connect_signal("tag::history::update", function() widget:refresh_visibility() end)

    -- Return it
    return widget
end
