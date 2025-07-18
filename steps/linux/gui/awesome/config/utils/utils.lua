local gears = require("gears")
local beautiful = require("beautiful")
local awful = require("awful")
local cairo = require("lgi").cairo

local function set_wallpaper(s)
    -- Wallpaper
    if beautiful.wallpaper then
        local wallpaper = beautiful.wallpaper
        if type(wallpaper) == "function" then
            wallpaper = wallpaper(s)
        end

        gears.wallpaper.maximized(wallpaper, s, true)
    end
end

local function taglist_square_top_rect(color)
    local img = cairo.ImageSurface(cairo.Format.ARGB32, 50, 3)
    local cr = cairo.Context(img)
    cr:set_source(gears.color(color))
    cr:paint()
    return img
end

local function enable_viewed_tag_preserving()
    local cache_path = '/tmp/awesomewm-last-selected-tags'

    awesome.connect_signal('exit', function(reason_restart)
        if not reason_restart then return end

        local file = io.open(cache_path, 'w')

        for s in screen do
           file:write(s.selected_tag.index, '\n')
        end

        file:close()
     end)

    awesome.connect_signal('startup', function()
       local file = io.open(cache_path, 'r')
       if not file then return end

       local selected_tags = {}

       for line in file:lines() do
          table.insert(selected_tags, tonumber(line))
       end

       for s in screen do
          local i = selected_tags[s.index]
          local t = s.tags[i]
          t:view_only()
       end

       file:close()
    end)
end

local function get_per_tag_keys(modkey, group)
    -- Bind all key numbers to tags.
    -- Be careful: we use keycodes to make it work on any keyboard layout.
    -- This should map on the top row of your keyboard, usually 1 to 9.
    local keys = {}
    for i = 1, 9 do
        keys = gears.table.join(keys,
            -- View tag only.
            awful.key({ modkey }, "#" .. i + 9,
                    function ()
                            local screen = awful.screen.focused()
                            local tag = screen.tags[i]
                            if tag then
                                tag:view_only()
                            end
                    end,
                    {description = "View tag", group = group}),
            -- Toggle tag display.
            awful.key({ modkey, "Control" }, "#" .. i + 9,
                    function ()
                        local screen = awful.screen.focused()
                        local tag = screen.tags[i]
                        if tag then
                            awful.tag.viewtoggle(tag)
                        end
                    end,
                    {description = "Toggle tag", group = group}),
            -- Move client to tag.
            awful.key({ modkey, "Shift" }, "#" .. i + 9,
                    function ()
                        if client.focus then
                            local tag = client.focus.screen.tags[i]
                            if tag then
                                client.focus:move_to_tag(tag)
                            end
                        end
                    end,
                    {description = "Move focused client to tag", group = group}),
            -- Toggle tag on focused client.
            awful.key({ modkey, "Control", "Shift" }, "#" .. i + 9,
                    function ()
                        if client.focus then
                            local tag = client.focus.screen.tags[i]
                            if tag then
                                client.focus:toggle_tag(tag)
                            end
                        end
                    end,
                    {description = "Toggle focused client on tag", group = group})
        )
    end
    return keys
end

function set_layout_key(mods, key, layout)
    return awful.key(mods, key, function () awful.layout.set(layout) end, {description = "set " .. layout.name .. " for the current tag", group = "layout"})
end

function spawn_terminal_from_thunar()
    command = "$PAI_SETUP_ROOT/steps/linux/gui/scripts/get_thunar_cwd.sh"
    awful.spawn.easy_async_with_shell(command, function(stdout, stderr, exitreason, exitcode)
        if exitcode == 0 then
            stdout = stdout:gsub("%s+$", "")
            terminal_command = "sh -c 'cd \"" .. stdout .. "\" ; $TERMINAL'"
        else
            terminal_command = "$TERMINAL"
        end
        awful.spawn.with_shell(terminal_command)
    end)
end

function switch_to_empty_tag()
    local screen = awful.screen.focused()
    for _, t in ipairs(screen.tags) do
        if #t:clients() == 0 then
            t:view_only()
            return
        end
    end
end

function switch_to_fairv()
    local tag = awful.screen.focused().selected_tag
    if tag then
        tag.layout = awful.layout.suit.fair
    end
end

return {
    set_wallpaper = set_wallpaper,
    enable_viewed_tag_preserving = enable_viewed_tag_preserving,
    taglist_square_top_rect = taglist_square_top_rect,
    get_per_tag_keys = get_per_tag_keys,
    set_layout_key = set_layout_key,
    spawn_terminal_from_thunar = spawn_terminal_from_thunar,
    switch_to_empty_tag = switch_to_empty_tag,
    switch_to_fairv = switch_to_fairv,
}
