#!/bin/sh

get_rate() {
    buy="$1"
    buy_unit="$2"
    sell="$3"
    sell_unit="$4"
    result="$(curl http://www.floatrates.com/daily/$buy.json 2>/dev/null | jq .$sell.rate)"
    if [ $? != 0 ] || [ -z "$result" ]; then
        value="Could not get exchange rate"
    else
        value="$(echo "$result" | cut -c -5)"
    fi
    #echo "$sell->$buy: 1$buy_unit = $value$sell_unit"
    echo "1$buy_unit $value$sell_unit"
}
get_rate "usd" "$" "pln" "zł"
get_rate "eur" "€" "pln" "zł"
get_rate "rub" "₽" "pln" "zł"
