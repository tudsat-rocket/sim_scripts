import thermo

nitrous_oxide = thermo.chemical.Chemical('nitrous oxide')
nitrous_oxide.calculate(T=283, P=4e6)
print(nitrous_oxide.rho)
print(nitrous_oxide.phase)
