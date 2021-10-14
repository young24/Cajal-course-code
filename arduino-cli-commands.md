

## To find the cores to install
arduino-cli core search nano // "nano" is your board

## updata the core index
arduino-cli core update-index

## compile a sketch
arduino-cli compile -b arduino:avr:nano [SKETCH] // -b is "--fqbq" in the old system

## upload a sketch to the board
/// the port is "/dev/ttyUSB0"

arduino-cli upload blink/blink.ino -p /dev/ttyUSB0 -b arduino:avr:nano

