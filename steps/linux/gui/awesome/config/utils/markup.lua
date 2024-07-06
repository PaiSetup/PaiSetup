local function wrap_span(text, foreground, background)
    local open_tag = "<span"
    if foreground ~= nil then
        open_tag = open_tag .. " foreground='" .. foreground .. "'"
    end
    if background ~= nil then
        open_tag = open_tag .. " background='" .. background .. "'"
    end
    open_tag = open_tag .. ">"

    return open_tag .. text .. "</span>"
end

return {
    wrap_span = wrap_span,
}
