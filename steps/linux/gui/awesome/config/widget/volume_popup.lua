local wibox = require("wibox")
local awful = require("awful")
local gears = require("gears")
local beautiful = require("beautiful")
local markup_utils = require("utils.markup")
local widget_wrappers = require("widget.wrappers")
local create_toggle_button = require("widget.toggle_button")
local dpi = require("beautiful.xresources").apply_dpi


local log = require("naughty").notify

return function(screen)
    -- Constants
    local window_width = dpi(50)
    local window_height = dpi(200)
    local screen_pos_percentage_x = 0.96
    local screen_pos_percentage_y = 0.06
    local show_duration_s = 1.4

    local widget = wibox.widget {
        -- The 'align' layout appropriately sizes first and third widgets and the rest of size
        -- goes to the second widget. We want to have a progress bar take most of the space
        -- and the text below to be small. We need to create a dummy first widget to satisfy this.
        layout = wibox.layout.align.vertical,
        {
            widget = wibox.container.constraint,
            width  = 0,
            height = 0,
        },
        {
            direction     = 'east',
            layout        = wibox.container.rotate,
            {
                widget = wibox.widget.progressbar,
                id         = "bar",
                value         = 0.5,
                background_color = beautiful.color_gray_light,
                color = beautiful.color_theme,
            },
        },
        {
            layout = wibox.layout.stack,
            {
                widget = wibox.widget.textbox,
                id = "text_percentage",
                markup   = "??",
                align = "center",
                font = "sans " .. tostring(20),
            },
            {
                widget = wibox.widget.textbox,
                id = "text_x",
                markup = markup_utils.wrap_span("X", "#000000"),
                align = "center",
                font = "sans " .. tostring(20),
            },
        },
    }

    local popup = wibox {
        width = window_width,
        height = window_height,
        x = screen_pos_percentage_x * screen.geometry.width,
        y = screen_pos_percentage_y * screen.geometry.height,
        ontop = true,
        visible = false,
        widget = widget,
    }

    popup:connect_signal("button::press", function()
        popup.visible = false
    end)

    local hide_timer = gears.timer {
        timeout = show_duration_s,
        single_shot = true,
        callback = function()
            popup.visible = false
        end,
    }

    awesome.connect_signal("refresh:volume", function()
        awful.spawn.easy_async_with_shell("pamixer --get-mute --get-volume", function(stdout)
            -- Parse output. Pamixer will print a line like "true 44"
            local is_muted, volume  = stdout:match("^(%S+)%s+(%S+)\n$")
            is_muted = is_muted == "true"

            -- Set slider value
            local bar = widget:get_children_by_id("bar")[1]
            bar.value = tonumber(volume) / 100

            -- Set volume text
            local widget_text = widget:get_children_by_id("text_percentage")[1]
            local text_color = "#ffffff"
            if is_muted then
                text_color = "#aaaaaa"
            end
            widget_text.markup = markup_utils.wrap_span(volume, text_color)

            -- Set visibility of an 'X' denoting whether sound is muted
            local widget_x= widget:get_children_by_id("text_x")[1]
            widget_x.visible = is_muted

            -- Make the popup visible and start a timer that will hide it after some timeout
            popup.visible = true
            hide_timer:again()
        end)
    end)

    return popup
end
