# Description: Ein einfaches Wachstumsmodell für Pflanzen nach dem Gompertz-Modell
# Parameter
W_max = 30  # Maximale Höhe in cm (Beispiel: Römersalat)
k = 0.1     # Wachstumsrate
t_0 = 5     # Startzeitpunkt des Wachstums
n = 2       # Formparameter
T = 700      # Simulationszeitraum in Tagen
e = 2.71828 # Eulersche Zahl

# Initialisierung
t = t_0
W_total = 0
delta_t = 1  # Zeitschritt (ein Tag)

# Simulation über T Tage
for day in range(T):
    # Berechnung der Ableitung (Wachstumsrate)
    growth_rate = W_max * n * (1 - e**(-k * (t - t_0)))**(n - 1) * k * e**(-k * (t - t_0))
    
    # Update der Gesamthöhe
    W_total += growth_rate * delta_t
    
    # Zeit fortschreiten lassen
    t += delta_t
    
    # Ausgabe der Höhe für den aktuellen Tag
    print(f"Tag {day + 1}: Höhe = {W_total:.2f} cm")

# Gesamthöhe nach T Tagen
print(f"Gesamthöhe nach {T} Tagen: {W_total:.2f} cm")
