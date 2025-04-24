import numpy as np
import pandas as pd

# Function to solve the Lotka voltera model from this paper https://doi.org/10.1158/0008-5472.CAN-23-2040
def LV_model(t,params,D):

    # Parameters
    r_s = params[0]
    r_R_mult = params[1]
    d_s = params[2]
    d_R = params[3]
    d_D = params[4]
    k = params[5]
    IC = params[6:8]
    

    dt = t[1] - t[0]
    # Initial conditions
    s = np.zeros(len(t))
    r = np.zeros(len(t))
    s[0] = IC[0]
    r[0] = IC[1]

    r_R = r_s * r_R_mult

    for i in range(len(t) - 1):
        s[i+1] = s[i] + dt * (r_s*s[i]*(1 - (s[i] + r[i]) /k) * (1 - d_D*D)  - d_s*s[i])
        r[i+1] = r[i] + dt* (r_R*r[i] *(1 - (s[i] + r[i]) / k)  - d_R*r[i])

    sol = np.array([s,r])
    return sol