# i2c-tool

Python script for scanning addresses on an I2C bus, and dumping memory chips.  
Based on [pyftdi](https://eblot.github.io/pyftdi/index.html), so it needs a compatible FTDI device (FT2232C/D, FT232H, FT2232H, FT4232H, FT4232HA).

Tested with: 
- Tigard board v1.1 (FT2232HQ)
- Atmel AT24C04D (EEPROM)
- Python 3.10.12
- pyftdi 0.55.4

## Requirements

- Python 3
- pyftdi (0.55.4)
