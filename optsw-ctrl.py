# standard library
import time
from logging import basicConfig, INFO
from logging import FileHandler, StreamHandler
from os import environ as env
from pathlib import Path


# dependencies
from scpi import connect


# constants
preset = Path() / "preset"
logname = "optsw-ctrl.log"


# logging
basicConfig(
    level=INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=(StreamHandler(), FileHandler(logname)),
)


# main script
def main():
    # get FG and PG addresses
    fg_addr = env["FG_HOST"], int(env["FG_PORT"])
    pg_addr = env["PG_HOST"], int(env["PG_PORT"])

    with connect(*fg_addr) as fg, connect(*pg_addr) as pg:
        # FG setup before main loop
        fg.send_from(preset / "33500B_initialization.txt")
        fg.send_from(preset / "33500B_1pps_signal.txt")
        fg.send_from(preset / "33500B_output_for_1Hz_switch.txt")
        fg.send_from(preset / "33500B_trigger_for_1Hz_switch.txt")

        # PG setup before main loop
        pg.send_from(preset / "3390_initialization.txt")
        pg.send_from(preset / "3390_output_for_1Hz_switch_EE.txt")
        pg.send_from(preset / "3390_trigger.txt")

        # main loop
        try:
            input("Type any key to start control: ")

            fg.send("OUTP1 ON")
            fg.send("OUTP2 ON")
            fg.send("INIT1:CONT ON")
            time.sleep(1.0)
            pg.send("OUTP ON")
            pg.send("OUTP:TRIG ON")

            while True:
                fg.send("SYST:ERR?")
                pg.send("SYST:ERR?")
                time.sleep(10.0)
        except (EOFError, KeyboardInterrupt):
            print("Control was interrupted by user")
        finally:
            fg.send_from(preset / "33500B_initialization.txt")
            pg.send_from(preset / "3390_initialization.txt")


# run main script
if __name__ == "__main__":
    main()
