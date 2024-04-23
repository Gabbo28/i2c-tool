#!/usr/bin/env python3

from sys import stderr
import argparse
from pyftdi.ftdi import Ftdi
from pyftdi.i2c import I2cController, I2cNackError

## create the parser for the "b" command
#parser_b = subparsers.add_parser('b', help='b help')
#parser_b.add_argument('--baz', choices='XYZ', help='baz help')

def list_devices(args):
    Ftdi.show_devices()

def scan(args):

    print(f"Scanning with \"{args.device}\"")

    HIGHEST_I2C_SLAVE_ADDRESS = 0x78
    i2c = I2cController()
    slaves = []
    #i2c.configure(args.device, frequency = 400) # TODO: accept freq as parameter

    try:
        i2c.set_retry_count(2)
        i2c.force_clock_mode(False) # TODO: maybe change
        i2c.configure(args.device, frequency = 400) # TODO: accept freq as parameter
        for addr in range(HIGHEST_I2C_SLAVE_ADDRESS+1):
            port = i2c.get_port(addr)
            try:
                port.read(0)
                slaves.append(str(hex(addr))+'(R)')
            except I2cNackError:
                pass

            try:
                port.write([])
                slaves.append(str(hex(addr))+'(W)')
            except I2cNackError:
                pass
    finally:
        i2c.terminate()

    print(slaves)
    return(slaves)

def dump(args):

    # check address is available and readable
    if (args.address+'(R)') in scan(args):
        print(f"Dumping memory at {args.address} with {args.device}.")

        I2C_SLAVE_ADDRESS = int(args.address, 16)
        SIZE = int(args.size)

        

        i2c = I2cController()

        try:
            # setup i2c instance and slave
            i2c.set_retry_count(1)
            i2c.force_clock_mode(False) # TODO: maybe change
            i2c.configure(args.device, frequency = 400) # TODO: accept freq as parameter
            slave = i2c.get_port(I2C_SLAVE_ADDRESS)

            # read memory
            dump = bytes(slave.read_from(0,SIZE))

            if args.outfile:
                OUTFILE = args.outfile
                with open(OUTFILE, "wb") as out_file:
                    out_file.write(bytes(dump))
            else:
                print(dump)

        finally:
            i2c.terminate()
    else: 
        print("Specified I2C adrress not available or not readable.")

def main():

    # create the top-level parser
    parser = argparse.ArgumentParser()
    
    subparsers = parser.add_subparsers(required = True)

    # create the parser for the "list_devices" command
    parser_dev = subparsers.add_parser('list_devices', help='Lists attached FTDI devices. Example: ./i2c_tool.py list_devices')
    parser_dev.set_defaults(func = list_devices)
    
    # create the parser for the "scan" command
    parser_scan = subparsers.add_parser('scan', help="Scan available R/W addresses in the I2C bus of the specified device. Example: ./i2c_tool scan -d 'ftdi://ftdi:2232:1:23f/2'")
    parser_scan.add_argument("-d", "--device", required = True,
            help="FTDI device, use \"list_devices\" mode to discover them.")
    parser_scan.set_defaults(func = scan)

    # create the parser for the "dump" command

    parser_dump = subparsers.add_parser('dump', help = "Dump I2C memory at the given address, using chosen device. Example: ./i2c_tool scan -d 'ftdi://ftdi:2232:1:23f/2' -a 0x50")
    parser_dump.add_argument("-d", "--device", required = True,
            help="FTDI device, use \"list_devices\" mode to discover them.")
    parser_dump.add_argument("-a", "--address", required = True,
            help="Readable slave address, use \"scan\" mode to discover them.")
    parser_dump.add_argument("-s", "--size", required = True,
            help="EEPROM memory size to read, in bytes. See the EEPROM's data sheet.")
    parser_dump.add_argument("-o", "--outfile", required = False,
            help="Output file. If not specified, bytes are printed to stdout.")
    parser_dump.set_defaults(func = dump)

    # parse arguments
    args = parser.parse_args()
    
    # execute sub-commands functions
    args.func(args)


if __name__ == '__main__':
    try:
        main()
    except Exception as _exc:
        print(str(_exc), file=stderr)
