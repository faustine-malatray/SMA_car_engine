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
        "crit_order": [CriterionName.PRODUCTION_COST, CriterionName.CONSUMPTION],
    }

    A2 = {
        diesel_engine: {
            CriterionName.PRODUCTION_COST: Value.VERY_BAD,
            CriterionName.CONSUMPTION: Value.VERY_GOOD,
        },
        electric_engine: {
            CriterionName.PRODUCTION_COST: Value.BAD,
            CriterionName.CONSUMPTION: Value.BAD,
        },
        "crit_order": [CriterionName.PRODUCTION_COST, CriterionName.CONSUMPTION],
    }

    # Create the Buyer and the seller
    Buyer = ArgumentAgent(1, argument_model, "Buyer", preferences=A1)
    Seller = ArgumentAgent(2, argument_model, "Seller", preferences=A2)

    # add au scheduler
    print(f"L'agent {Buyer.get_name()} a été créé")
    argument_model.schedule.add(Buyer)
    print(f"L'agent {Seller.get_name()} a été créé")
    argument_model.schedule.add(Seller)

    message = Message(
        Seller.get_name(),
        Buyer.get_name(),
        MessagePerformative.PROPOSE,
        "Diesel Engine",
    )
    message2 = Message(
        Seller.get_name(), Buyer.get_name(), MessagePerformative.ACCEPT, "Diesel Engine"
    )
    message3 = Message(
        Seller.get_name(), Buyer.get_name(), MessagePerformative.COMMIT, "Diesel Engine"
    )
    message4 = Message(
        Seller.get_name(),
        Buyer.get_name(),
        MessagePerformative.PROPOSE,
        "Electric Engine",
    )
    message5 = Message(
        Seller.get_name(),
        Buyer.get_name(),
        MessagePerformative.ASK_WHY,
        "Electric Engine",
    )

    arg = Argument(False, diesel_engine)

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
    assert type(Buyer.get_preference()) == Preferences
    assert len(list(Buyer.get_preference().get_criterion_name_list())) == 2
    assert len(list(Buyer.get_preference().get_criterion_value_list())) == 4
    assert list(Buyer.get_preference().get_criterion_order_preference()) == [
        CriterionName.PRODUCTION_COST,
        CriterionName.CONSUMPTION,
    ]
    print("La fonction get_preference fonctionne")
    assert Buyer.get_preference_dict() == A1
    print("La fonction get_preference_dict fonctionne")
    assert type(Buyer.get_model()) == ArgumentModel
    print("La fonction get_model fonctionne")
    assert list(Buyer.get_item_list()) == [diesel_engine, electric_engine]
    print("La fonction get_item_list fonctionne")
    assert type(Buyer.get_criteria_from_name("PRODUCTION_COST")) == CriterionName
    assert (
        Buyer.get_criteria_from_name("PRODUCTION_COST") == CriterionName.PRODUCTION_COST
    )
    print("La fonction get_criteria_from_name fonctionne")
    assert type(Buyer.get_value_from_name("VERY_BAD")) == Value
    assert Buyer.get_value_from_name("VERY_BAD") == Value.VERY_BAD
    print("La fonction get_value_from_name fonctionne")
    assert type(Buyer.get_item_from_name("Diesel Engine")) == Item
    assert Buyer.get_item_from_name("Diesel Engine") == diesel_engine
    print("La fonction get_item_from_name fonctionne")

    # Buyer.send_specific_message
    # on devrait print un string à la fin
    # à chaque fois on fait un envoi de message
    # selon les combinaisons d'argument, on envoie le bon contenu

    assert (Buyer.send_specific_message(message, MessagePerformative.ACCEPT)) == None
    # Le print devrait afficher : "1 : Buyer to Seller - ACCEPT(Diesel Engine)"
    assert (Buyer.send_specific_message(message2, MessagePerformative.COMMIT)) == None
    # Le print devrait afficher : "2 : Buyer to Seller - COMMIT(Diesel Engine)"
    assert (Buyer.send_specific_message(message3, MessagePerformative.COMMIT)) == None
    # Le print devrait afficher : "3 : Buyer to Seller - COMMIT(Diesel Engine)"
    assert (Buyer.send_specific_message(message4, MessagePerformative.ASK_WHY)) == None
    # Le print devrait afficher : "4 : Buyer to Seller - ASK_WHY(Electric Engine)"
    assert (Buyer.send_specific_message(message5, MessagePerformative.ARGUE)) == None
    # Le print devrait afficher : "5 : Buyer to Seller - ARGUE(None)"
    print("La fonction send_specific_message fonctionn")

    print("* 6) Testing Arguments")

    assert type(Buyer.support_proposal(diesel_engine)) == Argument
    print("La fonction support_proposal fonctionne")

    assert (
        type(arg.List_supporting_proposal(diesel_engine, Buyer.get_preference()))
        == list
    )
    assert len(arg.List_supporting_proposal(diesel_engine, Buyer.get_preference())) == 2
    assert (
        len(arg.List_supporting_proposal(diesel_engine, Seller.get_preference())) == 1
    )
    assert (
        type(arg.List_supporting_proposal(diesel_engine, Seller.get_preference())[0])
        == CriterionName
    )
    print("La fonction List_support_proposal fonctionne")

    assert (
        Buyer.get_preference().get_value(diesel_engine, CriterionName.PRODUCTION_COST)
        == None
        or Buyer.get_preference().get_value(
            diesel_engine, CriterionName.PRODUCTION_COST
        )
        == Value.VERY_GOOD
    )
    assert (
        Buyer.get_preference().get_value(diesel_engine, CriterionName.PRODUCTION_COST)
        == None
        or Buyer.get_preference()
        .get_value(diesel_engine, CriterionName.PRODUCTION_COST)
        .value
        == 4
    )
