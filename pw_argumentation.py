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
        # supposons une structure de preference:
        # {item1:{crit1:value1,
        #         crit2:val2...},
        #  item2: ...}
        self.preference = preferences

    def step(self):
        super().step()

    def get_preference(self):
        return self.preference

    def generate_preferences(self, List_items):
        for item in List_items:
            pref = Preferences()
            pref.set_criterion_name_list(self.preference[item].keys())
            for criteria, value in item.items():
                pref.add_criterion_value(CriterionValue(item, criteria, value))


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
        self . running = True

    def step(self):
        self . __messages_service . dispatch_messages()
        self . schedule . step()

    # def send_specific_message(self, message_received, performative):
    #     sender = message_received.get_exp()
    #     if performative.__str__() == "PROPOSE":
    #         content = self.get_v()
    #     elif performative.__str__() == "ACCEPT":
    #         content = "ok tiptop"
    #     elif performative.__str__() == "QUERY_REF":
    #         content = "v?"
    #     message = Message(self.name, sender, performative, content)
    #     self.send_message(message)
    #     print(message.__str__())

    # def step(self):
    #     # il faut recevoir les messages
    #     new_messages = set(self.get_new_messages())
    #     message = None

    #     if new_messages:
    #         new_ask_why = new_messages.intersection(
    #             set(self.get_messages_from_performative(MessagePerformative.ASK_WHY)))
    #         if new_ask_why:
    #             for mess in new_ask_why:
    #                 self.send_specific_message(
    #                     mess, MessagePerformative.QUERY_REF)

    #         # if on a reçu un commit
    #         new_commit = new_messages.intersection(
    #             set(self.get_messages_from_performative(MessagePerformative.COMMIT)))
    #         if new_commit:
    #             for mess in new_commit:
    #                 self.send_specific_message(
    #                     mess, MessagePerformative.ACCEPT)

    #         # if on a reçu des inform_ref
    #         new_inform_ref = new_messages.intersection(set(self.get_messages_from_performative(
    #             MessagePerformative.INFORM_REF)))
    #         if new_inform_ref:
    #             for mess in new_inform_ref:
    #                 value = mess.get_content()
    #                 if self.__v == value:
    #                     self.send_specific_message(
    #                         mess, MessagePerformative.ACCEPT)
    #                 else:
    #                     self.send_specific_message(
    #                         mess, MessagePerformative.PROPOSE)


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
    Buyer = ArgumentAgent(1, argument_model, "Buyer", A1)
    Seller = ArgumentAgent(2, argument_model, "Seller", A2)

    # add au scheduler
    print(f"L'agent {Buyer.get_name()} a été créé")
    argument_model.schedule.add(Buyer)
    print(f"L'agent {Seller.get_name()} a été créé")
    argument_model.schedule.add(Seller)

    # Launch the Communication part
    # message = Message("Alice", "Charles", MessagePerformative.QUERY_REF, "v?")
    # print(message.__str__())
    # Alice.send_message(message)
    # message = Message("Bob", "Charles", MessagePerformative.QUERY_REF, "v?")
    # print(message.__str__())
    # Bob.send_message(message)

    step = 0
    while step < 100:
        argument_model.step()
        step += 1
