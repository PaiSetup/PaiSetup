local wibox = require("wibox")
local gears = require("gears")
local awful = require("awful")
local dpi = require("beautiful.xresources").apply_dpi

return function(screen, modkey)
    local taglist_buttons = gears.table.join(
        awful.button({ },        1, function(t) t:view_only()                                        end),
        awful.button({ modkey }, 1, function(t) if client.focus then client.focus:move_to_tag(t) end end),
        awful.button({ },        3, awful.tag.viewtoggle                                                ),
        awful.button({ modkey }, 3, function(t) if client.focus then client.focus:toggle_tag(t)  end end),
        awful.button({ },        4, function(t) awful.tag.viewnext(t.screen)                         end),
        awful.button({ },        5, function(t) awful.tag.viewprev(t.screen)                         end)
    )

    return awful.widget.taglist {
        screen  = screen,
        filter  = function(t) return not t.is_home end,
        buttons = taglist_buttons,
        widget_template =
        {
            {
                {
                    {
                        id     = 'text_role',
                        widget = wibox.widget.textbox,
                    },
                    layout = wibox.layout.fixed.horizontal,
                },
                left  = dpi(13),
                right = dpi(13),
                widget = wibox.container.margin
            },
            id     = 'background_role',
            widget = wibox.container.background,
        },
    }
end
