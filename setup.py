from setuptools import setup, find_packages

setup(
    name='artiq_tektronix_osc',
    version='1.0.0',
    description='ARTIQ NDSP for Tektronix 4 Series Oscilloscopes',
    author='Mikołaj Sowiński',
    author_email='mikolaj.sowinski@pw.edu.pl',
    url='https://github.com/elhep/artiq_tektronix_oscilloscope',
    packages=[
        "artiq_tektronix_osc"
    ],
    install_requires=[
        "PyVISA-py",
        "sipyco @ git+https://github.com/m-labs/sipyco",
        "zeroconf",
        "psutil",
        "numpy"
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points={
        'console_scripts': [
            'aqctl_tektronix_osc=artiq_tektronix_osc.aqctl_tektronix_osc:main'
        ]
    }
)