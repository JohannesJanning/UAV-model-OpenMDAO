# -----------------------------------------------------------------------------
# Atmosphere
# -----------------------------------------------------------------------------
RHO_AIR = 1.225  # kg/m^3  ; air density

# -----------------------------------------------------------------------------
# Mission timing
# -----------------------------------------------------------------------------
T_HOVER = 60.0  # s  ; hover time per landing/takeoff event

# -----------------------------------------------------------------------------
# Rotor configuration
# -----------------------------------------------------------------------------
N_ROTOR = 6  # -  ; number of rotors
SIGMA = 0.13  # -  ; rotor solidity
CD0_ROTOR = 0.012  # -  ; blade profile drag coefficient
ETA_HOVER = 0.75  # -  ; hover efficiency
BETA_HEX = 0.20  # -  ; frame mass fraction
KAPPA_MAX = 1.15  # -  ; upper limit for induced-power factor

# -----------------------------------------------------------------------------
# Battery
# -----------------------------------------------------------------------------
BATTERY_DENSITY = 158.0  # Wh/kg  ; specific energy density
BATTERY_EFF = 0.85  # -  ; battery efficiency

# -----------------------------------------------------------------------------
# Physical constants
# -----------------------------------------------------------------------------
G = 9.81  # m/s^2  ; gravitational acceleration

# -----------------------------------------------------------------------------
# Mass/weight regression coefficients
# -----------------------------------------------------------------------------
K_MOTOR = 2.506e-4  # kg/W  ; motor mass coefficient
K_ESC = 3.594e-4  # kg/W  ; ESC mass coefficient
K_ROTOR_A = 0.7484  # kg/m^2  ; rotor mass coefficient (per rotor)
K_ROTOR_B = 0.0403  # kg/m  ; rotor mass offset (per rotor)

# -----------------------------------------------------------------------------
# Constraint limits
# -----------------------------------------------------------------------------
DL_MAX = 250.0  # N/m^2  ; disk loading limit
BL_MAX = 0.14  # -  ; blade loading limit

# -----------------------------------------------------------------------------
# Design variable bounds
# -----------------------------------------------------------------------------
W_TOTAL_BOUNDS = (0.5 * G, 50.0 * G)  # N  ; total aircraft weight range
V_INF_BOUNDS = (10.0, 50.0)  # m/s  ; cruise speed range
R_BOUNDS = (0.05, 1.0)  # m  ; rotor radius range
MU_BOUNDS = (0.01, 0.5)  # -  ; edgewise advance-ratio range
