#!/usr/bin/env python3
import copy
import traceback

import tcod

import pyrouge.color
import pyrouge.exceptions
import pyrouge.input_handlers
from pyrouge.engine import Engine
from pyrouge.entity_factory import player_factory
from pyrouge.procgen import generate_dungeon


def main() -> None:
    screen_width = 80
    screen_height = 51

    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    max_monsters_per_room = 2
    max_items_per_room = 2

    tileset = tcod.tileset.load_tilesheet(
        "pyrouge/resources/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    player = copy.deepcopy(player_factory)

    engine = Engine(player=player)

    engine.game_map = generate_dungeon(
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        max_monsters_per_room=max_monsters_per_room,
        max_items_per_room=max_items_per_room,
        engine=engine
    )

    engine.update_fov()

    engine.message_log.add_message(
        "Hello and welcome, adventurer, to yet another dungeon!", pyrouge.color.welcome_text
    )

    handler: pyrouge.input_handlers.BaseEventHandler = pyrouge.input_handlers.MainGameEventHandler(
        engine)

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title="PyRouge",
        vsync=True,
    ) as context:
        root_console = tcod.console.Console(
            screen_width, screen_height, order="F")
        try:
            while True:
                root_console.clear()
                handler.on_render(console=root_console)
                context.present(root_console)

                try:
                    for event in tcod.event.wait():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:  # Handle exceptions in game.
                    traceback.print_exc()  # Print error to stderr.
                    # Then print the error to the message log.
                    if isinstance(handler, pyrouge.input_handlers.EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), pyrouge.color.error
                        )
        except pyrouge.exceptions.QuitWithoutSaving:
            raise
        except SystemExit:  # Save and quit.
            # TODO: Add the save function here
            raise
        except BaseException:  # Save on any other unexpected exception.
            # TODO: Add the save function here
            raise


if __name__ == "__main__":
    main()
