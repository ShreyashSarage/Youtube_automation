-- wrk script: POST an order with 10 items
wrk.method = "POST"
wrk.headers["Content-Type"] = "application/json"
local items = {}
for i = 1, 10 do items[#items + 1] = string.format('{"price": %d.99, "qty": %d}', i, i) end
wrk.body = '{"items": [' .. table.concat(items, ", ") .. ']}'
