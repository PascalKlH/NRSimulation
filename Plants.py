# Pests
APHIDS = {
    "name": "Aphids",
    "period": "04-01:11-01",
    "majorperiod": "01-05;30-06",
    "impact": 3,
    "EndangeredCrop": "RedCabage",
    "min_temperature": 10,
    "max_temperature": 35,
}
THRIPS = {
    "name": "Thrips",
    "period": "06-10:08-31",
    "majorperiod": "15.07-15.08",
    "impact": 3,
    "EndangeredCrop": "WhiteCabage",
    "min_temperature": 10,
    "max_temperature": 35,
}
CABBAGEWHIEBUTTERFLY = {
    "name": "Cabbage White Butterfly",
    "period": "05-01:09-15",
    "majorperiod": "01.06-31.07",
    "impact": 2,
    "min_temperature": 10,
    "max_temperature": 35,
}
CABBAGEFLY = {
    "name": "Cabbagefly",
    "period": "04-15:05-15",
    "period2": "06-15:10-15",
    "majorperiod": "15-04,15-05",
    "impact": 3,
    "min_temperature": 10,
    "max_temperature": 35,
}
# Illnesses
BACTERIALSOFTROT = {
    "name": "Bacterial soft rot",
    "period": "05-01:10-01",
    "impact": 2,
    "min_temperature": 20,
    "max_temperature": 30,
}
LEAFSPOT = {
    "name": "Leaf spot",
    "period": "05-01:10-01",
    "impact": 1,
    "min_temperature": 20,
    "max_temperature": 30,
}
# Falscher Mehltau
MILDEW = {
    "name": " Mildew",
    "period": "05-01:10-01",
    "majorperiod": "01-05:01-08",
    "impact": 2,
    "min_temperature": 15,
    "max_temperature": 25,
}
# Kohlhernie
CLUBROOT = {
    "name": "Clubroot",
    "period": "05-01:10-01",
    "majorperiod": "01-05:01-08",
    "impact": 3,
    "min_temperature": 18,
    "max_temperature": 25,
}
# Ringfleckenkrankheit
RINGSPOTDISEASE = {
    "name": " Ring spot disease",
    "period": "05-01:10-01",
    "majorperiod": "01-05:01-08",
    "impact": 3,
    "min_temperature": 15,
    "max_temperature": 25,
}
CARROT = {
    "name": "Carrot",
    "stage1": {"Kc": 0.3, "depth": 30, "BBCH": 9, "radius": 0.5},
    "stage2": {"Kc": 0.6, "depth": 30, "BBCH": 15, "radius": 4},
    "stage3": {"Kc": 0.8, "depth": 60, "BBCH": 43, "radius": 10},
    "stage4": {"Kc": 1.0, "depth": 60, "BBCH": 65, "radius": 15},
    "is_weed": False,
    "needs_irrigation": True,
    "optimal_soil": "Sand",
    "growth_speed": 10,  ##0.0291666, #bbch per hour
    "earliest_harvest": 41,  # BBCH to harvest
    "latest_harvest": 49,  # BBCH to harvest
    "max_temperature": 25,
    "min_temperature": -15,
    "earliest_sowing_time": 30,
    "latest_sowing_time": 100,
    "min_growth_temperature": 4,
    "max_growth_temperature": 30,
    "optimal_growth_temperature": 20,
    "optimal_water": 40,
    "row_distance": 20,
    "plant_distance": 20,
    "optimal_ph": 6,
    "harvest_yield": 0.1,  # Kg/plant
}
ASAINLETTUCE = {
    "name": "Asainlettuce",
    "stage1": {"Kc": 0.3, "depth": 30, "BBCH": 9},
    "stage2": {"Kc": 0.6, "depth": 30, "BBCH": 15},
    "stage3": {"Kc": 0.8, "depth": 60, "BBCH": 43},
    "stage4": {"Kc": 1.0, "depth": 60, "BBCH": 65},
    "is_weed": False,
    "needs_irrigation": True,
    "optimal_soil": "Sand",
    "max_temperature": 25,
    "min_temperature": -15,
    "earliest_sowing_time": 30,
    "latest_sowing_time": 100,
    "min_growth_temperature": 4,
    "max_growth_temperature": 30,
    "optimal_growth_temperature": 20,
    "row_distance": 15,
    "plant_distance": 3,
    "optimal_ph": 6,
}
REDCABAAGE = {
    "name": "Redcabbage",
    "stage1": {"Kc": 0.3, "depth": 30, "BBCH": 9},
    "stage2": {"Kc": 0.6, "depth": 30, "BBCH": 15},
    "stage3": {"Kc": 0.8, "depth": 60, "BBCH": 43},
    "stage4": {"Kc": 1.0, "depth": 60, "BBCH": 65},
    "is_weed": False,
    "needs_irrigation": True,
    "optimal_soil": "Sand",
    "max_temperature": 25,
    "min_temperature": -15,
    "earliest_sowing_time": 30,
    "latest_sowing_time": 100,
    "min_growth_temperature": 4,
    "max_growth_temperature": 30,
    "optimal_growth_temperature": 20,
    "row_distance": 15,
    "plant_distance": 3,
    "optimal_ph": 6,
}
WHITHECABBAGE = {
    "name": "Whitecabbage",
    "stage1": {"Kc": 0.3, "depth": 30, "BBCH": 9},
    "stage2": {"Kc": 0.6, "depth": 30, "BBCH": 15},
    "stage3": {"Kc": 0.8, "depth": 60, "BBCH": 43},
    "stage4": {"Kc": 1.0, "depth": 60, "BBCH": 65},
    "is_weed": False,
    "needs_irrigation": True,
    "optimal_soil": "Sand",
    "max_temperature": 25,
    "min_temperature": -15,
    "earliest_sowing_time": 30,
    "latest_sowing_time": 100,
    "min_growth_temperature": 4,
    "max_growth_temperature": 30,
    "optimal_growth_temperature": 20,
    "row_distance": 15,
    "plant_distance": 3,
    "optimal_ph": 6,
}
BAYBLEAFSPINACH = {
    "name": "Baybleafspinach",
    "stage1": {"Kc": 0.3, "depth": 30, "BBCH": 9},
    "stage2": {"Kc": 0.6, "depth": 30, "BBCH": 15},
    "stage3": {"Kc": 0.8, "depth": 60, "BBCH": 43},
    "stage4": {"Kc": 1.0, "depth": 60, "BBCH": 65},
    "is_weed": False,
    "needs_irrigation": True,
    "optimal_soil": "Sand",
    "max_temperature": 25,
    "min_temperature": -15,
    "earliest_sowing_time": 30,
    "latest_sowing_time": 100,
    "min_growth_temperature": 4,
    "max_growth_temperature": 30,
    "optimal_growth_temperature": 20,
    "row_distance": 15,
    "plant_distance": 3,
    "optimal_ph": 6,
}
FRENCHHERB = {  ##Franzosenkraut
    "name": "Frenchherb",
    "stage1": {"Kc": 0.3, "depth": 30, "BBCH": 9, "radius": 0.5},
    "stage2": {"Kc": 0.6, "depth": 30, "BBCH": 15, "radius": 4},
    "stage3": {"Kc": 0.8, "depth": 60, "BBCH": 43, "radius": 10},
    "stage4": {"Kc": 1.0, "depth": 60, "BBCH": 65, "radius": 15},
    "is_weed": True,
    "impact": "Bad",
    "optimal_soil": "sand",
    "growth_speed": 1.2,  # 0.0391666, #bbch per hour
    "optimal_water": 45,
    "optimal_ph": 6,
    "max_high": 80,  # cm
    "max_width": 15,  # Radius des Beschatteten Bereichs
    "waterusage": 0.125,  # mm/Stunde
    "earliest_appearance": "03-01",
    "latest_appearance": "11-30",
    "growth_period": 75,  # days
    "optimal_growth_temperature": 20,
    "min_growth_temperature": 5,
    "max_growth_temperature": 30,
}
JACOBSRAGWORT = {  ##Jakobs-Greiskraut
    "name": "Jacobsragwort",
    "stage1": {"Kc": 0.3, "depth": 30, "BBCH": 9, "radius": 0.5},
    "stage2": {"Kc": 0.6, "depth": 30, "BBCH": 15, "radius": 4},
    "stage3": {"Kc": 0.8, "depth": 60, "BBCH": 43, "radius": 10},
    "stage4": {"Kc": 1.0, "depth": 60, "BBCH": 65, "radius": 15},
    "is_weed": True,
    "impact": "Bad",
    "optimal_water": 30,
    "optimal_soil": "sand",
    "growth_speed": 1.5,  # 0.021666, #bbch per hour
    "optimal_ph": 6,
    "max_high": 80,  # cm
    "max_width": 15,  # Radius des Beschatteten Bereichs
    "waterusage": 0.125,  # mm/Stunde
    "earliest_appearance": "03-01",
    "latest_appearance": "11-30",
    "growth_period": 75,  # days
    "optimal_growth_temperature": 20,
    "min_growth_temperature": 5,
    "max_growth_temperature": 30,
}
THISTLE = {  ##Distel
    "name": "Thistle",
    "stage1": {"Kc": 0.3, "depth": 30, "BBCH": 9, "radius": 0.5},
    "stage2": {"Kc": 0.6, "depth": 30, "BBCH": 15, "radius": 4},
    "stage3": {"Kc": 0.8, "depth": 60, "BBCH": 43, "radius": 10},
    "stage4": {"Kc": 1.0, "depth": 60, "BBCH": 65, "radius": 15},
    "is_weed": True,
    "impact": "Bad",
    "optimal_soil": "sand",
    "growth_speed": 1.2,  # 0.0391666, #bbch per hour
    "optimal_water": 45,
    "optimal_ph": 6,
    "max_high": 80,  # cm
    "max_width": 15,  # Radius des Beschatteten Bereichs
    "waterusage": 0.125,  # mm/Stunde
    "earliest_appearance": "03-01",
    "latest_appearance": "11-30",
    "growth_period": 75,  # days
    "optimal_growth_temperature": 20,
    "min_growth_temperature": 5,
    "max_growth_temperature": 30,
}
COUCHGRASS = {  ##Quecke
    "name": "Couchgrass",
    "stage1": {"Kc": 0.3, "depth": 30, "BBCH": 9, "radius": 0.5},
    "stage2": {"Kc": 0.6, "depth": 30, "BBCH": 15, "radius": 4},
    "stage3": {"Kc": 0.8, "depth": 60, "BBCH": 43, "radius": 10},
    "stage4": {"Kc": 1.0, "depth": 60, "BBCH": 65, "radius": 15},
    "is_weed": True,
    "impact": "Bad",
    "optimal_soil": "sand",
    "growth_speed": 1.2,  # 0.0391666, #bbch per hour
    "optimal_water": 45,
    "optimal_ph": 6,
    "max_high": 80,  # cm
    "max_width": 15,  # Radius des Beschatteten Bereichs
    "waterusage": 0.125,  # mm/Stunde
    "earliest_appearance": "03-01",
    "latest_appearance": "11-30",
    "growth_period": 75,  # days
    "optimal_growth_temperature": 20,
    "min_growth_temperature": 5,
    "max_growth_temperature": 30,
}
CHICKWEED = {  ##Voegelmiere
    "name": "Chickweed",
    "stage1": {"Kc": 0.3, "depth": 30, "BBCH": 9, "radius": 0.5},
    "stage2": {"Kc": 0.6, "depth": 30, "BBCH": 15, "radius": 4},
    "stage3": {"Kc": 0.8, "depth": 60, "BBCH": 43, "radius": 10},
    "stage4": {"Kc": 1.0, "depth": 60, "BBCH": 65, "radius": 15},
    "is_weed": True,
    "impact": "Bad",
    "optimal_soil": "sand",
    "growth_speed": 1.2,  # 0.0391666, #bbch per hour
    "optimal_water": 45,
    "optimal_ph": 6,
    "max_high": 80,  # cm
    "max_width": 15,  # Radius des Beschatteten Bereichs
    "waterusage": 0.125,  # mm/Stunde
    "earliest_appearance": "03-01",
    "latest_appearance": "11-30",
    "growth_period": 75,  # days
    "optimal_growth_temperature": 20,
    "min_growth_temperature": 5,
    "max_growth_temperature": 30,
}

REPORT = {  ##Melde
    "name": "Report",
    "stage1": {"Kc": 0.3, "depth": 30, "BBCH": 9, "radius": 0.5},
    "stage2": {"Kc": 0.6, "depth": 30, "BBCH": 15, "radius": 4},
    "stage3": {"Kc": 0.8, "depth": 60, "BBCH": 43, "radius": 10},
    "stage4": {"Kc": 1.0, "depth": 60, "BBCH": 65, "radius": 15},
    "is_weed": True,
    "impact": "Bad",
    "optimal_soil": "sand",
    "growth_speed": 1.2,  # 0.0391666, #bbch per hour
    "optimal_water": 45,
    "optimal_ph": 6,
    "max_high": 80,  # cm
    "max_width": 15,  # Radius des Beschatteten Bereichs
    "waterusage": 0.125,  # mm/Stunde
    "earliest_appearance": "03-01",
    "latest_appearance": "11-30",
    "growth_period": 75,  # days
    "optimal_growth_temperature": 20,
    "min_growth_temperature": 5,
    "max_growth_temperature": 30,
}

SAND ={
    "name": "Sand",
    "nkf": 9,
    "fk": 15,
    "pwp": 1,
    "category": "light"
}
SLIGHTLYLOAMYSAND ={
    "name": "Slightly Loamy Sand",
    "nkf": 13,
    "fk": 15,
    "pwp": 1,
    "category": "light"

}
STRONGLOAMYSAND ={
    "name": "Strong Loamy Sand",
    "nkf": 16,
    "fk": 15,
    "pwp": 1,
    "category": "medium"
}
SANDYLOAM ={
    "name": "Sandy Loam",
    "nkf": 19,
    "fk": 40,
    "pwp": 10,
    "category": "medium"
}
SILTYCLAY ={
    "name": "Silty Clay",
    "nkf": 22,
    "fk": 40,
    "pwp": 10,
    "category": "medium"
}
CLAYEYLOAM ={
    "name": "Clayey Loam",
    "nkf": 17,
    "fk": 40,
    "pwp": 10,
    "category": "heavy"
}
CLAY ={
    "name": "Clay",
    "nkf": 14,
    "fk": 60,
    "pwp": 25,
    "category": "heavy"
}
PEAT ={
    "name": "Peat",
    "nkf": 30,
    "fk": 60,
    "pwp": 25,
    "category": "heavy"
}
