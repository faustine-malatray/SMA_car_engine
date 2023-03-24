#!/usr/bin/env python3

import random

from mesa import Model
from mesa.time import RandomActivation

from agent.CommunicatingAgent import CommunicatingAgent
from message.Message import Message
from message.MessagePerformative import MessagePerformative
from message.MessageService import MessageService


##################################
###### SELLER ####################
##################################

class SellerAgent(CommunicatingAgent):
    """ """

    def __init__(self, unique_id, model, name):
        super().__init__(unique_id, model, name)
        self.name = name

    def send_specific_message(self, message_received, performative):
        sender = message_received.get_exp()
        if performative.__str__() == "PROPOSE":
            content = self.get_v()
        elif performative.__str__() == "ACCEPT":
            content = "ok tiptop"
        elif performative.__str__() == "QUERY_REF":
            content = "v?"
        message = Message(self.name, sender, performative, content)
        self.send_message(message)
        print(message.__str__())

    def step(self):
        # il faut recevoir les messages
        new_messages = set(self.get_new_messages())
        message = None

        if new_messages:
            new_ask_why = new_messages.intersection(
                set(self.get_messages_from_performative(MessagePerformative.ASK_WHY)))
            if new_ask_why:
                for mess in new_ask_why:
                    self.send_specific_message(
                        mess, MessagePerformative.QUERY_REF)

            # if on a reçu un commit
            new_commit = new_messages.intersection(
                set(self.get_messages_from_performative(MessagePerformative.COMMIT)))
            if new_commit:
                for mess in new_commit:
                    self.send_specific_message(
                        mess, MessagePerformative.ACCEPT)

            # if on a reçu des inform_ref
            new_inform_ref = new_messages.intersection(set(self.get_messages_from_performative(
                MessagePerformative.INFORM_REF)))
            if new_inform_ref:
                for mess in new_inform_ref:
                    value = mess.get_content()
                    if self.__v == value:
                        self.send_specific_message(
                            mess, MessagePerformative.ACCEPT)
                    else:
                        self.send_specific_message(
                            mess, MessagePerformative.PROPOSE)

        # sinon, pas de message en attente

    def step_batch(self):
        pass


##################################
###### BUYER #####################
##################################

class BuyerAgent(CommunicatingAgent):
    def __init__(self, unique_id, model, name):
        super().__init__(unique_id, model, name)
        self.name = name

    def send_specific_message(self, message_received, performative):
        sender = message_received.get_exp()
        if performative.__str__() == "COMMIT":
            content = self.get_v()
        elif performative.__str__() == "ASK_WHY":
            content = "pourquoi cette requête ?"
        else:
            content = self.get_v()
        message = Message(self.name, sender, performative, content)
        self.send_message(message)
        print(message.__str__())

    def step(self):
        # il faut recevoir les messages
        new_messages = set(self.get_new_messages())
        # print([mess.__str__() for mess in new_messages])
        message = None

        if new_messages:
            new_accept = new_messages.intersection(
                set(self.get_messages_from_performative(MessagePerformative.ACCEPT)))
            if new_accept:
                for mess in new_accept:
                    self.send_specific_message(
                        mess, MessagePerformative.ASK_WHY)

            # if on a recu des propose
            new_propose = new_messages.intersection(
                set(self.get_messages_from_performative(MessagePerformative.PROPOSE)))
            if new_propose:
                for mess in new_propose:
                    self.__v = mess.get_content()
                    self.send_specific_message(
                        mess, MessagePerformative.COMMIT)

            # if on a reçu des query
            new_query_ref = new_messages.intersection(
                set(self.get_messages_from_performative(MessagePerformative.QUERY_REF)))
            if new_query_ref:
                # je le lis, j'identifie la valeur et l'envoyeur
                for mess in new_query_ref:
                    self.send_specific_message(
                        mess, MessagePerformative.INFORM_REF)

    def step_batch(self):
        pass


##################################
###### MODEL #####################
##################################

class CarEngineModel(Model):
    """ """

    def __init__(self):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)
        self.running = True

    def step(self):
        self.schedule.step()


##################################
###### RUN THE MODEL #############
##################################
if __name__ == "__main__":
    # Init model and agents
    car_engine_model = CarEngineModel()

    # Create the Buyer and the seller
    AgentBuyer = BuyerAgent(car_engine_model.next_id(),
                            car_engine_model, "AgentBuyer")
    AgentSeller = SellerAgent(
        car_engine_model.next_id(), car_engine_model, "AgentSeller")

    # add au scheduler
    print(f"L'agent {AgentBuyer.get_name()} a été créé")
    car_engine_model.schedule.add(AgentBuyer)
    print(f"L'agent {AgentSeller.get_name()} a été créé")
    car_engine_model.schedule.add(AgentSeller)

    # Launch the Communication part
    # message = Message("Alice", "Charles", MessagePerformative.QUERY_REF, "v?")
    # print(message.__str__())
    # Alice.send_message(message)
    # message = Message("Bob", "Charles", MessagePerformative.QUERY_REF, "v?")
    # print(message.__str__())
    # Bob.send_message(message)

    step = 0
    while step < 100:
        car_engine_model.step()
        step += 1
