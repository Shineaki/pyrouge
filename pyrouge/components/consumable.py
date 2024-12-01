from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pyrouge.color
import pyrouge.components.inventory
from pyrouge.actions import Action, ItemAction
from pyrouge.components.base_component import BaseComponent
from pyrouge.exceptions import Impossible

if TYPE_CHECKING:
    from entity import Actor, Item


class Consumable(BaseComponent):
    parent: Item

    def get_action(self, consumer: Actor) -> Optional[Action]:
        """Try to return the action for this item."""
        return ItemAction(consumer, self.parent)

    def activate(self, action: ItemAction) -> None:
        """Invoke this items ability.

        `action` is the context for this activation.
        """
        raise NotImplementedError()

    def consume(self) -> None:
        """Remove the consumed item from its containing inventory."""
        entity = self.parent
        inventory = entity.parent
        if isinstance(inventory, pyrouge.components.inventory.Inventory):
            inventory.items.remove(entity)


class HealingConsumable(Consumable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, action: ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name}, and recover {amount_recovered} HP!",
                pyrouge.color.health_recovered,
            )
            self.consume()
        else:
            raise Impossible(f"Your health is already full.")
