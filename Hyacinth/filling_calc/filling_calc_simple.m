m_final = 6.3; % kg
c = 2300; % J/kgK
delta_T = 25; %K
p_GSE = 55 *1e5; %Pa
rho = 880; % kg/m^3 at 5°C
delta_h = 210000; % J/kg
p_0 = 1*1e5; %Pa
A = pi * (0.0012/2)^2; % m^2


m_total = m_final*(1+(c*delta_T)/delta_h)

v = sqrt(2* (p_GSE-p_0)/rho) 

t = m_total/(rho*v*A)

volume_flow = v *A *3600


