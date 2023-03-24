from mesa import Model
from mesa . time import RandomActivation
from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative
from communication.preferences.Item import Item
from communication.preferences.Preferences import Preferences
from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Value import Value

#!/usr/bin/env python3

import random


##################################
###### ARGUMENT ##################
##################################


class ArgumentAgent(CommunicatingAgent):
    """ ArgumentAgent which inherit from CommunicatingAgent .
    """

    def __init__(self, unique_id, model, name, preferences):
        super().__init__(unique_id, model, name)
        self.preference = self.generate_preferences(preferences)
        self.preference_dict = preferences

    def step(self):
        new_messages = set(self.get_new_messages())

        if new_messages:
            new_ask_why = new_messages.intersection(
                set(self.get_messages_from_performative(MessagePerformative.ASK_WHY)))
            if new_ask_why:
                for mess in new_ask_why:
                    self.send_specific_message(mess, MessagePerformative.ARGUE)

            # if on a reçu un commit
            new_commit = new_messages.intersection(
                set(self.get_messages_from_performative(MessagePerformative.COMMIT)))
            if new_commit:
                for mess in new_commit:
                    item = mess.get_content()
                    if item in self.get_preference_dict().keys():
                        self.send_specific_message(
                            mess, MessagePerformative.COMMIT)
                        self.remove_item(item)
                    # print(self.get_preference_dict())

            # if on a reçu un accept
            new_accept = new_messages.intersection(
                set(self.get_messages_from_performative(MessagePerformative.ACCEPT)))
            if new_accept:
                for mess in new_accept:
                    item = mess.get_content()
                    if item in self.get_preference_dict().keys():
                        self.send_specific_message(
                            mess, MessagePerformative.COMMIT)
                        self.remove_item(item)

            # if on a reçu un propose
            new_propose = new_messages.intersection(set(self.get_messages_from_performative(
                MessagePerformative.PROPOSE)))
            if new_propose:
                for mess in new_propose:
                    is_in_10 = self.get_preference().is_item_among_top_10_percent(
                        mess.get_content(), list(self.get_preference_dict().keys()))
                    if is_in_10:
                        self.send_specific_message(
                            mess, MessagePerformative.ACCEPT)
                    else:
                        self.send_specific_message(
                            mess, MessagePerformative.ASK_WHY)

    def get_preference(self):
        return self.preference

    def get_preference_dict(self):
        return self.preference_dict

    def remove_item(self, item):
        self.get_preference_dict().pop(item)
        self.get_preference().remove_item(item)

    def generate_preferences(self, List_items):
        # supposons une structure de preference:
        # {item1:{crit1:value1,
        #         crit2:val2...},
        #  item2: ...}
        # print(List_items)
        for item in List_items:
            pref = Preferences()
            pref.set_criterion_name_list(List_items[item].keys())
            for criteria in List_items[item]:
                pref.add_criterion_value(CriterionValue(
                    item, criteria, List_items[item][criteria]))
        return pref

    def send_specific_message(self, message_received, performative):
        sender = message_received.get_exp()
        content = message_received.get_content()
        if performative.__str__() == "PROPOSE":
            new_content = content
        elif performative.__str__() == "ACCEPT":
            new_content = content
        elif performative.__str__() == "ASK_WHY":
            new_content = content
        elif performative.__str__() == "COMMIT":
            new_content = content
        elif performative.__str__() == "ARGUE":
            new_content = ""
        message = Message(self.get_name(), sender,
                          performative, new_content)
        self.send_message(message)
        print(message.__str__())


##################################
###### MODEL #####################
##################################

class ArgumentModel (Model):
    """ ArgumentModel which inherit from Model .
    """

    def __init__(self):
        super().__init__()
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
        self.current_step += 1
        self.__messages_service.dispatch_messages()
        # print(str(self.current_step)+": ")
        self.schedule.step()


##################################
###### RUN THE MODEL #############
##################################
if __name__ == "__main__":
    # Init model and agents
    argument_model = ArgumentModel()

    # Objects
    diesel_engine = Item("Diesel Engine", "A super cool diesel engine")
    electric_engine = Item("Electric Engine", "A very quiet engine")

    # Criterion list
    # criterion = [CriterionName.PRODUCTION_COST, CriterionName.ENVIRONMENT_IMPACT,
    #              CriterionName.CONSUMPTION, CriterionName.DURABILITY,
    #              CriterionName.NOISE]

    # Create preference system for A1
    A1 = {diesel_engine: {CriterionName.PRODUCTION_COST: Value.VERY_GOOD,
                          CriterionName.ENVIRONMENT_IMPACT: Value.VERY_BAD,
                          CriterionName.CONSUMPTION: Value.GOOD,
                          CriterionName.DURABILITY: Value.VERY_GOOD,
                          CriterionName.NOISE: Value.BAD},
          electric_engine: {CriterionName.PRODUCTION_COST: Value.BAD,
                            CriterionName.ENVIRONMENT_IMPACT: Value.VERY_GOOD,
                            CriterionName.CONSUMPTION: Value.VERY_BAD,
                            CriterionName.DURABILITY: Value.GOOD,
                            CriterionName.NOISE: Value.VERY_GOOD}}

    # System preference for A2
    A2 = {diesel_engine: {CriterionName.PRODUCTION_COST: Value.GOOD,
                          CriterionName.ENVIRONMENT_IMPACT: Value.BAD,
                          CriterionName.CONSUMPTION: Value.GOOD,
                          CriterionName.DURABILITY: Value.VERY_BAD,
                          CriterionName.NOISE: Value.VERY_BAD},
          electric_engine: {CriterionName.PRODUCTION_COST: Value.GOOD,
                            CriterionName.ENVIRONMENT_IMPACT: Value.BAD,
                            CriterionName.CONSUMPTION: Value.BAD,
                            CriterionName.DURABILITY: Value.VERY_GOOD,
                            CriterionName.NOISE: Value.VERY_GOOD}}

    # Create the Buyer and the seller
    Buyer = ArgumentAgent(1, argument_model, "A1", A1)
    Seller = ArgumentAgent(2, argument_model, "A2", A2)

    # add au scheduler
    print(f"L'agent {Buyer.get_name()} a été créé")
    argument_model.schedule.add(Buyer)
    print(f"L'agent {Seller.get_name()} a été créé")
    argument_model.schedule.add(Seller)

    # Launch the Communication part
    message = Message("A1", "A2", MessagePerformative.PROPOSE,
                      electric_engine)
    # message = Message("A1", "A2", MessagePerformative.PROPOSE,
    #                   diesel_engine)
    # message = Message("A2", "A1", MessagePerformative.PROPOSE,
    #                   electric_engine)
    # message = Message("A2", "A1", MessagePerformative.PROPOSE,
    #                   diesel_engine)
    print(message.__str__())
    Buyer.send_message(message)

    step = 0
    while step < 100:
        argument_model.step()
        step += 1
