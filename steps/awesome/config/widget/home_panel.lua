local wibox = require("wibox")
local awful = require("awful")
local gears = require("gears")
local beautiful = require("beautiful")
local markup_utils = require("utils.markup")
local widget_wrappers = require("utils.widget_wrappers")
local keygrabber = require("awful.keygrabber")
local dpi = require("beautiful.xresources").apply_dpi

local naughty = require("naughty")


----------------------------------------------------------------------------------- Global utils

-- The main function builds a grid layout. This constant represent the size of one cell
-- in the layout. All font sizes, margins, spacings, paddings, widget sizes should be some
-- multiple of this value
local tile_size = dpi(200)

local function wrap_widget(widget, rowspan, colspan)
    widget = widget_wrappers.margin(widget, tile_size * 0.04)
    widget = widget_wrappers.sized_bg(widget, beautiful.color_gray_light, colspan * tile_size, rowspan * tile_size)
    widget = wibox.widget(widget)
    return widget
end

----------------------------------------------------------------------------------- Individual widgets

local function create_disk_usage_widget(mount_point)
    -- This widget can display disk usage as an arc chart.
    -- It will show the mount point location inside the chart,
    -- as well as numerical info next to it.

    -- Mount point location inside the chart
    local mount_point_caption = wibox.widget.textbox()
    mount_point_caption.text = mount_point
    mount_point_caption.align = 'center'
    mount_point_caption.font = "sans " .. tostring(tile_size * 0.08)

    -- Main chart
    local chart = wibox.container.arcchart(mount_point_caption)
    chart.thickness = tile_size * 0.1
    chart.bg = beautiful.color_gray_dark
    chart.colors = { beautiful.color_theme }
    chart.min_value = 0
    chart.max_value = 100
    chart.forced_width = tile_size * 0.8
    chart.forced_height = tile_size * 0.8

    -- Additional text next to the chart
    local caption = wibox.widget.textbox()
    caption.text = ""
    caption.font = "sans " .. tostring(tile_size * 0.07)

    -- Chart and additional text wrapped in horizontal layout
    local widget = wibox.widget {
        layout  = wibox.layout.fixed.horizontal,
        spacing = tile_size * 0.1,
        chart,
        caption,
    }

    -- Watch widget will call our callback passing it the results of df command.
    -- Based on the output we will update the GUI
    local command = "bash -c 'df " .. mount_point .. " --output=used,size,pcent -h | tail +2'"
    widget = awful.widget.watch(command, 5, function (_, stdout)
            -- Get individual components of the output
            matcher = stdout:gmatch("%S+")
            used = matcher()
            size = matcher()
            percent = matcher()

            -- Update GUI
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
    return wrap_widget(widget, 1, 2)
end

local function create_repo_widget(linux_setup_root)
    -- This widget can display git repositories present in the system and some info about
    -- them. It relies upon get_repos.sh script written in bash. The script produces output
    -- like following: <repo_path> <master_branch> <flag1> <flag2> <flag3>, where
    --    repo_path - filesystem path to the repository
    --    master_branch - main branch used by repository ("master" or "main")
    --    flag1, flag2, flag3 - zero or more warnings about the state of repository
    --
    -- The widget is coded kind of sloppily and can be improved:
    --    the existence of maximum 3 flags is hardcoded
    --    at each update we remove all rows and recreate them

    -- A helper function to create on row representing one git repository
    local function create_row()
        local flag_color = "#c94c4c"
        local wrap_caption = function(caption, bg)
            caption.valign = 'bottom'
            caption = widget_wrappers.margin(caption, tile_size * 0.023)
            caption = widget_wrappers.bg(caption, bg)
            caption = wibox.widget(caption)
            return caption
        end

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
        row.set_values = function(self, repo, branch, flag1, flag2, flag3)
            caption_repo.text = " " .. repo
            caption_branch.text = branch
            caption_flag1.text = flag1
            wrapped_caption_flag1.visible = flag1 ~= ''
            caption_flag2.text = flag2
            wrapped_caption_flag2.visible = flag2 ~= ''
            caption_flag3.text = flag3
            wrapped_caption_flag3.visible = flag3 ~= ''
        end
        return row
    end

    -- Root layout. We'll be adding rows to it
    local vertical = wibox.layout.fixed.vertical()
    vertical.spacing = tile_size * 0.03
    vertical.mychild_count = 0 -- my custom field, not a part of AweosomeWM

    -- Watch widget will call our callback function and pass the results of get_repos.sh script
    -- We will update GUI based on those results
    local command = linux_setup_root .. "/steps/awesome/get_repos.sh"
    widget = awful.widget.watch(command, 10, function (_, stdout)
            -- Remove all children. This is sloppy...
            for i=vertical.mychild_count,1,-1 do
                vertical:remove(i)
            end
            vertical.mychild_count = 0

            -- Iterate over lines of output. Each line represents one repository
            for line in stdout:gmatch("[^\r\n]+") do
                -- Get components of the repository info
                local matcher = line:gmatch("%S+")
                local path = matcher()
                local master_branch = matcher()
                local flag1 = matcher() or ''
                local flag2 = matcher() or ''
                local flag3 = matcher() or ''

                -- Add the row to GUI
                local row = create_row()
                row:set_values(path, master_branch, flag1, flag2, flag3)
                vertical:add(row)
                vertical.mychild_count = vertical.mychild_count + 1
            end
        end,
        vertical
    )
    return wrap_widget(widget, 1, 2)
end

local function create_calendar()
    -- A simple calendar widget. Nothing special, it isn't interactive or anything

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
    return wrap_widget(widget, 1, 1)
end

----------------------------------------------------------------------------------- Main

return function(visible_tag, linux_setup_root, screen)
    -- Main function composing the panel from above widgets

    -- Some size constants
    local rows = 3
    local columns = 4
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
    root_layout:add_widget_at(create_repo_widget(linux_setup_root),    3, 1,   1, 3)
    root_layout:add_widget_at(create_calendar(),                       3, 4,   1, 1)

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
        local current_tag = awful.tag.selected(1)
        self.visible = current_tag ~= nil and visible_tag == current_tag.name
    end
    widget:refresh_visibility()
    screen:connect_signal("tag::history::update", function() widget:refresh_visibility() end)

    -- Return it
    return widget
end
