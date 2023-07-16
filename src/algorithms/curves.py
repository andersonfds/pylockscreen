import numpy as np
from src.logger import Logger

def get_distance(power : float, rssi : float):
    return 10 ** ((power - rssi) / 20)

def progressive_increase(distances : np.array, logger : Logger):
    # This function will return true if the curve is increasing
    # It works by checking if the next value is larger than the previous value
    # If this is true for most of the ending values, the curve is increasing

    if len(distances) < 10:
        logger.log("Not enough data to determine curve")
        return False
    
    values = np.array([])
    previous_value = distances[0]

    for value in distances[1:]:
        values = np.append(values, value > previous_value)
        previous_value = value


    if len(values) < 5:
        return False

    return np.mean(values) > 0.5

def progressive_decrease(distances : np.array, logger : Logger):
    value = progressive_increase(distances, logger)

    if len(distances) < 10:
        logger.log("Not enough data to determine curve")
        return False
        
    return not value

def calculate_curve(distances : np.array, curve: str, logger : Logger):
    # when [distances] values get progressively smaller, the curve is decreasing
    # when [distances] values get progressively larger, the curve is increasing
    # when [distances] values are the same, the curve is flat

    if len(distances) < 10:
        logger.log("[INFO] Not enough data to determine curve")
        return False
    
    if curve == "decreasing":
        return progressive_decrease(distances, logger)

    elif curve == "increasing":
        return progressive_increase(distances, logger)
    
    elif curve == "flat":
        # check if mean is similar to average with a margin of 5
        average = np.mean(distances)
        mean = np.mean(distances)
        return mean - 5 < average < mean + 5
    
    else:
        raise Exception("Curve type not supported")