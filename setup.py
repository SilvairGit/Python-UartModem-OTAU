from setuptools import setup

setup(
    name="silvair_otau_demo",
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
                      "silvair-uart-common-libs==0.0.1"
                    ],
    dependency_links=[
        "git+ssh://git@github.com/SilvairGit/Python-UartModem-Common.git#egg=silvair-uart-common-libs-0.0.1"
    ],
    entry_points='''
    [console_scripts]
        silvair_otau_demo=main:start
    ''',
)
