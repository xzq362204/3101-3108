#!/bin/bash

# check reg value of 0x10005200, the 7th bit value from the bottom should be 1 when Pen plug in
main(){
    #local reg_value=$(mem r 0x10005200)
    local gpio_value=$(ectool gpioget PEN_DET_ODL)

    echo $gpio_value
    local reg_bit=${gpio_value:0-1}
    echo $reg_bit
    if [[ ${reg_bit} -eq 0 ]]; then
        echo 'switch is ON and power pin is ON'
        exit 0
    else
        echo ' Switch is still OFF, Check if pen is plugged in'
        exit 1
    fi
}

main "$@"
