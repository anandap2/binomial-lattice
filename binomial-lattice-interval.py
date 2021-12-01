import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta
from enum import Enum

class Payment:
    def __init__(self, time, amount, rate):
        self.time = time
        self.amount = amount
        self.rate = rate

class UpDownSpecification (Enum):
    TRADITIONAL = 1
    ALTERNATIVE = 2

class OptionType (Enum):
    EUROPEAN_CALL = 1
    AMERICAN_CALL = 2
    EUROPEAN_PUT = 3
    AMERICAN_PUT = 4

class Discrete_Payment_Node:
    def __init__(self, time, time_delta, periods_left, rate, payments):
        self.time = time
        value = 0
        for payment in payments:
            if (payment.time > time):
                value = value + math.exp(-1*rate*(payment.time - time))*payment.amount
        if (periods_left > 0):
            self.up_child = Discrete_Payment_Node(time + time_delta, time_delta, periods_left - 1, rate, payments)
            self.down_child = Discrete_Payment_Node(time + time_delta, time_delta, periods_left - 1, rate, payments)
        else:
            self.up_child = None
            self.down_child = None
        self.value = value



class Lattice_Node_Interval:
    def __init__(self, present_value, up, down, levels_outstanding, parent, paymentNode):
        self.parent = parent
        if (paymentNode != None):
            self.present_value = present_value + paymentNode.value
            next_up_value = (self.present_value - paymentNode.value)*up
            next_down_value = (self.present_value - paymentNode.value)*down
        else:
            self.present_value = present_value
            next_up_value = (self.present_value)*up
            next_down_value = (self.present_value)*down
        if (levels_outstanding > 0):
            if (paymentNode != None):
                self.up_child = Lattice_Node_Interval(next_up_value, up, down, levels_outstanding - 1, self, paymentNode.up_child)
                self.down_child = Lattice_Node_Interval(next_down_value, up, down, levels_outstanding - 1, self, paymentNode.down_child)
            else:
                self.up_child = Lattice_Node_Interval(present_value*up, up, down, levels_outstanding - 1, self, None)
                self.down_child = Lattice_Node_Interval(present_value*down, up, down, levels_outstanding - 1, self, None)
        else:
            self.up_child = None
            self.down_child = None
    def calculate_european_call_price(self, strike_price, risk_neutral_probability, rate, delta_t):
        if (self.up_child == None and self.down_child == None):
            self.option_value = max(self.present_value - strike_price, 0)
        else:
            self.option_value = (((risk_neutral_probability)*(self.up_child.calculate_european_call_price(strike_price, risk_neutral_probability, rate, delta_t)) + (1 - risk_neutral_probability)*(self.down_child.calculate_european_call_price(strike_price, risk_neutral_probability, rate, delta_t)))*math.exp(-1*rate*delta_t))
        return self.option_value
    
    def calculate_american_call_price(self, strike_price, risk_neutral_probability, rate, delta_t):
        if (self.up_child == None and self.down_child == None):
            self.option_value = max(self.present_value - strike_price, 0)
        else:
            self.option_value = max((((risk_neutral_probability)*(self.up_child.calculate_american_call_price(strike_price, risk_neutral_probability, rate, delta_t)) + (1 - risk_neutral_probability)*(self.down_child.calculate_american_call_price(strike_price, risk_neutral_probability, rate, delta_t)))*math.exp(-1*rate*delta_t)), self.present_value - strike_price, 0)
        return self.option_value

    def calculate_european_put_price(self, strike_price, risk_neutral_probability, rate, delta_t):
        if (self.up_child == None and self.down_child == None):
            self.option_value = max(strike_price - self.present_value, 0)
        else:
            self.option_value = (((risk_neutral_probability)*(self.up_child.calculate_european_put_price(strike_price, risk_neutral_probability, rate, delta_t)) + (1 - risk_neutral_probability)*(self.down_child.calculate_european_put_price(strike_price, risk_neutral_probability, rate, delta_t)))*math.exp(-1*rate*delta_t))
        return self.option_value

    def calculate_american_put_price(self, strike_price, risk_neutral_probability, rate, delta_t):
        if (self.up_child == None and self.down_child == None):
            self.option_value = max(strike_price - self.present_value, 0)
        else:
            self.option_value = max((((risk_neutral_probability)*(self.up_child.calculate_american_put_price(strike_price, risk_neutral_probability, rate, delta_t)) + (1 - risk_neutral_probability)*(self.down_child.calculate_american_put_price(strike_price, risk_neutral_probability, rate, delta_t)))*math.exp(-1*rate*delta_t)), strike_price - self.present_value, 0)
        return self.option_value

    def print_node_csv(self, parent_identifier, action, node_list):
        if (self.down_child != None and self.up_child != None):
            curr_identifer = parent_identifier + action if parent_identifier and action else 'Base'
            node = {
                "identifier": curr_identifer,
                "value": self.option_value,
                "spot_value": self.present_value,
                "parent": parent_identifier,
                "upChild": curr_identifer + "_U",
                "downChild": curr_identifer + "_D"
            }
            node_list.append(node)
            self.up_child.print_node_csv(curr_identifer, "_U", node_list)
            self.down_child.print_node_csv(curr_identifer, "_D", node_list)
        else:
            df = pd.DataFrame(node_list)
            df.to_csv('./lattice-output.csv', index=True)

class Binomial_Lattice_Tree_Interval:
    def __init__(self, specification, option, present_spot, strike_price, risk_free_rate, up, down, tenure, num_period, continuous_income_rate, volatility, paymentNodes):
        self.specification = specification
        self.option = option
        self.present_spot = present_spot
        self.strike_price = strike_price
        self.risk_free_rate = risk_free_rate
        self.up = up
        self.down = down
        self.tenure = tenure
        self.num_period = num_period
        self.continuous_income_rate = continuous_income_rate if continuous_income_rate else 0
        self.volatility = volatility
        self.paymentNodes = paymentNodes

        time_delta = self.tenure/self.num_period
        # self.tree = Lattice_Node_Interval(self.present_spot, self.up, self.down, self.num_period, None, self.paymentNodes)

        if (self.specification == UpDownSpecification.TRADITIONAL):
            self.risk_neutral_probability = ((math.exp((self.risk_free_rate - self.continuous_income_rate)*time_delta) - self.down)/(self.up - self.down))
        if (self.specification == UpDownSpecification.ALTERNATIVE):
            self.risk_neutral_probability = 0.5
            self.up = math.exp((self.risk_free_rate - self.continuous_income_rate - (self.volatility**2)/2)*time_delta + self.volatility*math.sqrt(time_delta))
            self.down = math.exp((self.risk_free_rate - self.continuous_income_rate - (self.volatility**2)/2)*time_delta - self.volatility*math.sqrt(time_delta))
        
        if (self.paymentNodes != None):
            self.tree = Lattice_Node_Interval(self.present_spot - self.paymentNodes.value, self.up, self.down, self.num_period, None, self.paymentNodes)
        else:
            self.tree = Lattice_Node_Interval(self.present_spot, self.up, self.down, self.num_period, None, self.paymentNodes)


        if (option == OptionType.EUROPEAN_CALL):
            print(self.tree.calculate_european_call_price(self.strike_price, self.risk_neutral_probability, self.risk_free_rate, time_delta))
        if (option == OptionType.EUROPEAN_PUT):
            print(self.tree.calculate_european_put_price(self.strike_price, self.risk_neutral_probability, self.risk_free_rate, time_delta))
        if (option == OptionType.AMERICAN_CALL):
            print(self.tree.calculate_american_call_price(self.strike_price, self.risk_neutral_probability, self.risk_free_rate, time_delta))
        if (option == OptionType.AMERICAN_PUT):
            print(self.tree.calculate_american_put_price(self.strike_price, self.risk_neutral_probability, self.risk_free_rate, time_delta))
        self.tree.print_node_csv(None, 0, [])
        self.compute_greeks()
    
    def compute_greeks(self):
        self.delta = (self.tree.up_child.option_value - self.tree.down_child.option_value)/(self.tree.up_child.present_value - self.tree.down_child.present_value)
        gamma_param1 = (self.tree.up_child.up_child.option_value - self.tree.up_child.down_child.option_value)/(self.tree.up_child.up_child.present_value - self.tree.up_child.down_child.present_value)
        gamma_param2 = (self.tree.up_child.down_child.option_value - self.tree.down_child.down_child.option_value)/(self.tree.up_child.down_child.present_value - self.tree.down_child.down_child.present_value)
        self.gamma = (gamma_param1 - gamma_param2)/(0.5 * (self.present_spot * self.up**2 - self.present_spot * self.down**2))
        self.theta = (self.tree.up_child.down_child.option_value - self.tree.option_value)/(2*self.tenure/self.num_period)
        self.theta = self.theta
        print('''
            delta: {0},
            gamma: {1},
            theta: {2}
        '''.format(self.delta, self.gamma, self.theta))
def main():

    # Traditional approach
    specification = UpDownSpecification.ALTERNATIVE
    option = OptionType.EUROPEAN_PUT
    tenure = 1
    numperiod = 4
    time_delta = tenure/numperiod
    volatility = 0.15
    risk_free_rate = 0.005
    spot_price = 1.65
    strike_price = 1.65
    continuous_income_rate = 0.02
    up = math.exp(volatility * math.sqrt(time_delta))
    down = math.exp(-1*volatility * math.sqrt(time_delta))

    payments = [Payment(1, 0.03*spot_price, risk_free_rate)]
    paymentNode = None # Discrete_Payment_Node(0, time_delta, numperiod, risk_free_rate, payments)
    tree = Binomial_Lattice_Tree_Interval(specification, option, spot_price, strike_price, risk_free_rate, up, down, tenure, numperiod, continuous_income_rate, volatility, paymentNode)

if __name__ == "__main__":
    main()