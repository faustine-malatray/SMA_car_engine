from mesa import Model
from mesa.time import RandomActivation
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
from pw_argumentation import ArgumentModel, ArgumentAgent

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
    A1 = {
        diesel_engine: {
            CriterionName.PRODUCTION_COST: Value.VERY_GOOD,
            CriterionName.CONSUMPTION: Value.VERY_GOOD,
        },
        electric_engine: {
            CriterionName.PRODUCTION_COST: Value.BAD,
            CriterionName.CONSUMPTION: Value.BAD,
        },
    }

    # Create the Buyer and the seller
    Buyer = ArgumentAgent(1, argument_model, "Buyer", preferences=A1)

    print("*---- Testing preference package ----")
    print("*")
    print("* 3) Testing Most Preferred")
    assert len(Buyer.get_item_list()) == 2
    assert Buyer.get_preference().most_preferred(Buyer.get_item_list()) is not None
    assert Buyer.get_preference().most_preferred(Buyer.get_item_list()) == diesel_engine
    print("on est contents : le Buyer préfère le diesel et il existe 2 items.")

    print("* 4) Testing Top 10%")
    assert Buyer.get_preference().is_item_among_top_10_percent(
        diesel_engine, Buyer.get_item_list()
    )
    assert not Buyer.get_preference().is_item_among_top_10_percent(
        electric_engine, Buyer.get_item_list()
    )
    print("Le top 10% fonctionne")

    print("* 5) Testing Agents and messages")
