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
local create_rpi_led_tile = require("widget.rpi_led_widget")

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
local function create_spinner(size)
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

local function create_json_oriented_script_widget(create_row_callback, update_row_callback, empty_results_widget, command, interval, horizontal_layout, center_vertically, center_horizontally, scroll)
    -- This function wraps a script that is periodically called and its results are used to populate rows of a
    -- layout. It does not know how to create and populate the rows, but uses callbacks specified by the caller.
    -- Parameters:
    --  create_row_callback (func) - function without parameter returning a widget
    --  update_row_callback (func) - function taking a widget (result of create_row_callback) and a decoded JSON value (element of the array)
    --  empty_results_widget (widget) - used whenever the array is empty. Optional
    --  command (string) - command to call periodically; must print a JSON array
    --  interval (number) - interval of calling the command in seconds
    --  horizontal_layout (bool) - lay rows out left to right instead of top to bottom
    --  center_vertically (bool) - whether the content should be centered on the vertical axis
    --  center_horizontally (bool) - whether the content should be centered on the horizontal axis
    --  scroll (bool) - whether the rows should be scrollable if there are too many to fit. Scrolls along the layout direction

    local layout_type = horizontal_layout and wibox.layout.fixed.horizontal or wibox.layout.fixed.vertical

    local rows_widget = layout_type()
    rows_widget.spacing = tile_size * 0.03
    rows_widget.myrows = {} -- my custom field, not a part of AwesomeWM

    local content_widget = rows_widget
    if empty_results_widget ~= nil then
        empty_results_widget.visible = false
        content_widget = wibox.widget {
            layout = layout_type,
            content_widget,
            empty_results_widget
        }
    end
    if scroll then
        local scroll_widget = wibox.widget {
            layout = horizontal_layout and wibox.container.scroll.horizontal or wibox.container.scroll.vertical,
            step_function = wibox.container.scroll.step_functions.waiting_nonlinear_back_and_forth,
            speed = 100,
            content_widget
        }
        scroll_widget:connect_signal("mouse::enter", function() scroll_widget:pause() end)
        scroll_widget:connect_signal("mouse::leave", function() scroll_widget:continue() end)
        content_widget = scroll_widget
    end
    if center_vertically or center_horizontally then
        content_widget = wibox.widget {
            content_widget,
            halign = "center",
            valign = "center",
            content_fill_horizontal = not center_horizontally,
            content_fill_vertical   = not center_vertically,
            widget = wibox.container.place,
        }
    end

    -- Prepare bottom widget: a spinner showed when the command is running
    local spinner_duration_widget = wibox.widget {
        widget = wibox.widget.textbox,
        text = " ",
    }
    spinner_duration_widget.my_update_timer = gears.timer {
        timeout   = 0.2,
        callback  = function() spinner_duration_widget:inc_duration() end,
    }
    function spinner_duration_widget:start()
        self.text = "0s"
        self.my_start_time = lgi.GLib.get_monotonic_time()
        self.my_update_timer:start()
    end
    function spinner_duration_widget:inc_duration()
        local seconds = (lgi.GLib.get_monotonic_time() - self.my_start_time) / 1e6
        self.text = string.format("%.1fs", seconds)
    end
    function spinner_duration_widget:stop()
        self.my_update_timer:stop()
        self.text = " "
    end
    local spinner_widget = create_spinner(20)
    local bottom_widget = wibox.widget {
        widget = wibox.container.place,
        halign = "right",
        {
            spinner_duration_widget,
            spinner_widget,
            layout = wibox.layout.fixed.horizontal,
            spacing = tile_size * 0.04,
        },
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
                title   = "Invalid JSON from " .. command,
                text    = stdout,
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
        spinner_duration_widget:start()

        awful.spawn.easy_async_with_shell(command, function(stdout)
            process_json(stdout)

            spinner_duration_widget:stop()
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
        font = "sans " .. tostring(tile_size * 0.06)
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
    local function create_label()
        return wibox.widget {
            widget = wibox.widget.textbox,
            text   = "?",
            align  = 'center',
            font   = "sans " .. tostring(tile_size * 0.06),
        }
    end

    local function create_row()
        local vertical = wibox.layout.fixed.vertical()
        local row = widget_wrappers.horizontal_margin(vertical, tile_size * 0.08)
        row = wibox.widget(row)
        row.spacing = tile_size * 0.02
        row.chart = create_arcchart_widget()
        row.mount = create_label()
        row.device = create_label()
        row.usage = create_label()
        vertical:add(row.chart, row.device, row.mount, row.usage)
        return row
    end

    local function update_row(row, item)
        row.chart:update(item.used_gb / item.total_gb)
        row.mount.text = "Device: " .. item.device_path
        row.device.text = "Mount: " .. item.mount_path
        row.usage.text = "Used: " .. item.used_gb .. "GiB / " .. item.total_gb .. "GiB"
    end

    local empty_results_widget = nil
    local command = pai_setup_root .. "/steps/linux/gui/awesome/get_disk_usage.sh"
    local interval = 5
    local center_vertically = true
    local center_horizontally = false
    local horizontal_layout = true
    local scroll = false
    return create_json_oriented_script_widget(create_row, update_row, empty_results_widget, command, interval, horizontal_layout, center_vertically, center_horizontally, scroll)
end

local function create_repo_tile(pai_setup_root)
    local max_labels = 3 -- labels beyond this count are ignored
    local label_color = "#c94c4c"

    local function create_textbox(color)
        local textbox = wibox.widget.textbox()
        local wrapped = wrap_caption(textbox, color)

        function wrapped:set_text(new_text)
            local new_text = new_text or ""
            textbox.text = new_text
            wrapped.visible = new_text ~= ""
        end

        return wrapped
    end

    local function create_row()
        local row = wibox.layout.fixed.horizontal()
        row.spacing = tile_size * 0.03

        row.repo = create_textbox(beautiful.color_gray_dark)
        row.main_branch = create_textbox(beautiful.color_theme)
        row.current_branch = create_textbox(beautiful.color_theme)
        row:add(row.repo, row.main_branch, row.current_branch)

        row.labels = {}
        for i = 1, max_labels do
            row.labels[i] = create_textbox(label_color, "")
            row:add(row.labels[i])
        end
        return row
    end

    local function update_row(row, item)
        if item.vcs == "git" then
            row.repo:set_text(" " .. item.path)
            row.main_branch:set_text(" " .. item.main_branch)
            row.current_branch:set_text(" " .. item.current_branch)
        else
            row.repo:set_text("  " .. item.path)
            row.main_branch:set_text(nil)
            row.current_branch:set_text(nil)
        end

        for i = 1, max_labels do
            row.labels[i]:set_text(item.labels[i])
        end
    end

    local empty_results_widget = nil
    local command = pai_setup_root .. "/steps/linux/gui/awesome/get_repos.sh"
    local interval = 10
    local horizontal_layout = false
    local center_vertically = false
    local center_horizontally = false
    local scroll = false
    return create_json_oriented_script_widget(create_row, update_row, empty_results_widget, command, interval, horizontal_layout, center_vertically, center_horizontally, scroll)
end

local function create_system_usage_tile(pai_setup_root)
    local interval = 2
    local command = pai_setup_root .. "/steps/linux/gui/awesome/get_cpu_idle.sh"

    local rows_layout = wibox.layout.fixed.vertical()
    rows_layout.spacing = tile_size * 0.03
    local bars = {} -- Not an AwesomeWM property

    local function update(_, stdout)
        if #bars == 0 then
            local captions = {}
            local max_width = 0

            for line in stdout:gmatch("[^\r\n]+") do
                local caption = wibox.widget.textbox()
                caption.text = line:match("(%S+)")
                caption.font = "sans " .. tostring(tile_size * 0.07)
                table.insert(captions, caption)

                local w = caption:get_preferred_size(screen.primary)
                max_width = math.max(max_width, w)

                table.insert(bars, create_horizontal_progress_bar_widget())
            end

            for i, caption in ipairs(captions) do
                caption.forced_width = max_width + tile_size * 0.1  -- includes the gap before the bar
                local row = wibox.layout.align.horizontal()
                row:set_first(caption)
                row:set_second(bars[i])
                rows_layout:add(row)
            end
        end

        local idx = 1
        for line in stdout:gmatch("[^\r\n]+") do
            local _, value = line:match("(%S+)%s+(%S+)")
            bars[idx]:update(1 - tonumber(value) / 100)
            idx = idx + 1
        end
    end

    local widget = awful.widget.watch(command, interval, update, rows_layout)
    return wibox.widget {
        widget,
        fill_horizontal = true,
        valign = "center",
        widget = wibox.container.place,
    }
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
    local command = pai_setup_root .. "/steps/linux/spieven/spieven_checks.py json"
    local interval = 30
    local horizontal_layout = false
    local center_vertically = true
    local center_horizontally = true
    local scroll = false
    return create_json_oriented_script_widget(create_row, update_row, empty_results_widget, command, interval, horizontal_layout, center_vertically, center_horizontally, scroll)
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
    local interval = 90
    local horizontal_layout = false
    local center_vertically = true
    local center_horizontally = true
    local scroll = false
    return create_json_oriented_script_widget(create_row, update_row, empty_results_widget, command, interval, horizontal_layout, center_vertically, center_horizontally, scroll)
end

----------------------------------------------------------------------------------- Main

return function(visible_tag, pai_setup_root, user, screen, rpi_led_enabled)
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
    if rpi_led_enabled then
        add_widget_to_grid(create_rpi_led_tile(pai_setup_root),     1, 3,   1, 1)
    end
    add_widget_to_grid(create_repo_tile(pai_setup_root),            2, 1,   4, 3)
    add_widget_to_grid(create_system_usage_tile(pai_setup_root),    6, 1,   3, 3)
    add_widget_to_grid(create_multimedia_sync_tile(pai_setup_root), 1, 4,   2, 1)
    add_widget_to_grid(create_warnings_tile(pai_setup_root),        3, 4,   2, 1)
    add_widget_to_grid(create_disk_usage_tile(pai_setup_root),      5, 4,   4, 1)

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
