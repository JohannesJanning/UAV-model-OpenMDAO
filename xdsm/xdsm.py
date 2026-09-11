"""Generate separate XDSM diagrams for the QBiT and hexarotor sizing models."""

import os
from pathlib import Path

from pyxdsm.XDSM import FUNC, IFUNC, OPT, XDSM


OUTPUT_DIR = Path(__file__).parent


def add_common_systems(xdsm: XDSM) -> None:
    xdsm.add_system('opt', OPT, r'\text{SLSQP Optimizer}')
    xdsm.add_system('hover', FUNC, r'\text{Hover Power}')
    xdsm.add_system('trim', FUNC, r'\text{Aerodynamic Trim}')
    xdsm.add_system('cruise', FUNC, r'\text{Cruise Power}')
    xdsm.add_system('installed', FUNC, r'\text{Installed Power}')
    xdsm.add_system('empty', FUNC, r'\text{Empty Weight}')
    xdsm.add_system('energy', FUNC, r'\text{Mission Energy}')
    xdsm.add_system('battery', FUNC, r'\text{Battery Weight}')
    xdsm.add_system('balance', IFUNC, r'\text{Weight Balance}')
    xdsm.add_system('constraints', FUNC, r'\text{Constraints}')


def add_common_connections(xdsm: XDSM, trim_variables: str, empty_variables: str) -> None:

    xdsm.connect('opt', 'hover', r'W_{total}, r')
    xdsm.connect('opt', 'trim', trim_variables)
    xdsm.connect('opt', 'empty', empty_variables)
    xdsm.connect('opt', 'energy', r'R, n_c, V_\infty')
    xdsm.connect('opt', 'balance', r'W_{total}, W_{pay}')
    xdsm.connect('opt', 'constraints', r'W_{total}, r')

    xdsm.connect('hover', 'installed', r'P_{hover}')
    xdsm.connect('hover', 'energy', r'P_{hover}')
    xdsm.connect('trim', 'cruise', r'T_{cruise}, V_i, P_0')
    xdsm.connect('trim', 'constraints', r'C_T')
    xdsm.connect('cruise', 'installed', r'P_{cruise}')
    xdsm.connect('cruise', 'energy', r'P_{cruise}')
    xdsm.connect('installed', 'empty', r'P_{inst}')
    xdsm.connect('energy', 'battery', r'E_{req}')
    xdsm.connect('battery', 'balance', r'W_{battery}')
    xdsm.connect('empty', 'balance', r'W_{empty}')

    xdsm.connect('balance', 'opt', r'W_{total} - W_{pay} - W_{battery} - W_{empty}')
    xdsm.connect('constraints', 'opt', r'\text{loading constraints}')


def build_qbit_xdsm() -> XDSM:
    xdsm = XDSM()
    add_common_systems(xdsm)
    xdsm.add_input('opt', r'W_{pay}, R, n_c; W_{total}^{(0)}, V_\infty^{(0)}, r^{(0)}, J^{(0)}, S_w^{(0)}')
    add_common_connections(
        xdsm,
        r'W_{total}, V_\infty, r, S_w, J',
        r'W_{total}, r, S_w',
    )

    xdsm.connect('opt', 'cruise', r'V_\infty, r')
    xdsm.connect('opt', 'constraints', r'V_\infty, S_w')
    xdsm.connect('trim', 'constraints', r'C_L')
    xdsm.add_output('opt', r'\min W_{total}; W_{total}^*, V_\infty^*, r^*, J^*, S_w^*', side='right')
    return xdsm


def build_hexarotor_xdsm() -> XDSM:
    xdsm = XDSM()
    add_common_systems(xdsm)
    xdsm.add_input('opt', r'W_{pay}, R, n_c; W_{total}^{(0)}, V_\infty^{(0)}, r^{(0)}, \mu^{(0)}')
    add_common_connections(
        xdsm,
        r'W_{total}, V_\infty, r, \mu',
        r'W_{total}, r',
    )

    xdsm.connect('opt', 'cruise', r'V_\infty, r')
    xdsm.add_output('opt', r'\min W_{total}; W_{total}^*, V_\infty^*, r^*, \mu^*', side='right')
    return xdsm


def write_xdsms() -> None:
    previous_dir = Path.cwd()
    os.chdir(OUTPUT_DIR)
    try:
        build_qbit_xdsm().write('qbit_xdsm', build=True, cleanup=True)
        build_hexarotor_xdsm().write('hexarotor_xdsm', build=True, cleanup=True)
    finally:
        os.chdir(previous_dir)

    for stem in ('qbit_xdsm', 'hexarotor_xdsm'):
        for extension in ('.aux', '.log', '.tex', '.tikz'):
            (OUTPUT_DIR / f'{stem}{extension}').unlink(missing_ok=True)


if __name__ == '__main__':
    write_xdsms()