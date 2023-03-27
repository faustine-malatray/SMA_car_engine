# !/usr/bin/env python 3

from arguments.Comparison import Comparison
from arguments.CoupleValue import CoupleValue
from preferences.Value import Value
from preferences.Preferences import Preferences


class Argument:
    # Argument class.
    # The class implements an argument used during the interaction.InterruptedError

    # attr:
    #     decision:
    #     item:
    #     comparison_list:
    #     couple_value_list:

    def __init__(self, boolean_decision, item):
        self.decision = boolean_decision
        self.item = item
        self.comparison_list = []
        self.couple_values_list = []

    def add_premiss_comparison(self, criterion_name_1, criterion_name_2):
        # first arg is supposed to be best_criterion
        # second arg is supposed to be worst_criterion
        # we could use item.get_score() but need preference and so an agent
        comparaison = Comparison(criterion_name_1, criterion_name_2)
        self.comparison_list.append(comparaison)
        # self.comparison_list.append((criterion_name_1,criterion_name_2))

    def add_premiss_couple_values(self, criterion_name, value):
        couplevalue = CoupleValue(criterion_name, value)
        self.couple_values_list.append(couplevalue)
        # self.couple_values_list.append((criterion_name,value))

    def List_supporting_proposal(self, item, preferences):
        res = []
        for criteria in preferences.get_criterion_name_list():
            if (preferences.get_value(item, criteria) == Value.GOOD) or (preferences.get_value(item, criteria) == Value.VERY_GOOD):
                res.append(criteria)
        return res

    def List_attacking_proposal(self, item, preferences):
        res = []
        for criteria in preferences.get_criterion_name_list():
            if (preferences.get_value(item, criteria) == Value.BAD) or (preferences.get_value(item, criteria) == Value.VERY_BAD):
                res.append(criteria)
        return res
