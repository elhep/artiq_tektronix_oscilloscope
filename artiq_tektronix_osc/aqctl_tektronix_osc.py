import argparse

from sipyco.pc_rpc import simple_server_loop
from sipyco import common_args
from artiq_tektronix_osc.driver import Tektronix4SeriesScope, logger


def get_argparser():
    parser = argparse.ArgumentParser(
        description="ARTIQ controller for the Andor iXon Ultra 897 camera.")
    parser.add_argument("--ip", required=True, help="IP address of the oscilloscope")
    common_args.simple_network_args(parser, 3253)
    common_args.verbosity_args(parser)
    return parser


def main():
    args = get_argparser().parse_args()
    common_args.init_logger_from_args(args)
    logger.info(f"Starting NDSP controller...")
    with Tektronix4SeriesScope(args.ip) as scope:
        simple_server_loop({"scope": scope},
                           common_args.bind_address_from_args(args), args.port)

if __name__ == "__main__":
    main()