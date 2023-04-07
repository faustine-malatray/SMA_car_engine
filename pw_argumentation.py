from mesa import Model
from mesa.time import RandomActivation, BaseScheduler
from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative
from communication.preferences.Item import Item
from communication.preferences.Preferences import Preferences
from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Value import Value
from communication.arguments.Argument import Argument

#!/usr/bin/env python3

import random


##################################
###### ARGUMENT ##################
##################################


class ArgumentAgent(CommunicatingAgent):
    """ArgumentAgent which inherit from CommunicatingAgent ."""

    def __init__(self, unique_id, model, name, preferences):
        super().__init__(unique_id, model, name)
        self.preference = Preferences()
        self.generate_preferences(preferences)
        self.preference_dict = preferences

    def step(self):
        new_messages = set(self.get_new_messages())

        if new_messages:
            new_argue = new_messages.intersection(
                set(self.get_messages_from_performative(
                    MessagePerformative.ARGUE))
            )
            if new_argue:
                for mess in new_argue:
                    # self.get_model().update_step()
                    other_agent = mess.get_exp()
                    item, previous_premise = self.argument_parsing(
                        mess.get_content())
                    new_premise, conclusion = self.update_argument(
                        item, previous_premise, other_agent)
                    if conclusion:
                        self.send_specific_message(
                            mess, MessagePerformative.ACCEPT, rebutal=True)
                    else:
                        self.send_specific_message(
                            mess, MessagePerformative.ARGUE, rebutal=True, premise=new_premise)

            new_ask_why = new_messages.intersection(
                set(self.get_messages_from_performative(
                    MessagePerformative.ASK_WHY))
            )
            if new_ask_why:
                for mess in new_ask_why:
                    self.send_specific_message(
                        mess, MessagePerformative.ARGUE)

            # if on a reçu un commit
            new_commit = new_messages.intersection(
                set(self.get_messages_from_performative(
                    MessagePerformative.COMMIT))
            )
            if new_commit:
                for mess in new_commit:
                    item = mess.get_content()
                    if item in self.get_preference_dict().keys():
                        self.send_specific_message(
                            mess, MessagePerformative.COMMIT)
                        self.remove_item(item)

            # if on a reçu un accept
            new_accept = new_messages.intersection(
                set(self.get_messages_from_performative(
                    MessagePerformative.ACCEPT))
            )
            if new_accept:
                for mess in new_accept:
                    item = mess.get_content()
                    if item in self.get_preference_dict().keys():
                        self.send_specific_message(
                            mess, MessagePerformative.COMMIT)
                        self.remove_item(item)

            # if on a reçu un propose
            new_propose = new_messages.intersection(
                set(self.get_messages_from_performative(
                    MessagePerformative.PROPOSE))
            )
            if new_propose:
                for mess in new_propose:
                    is_in_10 = self.get_preference().is_item_among_top_10_percent(
                        mess.get_content(), list(self.get_preference_dict().keys())
                    )
                    if is_in_10:
                        self.send_specific_message(
                            mess, MessagePerformative.ACCEPT)
                    else:
                        self.send_specific_message(
                            mess, MessagePerformative.ASK_WHY)

        else:
            others = []
            for agent in self.get_model().get_agents():
                if agent != self:
                    others.append(agent)
            other = random.choice(others)
            proposition = self.get_preference().most_preferred(self.get_item_list())
            message = Message(self.get_name(), other.get_name(),
                              MessagePerformative.PROPOSE, proposition)
            self.get_model().update_step()
            print(str(self.get_model().get_step()) + " : " + message.__str__())
            self.send_message(message)

    def get_preference(self):
        return self.preference

    def get_preference_dict(self):
        return self.preference_dict

    def get_model(self):
        return self.model

    def remove_item(self, item):
        self.get_preference_dict().pop(item)
        self.get_preference().remove_item(item)

    def generate_preferences(self, List_items):
        # supposons une structure de preference:
        # {item1:{crit1:value1,
        #         crit2:val2...},
        #  item2: ...,
        # "crit_order": [c1, ci, ]}
        # where the agents preferes c1 > ci ...
        pref = Preferences()
        pref.set_criterion_order_preference(List_items["crit_order"])
        List_items.pop("crit_order")
        for item in List_items:
            pref.set_criterion_name_list(List_items[item].keys())
            for criteria in List_items[item]:
                pref.add_criterion_value(
                    CriterionValue(item, criteria, List_items[item][criteria])
                )
        self.preference = pref

    def get_item_list(self):
        item_list = self.get_preference_dict().keys()
        return item_list

    def send_specific_message(self, message_received, performative, proposition=None, rebutal=False, premise=None):
        sender = message_received.get_exp()
        content = message_received.get_content()
        if performative.__str__() == "PROPOSE":
            if proposition:
                new_content = proposition
        elif performative.__str__() == "ACCEPT":
            if rebutal:
                new_content = content.split(' <- ')[0]
            else:
                new_content = content
        elif performative.__str__() == "ASK_WHY":
            new_content = content
        elif performative.__str__() == "COMMIT":
            new_content = content
        elif performative.__str__() == "ARGUE":
            if rebutal and premise:
                # premise are the new arguments used
                new_content = premise
            else:
                arg = self.support_proposal(content)
                new_content = arg.__str__()
        message = Message(self.get_name(), sender, performative, new_content)
        self.send_message(message)
        self.get_model().update_step()
        print(str(self.get_model().get_step()) + " : " + message.__str__())

    def support_proposal(self, item):
        """
        Used when the agent receives "ASK_WHY" after having proposed an item
        :param item: str - name of the item which was proposed
        :return: string - the strongest supportive argument
        """
        arg = Argument(False, item)
        proposals = arg.List_supporting_proposal(item, self.get_preference())
        best_criteria = random.choice([argu for argu in proposals if self.get_preference().get_value(item, argu).value ==
                                       max([self.get_preference().get_value(item, i).value for i in proposals])])
        arg.add_premiss_couple_values(
            best_criteria, self.get_preference().get_value(item, best_criteria)
        )
        return arg

    def argument_parsing(self, argument_str):
        item = None
        if len(argument_str.split(" <- ")) > 1:
            # a new argument was given
            item_name, arguments = argument_str.split(" <- ")
        else:
            # its a refusal
            item_name, arguments = argument_str.split(" , ")
            item_name = item_name[4:]
        for i in self.get_item_list():
            if i.__str__() == item_name:
                item = i
                break
        premisces = arguments.split(", ")
        return [item, premisces]

    def update_argument(self, item, premisces, other_agent_name):
        premisce = premisces[0]
        if len(premisce.split(" = ")) > 1:
            criteria, value = premisce.split(" = ")
        elif len(premisce.split(" > ")) > 1:
            criteria, value = premisce.split(" > ")
        print(criteria)
        print(value)
        criteria, value = self.get_criteria_from_name(
            criteria), self.get_value_from_name(value)
        # The criterion is not important for him (regarding his order)
        # On suppose qu'il n'est pas important s'il est dans la seconde moitié des critères selon l'ordre de préférence de l'agent
        if criteria in self.get_preference().get_criterion_order_preference()[-len(CriterionName):]:
            return ["not "+item.get_name()+" , because 2", False]
        # Its local value for the item is lower than the one of the other agent on the considered criteria
        other_agent = self.get_model().agent_from_string(other_agent_name)
        if self.get_preference().get_value(item, criteria).value < other_agent.get_preference().get_value(item, criteria).value:
            return ["not "+item.get_name()+" , because 2", False]
        # He prefers another item and he can defend it by an argument with a better value on the same criterion.
        return [None, True]

    def get_criteria_from_name(self, criteria_name):
        for crit in CriterionName:
            if crit.__str__() == criteria_name:
                return crit

    def get_value_from_name(self, value_name):
        for val in Value:
            if val.__str__() == value_name:
                return val


##################################
###### MODEL #####################
##################################


class ArgumentModel(Model):
    """ArgumentModel which inherit from Model ."""

    def __init__(self):
        super().__init__()
        # self.schedule = BaseScheduler(self)
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)
        # To be completed
        #
        # a = ArgumentAgent (id , " agent_name ")
        # a. generate_preferences ( preferences )
        # self . schedule .add(a)
        # ...
        self.running = True
        self.current_step = 0

    def step(self):
        self.__messages_service.dispatch_messages()
        self.schedule.step()

    def get_step(self):
        return self.current_step

    def update_step(self):
        self.current_step += 1

    def get_agents(self):
        return self.schedule.agents

    def agent_from_string(self, name):
        for agent in self.get_agents():
            if agent.get_name() == name:
                return agent
        return None


##################################
###### RUN THE MODEL #############
##################################
if __name__ == "__main__":
    # Init model and agents
    argument_model = ArgumentModel()

    # Objects
    diesel_engine = Item("Diesel Engine", "A super cool diesel engine")
    electric_engine = Item("Electric Engine", "A very quiet engine")

    # Create preference system for A1
    A1 = {
        diesel_engine: {
            CriterionName.PRODUCTION_COST: Value.VERY_GOOD,
            CriterionName.ENVIRONMENT_IMPACT: Value.VERY_BAD,
            CriterionName.CONSUMPTION: Value.GOOD,
            CriterionName.DURABILITY: Value.VERY_GOOD,
            CriterionName.NOISE: Value.BAD,
        },
        electric_engine: {
            CriterionName.PRODUCTION_COST: Value.BAD,
            CriterionName.ENVIRONMENT_IMPACT: Value.VERY_GOOD,
            CriterionName.CONSUMPTION: Value.VERY_BAD,
            CriterionName.DURABILITY: Value.GOOD,
            CriterionName.NOISE: Value.VERY_GOOD,
        },
        "crit_order": [CriterionName.PRODUCTION_COST, CriterionName.ENVIRONMENT_IMPACT, CriterionName.CONSUMPTION, CriterionName.DURABILITY, CriterionName.NOISE]
    }

    # System preference for A2
    A2 = {
        diesel_engine: {
            CriterionName.PRODUCTION_COST: Value.GOOD,
            CriterionName.ENVIRONMENT_IMPACT: Value.BAD,
            CriterionName.CONSUMPTION: Value.GOOD,
            CriterionName.DURABILITY: Value.VERY_BAD,
            CriterionName.NOISE: Value.VERY_BAD,
        },
        electric_engine: {
            CriterionName.PRODUCTION_COST: Value.GOOD,
            CriterionName.ENVIRONMENT_IMPACT: Value.BAD,
            CriterionName.CONSUMPTION: Value.BAD,
            CriterionName.DURABILITY: Value.VERY_GOOD,
            CriterionName.NOISE: Value.VERY_GOOD,
        },
        "crit_order": [CriterionName.ENVIRONMENT_IMPACT, CriterionName.NOISE, CriterionName.PRODUCTION_COST,  CriterionName.CONSUMPTION, CriterionName.DURABILITY]
    }

    # Create the Buyer and the seller
    Buyer = ArgumentAgent(1, argument_model, "Buyer", A1)
    Seller = ArgumentAgent(2, argument_model, "Seller", A2)

    # add au scheduler
    print(f"L'agent {Buyer.get_name()} a été créé")
    argument_model.schedule.add(Buyer)
    print(f"L'agent {Seller.get_name()} a été créé")
    argument_model.schedule.add(Seller)

    step = 0
    while step < 10:
        argument_model.step()
        step += 1
