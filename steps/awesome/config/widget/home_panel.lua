local wibox = require("wibox")
local awful = require("awful")
local gears = require("gears")
local beautiful = require("beautiful")
local markup_utils = require("utils.markup")
local widget_wrappers = require("widget.wrappers")
local shutdown_popup = require("widget.shutdown_popup")
local rules_utils = require("utils.rules")
local keygrabber = require("awful.keygrabber")
local dpi = require("beautiful.xresources").apply_dpi

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

----------------------------------------------------------------------------------- Generic widgets

local function create_line_oriented_script_widget(create_row_callback, update_row_callback, command, interval, center_vertically)
    -- This function wraps a bash script that is periodically called and its results
    -- are used to populate rows of a vertical layout. It does not know how to create
    -- the rows, but uses callbacks specified by the caller. Parameters:
    --  command (string) - path to script to call periodically
    --  interval (number) - interval of calling the script in seconds
    --  create_row_callback - function without parameter returning a widget
    --  update_row_callback - function taking a widget (result of create_row_callback) and a string (line of script output)

    -- Root layout. We'll be adding rows to it
    local vertical = wibox.layout.fixed.vertical()
    vertical.spacing = tile_size * 0.03
    vertical.mychild_count = 0 -- my custom field, not a part of AweosomeWM
    vertical.myrows = {} -- my custom field, not a part of AweosomeWM

    -- Watch widget will call our callback function and pass the results of get_repos.sh script
    -- We will update GUI based on those results
    local widget = awful.widget.watch(command, interval, function (_, stdout)
            local line_index = 1

            -- Iterate over lines of output
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
        end,
        vertical
    )

    if center_vertically then
        widget = wibox.container.place(widget)
    end
    return widget
end

local function create_arcchart_widget(set_captions_callback, extra_caption_vertical, command, interval)
    -- This function wraps a bash script that is periodically called and its results
    -- are used to populate an arc chart along with text inside it. There is also
    -- additional text box called "extra_caption" which can located either below or
    -- next to the graph, depending on parameters.
    --
    -- The script should output one line containing  a value between 0 and 100, which
    -- will be used as the value for arc chart. Subsequent contents of the line are
    -- passed to the callback and can be used by caller.
    --
    -- Parameters:
    --  set_captions_callback - function receiving both textbox widgets and the value returned by script
    --  extra_caption_vertical (boolean) - whether the extra_caption should be below the chart
    --  command (string) - path to script to call periodically
    --  interval (number) - interval of calling the script in seconds

    -- Text inside the chart
    local middle_caption = wibox.widget.textbox()
    middle_caption.text = ''
    middle_caption.align = 'center'
    middle_caption.font = "sans " .. tostring(tile_size * 0.08)

    -- Main chart
    local chart = wibox.container.arcchart(middle_caption)
    chart.thickness = tile_size * 0.1
    chart.bg = beautiful.color_gray_dark
    chart.colors = { beautiful.color_theme }
    chart.min_value = 0
    chart.max_value = 100
    chart.forced_width = tile_size * 0.5
    chart.forced_height = tile_size * 0.5

    -- Additional text and a linear layout wrapping it with the chart
    local extra_caption = wibox.widget.textbox()
    extra_caption.text = ""
    extra_caption.font = "sans " .. tostring(tile_size * 0.07)
    local content = nil
    if extra_caption_vertical then
        extra_caption.align = 'center'
        content = wibox.layout.fixed.vertical (chart, extra_caption)
    else
        content = wibox.layout.fixed.horizontal (chart, extra_caption)
        extra_caption.valign = 'center'
    end
    content.spacing = tile_size * 0.1

    -- Watch widget will call our callback passing it the results of the command
    -- Based on the output we will update the GUI
    local widget = awful.widget.watch(command, interval, function (_, stdout)
            -- Get individual components of the output
            matcher = stdout:gmatch("%S+")
            value = matcher()
            value = tonumber(value)

            -- Update GUI
            if value ~= nil and value >= 0 and value <= 100 then
                chart.value = value
                set_captions_callback(middle_caption, extra_caption, value, matcher)
            else
                chart.value = 0
                middle_caption.text = "ERR"
                extra_caption.text = "ERR"
            end
        end,
        content
    )
    return widget
end

----------------------------------------------------------------------------------- Concrete widgets

local function create_disk_usage_widget(linux_setup_root)
    local set_captions_callback = function(middle_caption, extra_caption, value, matcher)
        size = matcher()
        used = matcher()
        mount_point = matcher()

        middle_caption.markup = markup_utils.wrap_span(mount_point, beautiful.color_theme, nil)
        extra_caption.text = used .. " / " .. size .. " (" .. value .. "%)"
    end
    local interval = 5
    local command = linux_setup_root .. "/steps/awesome/get_disk_usage.sh "

    -- Widget for mountpoints
    local widget1 = create_arcchart_widget(set_captions_callback, true, command .. "/",         interval)
    local widget2 = create_arcchart_widget(set_captions_callback, true, command .. "/dev/sdb1", interval)

    -- Combine them
    local widget = wibox.layout.fixed.horizontal(widget1, widget2)
    widget.spacing = tile_size * 0.3
    widget = wibox.container.place(widget) -- center horizontally
    return widget
end

local function create_repo_widget(linux_setup_root)
    -- This widget can display git repositories present in the system and some info about
    -- them. It relies upon get_repos.sh script written in bash. The script produces output
    -- like following: <repo_path> <master_branch> <flag1> <flag2> <flag3>, where
    --    repo_path - filesystem path to the repository
    --    master_branch - main branch used by repository ("master" or "main")
    --    flag1, flag2, flag3 - zero or more warnings about the state of repository

    local function create_row()
        local flag_color = "#c94c4c"

        -- Prepare textboxes. We have to store both raw textboxes and their wrapped versions,
        -- because we set text on the former, but alter visibility of the latter.
        local caption_repo = wibox.widget.textbox()
        local caption_branch = wibox.widget.textbox()
        local caption_flag1 = wibox.widget.textbox()
        local caption_flag2 = wibox.widget.textbox()
        local caption_flag3 = wibox.widget.textbox()
        local wrapped_caption_repo = wrap_caption(caption_repo, beautiful.color_gray_dark)
        local wrapped_caption_branch = wrap_caption(caption_branch, beautiful.color_theme)
        local wrapped_caption_flag1 = wrap_caption(caption_flag1, flag_color)
        local wrapped_caption_flag2 = wrap_caption(caption_flag2, flag_color)
        local wrapped_caption_flag3 = wrap_caption(caption_flag3, flag_color)

        -- Create row
        local row = wibox.layout.fixed.horizontal(wrapped_caption_repo, wrapped_caption_branch, wrapped_caption_flag1, wrapped_caption_flag2, wrapped_caption_flag3)
        row.spacing = tile_size * 0.03
        row.caption_repo = caption_repo
        row.caption_branch = caption_branch
        row.caption_flag1 = caption_flag1
        row.caption_flag2 = caption_flag2
        row.caption_flag3 = caption_flag3
        row.wrapped_caption_repo = wrapped_caption_repo
        row.wrapped_caption_branch = wrapped_caption_branch
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
            local master_branch = matcher()
            row.caption_repo.text = " " .. repo_path
            row.caption_branch.text = master_branch
            row.wrapped_caption_branch.visible = master_branch ~= '?'
        else
            row.caption_repo.text = "   " .. repo_path
            row.wrapped_caption_branch.visible = false
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

    local command = linux_setup_root .. "/steps/awesome/get_repos.sh"
    local interval = 10
    local center_vertically = false
    return create_line_oriented_script_widget(create_row, update_row, command, interval, center_vertically)
end

local function create_calendar_widget()
    local bold = function(t) return '<b>' .. t .. '</b>' end
    local styles = {
        month = {
            bg_color     = beautiful.color_gray_light,
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

    local widget = wibox.widget.calendar.month(os.date('*t')) -- This will not work after midnight...
    widget.spacing = 0
    widget.week_numbers = true
    widget.fn_embed = decorate_cell
    return widget
end

local function create_currency_widget(linux_setup_root)
    local create_row = function()
        local left_currency = wibox.widget.textbox()
        local middle_arrow = wibox.widget.textbox()
        middle_arrow.markup = markup_utils.wrap_span('', beautiful.color_theme, nil)
        middle_arrow.align = 'center'
        local right_currency = wibox.widget.textbox()
        local row = wibox.layout.fixed.horizontal(
            wrap_caption(left_currency, beautiful.color_theme),
            middle_arrow,
            wrap_caption(right_currency, beautiful.color_theme)
        )
        row.spacing = tile_size * 0.035
        row = wibox.container.place(row) -- center horizontally
        row.left_currency = left_currency
        row.right_currency = right_currency
        return row
    end
    local update_row = function(row, line)
        matcher = line:gmatch("%S+")
        row.left_currency.text = matcher()
        row.right_currency.text = matcher()
    end
    local command = linux_setup_root .. "/steps/awesome/get_currency_exchange.sh"
    local interval = 3600
    local center_vertically = true
    return create_line_oriented_script_widget(create_row, update_row, command, interval, center_vertically)
end

local function create_system_usage_widget(linux_setup_root)
    local interval = 2

    -- CPU widget
    local set_middle_caption_callback = function(middle_caption, extra_caption, value)
        middle_caption.markup = markup_utils.wrap_span('', beautiful.color_theme, nil)
        extra_caption.text = value .. "%"
    end
    local command = linux_setup_root .. "/steps/awesome/get_cpu_usage.sh"
    local cpu_widget = create_arcchart_widget(set_middle_caption_callback, true, command, interval)

    -- Memory widget
    local set_middle_caption_callback = function(middle_caption, extra_caption, value)
        middle_caption.markup = markup_utils.wrap_span('', beautiful.color_theme, nil)
        extra_caption.text = value .. "%"
    end
    local command = linux_setup_root .. "/steps/awesome/get_mem_usage.sh"
    local mem_widget = create_arcchart_widget(set_middle_caption_callback, true, command, interval)

    -- Combine them
    local widget = wibox.layout.fixed.horizontal(cpu_widget, mem_widget)
    widget.spacing = tile_size * 0.3
    widget = wibox.container.place(widget) -- center horizontally
    return widget
end

local function create_layout_list_widget()
    local widget = awful.widget.layoutlist {
        base_layout = wibox.widget {
            spacing = tile_size * 0.03,
            layout = wibox.layout.fixed.vertical,
        },
        widget_template = {
            widget = wibox.container.background,
            id = 'background_role',
            shape = gears.shape.rounded_rect,
            {
                layout = wibox.layout.fixed.horizontal,
                spacing = tile_size * 0.04,
                {
                    widget = wibox.widget.imagebox,
                    id = 'icon_role',
                    forced_height = tile_size * 0.185,
                    forced_width = tile_size * 0.185,
                },
                {
                    widget = wibox.widget.textbox,
                    id = 'text_role',
                },
            },
        }
    }
    widget:buttons(gears.table.join(
        awful.button({ }, 4, function () awful.layout.inc(-1) end),
        awful.button({ }, 5, function () awful.layout.inc( 1) end)
    ))
    local layout_popup = awful.popup {
        widget = wibox.widget {ll, margins = 4, widget = wibox.container.margin},
        border_color = beautiful.border_color,
        border_width = beautiful.border_width,
        placement = awful.placement.centered,
        ontop = true,
        visible = false,
        shape = gears.shape.rounded_rect
    }

    return widget
end

local function create_greeting_widget(user)
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
    widget = wibox.container.place(widget)

    return widget
end



----------------------------------------------------------------------------------- Main

return function(visible_tag, linux_setup_root, user, screen)
    -- Main function composing the panel from above widgets

    -- Some size constants
    local vertical_placement_percent = 0.2 -- value between 0 (snap to top) and 1 (snap to bottom)
    local horizontal_placement_percent = 0.5 -- value between 0 (snap to left) and 1 (snap to right)
    local rows = 3
    local columns = 5
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
    local function add_widget_to_grid(widget, row, col, rowspan, colspan)
        local widget = widget_wrappers.margin(widget, tile_size * 0.04)
        widget = widget_wrappers.sized_bg(widget, beautiful.color_gray_light, colspan * tile_size, rowspan * tile_size)
        widget = wibox.widget(widget)
        root_layout:add_widget_at(widget, row, col, rowspan, colspan)
    end
    add_widget_to_grid(create_greeting_widget(user),                 1, 1,   2, 1)
    add_widget_to_grid(create_layout_list_widget(linux_setup_root),  3, 1,   1, 1)
    add_widget_to_grid(create_repo_widget(linux_setup_root),         1, 3,   2, 3)
    add_widget_to_grid(create_currency_widget(linux_setup_root),     1, 2,   1, 1)
    add_widget_to_grid(create_calendar_widget(),                     2, 2,   1, 1)
    add_widget_to_grid(create_system_usage_widget(linux_setup_root), 3, 2,   1, 2)
    add_widget_to_grid(create_disk_usage_widget(linux_setup_root),   3, 4,   1, 2)

    -- Setup window and embed the grid layout in it
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
        local current_tag = awful.tag.selected(1)
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
    local client_class = "ST_CAVA" .. screen.index
    local cava_pid = awful.spawn('st -A 0 -B "#000000" -c ' .. client_class .. ' -e cava')
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
