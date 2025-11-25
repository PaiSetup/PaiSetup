local awful = require("awful")
local beautiful = require("beautiful")
local dpi = require("beautiful.xresources").apply_dpi

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

local function get_non_floating_clients_rule()
    return {
        rule_any = {
            class = {
                "Xephyr",
            },
        },
        properties = { floating = false }
    }
end


local function get_no_border_rules(tags)
    return {
        {
            rule_any = {
                class = {
                    "Ulauncher",
                    "Image Lounge", -- nomacs
                }
            },
            properties = { border_width = 0 }
        },
    }
end

local function get_tag_mappings_rules(tags)
    return {
        {
            rule = {
                instance = "Navigator",
                class = "firefox",
            },
            properties = { tag = tags.web }
        },
        {
            rule = { class = "jetbrains-clion" },
            properties = { tag = tags.code },
        },
        {
            rule = { class = "Gimp" },
            properties = { tag = tags.draw },
        },
        {
            rule = { class = "vlc", },
            properties = { tag = tags.video }
        },
    }
end

local function get_home_panel_cava_rule(tag, client_class, screen_width, screen_height, screen_height_percentage)
    local client_height = math.floor(screen_height * screen_height_percentage)

    -- st snaps its position to some grid and the additional 20 pixels makes sure it's really snapped to bottom
    -- this can be removed if other terminal emulator is used
    local client_y = screen_height - client_height + dpi(20)

    return {
        rule = { class = client_class },
        properties = {
            tag = tag,
            focusable = false,
            floating = true,
            size_hints_honor = false,
            border_width = 0,
            x = 0,
            y = client_y,
            width = screen_width,
            height = client_height,
            is_home_panel = true, -- custom property, not a part of AwesomeWM
        },
    }
end

return {
    get_default_rule = get_default_rule,
    get_no_border_rules = get_no_border_rules,
    get_floating_clients_rule = get_floating_clients_rule,
    get_non_floating_clients_rule = get_non_floating_clients_rule,
    get_tag_mappings_rules = get_tag_mappings_rules,
    get_home_panel_cava_rule = get_home_panel_cava_rule,
}
