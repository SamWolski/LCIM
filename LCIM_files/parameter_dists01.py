## definitions of pdf functions for parameter drawing
## based on parameters for IDM

# acceleration (alpha)
acc_std = 0.2#0.02
# acceleration_scale = 1.
acceleration_range = (0.6, 1.1)
acceleration_peak = 0.73
acceleration_pdf_object = sp.stats.truncnorm((-acceleration_peak+acceleration_range[0])/acc_std, (acceleration_range[1]-acceleration_peak)/acc_std, loc = acceleration_peak, scale = acc_std)
def generate_acceleration():
    return 1.5#0.73
# 	return acceleration_pdf_object.rvs(size = 1)[0]
def generate_braking():
    return 1.67
    
def generate_overbraking_factor():
	return 1e5#5.0
# braking threshold velocity
bth_std = 1.0
bth_range = (1.0/3.6, 3.5/3.6)
bth_peak = 2.5/3.6
bth_pdf_object = sp.stats.truncnorm((-bth_peak+bth_range[0])/bth_std, (bth_range[1] - bth_peak)/bth_std, loc = bth_peak, scale = bth_std)
def generate_braking_threshold():
	return 0.0
# 	return bth_pdf_object.rvs(size = 1)[0]
    
# desired velocity (u) 
desired_velocity_std = 0.1*60./3.6 
desired_velocity_range = (45./3.6, 75./3.6)
desired_velocity_mid = 60./3.6
desired_velocity_pdf_object = sp.stats.truncnorm((-desired_velocity_mid+desired_velocity_range[0])/desired_velocity_std, (desired_velocity_range[1]-desired_velocity_mid)/desired_velocity_std, loc = desired_velocity_mid, scale = desired_velocity_std)
def generate_desired_velocity():
    return 60./3.6
#     return ((70. - 10.)/3.6)*np.random.random() + 10./3.6
# 	return desired_velocity_pdf_object.rvs(size = 1)[0] 
def generate_car_length():
    return 5.0
def generate_safe_time_headway():
    return 1.2#1.6
def generate_jam_distance():
    return (2.0, 0.0) #(2.0, 0.0)
def generate_reaction_time():
    return 10
def generate_joining_braking_factor():
	return 1.0#0.5
def generate_continuation_factor():
	return 0.3
##