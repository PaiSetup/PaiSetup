local wibox = require("wibox")
local markup_utils = require("utils.markup")

return function(text, on_color, off_color, initial_value, callback, callback_data)
    local widget = wibox.widget.textbox()
    widget.is_clicked = false
    widget.font = "sans 40"
    widget.refresh = function (self)
        local color = off_color
        if self.is_clicked then
            color = on_color
        end
        self.markup = markup_utils.wrap_span(text, color, nil)
    end
    widget.set_is_clicked = function (self, new_value)
        self.is_clicked = new_value
        self:refresh()
        callback(self, self.is_clicked, callback_data)
    end
    widget:connect_signal("button::press", function (self, lx, ly, button, mods, metadata)
        if button == 1 then
            self:set_is_clicked(not self.is_clicked)
        end
    end)

    widget:set_is_clicked(initial_value)

    return widget
end
