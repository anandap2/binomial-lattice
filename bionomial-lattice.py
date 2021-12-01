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
 

class Binomial_Lattice_Tree:
    def __init__(self, specification, option, present_spot, strike_price, risk_free_rate, up, down, start_date, end_date, num_period, continuous_income_rate, volatility):
        self.specification = specification
        self.option = option
        self.present_spot = present_spot
        self.strike_price = strike_price
        self.risk_free_rate = risk_free_rate
        self.up = up
        self.down = down
        self.start_date = start_date
        self.end_date = end_date
        self.num_period = num_period
        self.continuous_income_rate = continuous_income_rate if continuous_income_rate else 0
        self.volatility = volatility

        time_delta = ((self.end_date - self.start_date).days/365)/self.num_period
        self.tree = Lattice_Node(self.present_spot, self.up, self.down, self.num_period, None)

        if (self.specification == UpDownSpecification.TRADITIONAL):
            self.risk_neutral_probability = ((math.exp((self.risk_free_rate - self.continuous_income_rate)*time_delta) - self.down)/(self.up - self.down))
        if (self.specification == UpDownSpecification.ALTERNATIVE):
            self.risk_neutral_probability = 0.5
            self.up = math.exp((self.risk_free_rate - self.continuous_income_rate - (self.volatility**2)/2)*time_delta + self.volatility*math.sqrt(time_delta))
            self.down = math.exp((self.risk_free_rate - self.continuous_income_rate - (self.volatility**2)/2)*time_delta - self.volatility*math.sqrt(time_delta))
        
        self.tree = Lattice_Node(self.present_spot, self.up, self.down, self.num_period, None)

        if (option == OptionType.EUROPEAN_CALL):
            print(self.tree.calculate_european_call_price(self.strike_price, self.risk_neutral_probability, self.risk_free_rate, time_delta))
        if (option == OptionType.EUROPEAN_PUT):
            print(self.tree.calculate_european_put_price(self.strike_price, self.risk_neutral_probability, self.risk_free_rate, time_delta))
        if (option == OptionType.AMERICAN_CALL):
            print(self.tree.calculate_american_call_price(self.strike_price, self.risk_neutral_probability, self.risk_free_rate, time_delta))
        if (option == OptionType.AMERICAN_PUT):
            print(self.tree.calculate_american_put_price(self.strike_price, self.risk_neutral_probability, self.risk_free_rate, time_delta))
    
    def create_tree(self):
        time_delta = ((self.end_date - self.start_date).days/365)/self.num_period
        risk_neutral_probability = ((math.exp(self.risk_free_rate*time_delta) - self.down)/(self.up - self.down))

        self.tree = Lattice_Node(self.present_spot, self.up, self.down, self.num_period, None)
        print(self.tree.calculate_american_put_price(self.strike_price, risk_neutral_probability, self.risk_free_rate, time_delta))

    def create_tree_continuous_rate(self, income_rate):
        time_delta = ((self.end_date - self.start_date).days/365)/self.num_period
        risk_neutral_probability = ((math.exp((self.risk_free_rate - income_rate)*time_delta) - self.down)/(self.up - self.down))

        self.tree = Lattice_Node(self.present_spot, self.up, self.down, self.num_period, None)
        print(self.tree.calculate_european_call_price(self.strike_price, risk_neutral_probability, self.risk_free_rate, time_delta))

    def create_tree_alternative_continuous_rate(self, income_rate):
        time_delta = ((self.end_date - self.start_date).days/365)/self.num_period
        risk_neutral_probability = 0.5


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





if __name__ == "__main__":
    main()