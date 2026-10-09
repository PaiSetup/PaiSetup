local wibox = require("wibox")
local awful = require("awful")
local gears = require("gears")
local lgi = require("lgi")
local beautiful = require("beautiful")
local markup_utils = require("utils.markup")
local widget_wrappers = require("widget.wrappers")
local shutdown_popup = require("widget.shutdown_popup")
local rules_utils = require("utils.rules")
local dpi = require("beautiful.xresources").apply_dpi
local json = require("utils.json")
local naughty = require("naughty")

----------------------------------------------------------------------------------- Global utils

-- The main function builds a grid layout. This constant represent the size of one cell
-- in the layout. All font sizes, margins, spacings, paddings, widget sizes should be some
-- multiple of this value
local tile_size = dpi(200)

local function wrap_caption(caption, bg)
    -- Helper function to wrap text boxes with a couple of containers to make them look prettier
    caption.valign = 'bottom'
    caption = widget_wrappers.margin(caption, tile_size * 0.023)
    caption = widget_wrappers.bg(caption, bg)
    caption = wibox.widget(caption)
    return caption
end



----------------------------------------------------------------------------------- Generic helper widgets
local function create_line_oriented_script_widget(create_row_callback, update_row_callback, empty_results_widget, command, interval, center_vertically, scroll_vertically)
    -- This function wraps a bash script that is periodically called and its results
    -- are used to populate rows of a vertical layout. It does not know how to create
    -- the rows, but uses callbacks specified by the caller. Parameters:
    --  create_row_callback (func) - function without parameter returning a widget
    --  update_row_callback (func) - function taking a widget (result of create_row_callback) and a string (line of script output)
    --  empty_results_widget (widget) - a widget used whenever there are no rows returned by the command. Optional
    --  command (string) - path to script to call periodically
    --  interval (number) - interval of calling the script in seconds
    --  center_vertically (bool) - whether the rows should be centered vertically
    --  scroll_vertically (bool) - whether the rows should be scrollable if there are too many to fit

    -- Root layout. We'll be adding rows to it
    local vertical = wibox.layout.fixed.vertical()
    vertical.spacing = tile_size * 0.03
    vertical.mychild_count = 0 -- my custom field, not a part of AweosomeWM
    vertical.myrows = {} -- my custom field, not a part of AweosomeWM
    vertical.using_empty_widget = false

    -- Watch widget will call our command and execute a function, which will update GUI.
    local widget = awful.widget.watch(command, interval, function (_, stdout)
            local needs_empty_widget = empty_results_widget ~= nil and not stdout:find("[^\r\n]")

            -- Remove empty widget if needed
            if not needs_empty_widget and vertical.using_empty_widget then
                vertical:remove(1)
                vertical.using_empty_widget = false
            end

            -- Iterate over lines of output
            local line_index = 1
            for line in stdout:gmatch("[^\r\n]+") do
                -- Get row to set
                local row = nil
                if line_index > vertical.mychild_count then
                    -- Create a new row and add it to the view
                    row = create_row_callback()
                    vertical:add(row)

                    -- Store the row in our custom fields. It's hard to get these things from AwesomeWM, so we track it manually
                    vertical.mychild_count = vertical.mychild_count + 1
                    table.insert(vertical.myrows, row)
                else
                    -- Get an existing row
                    row = vertical.myrows[line_index]
                end

                -- Set current info from current line to our row and show it
                update_row_callback(row, line)
                row.visible = true

                -- Increment iteration variable
                line_index = line_index + 1
            end

            -- Iterate over rest of the lines that are created and delete them
            for i=vertical.mychild_count, line_index, -1 do
                -- Remove the row from our custom fields
                table.remove(vertical.myrows, i)
                vertical.mychild_count = vertical.mychild_count - 1

                -- Remove the row from view
                vertical:remove(i)
            end

            -- Add empty widget if needed
            if needs_empty_widget and not vertical.using_empty_widget then
                vertical:add(empty_results_widget)
                vertical.using_empty_widget = true
            end
        end,
        vertical
    )

    if center_vertically then
        widget = wibox.container.place(widget)
    end

    if scroll_vertically then
        widget = wibox.widget {
            layout = wibox.container.scroll.vertical,
            step_function = wibox.container.scroll.step_functions.waiting_nonlinear_back_and_forth,
            speed = 100,
            widget
        }
        widget:connect_signal("mouse::enter", function ()
            widget:pause()
        end)
        widget:connect_signal("mouse::leave", function ()
            widget:continue()
        end)
    end

    return widget
end

local function make_spinner(size)
    local angle = 0
    local running = false
    local w = wibox.widget.base.make_widget()

    function w:fit(_, _, _) return size, size end

    function w:draw(_, cr, width, height)
        if not running then return end
        local r = size / 2 - 2            -- fixed radius, not width/height
        cr:translate(width / 2, height / 2)  -- center in whatever area we got
        cr:rotate(angle)
        cr:set_line_width(2)
        cr:set_line_cap(lgi.cairo.LineCap.ROUND)
        cr:set_source(gears.color(beautiful.color_theme))
        cr:arc(0, 0, r, 0, math.pi * 1.5)
        cr:stroke()
    end

    local timer = gears.timer {
        timeout = 1 / 30,
        callback = function()
            angle = (angle + 0.25) % (2 * math.pi)
            w:emit_signal("widget::redraw_needed")
        end,
    }

    function w:start() running = true;  timer:start() end
    function w:stop()
        running = false
        timer:stop()
        w:emit_signal("widget::redraw_needed")  -- clear the last frame
    end

    return w
end

local function create_json_oriented_script_widget(create_row_callback, update_row_callback, empty_results_widget, command, interval, center_vertically, scroll_vertically)
    -- This function wraps a script that is periodically called and its results are used to populate rows of a vertical
    -- layout. It does not know how to create and populate the rows, but uses callbacks specified by the caller.
    -- Parameters:
    --  create_row_callback (func) - function without parameter returning a widget
    --  update_row_callback (func) - function taking a widget (result of create_row_callback) and a decoded JSON value (element of the array)
    --  empty_results_widget (widget) - used whenever the array is empty. Optional
    --  command (string) - command to call periodically; must print a JSON array
    --  interval (number) - interval of calling the command in seconds
    --  center_vertically (bool) - whether the rows should be centered vertically
    --  scroll_vertically (bool) - whether the rows should be scrollable if there are too many to fit

    -- Prepare content widget: a vertical list of rows, one row per json object. Optionally also special widget for empty results.
    local rows_widget = wibox.layout.fixed.vertical()
    rows_widget.spacing = tile_size * 0.03
    rows_widget.myrows = {} -- my custom field, not a part of AwesomeWM

    local content_widget = rows_widget
    if empty_results_widget ~= nil then
        empty_results_widget.visible = false
        content_widget = wibox.widget {
            layout = wibox.layout.fixed.vertical,
            content_widget,
            empty_results_widget
        }
    end
    if scroll_vertically then
        local scroll = wibox.widget {
            layout = wibox.container.scroll.vertical,
            step_function = wibox.container.scroll.step_functions.waiting_nonlinear_back_and_forth,
            speed = 100,
            content_widget
        }
        scroll:connect_signal("mouse::enter", function() scroll:pause() end)
        scroll:connect_signal("mouse::leave", function() scroll:continue() end)
        content_widget = scroll
    end
    if center_vertically then
        content_widget = wibox.container.place(content_widget)
    end

    -- Prepare bottom widget: a spinner showed when the command is running
    local spinner_widget = make_spinner(20)
    local bottom_widget = wibox.widget {
        spinner_widget,
        halign = "right",
        widget = wibox.container.place,
    }

    -- Prepare the final widget. Content widget takes majority of vertical space, and bottom widget is fitted at the bottom.
    local out_widget = wibox.widget {
        nil,
        content_widget,
        bottom_widget,
        layout = wibox.layout.align.vertical,
    }

    local function process_json(stdout)
        -- Try to parse the json
        local ok, items = pcall(json.decode, stdout)
        if not ok or type(items) ~= "table" then
            naughty.notify({
                preset  = naughty.config.presets.warn,
                text   = "Invalid JSON from " .. command,
                timeout = 10,
            })
            return
        end

        if empty_results_widget ~= nil then
            empty_results_widget.visible = #items == 0
        end

        -- Iterate over objects of the array, creating rows as needed
        for item_index, item in ipairs(items) do
            local row = rows_widget.myrows[item_index]
            if row == nil then
                row = create_row_callback()
                rows_widget:add(row)
                table.insert(rows_widget.myrows, row)
            end
            update_row_callback(row, item)
        end

        -- Delete rows that are no longer needed
        for i = #rows_widget.myrows, #items + 1, -1 do
            table.remove(rows_widget.myrows, i)
            rows_widget:remove(i)
        end
    end

    local is_update_running = false
    local function update()
        if is_update_running then return end

        is_update_running = true
        spinner_widget:start()
        awful.spawn.easy_async_with_shell(command, function(stdout)
            process_json(stdout)
            spinner_widget:stop()
            is_update_running = false
        end)
    end

    local timer = gears.timer {
        timeout   = interval,
        call_now  = true,
        autostart = true,
        callback  = update,
    }

    local function refresh_timer()
        timer:again()
        update()
    end

    out_widget:buttons(gears.table.join(
        awful.button({}, 1, refresh_timer),
        awful.button({}, 3, refresh_timer)
    ))

    return out_widget
end

local function create_horizontal_progress_bar_widget()
    local chart_widget = wibox.widget {
        widget = wibox.widget.progressbar,
        max_value     = 1,
        value         = 0.5,
        forced_height = tile_size * 0.1,
        background_color = beautiful.color_gray_dark,
        color = beautiful.color_theme,
    }
    local text_widget = wibox.widget {
        widget = wibox.widget.textbox,
        text   = '?%',
        align = 'center',
        font = "sans " .. tostring(tile_size * 0.08)
    }
    local widget = wibox.widget {
        chart_widget,
        text_widget,
        layout = wibox.layout.stack
    }
    widget.update = function(_, value)
        chart_widget:set_value(value)
        text_widget.text = tostring(value * 100) .. "%"
    end
    return widget
end

local function create_arcchart_widget()
    local text_widget = wibox.widget {
        widget = wibox.widget.textbox,
        text   = '?%',
        align = 'center',
        font = "sans " .. tostring(tile_size * 0.08)
    }
    local chart_widget = wibox.container.arcchart(text_widget)
    chart_widget.thickness = tile_size * 0.1
    chart_widget.bg = beautiful.color_gray_dark
    chart_widget.colors = { beautiful.color_theme }
    chart_widget.min_value = 0
    chart_widget.max_value = 1
    chart_widget.value = 0.5
    chart_widget.forced_width = tile_size * 0.5
    chart_widget.forced_height = tile_size * 0.5
    chart_widget.update = function(_, value)
        chart_widget.value = value
        text_widget.text = string.format("%.1f%%", value * 100)
    end
    return chart_widget
end

----------------------------------------------------------------------------------- Tile widgets
local function create_greeting_tile(user)
    local icon = wibox.widget.imagebox(beautiful.arch_logo, true, gears.shape.rect)
    icon.forced_height = tile_size * 0.9
    icon.forced_width = tile_size * 0.9
    icon = widget_wrappers.horizontal_margin(icon, tile_size * 0.08)
    icon = wibox.widget(icon)

    local greeting = wibox.widget.textbox('Hello, ' .. user .. '!')
    greeting.align = 'center'
    greeting.font = "sans " .. tostring(tile_size * 0.12)

    local shutdown_button = wibox.widget.textbox()
    shutdown_button.align = 'center'
    shutdown_button.font = "sans " .. tostring(tile_size * 0.15)
    shutdown_button.markup = markup_utils.wrap_span('', beautiful.color_theme, nil)
    shutdown_button:connect_signal("button::press", function (self, lx, ly, button, mods, metadata)
        if button == 1 then
            shutdown_popup()
        end
    end)

    local widget = wibox.layout.fixed.vertical(icon, greeting, shutdown_button)
    widget.spacing = tile_size * 0.2
    return widget
end

local function create_disk_usage_tile(pai_setup_root)
    local interval = 1
    local command = pai_setup_root .. "/steps/linux/gui/awesome/get_disk_usage.sh"

    local function format_kb_to_gb(caption, kilobytes)
        return string.format("%s%.1fGiB", caption, kilobytes / 1024 / 1024)
    end

    local root_grid = wibox.layout.grid()
    root_grid.expand = true
    root_grid.vertical_homogeneous = false
    root_grid.horizontal_homogeneous = true
    root_grid.charts_count = 0 -- Not an AwesomeWM property

    local widget = awful.widget.watch(command, interval, function (_, stdout)
        -- Iterate over output lines. Allocate chart widget as needed and update them.
        local disks_count = 0
        for line in stdout:gmatch("([^\n]*)\n?") do
            disks_count = disks_count + 1

            local mount_path, device_path, avail_kb, total_kb = line:match("^(%S+)%s+(%S+)%s+(%S+)%s+(%S+)$")

            -- Create the per-disk child if it doesn't exist
            if disks_count > root_grid.charts_count then
                root_grid.charts_count = root_grid.charts_count + 1

                local chart_widget = create_arcchart_widget()
                local mount_path_widget = wibox.widget {
                    widget = wibox.widget.textbox,
                    text   = mount_path,
                    align = 'center',
                    font = "sans " .. tostring(tile_size * 0.06),
                }
                local total_bytes_widget = wibox.widget {
                    widget = wibox.widget.textbox,
                    text   = "?",
                    align = 'center',
                    font = "sans " .. tostring(tile_size * 0.06),
                }
                local avail_bytes_widget = wibox.widget {
                    widget = wibox.widget.textbox,
                    text   = "?",
                    align = 'center',
                    font = "sans " .. tostring(tile_size * 0.06),
                }

                root_grid:add_widget_at(chart_widget, 1, root_grid.charts_count)
                root_grid:add_widget_at(mount_path_widget, 2, root_grid.charts_count)
                root_grid:add_widget_at(total_bytes_widget, 3, root_grid.charts_count)
                root_grid:add_widget_at(avail_bytes_widget, 4, root_grid.charts_count)
            end

            avail_kb = tonumber(avail_kb)
            total_kb = tonumber(total_kb)
            local usage = (total_kb - avail_kb) / total_kb

            -- Update the child
            local chart_widget = root_grid:get_widgets_at(1, disks_count)[1]
            chart_widget:update(usage)
            local total_bytes_widget = root_grid:get_widgets_at(3, disks_count)[1]
            total_bytes_widget.text = format_kb_to_gb("Total: ", total_kb)
            local avail_bytes_widget = root_grid:get_widgets_at(4, disks_count)[1]
            avail_bytes_widget.text = format_kb_to_gb("Free: ", avail_kb)
        end

        -- Iterate over chart widgets that started to be unused and remove them.
        for i = root_grid.charts_count, disks_count + 1, -1 do
            root_grid:remove_widgets_at(1, i, 4, 1)
            root_grid.charts_count = root_grid.charts_count - 1
        end

        end,
        root_grid
    )
    return widget
end

local function create_repo_tile(pai_setup_root)
    -- This widget can display git repositories present in the system and some info about
    -- them. It relies upon get_repos.sh script written in bash. The script produces output
    -- like following: <repo_path> <master_branch> <current_branch> <flag1> <flag2> <flag3>, where
    --    repo_path - filesystem path to the repository
    --    master_branch - main branch used by repository ("master" or "main")
    --    flag1, flag2, flag3 - zero or more warnings about the state of repository

    local function create_row()
        local flag_color = "#c94c4c"
        -- Prepare textboxes. We have to store both raw textboxes and their wrapped versions,
        -- because we set text on the former, but alter visibility of the latter.
        local caption_repo = wibox.widget.textbox()
        local caption_master_branch = wibox.widget.textbox()
        local caption_current_branch = wibox.widget.textbox()
        local caption_flag1 = wibox.widget.textbox()
        local caption_flag2 = wibox.widget.textbox()
        local caption_flag3 = wibox.widget.textbox()
        local wrapped_caption_repo = wrap_caption(caption_repo, beautiful.color_gray_dark)
        local wrapped_caption_master_branch = wrap_caption(caption_master_branch, beautiful.color_theme)
        local wrapped_caption_current_branch = wrap_caption(caption_current_branch, beautiful.color_theme)
        local wrapped_caption_flag1 = wrap_caption(caption_flag1, flag_color)
        local wrapped_caption_flag2 = wrap_caption(caption_flag2, flag_color)
        local wrapped_caption_flag3 = wrap_caption(caption_flag3, flag_color)

        -- Create row
        local row = wibox.layout.fixed.horizontal(wrapped_caption_repo, wrapped_caption_master_branch, wrapped_caption_current_branch, wrapped_caption_flag1, wrapped_caption_flag2, wrapped_caption_flag3)
        row.spacing = tile_size * 0.03
        row.caption_repo = caption_repo
        row.caption_master_branch = caption_master_branch
        row.caption_current_branch = caption_current_branch
        row.caption_flag1 = caption_flag1
        row.caption_flag2 = caption_flag2
        row.caption_flag3 = caption_flag3
        row.wrapped_caption_repo = wrapped_caption_repo
        row.wrapped_caption_master_branch = wrapped_caption_master_branch
        row.wrapped_caption_current_branch = wrapped_caption_current_branch
        row.wrapped_caption_flag1 = wrapped_caption_flag1
        row.wrapped_caption_flag2 = wrapped_caption_flag2
        row.wrapped_caption_flag3 = wrapped_caption_flag3
        return row
    end

    local function update_row(row, line)
        local matcher = line:gmatch("%S+")

        -- Get basic info
        local repo_type = matcher()
        local repo_path = matcher()

        -- Report main branch of the repository.
        if repo_type == 'git' then
            row.caption_repo.text = " " .. repo_path

            local master_branch = matcher()
            row.caption_master_branch.text = " " .. master_branch
            row.wrapped_caption_master_branch.visible = master_branch ~= '?'

            local current_branch = matcher()
            if current_branch == '?' then
                row.caption_current_branch.text = " DETACHED"
            else
                row.caption_current_branch.text = " " .. current_branch
            end
            row.wrapped_caption_current_branch.visible = current_branch ~= master_branch
        else
            row.caption_repo.text = "   " .. repo_path
            row.wrapped_caption_master_branch.visible = false
            row.wrapped_caption_current_branch.visible = false
        end

        -- Report additional warnings
        local flag1 = matcher() or ''
        local flag2 = matcher() or ''
        local flag3 = matcher() or ''
        row.caption_flag1.text = flag1
        row.wrapped_caption_flag1.visible = flag1 ~= ''
        row.caption_flag2.text = flag2
        row.wrapped_caption_flag2.visible = flag2 ~= ''
        row.caption_flag3.text = flag3
        row.wrapped_caption_flag3.visible = flag3 ~= ''
    end

    local empty_results_widget = nil
    local command = pai_setup_root .. "/steps/linux/gui/awesome/get_repos.sh"
    local interval = 10
    local center_vertically = false
    local scroll_vertically = false
    return create_line_oriented_script_widget(create_row, update_row, empty_results_widget, command, interval, center_vertically, scroll_vertically)
end

local function create_system_usage_tile(pai_setup_root)
    local interval = 2
    local command = pai_setup_root .. "/steps/linux/gui/awesome/get_cpu_idle.sh"

    local root_grid = wibox.layout.grid()
    root_grid.horizontal_spacing = tile_size * 0.1
    root_grid.vertical_spacing = tile_size * 0.03
    root_grid.vertical_homogeneous = true
    root_grid.horizontal_homogeneous = false
    root_grid.rows_count = 0 -- Not an AwesomeWM property

    local widget = awful.widget.watch(command, interval, function (_, stdout)
        if root_grid.rows_count == 0 then
            for line in stdout:gmatch("([^\n]*)\n?") do
                local bar_widget = create_horizontal_progress_bar_widget()

                local caption_widget = wibox.widget.textbox()
                caption_widget.text = line:match("(%S+)")
                caption_widget.font = "sans " .. tostring(tile_size * 0.07)

                root_grid.rows_count = root_grid.rows_count + 1
                root_grid:add_widget_at(caption_widget, root_grid.rows_count, 1)
                root_grid:add_widget_at(bar_widget, root_grid.rows_count, 2)
            end
        end

        local child_idx = 1
        for line in stdout:gmatch("([^\n]*)\n?") do
            local _, value = line:match("(%S+)%s+(%S+)")
            value = 1 - tonumber(value) / 100

            local bar_widget = root_grid:get_widgets_at(child_idx, 2)[1]
            bar_widget:update(value)

            child_idx = child_idx + 1
        end
        end,
        root_grid
    )
    widget = wibox.container.place(widget) -- center the widget
    return widget
end

local function create_warnings_tile(pai_setup_root)
    -- This widget queries current warnings from Spieven and displays them in a tile.
    local function create_textbox(color, initial_text)
        local text = wibox.widget.textbox()
        text.text = initial_text
        local row = wrap_caption(text, color)
        row.text = text
        return row
    end
    local function create_row()
        return create_textbox("#8B8000", "")
    end
    local function update_row(row, line)
        row.text.text = "⚠️ " .. line
    end

    local empty_results_widget = create_textbox("#008800", "✅ No warnings")
    empty_results_widget.text.font = "sans " .. tostring(tile_size * 0.1)
    local command = pai_setup_root .. "/steps/linux/spieven/spieven_checks.py 0"
    local interval = 30
    local center_vertically = true
    local scroll_vertically = true
    return create_line_oriented_script_widget(create_row, update_row, empty_results_widget, command, interval, center_vertically, scroll_vertically)
end

local function create_multimedia_sync_tile(pai_setup_root)
    -- Shows pending multimedia sync operations (copies/moves/deletes) in a tile.
    local function create_textbox(color, initial_text)
        local text = wibox.widget.textbox()
        text.text = initial_text
        local row = wrap_caption(text, color)
        row.text = text
        return row
    end

    local function create_row()
        return create_textbox(beautiful.color_gray_dark, "")
    end

    local function update_row(row, item)
        local text = string.format("%s: %d (%.2fMiB)", gears.string.xml_escape(item.caption), item.count, item.sizeMb)
        local color = (item.count == 0) and beautiful.color_gray_light or beautiful.color_font
        row.text.markup = markup_utils.wrap_span(text, color, nil)
    end

    local empty_results_widget = create_textbox("#008800", "✅ Nothing to sync")
    empty_results_widget.text.font = "sans " .. tostring(tile_size * 0.1)

    local command = pai_setup_root .. "/steps/linux/encryption/sync_multimedia.sh --query"
    local interval = 30
    local center_vertically = true
    local scroll_vertically = true
    return create_json_oriented_script_widget(create_row, update_row, empty_results_widget, command, interval, center_vertically, scroll_vertically)
end

----------------------------------------------------------------------------------- Main

return function(visible_tag, pai_setup_root, user, screen)
    -- Main function composing the panel from above widgets

    -- Some size constants
    local vertical_placement_percent = 0.2 -- value between 0 (snap to top) and 1 (snap to bottom)
    local horizontal_placement_percent = 0.5 -- value between 0 (snap to left) and 1 (snap to right)
    local spacing = tile_size * 0.1

    -- Setup the grid layout with widgets
    local root_layout = wibox.layout.grid()
    root_layout.spacing = spacing
    root_layout.expand = false
    root_layout.homogeneous = true
    local function add_widget_to_grid(widget, col, row, colspan, rowspan)
        local widget = widget_wrappers.margin(widget, tile_size * 0.04)
        widget = widget_wrappers.sized_bg(widget, beautiful.color_gray_light, colspan * tile_size, rowspan * tile_size)
        widget = wibox.widget(widget)
        root_layout:add_widget_at(widget, row, col, rowspan, colspan)
    end
    add_widget_to_grid(create_greeting_tile(user),                  1, 1,   1, 2)
    add_widget_to_grid(create_repo_tile(pai_setup_root),            2, 1,   5, 3)
    add_widget_to_grid(create_system_usage_tile(pai_setup_root),    7, 1,   3, 3)
    add_widget_to_grid(create_disk_usage_tile(pai_setup_root),      6, 4,   4, 1)
    add_widget_to_grid(create_warnings_tile(pai_setup_root),        4, 4,   2, 1)
    add_widget_to_grid(create_multimedia_sync_tile(pai_setup_root), 2, 4,   2, 1)

    -- Setup a wibox (a window) and embed the grid layout in it
    local rows, columns = root_layout:get_dimension()
    local grid_width = columns * tile_size + (columns - 1) * spacing
    local grid_height = rows * tile_size + (rows - 1) * spacing
    local window_width = grid_width + 2 * spacing -- There are margins
    local window_height = grid_height + 2 * spacing -- There are margins
    local widget = wibox {
        width = window_width,
        height = window_height,
        x = (screen.geometry.width - window_width) * horizontal_placement_percent,
        y = (screen.geometry.height - window_height) * vertical_placement_percent,
        bg = "#00000000",
        screen = screen,
    }
    widget:setup(widget_wrappers.bg(widget_wrappers.margin(root_layout, spacing), '#00000000'))

    -- Setup visibility of the panel. It should only show itself on one selected tag
    widget.refresh_visibility = function(self)
        local current_tag = screen.selected_tag
        self.visible = current_tag ~= nil and visible_tag == current_tag.name
    end
    widget:refresh_visibility()
    screen:connect_signal("tag::history::update", function() widget:refresh_visibility() end)

    -- Launch cava audio visualizer on the bottom of the screen.
    --
    -- We need to define an awful.rule to set some properties to make it look good. Because this rule depend on screen resolution, it
    -- will have to be different for each screen. Hence, we generate a separate client class for each screen, so they are distinguishable.
    --
    -- Another nitpick is killing the old client before AwesomeWM restarts. Fortunately there is an 'exit' signal that we can use.
    local client_class = "HOME_CAVA" .. screen.index
    local cava_pid = awful.spawn('alacritty --class ' .. client_class .. ' --option window.opacity=0 --command cava')
    awesome.connect_signal('exit', function(reason_restart)
        awful.spawn("kill -9 " .. cava_pid) -- kill the client before restarting
    end)
    awful.rules.rules = gears.table.join(
        awful.rules.rules,
        {
            rules_utils.get_home_panel_cava_rule(visible_tag, client_class, screen.geometry.width, screen.geometry.height, 0.3)
        }
    )
end
