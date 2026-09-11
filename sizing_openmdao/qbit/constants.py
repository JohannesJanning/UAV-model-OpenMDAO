import numpy as np

# -----------------------------------------------------------------------------
# Atmosphere
# -----------------------------------------------------------------------------
RHO_AIR = 1.225  # kg/m^3  ; air density

# -----------------------------------------------------------------------------
# Mission timing
# -----------------------------------------------------------------------------
T_HOVER = 60.0  # s  ; hover time per landing/takeoff event

# -----------------------------------------------------------------------------
# Airframe and rotor parameters
# -----------------------------------------------------------------------------
BETA_QBIT = 0.18  # -  ; frame weight fraction
ETA_HOVER = 0.65  # -  ; hover efficiency
CD0_WING = 0.01  # -  ; wing profile drag coefficient
E_OSWALD = 0.8  # -  ; wing Oswald efficiency
AR_FIXED = 8.0  # -  ; fixed wing aspect ratio
N_ROTOR = 4  # -  ; number of rotors
SIGMA = 0.13  # -  ; rotor solidity
CD0_ROTOR = 0.012  # -  ; rotor profile drag coefficient
KAPPA_MAX = 1.15  # -  ; upper limit for induced-power factor
BETA_CRUISE = np.radians(85.0)  # rad  ; fixed cruise shaft tilt

# -----------------------------------------------------------------------------
# Battery
# -----------------------------------------------------------------------------
BATTERY_DENSITY = 158.0  # Wh/kg  ; pack energy density
BATTERY_EFF = 0.85  # -  ; battery/transmission efficiency

# -----------------------------------------------------------------------------
# Physical constants
# -----------------------------------------------------------------------------
G = 9.81  # m/s^2  ; gravity

# -----------------------------------------------------------------------------
# Weight regression coefficients
# -----------------------------------------------------------------------------
K_MOTOR = 2.506e-4  # kg/W  ; motor mass coefficient
K_ESC = 3.594e-4  # kg/W  ; ESC mass coefficient
K_ROTOR_A = 0.7484  # kg/m^2  ; rotor mass coefficient (per rotor)
K_ROTOR_B = 0.0403  # kg/m  ; rotor mass offset (per rotor)
K_WING_A = -0.0802  # kg  ; wing mass intercept
K_WING_B = 2.2854  # kg/m^2  ; wing mass slope

# -----------------------------------------------------------------------------
# Constraint limits
# -----------------------------------------------------------------------------
DL_MAX = 250.0  # N/m^2  ; disk-loading limit
BL_MAX = 0.14  # -  ; blade-loading limit
CL_MAX = 0.6  # -  ; cruise lift-coefficient limit

# -----------------------------------------------------------------------------
# Design variable bounds
# -----------------------------------------------------------------------------
W_TOTAL_BOUNDS = (0.5 * G, 50.0 * G)  # N  ; total aircraft weight range
V_INF_BOUNDS = (10.0, 50.0)  # m/s  ; cruise speed range
R_BOUNDS = (0.05, 1.0)  # m  ; rotor radius range
J_BOUNDS = (0.01, 1.3)  # -  ; propeller advance-ratio range
S_W_BOUNDS = (0.05, 5.0)  # m^2  ; wing area range
