local awful = require("awful")
local beautiful = require("beautiful")

local function get_default_rule(clientkeys, clientbuttons)
    return {
        rule = {},
        properties = {
            border_width = beautiful.client_border_width,
            border_color = beautiful.border_normal,
            focus = awful.client.focus.filter,
            raise = true,
            keys = clientkeys,
            buttons = clientbuttons,
            screen = awful.screen.preferred,
            placement = awful.placement.no_overlap + awful.placement.no_offscreen
        }
    }
end

local function get_floating_clients_rule()
    return {
        rule_any = {
            instance = {
                "DTA",  -- Firefox addon DownThemAll.
                "copyq",  -- Includes session name in class.
                "pinentry",
            },
            class = {
                "Arandr",
                "Blueman-manager",
                "Gpick",
                "Kruler",
                "MessageWin",  -- kalarm.
                "Sxiv",
                "Tor Browser", -- Needs a fixed window size to avoid fingerprinting by screen size.
                "Wpa_gui",
                "veromix",
                "xtightvncviewer",
                "Yad",
                "LearnOpenGL",
            },
            name = {
                "Event Tester",  -- xev.
            },
            role = {
                "AlarmWindow",  -- Thunderbird's calendar.
                "ConfigManager",  -- Thunderbird's about:config.
                "pop-up",       -- e.g. Google Chrome's (detached) Developer Tools.
            }
        },
        properties = { floating = true }
    }
end

local function get_no_border_rules(tags)
    return {
        {
            rule = { class = "Ulauncher" },
            properties = { border_width = 0 }
        },
    }
end

local function get_tag_mappings_rules(tags)
    return {
        {
            rule_any = {
                class = {
                    "firefox",
                    "chromium",
                }
            },
            properties = { tag = tags.web }
        },
        {
            rule = { class = "Gimp" },
            properties = { tag = tags.draw },
        },
        {
            rule = { class = "vlc", },
            properties = { tag = tags.video }
        },
        {
            rule = { class = "Rhythmbox", },
            properties = { tag = tags.music }
        },
    }
end

return {
    get_default_rule = get_default_rule,
    get_no_border_rules = get_no_border_rules,
    get_floating_clients_rule = get_floating_clients_rule,
    get_tag_mappings_rules = get_tag_mappings_rules,
}
