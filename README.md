# ARTIQ NDSP for Tektronix 4000 Series Scopes

## Installation

1. Create an empty virtual environment:

```bash
python -m venv env
```

2. Activate environment:

```
source env/bin/activate
```

3. Install NDSP:

```
python -m pip install git+https://github.com/elhep/artiq_tektronix_oscilloscope
```

4. Run with scope IP as `--ip` parameter:

```
aqctl_tektronix_osc --ip <SCOPE IP> -v
```

It should log scope identification, e.g.:

```
INFO:tektronix_osc:Starting NDSP controller...
INFO:tektronix_osc:Connected to scope at 192.168.95.182
INFO<2>:tektronix_osc:Scope identification: TEKTRONIX,MSO4104,C020799,CF:91.1CT FV:v2.48
```
