local wibox = require("wibox")
local awful = require("awful")
local markup_utils = require("utils.markup")

return function (callback, text)
    widget = wibox.widget.textbox()
    widget.setup_my_foreground = function(self, foreground)
        self.markup = markup_utils.wrap_span(text, foreground, nil)
    end
    widget:buttons(awful.button({ }, 1, function ()
        callback()
    end))
    return widget
end
