#!/usr/bin/env python3
"""This software is licensed under the GPL3
You should have gotten an copy of the GPL3 license anlonside this software
Feel free to contribute what ever you want to this game
New Pokete contributions are especially welcome
For this see the comments in the definations area
You can contribute here: https://github.com/lxgr-linux/pokete
Thanks to MaFeLP for your code review and your great feedback"""

import time
import os
import sys
import threading
import logging
from pathlib import Path
from datetime import datetime
import scrap_engine as se

from pokete_classes.asset_service.service import asset_service
from pokete_classes.input.recogniser import recogniser
from pokete_classes.multiplayer.communication import com_service
from pokete_classes.multiplayer.interactions.context_menu import ContextMenu
from pokete_classes.multiplayer.modeprovider import modeProvider, Mode
from pokete_classes.multiplayer.pc_manager import pc_manager
from pokete_classes.poke import Stats
from pokete_classes.fight import ProtoFigure
from pokete_classes import roadmap
from pokete_classes import animations, loops
from pokete_classes.context import Context
from pokete_classes.inv import inv, buy
from pokete_classes.menu import Menu
from pokete_classes.periodic_events import MovingGrassEvent, MovingWaterEvent, \
    TreatNPCEvent, NotifierEvent
from pokete_classes.poke import Poke
from pokete_classes.color import Color
from pokete_classes.pre_game import PreGameMap
from pokete_classes.save import read_save, save
from pokete_classes.input_loops import text_input
from pokete_classes.classes import PlayMap
from pokete_classes.settings import settings
from pokete_classes.audio import audio
from pokete_classes.tss import tss
from pokete_classes.side_loops import loading_screen, Help
from pokete_classes.input import _ev
from pokete_classes.mods import try_load_mods
from pokete_classes.pokete_care import pokete_care
from pokete_classes import deck, timer, ob_maps as obmp, \
    movemap as mvp
from pokete_classes.landscape import MapInteract
from pokete_classes.doors import Door
from pokete_classes.ui import notifier
from pokete_classes.input_loops import ask_bool, ask_text
from pokete_classes.achievements import achievements
from pokete_classes.input import get_action, Action, ACTION_DIRECTIONS
from pokete_classes.dex import Dex
from pokete_classes.game import (
    PeriodicEventManager, MapChangeExeption
)
from release import SPEED_OF_TIME, VERSION, CODENAME, SAVEPATH
from util.command import RootCommand, Flag

__t = time.time()

# Class definition
##################

"""
class SwapPokeNPCAction(NPCAction):
    def act(self, npc: NPCInterface, ui: UIInterface):
        swap_poke(npc.ctx)
"""


class Figure(se.Object, ProtoFigure):
    """The figure that moves around on the map and represents the player
    ARGS:
        _si: session_info dict"""

    def __init__(self, _si):
        r_char = _si.get("represent_char", "a")
        if len(r_char) != 1:
            logging.info(
                "[Figure] '%s' is no valid 'represent_char', resetting", r_char)
            r_char = "a"
        super().__init__(r_char, state="solid")
        ProtoFigure.__init__(
            self,
            [Poke.from_dict(_si["pokes"][poke]) for poke in _si["pokes"]],
            escapable=True,
            xp_multiplier=2
        )
        self.__money = _si.get("money", 10)
        self.inv = _si.get("inv", {"poketeballs": 10})
        self.name = _si.get("user", "DEFAULT")
        self.caught_pokes = _si.get("caught_poketes", [])
        self.visited_maps = _si.get("visited_maps", ["playmap_1"])
        self.used_npcs = _si.get("used_npcs", [])
        self.direction = "t"
        self.last_center_map = None
        self.oldmap = None
        self.oldmap_name = _si.get("oldmap", "playmap_1")
        self.map_name = _si.get("map", "playmap_1")
        self.last_center_map_name = _si.get("last_center_map",
                                            "playmap_1")
        self.x = _si["x"]
        self.y = _si["y"]

    def self_add(self):
        try:
            # Looking if figure would be in centermap,
            # so the player may spawn out of the center
            if self.map_name in ["centermap",
                                 "shopmap"] and modeProvider.mode != Mode.MULTI:
                _map = obmp.ob_maps[self.map_name]
                self.add(_map, _map.dor_back1.x, _map.dor_back1.y - 1)
            else:
                if self.add(obmp.ob_maps[self.map_name], self.x, self.y) == 1:
                    raise se.CoordinateError(
                        self, obmp.ob_maps.get(self.map_name, "undefined map"),
                        self.x, self.y)
        except se.CoordinateError:
            self.add(obmp.ob_maps["playmap_1"], 6, 5)
        # self.add(obmp.ob_maps[self.map_name], self.x, self.y)

    def set_args(self, _si):
        """Processes data from save file
        ARGS:
            _si: session_info dict"""
        self.last_center_map = obmp.ob_maps.get(
            _si.get(
                "last_center_map",
                "playmap_1"),
            PlayMap())
        self.oldmap = obmp.ob_maps.get(_si.get("oldmap", "playmap_1"),
                                       PlayMap())
        mvp.movemap.name_label.rechar(self.name, esccode=Color.thicc)
        mvp.movemap.code_label.rechar(self.map.pretty_name)
        mvp.movemap.balls_label_rechar(self.pokes)
        mvp.movemap.add_obs()

    def set(self, x, y):
        if super().set(x, y) == 0:
            self.update_server_pos()

    def add(self, _map, x, y):
        if super().add(_map, x, y) == 0:
            self.update_server_pos()

    def update_server_pos(self):
        if modeProvider.mode == Mode.MULTI:
            com_service.pos_update(self.map.name, self.x, self.y)

    def add_money(self, money):
        """Adds money
        ARGS:
            money: Amount of money being added"""
        self.set_money(self.__money + money)

    def get_money(self):
        """Getter for __money
        RETURNS:
            The current money"""
        return self.__money

    def set_money(self, money):
        """Sets the money to a certain value
        ARGS:
            money: New value"""
        assert money >= 0, "Money has to be positive."
        logging.info("[Figure] Money set to $%d from $%d",
                     money, self.__money)
        self.__money = money
        for cls in [inv, buy]:
            cls.money_label.rechar("$" + str(self.__money))  # TODO: Remove
            cls.box.set_ob(cls.money_label,
                           cls.box.width - 2 - len(cls.money_label.text), 0)

    def add_poke(self, poke: Poke, idx=None, caught_with=None):
        """Adds a Pokete to the players Poketes
        ARGS:
            poke: Poke object beeing added
            idx: Index of the Poke
            caught_with: Name of ball which was used"""
        poke.set_player(True)
        poke.set_poke_stats(
            Stats(poke.name, datetime.now(), caught_with=caught_with))
        self.caught_pokes.append(poke.identifier)
        if idx is None:
            id_list = [i.identifier for i in self.pokes]
            if "__fallback__" in id_list:
                idx = id_list.index("__fallback__")
                self.pokes[idx] = poke
            else:
                self.pokes.append(poke)
        else:
            self.pokes[idx] = poke
        logging.info("[Figure] Added Poke %s", poke.name)

    def give_item(self, item, amount=1):
        """Gives an item to the player"""
        assert amount > 0, "Amounts have to be positive!"
        if item not in self.inv:
            self.inv[item] = amount
        else:
            self.inv[item] += amount
        logging.info("[Figure] %d %s(s) given", amount, item)

    def has_item(self, item):
        """Checks if an item is already present
        ARGS:
            item: Generic item name
        RETURNS:
            If the player has this item"""
        return item in self.inv and self.inv[item] > 0

    def remove_item(self, item, amount=1):
        """Removes a certain amount of an item from the inv
        ARGS:
            item: Generic item name
            amount: Amount of items beeing removed"""
        assert amount > 0, "Amounts have to be positive!"
        assert item in self.inv, f"Item {item} is not in the inventory!"
        assert self.inv[item] - amount >= 0, f"There are not enought {item}s \
in the inventory!"
        self.inv[item] -= amount
        logging.info("[Figure] %d %s(s) removed", amount, item)


class Debug:
    """Debug class"""

    @classmethod
    def pos(cls):
        """Prints the figures' position"""
        print(figure.x, figure.y, figure.map.name)


# General use functions
#######################

def autosave():
    """Autosaves the game every 5 mins"""
    while True:
        time.sleep(SPEED_OF_TIME * 300)
        if settings("autosave").val:
            save(figure)


def exiter():
    """Exit function"""
    recogniser.reset()
    logging.info("[General] Exiting...")
    print("\033[?1049l\033[1A")
    if audio.curr is not None:
        audio.kill()


# Functions needed for mvp.movemap
##############################

def codes(string):
    """Cheats"""
    for i in string:
        if i == "w":
            save(figure)
        elif i == "!":
            exec(string[string.index("!") + 2:])
            return
        elif i == "e":
            try:
                exec(string[string.index("e") + 2:])
            except Exception as exc:
                print(exc)
            return
        elif i == "q":
            sys.exit()


# main functions
################

def teleport(poke):
    """Teleports the player to another towns pokecenter
    ARGS:
        poke: The Poke shown in the animation"""
    if (obj := roadmap.roadmap(
        Context(PeriodicEventManager([]), mvp.movemap, mvp.movemap, figure),
        choose=True)) is None:
        return
    if settings("animations").val:
        animations.transition(mvp.movemap, poke)
    cen_d = asset_service.get_assets().obmaps[obj.name].hard_obs["pokecenter"]
    Door("", state="float", arg_proto={
        "map": obj.name,
        "x": cen_d.x + 5,
        "y": cen_d.y + 6
    }).action(figure)


''' # this is awfull and has to be removed
def swap_poke(ctx: Context):
    """Trading with other players in the local network"""
    if not ask_bool(
        ctx, "Do you want to trade with another trainer?",
    ):
        return
    port = 65432
    save(figure)
    do = ask_bool(ctx, "Do you want to be the host?")
    if (index := deck.deck(ctx, 6, "Your deck", True)) is None:
        return
    if do:
        with InfoBox(f"Hostname: {socket.gethostname()}\nWaiting...",
                     ctx=ctx):
            host = ''
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind((host, port))
                sock.listen()
                conn = sock.accept()[0]
                with conn:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        decode_data = json.loads(data.decode())
                        conn.sendall(
                            str.encode(
                                json.dumps(
                                    {"mods": loaded_mods.mod_info,
                                     "name": figure.name,
                                     "poke": figure.pokes[index].dict()})))
    else:
        host = ""
        while host == "":
            host = ask_text(ctx, "Please type in the hosts hostname",
                            "Host:", "", "Hostname", 30)
            if host in ["localhost", "127.0.0.1", "0.0.0.0",
                        socket.gethostname()]:
                ask_ok(ctx,
                       "You're not allowed trade with your self!\nYou fool!")
                host = ""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((host, port))
            except Exception as err:
                ask_ok(ctx, str(err))
                return
            sock.sendall(
                str.encode(
                    json.dumps({"mods": loaded_mods.mod_info,
                                "name": figure.name,
                                "poke": figure.pokes[index].dict()})))
            data = sock.recv(1024)
            decode_data = json.loads(data.decode())
    logging.info("[Swap_poke] Recieved %s", decode_data)
    mod_info = decode_data.get("mods", {})
    if loaded_mods.mod_info != mod_info:
        ask_ok(
            ctx, f"""Conflicting mod versions!
Your mods: {', '.join(i + '-' + loaded_mods.mod_info[i] for i in loaded_mods.mod_info)}
Your partners mods: {', '.join(i + '-' + mod_info[i] for i in mod_info)}"""
        )
        return
    figure.add_poke(Poke(decode_data["poke"]["name"],
                         decode_data["poke"]["xp"],
                         decode_data["poke"]["hp"]), index)
    figure.pokes[index].set_ap(decode_data["poke"]["ap"])
    save(figure)  # to avoid duping
    ask_ok(ctx,
           f"You received: {figure.pokes[index].name.capitalize()} at level \
{figure.pokes[index].lvl()} from {decode_data['name']}.")
'''


def _game(_map: PlayMap):
    """Game function
    ARGS:
        _map: The map that will be shown"""
    _ev.clear()
    print("\033]0;Pokete - " + _map.pretty_name + "\a", end="")
    if _map.name not in figure.visited_maps:
        figure.visited_maps.append(_map.name)

    if audio.curr is None:
        audio.start(_map.song)
    else:
        audio.switch(_map.song)

    mvp.movemap.code_label.rechar(figure.map.pretty_name)
    mvp.movemap.resize_view()
    mvp.movemap.set(0, 0)
    mvp.movemap.bmap = _map
    pc_manager.movemap_move()
    mvp.movemap.full_show()
    pevm = PeriodicEventManager(
        [
            MovingGrassEvent(_map),
            MovingWaterEvent(_map),
            *([TreatNPCEvent()] if modeProvider.mode == Mode.SINGLE else []),
            NotifierEvent()
        ] + _map.extra_actions())
    ctx = Context(pevm, mvp.movemap, mvp.movemap, figure)
    MapInteract.set_ctx(ctx)  # Npcs need this global context
    inp_dict: dict[Action, tuple] = {
        Action.DECK: (deck.deck, (ctx, 6, "Your deck")),
        Action.MAP: (roadmap.roadmap, (ctx,)),
        Action.INVENTORY: (inv, (ctx,)),
        Action.POKEDEX: (Dex(), (ctx,)),
        Action.CLOCK: (timer.clock, (ctx,)),
        Action.MENU: (Menu(), (ctx,)),
        Action.HELP: (Help(), (ctx,)),
        Action.INTERACT: (ContextMenu(), (ctx,))
    }
    if _map.weather is not None:
        notifier.notify("Weather", "Info", _map.weather.info)
    while True:
        # Directions are not being used yet
        action = get_action()
        if action.triggers(*ACTION_DIRECTIONS):
            figure.direction = ''
            figure.set(
                figure.x + action.get_x_strength(),
                figure.y + action.get_y_strength()
            )
            pc_manager.check_interactable(figure)
        elif action.triggers(*inp_dict):
            for key, option in inp_dict.items():
                if action.triggers(key):
                    option[0](*option[1])
            _ev.clear()
            mvp.movemap.show(init=True)
        elif action.triggers(Action.CANCEL, Action.EXIT_GAME):
            if ask_bool(ctx, "Do you really wish to exit?"):
                save(figure)
                sys.exit()
        elif action.triggers(Action.CONSOLE):
            inp = text_input(ctx, mvp.movemap.code_label, ":",
                             mvp.movemap.width,
                             (mvp.movemap.width - 2)
                             * mvp.movemap.height - 1)[1:]
            mvp.movemap.code_label.outp(figure.map.pretty_name)
            codes(inp)
            _ev.clear()

        for statement, x, y in zip(
            [
                figure.x + 6 > mvp.movemap.x + mvp.movemap.width,
                figure.x < mvp.movemap.x + 6,
                figure.y + 6 > mvp.movemap.y + mvp.movemap.height,
                figure.y < mvp.movemap.y + 6
            ],
            [1, -1, 0, 0],
            [0, 0, 1, -1]
        ):
            if statement:
                mvp.movemap.set(mvp.movemap.x + x, mvp.movemap.y + y)
                pc_manager.movemap_move()

        loops.std(ctx)


def intro(ctx: Context):
    """Intro to Pokete"""
    mvp.movemap.set(0, 0)
    mvp.movemap.bmap = obmp.ob_maps["intromap"]
    mvp.movemap.full_show()
    while figure.name in ["DEFAULT", ""]:
        figure.name = ask_text(
            ctx,
            "Welcome to Pokete!\nPlease choose your name!\n",
            "Name:", "", "Name", 17
        )
    mvp.movemap.name_label_rechar(figure.name)
    mvp.movemap.text(ctx, 4, 3, ["Hello, my child.",
                                 "You're now ten years old.",
                                 "I think it's now time for you to travel \
     the world and be a Pokete-trainer.",
                                 "Therefore, I give you this powerful 'Steini', \
     15 'Poketeballs' to catch Poketes, and a "
                                 "'Healing potion'.",
                                 "You will be the best Pokete-Trainer in Nice \
     town.",
                                 "Now go out and become the best!"])


def main():
    """Main function"""
    os.system("")
    timing = threading.Thread(target=timer.time_threat, daemon=True)
    recognising = threading.Thread(target=recogniser, daemon=True)
    autosaving = threading.Thread(target=autosave, daemon=True)

    timing.start()
    recognising.start()
    autosaving.start()

    PreGameMap()(session_info, figure)
    figure.set_args(session_info)
    game_map = figure.map
    if figure.name == "DEFAULT":
        intro(
            Context(PeriodicEventManager([]), mvp.movemap, mvp.movemap, figure)
        )
        game_map = obmp.ob_maps["intromap"]
    while True:
        try:
            _game(game_map)
        except MapChangeExeption as err:
            game_map = err.map


# Actual code execution
#######################
if __name__ == "__main__":
    log_flag = Flag(["--log"], "Enables logging")
    mods_flag = Flag(["--no_mods"], "Disables mods")
    audio_flag = Flag(["--no_audio"], "Disables audio")

    do_logging = False
    load_mods = True
    audio.use_audio = True


    def root_fn(ex: str, options: list[str],
                flags: dict[str, list[str]]):
        global do_logging, load_mods
        for flag in flags:
            if log_flag.is_flag(flag):
                do_logging = True
            elif mods_flag.is_flag(flag):
                load_mods = False
            elif audio_flag.is_flag(flag):
                audio.use_audio = False


    c = RootCommand(
        "Pokete", f"{CODENAME} v{VERSION}", root_fn,
        flags=[log_flag, mods_flag, audio_flag],
        additional_info=f"""All save and logfiles are located in ~{SAVEPATH}/
Feel free to contribute.
See README.md for more information.
This software is licensed under the GPLv3, you should have gotten a
copy of it alongside this software.""",
        usage=""
    )

    c.exec()

    print("\033[?1049h")

    # resizing screen
    tss()
    loading_screen()

    # Home global
    HOME = Path.home()

    # readingŝ savefile
    session_info = read_save()

    # logging config
    log_file = (SAVEPATH / "pokete.log") if do_logging else None
    logging.basicConfig(filename=log_file,
                        format='[%(asctime)s][%(levelname)s]: %(message)s',
                        level=logging.DEBUG if do_logging else logging.ERROR)
    logging.info("=== Startup Pokete %s v%s ===", CODENAME, VERSION)

    # settings
    settings.from_dict(session_info.get("settings", {}))

    if not load_mods:
        settings("load_mods").val = False

    # Loading mods
    try_load_mods(loading_screen.map)

    # Figure
    figure = Figure(session_info)

    # Definiton of all additionaly needed obs and maps
    #############################################################

    # A dict that contains all world action functions for Attacks
    abb_funcs = {"teleport": teleport}

    # side fn definitions
    deck.deck = deck.Deck(tss.height - 1, tss.width, abb_funcs)
    pokete_care.from_dict(session_info.get("pokete_care", {
        "entry": 0,
        "poke": None,
    }))
    timer.time.set(session_info.get("time", 0))
    _ev.set_emit_fn(timer.time.emit_input)

    # Achievements
    achievements.set_achieved(session_info.get("achievements", []))
    for identifier, achievement_args in asset_service.get_base_assets().achievements.items():
        achievements.add(identifier, achievement_args.title,
                         achievement_args.desc)

    notifier.set_vars(mvp.movemap)

    __t = time.time() - __t
    logging.info("[General] Startup took %fs", __t)

    try:
        main()
    except KeyboardInterrupt:
        print("\033[?1049l\033[1A\nKeyboardInterrupt")
    finally:
        exiter()
