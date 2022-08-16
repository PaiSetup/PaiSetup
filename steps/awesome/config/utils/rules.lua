local awful = require("awful")
local beautiful = require("beautiful")

local function get_default_rule(clientkeys, clientbuttons)
    return {
        rule = {},
        properties = {
            border_width = beautiful.border_width,
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

local function get_tag_mappings_rules()
    return {
        {
            rule = {
                class = {
                    "firefox",
                    "chromium",
                }
            },
            properties = { tag = "1" }
        },
        {
            rule = {
                class = {
                    "Gimp",
                }
            },
            properties = { tag = "6" }
        },
        {
            rule = {
                class = {
                    "vlc",
                }
            },
            properties = { tag = "7" }
        },
        {
            rule = {
                class = {
                    "Rhythmbox",
                }
            },
            properties = { tag = "8" }
        },
    }
end

return {
    get_default_rule = get_default_rule,
    get_floating_clients_rule = get_floating_clients_rule,
    get_tag_mappings_rules = get_tag_mappings_rules,
}
