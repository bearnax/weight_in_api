

def weight_conversion(mass, units):
    if units == "lbs":
        return mass * 14.5833
    elif units == "kg": 
        return mass * 32.151
    else:
        return 0



def price_by_weight(mass, price):
    """ Take the mass in troy ounces and return a computed price
    """

    return mass * price