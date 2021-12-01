import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta
from enum import Enum

class UpDownSpecification (Enum):
    TRADITIONAL = 1
    ALTERNATIVE = 2

class OptionType (Enum):
    EUROPEAN_CALL = 1
    AMERICAN_CALL = 2
    EUROPEAN_PUT = 3
    AMERICAN_PUT = 4


class Lattice_Node:
    def __init__(self, present_value, up, down, levels_outstanding, parent):
        self.parent = parent
        self.present_value = present_value
        if (levels_outstanding > 0):
            self.up_child = Lattice_Node(present_value*up, up, down, levels_outstanding - 1, self)
            self.down_child = Lattice_Node(present_value*down, up, down, levels_outstanding - 1, self)
        else:
            self.up_child = None
            self.down_child = None
    def calculate_european_call_price(self, strike_price, risk_neutral_probability, rate, delta_t):
        if (self.up_child == None and self.down_child == None):
            return max(self.present_value - strike_price, 0)
        else:
            return (((risk_neutral_probability)*(self.up_child.calculate_european_call_price(strike_price, risk_neutral_probability, rate, delta_t)) + (1 - risk_neutral_probability)*(self.down_child.calculate_european_call_price(strike_price, risk_neutral_probability, rate, delta_t)))*math.exp(-1*rate*delta_t))
    
    def calculate_american_call_price(self, strike_price, risk_neutral_probability, rate, delta_t):
        if (self.up_child == None and self.down_child == None):
            return max(self.present_value - strike_price, 0)
        else:
            return max((((risk_neutral_probability)*(self.up_child.calculate_american_call_price(strike_price, risk_neutral_probability, rate, delta_t)) + (1 - risk_neutral_probability)*(self.down_child.calculate_american_call_price(strike_price, risk_neutral_probability, rate, delta_t)))*math.exp(-1*rate*delta_t)), self.present_value - strike_price, 0)

    def calculate_european_put_price(self, strike_price, risk_neutral_probability, rate, delta_t):
        if (self.up_child == None and self.down_child == None):
            return max(strike_price - self.present_value, 0)
        else:
            return (((risk_neutral_probability)*(self.up_child.calculate_european_put_price(strike_price, risk_neutral_probability, rate, delta_t)) + (1 - risk_neutral_probability)*(self.down_child.calculate_european_put_price(strike_price, risk_neutral_probability, rate, delta_t)))*math.exp(-1*rate*delta_t))

    def calculate_american_put_price(self, strike_price, risk_neutral_probability, rate, delta_t):
        if (self.up_child == None and self.down_child == None):
            return max(strike_price - self.present_value, 0)
        else:
            return max((((risk_neutral_probability)*(self.up_child.calculate_american_put_price(strike_price, risk_neutral_probability, rate, delta_t)) + (1 - risk_neutral_probability)*(self.down_child.calculate_american_put_price(strike_price, risk_neutral_probability, rate, delta_t)))*math.exp(-1*rate*delta_t)), strike_price - self.present_value, 0)
 

class Black_Scholes_Merton_Equation:
    def __init__(self, specification, option, present_spot, strike_price, risk_free_rate, up, down, start_date, end_date, num_period, continuous_income_rate, volatility):


def main():

    # Traditional approach
    specification = UpDownSpecification.ALTERNATIVE
    option = OptionType.AMERICAN_CALL
    enddate = datetime(2020, 10, 1)
    startdate = datetime(2020, 1, 1)
    numperiod = 3
    time_delta = ((enddate - startdate).days/365)/numperiod
    volatility = 0.05
    risk_free_rate = 0.05
    spot_price = 115
    strike_price = 115
    continuous_income_rate = 0.06
    up = math.exp(volatility * math.sqrt(time_delta))
    down = math.exp(-1*volatility * math.sqrt(time_delta))


    tree = Binomial_Lattice_Tree(specification, option, spot_price, strike_price, risk_free_rate, up, down, startdate, enddate, numperiod, continuous_income_rate, volatility)



