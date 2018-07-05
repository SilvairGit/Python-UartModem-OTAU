from setuptools import setup

__version__ = "2.8.0"

setup(
    name="silvair_otau_demo",
    version=__version__,
    author="Tomasz Szewczyk",
    author_email="tomasz.szewczyk@silvair.com",
    py_modules=["main"],
    packages=["silvair_otau_demo",
              "silvair_otau_demo.dfu_logic",
              "silvair_otau_demo.dfu_logic.states",
              "silvair_otau_demo.uart_logic",
              "silvair_otau_demo.uart_logic.states",
              ],
    include_package_data=True,
    python_requires=">=3.6.0",
    install_requires=["click>=6.7",
                      "termcolor>=1.1.0",
                      "tqdm>=4.22.0",
                      "silvair_uart_common_libs==2.8.0"
                    ],
    dependency_links=[
        "git+ssh://git@github.com/SilvairGit/Python-UartModem-Common.git@2.8.0#egg=silvair_uart_common_libs-2.8.0"
    ],
    entry_points='''
    [console_scripts]
        silvair_otau_demo=main:start
    ''',
)
