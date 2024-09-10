import time

from tektronix_osc.driver import Tektronix4SeriesScope

ip_addresses = [
    '192.168.95.142',
    '192.168.95.164',
    '192.168.95.165',
    '192.168.95.181',
    '192.168.95.182'
]


def test_scope(identifier):
    print(f"Testing scope for identifier: {identifier}")
    
    
    with Tektronix4SeriesScope(identifier) as scope:
        ident = scope.identify()
        print(f"\t=> {ident}")
        ident = "_".join([x.lower() for x in ident.split(',')[:3]])
        
        scope.reset()

        scope.set_current_datetime()
        scope.wait_for_idle(10)

        scope.set_channel(
            channel=1,
            vertical_scale=1.0,
            vertical_position=-3.0,
            termination_fifty_ohms=False,
            label="DIO SMA 0",
            ac_coupling=False
        )

        scope.set_channel(
            channel=2,
            vertical_scale=1.25,
            vertical_position=-1.0,
            termination_fifty_ohms=False,
            label="Urukul 0",
            ac_coupling=True
        )

        scope.set_channel(
            channel=3,
            vertical_scale=1.5,
            vertical_position=1.0,
            termination_fifty_ohms=False,
            label="Urukul 1",
            ac_coupling=True
        )

        scope.set_channel(
            channel=4,
            vertical_scale=2.0,
            vertical_position=3.0,
            termination_fifty_ohms=False,
            label="Phaser RF 0",
            ac_coupling=True
        )

        scope.set_horizontal_scale(100e-6)

        scope.set_trigger(
            channel=2,
            level=1.23,
            slope="FALL",
            mode="AUTO"
        )

        time.sleep(1)

        screen = scope.get_screen_png()
        with open(f"{ident}.png", "wb") as f:
            f.write(screen)


for r in ip_addresses:
    test_scope(r)