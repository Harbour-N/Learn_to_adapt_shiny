class Patient:
    def __init__(self, r_s, r_r_mult, d_s, d_R, d_D, k, s0, r0):
        self.r_s = r_s
        self.r_r_mult = r_r_mult
        self.d_s = d_s
        self.d_R = d_R  # Ensure consistency in naming
        self.d_D = d_D
        self.k = k
        self.s0 = s0
        self.r0 = r0

    def get_parameters(self):
        return [self.r_s, self.r_r_mult, self.d_s, self.d_R, self.d_D, self.k, self.s0, self.r0]

    def __repr__(self):
        return (f"Patient(r_s={self.r_s}, r_r_mult={self.r_r_mult}, d_s={self.d_s}, "
                f"d_R={self.d_R}, d_D={self.d_D}, k={self.k}, s0={self.s0}, r0={self.r0})")  # Use d_R
