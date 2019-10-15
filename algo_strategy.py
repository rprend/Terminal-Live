import gamelib
import random
import math
import warnings
from sys import maxsize
import json

import random


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips:

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical
  board states. Though, we recommended making a copy of the map to preserve
  the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """
        Read in config and perform any initial setup here
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]
        # This is a good place to do initial setup
        self.scored_on_locations = []




    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

        self.starter_strategy(game_state)

        game_state.submit_turn()


    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """


    def starter_strategy(self, game_state):
        """
        For defense we will use a spread out layout and some Scramblers early on.
        We will place destructors near locations the opponent managed to score on.
        For offense we will use long range EMPs if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Pings to try and score quickly.
        """
        # First, place basic defenses
        self.build_defences(game_state)
        # self.build_reactive_defense(game_state)
        self.stall_with_scramblers(game_state)
        #self.build_wall_from_left(game_state)

        if game_state.get_resource(game_state.BITS,0) > 7:
            empt_attack = True if random.randint(0,3) == 1 else False
            percent = .1 + (game_state.get_resource(game_state.BITS,0) - 10)*.08
            spawn_location_options = [[13, 0]]
            if(random.uniform(0,1) < percent):
                game_state.attempt_spawn(EMP if empt_attack else PING, spawn_location_options, 1000)

    def build_defences(self, game_state):
        encryptor_locations = [[2,13],[3,12],[4,11],[5,10],[6,9],[7,8],[8,7],[9,6],[10,5],[11,4],[12,3],[13,2],[14,3],[15,4],[16,5],[17,6],[18,7],[19,8],[20,9],[21,10],[23,12]]
        if(game_state.turn_number < 5):
            encryptor_locations += [[24,13],[25,13]]
        filter_locations = [[26,13],[27,13],[0,13],[1,13]]
        if(game_state.turn_number >5):
            filter_locations += [[24,13],[25,13]]
        game_state.attempt_spawn(ENCRYPTOR,encryptor_locations)
        game_state.attempt_spawn(FILTER,filter_locations)

        #game_state.attempt_spawn(FILTER, random.sample(filter_locations,4))

        # Place destructors that attack enemy units
        #simple heuristics. IDK if this is at all helpful...
        if game_state.turn_number >1:
            destructor__xtra_locations = [[17,7],[16,6],[15,5],[14,4],[13,3],[12,2],[11,3]]
            destructor_locations = [[22, 12], [20, 10], [19, 9], [18, 8],[17,7]]
            #add in
            if game_state.get_resource(game_state.CORES,0) > 20:
                destructor_locations += destructor__xtra_locations
                if game_state.get_resource(game_state.CORES,0) > 40:
                    destructor_locations += [[10,4],[9,5],[8,6],[7,7],[6,8],[5,9],[4,10],[3,11],[2,12]]
            # attempt_spawn will try to spawn units if we have resources, and will check if a blocking unit is already there
            elif game_state.get_resource(game_state.CORES,0) > 10:
                len_dest = len(destructor__xtra_locations)
                choice1 = random.randint(0, len_dest-1)
                destructor_locations.append(destructor__xtra_locations[choice1])
                choice2 = -1
                while(True and len_dest > 1):
                    choice2 = random.randint(0, len_dest-1)
                    if(choice1 != choice2):
                        destructor_locations.append(destructor__xtra_locations[choice2])
                        break

                # destructor_locations += random.choice(destructor__xtra_locations,2)


            game_state.attempt_spawn(DESTRUCTOR, destructor_locations)

            filter_locations2 = [[1,12],[2,12],[24,12],[25,12],[26,12]]
            game_state.attempt_spawn(FILTER,filter_locations2)

            filter_locations3 = [[24,10],[25,11],[26,12],[23,9],[22,8],[21,7],[20,6]]
            game_state.attempt_spawn(FILTER,filter_locations3)
        
            if game_state.get_resource(game_state.CORES,0) > 20:            

                add_filter_rand = []
                filter_locations4 = [[1,12],[2,11],[3,10],[4,9],[5,8],[6,7],[7,6],[8,5],[9,4],[10,3],[11,2],[12,1],[14,0],[18,4],[17,3],[16,2],[15,1]]
                len_dest = len(filter_locations4)
                choice1 = random.randint(0, len_dest-1)
                add_filter_rand.append(filter_locations4[choice1])
                choice2 = -1
                while(True and len_dest > 1):
                    choice2 = random.randint(0, len_dest-1)
                    if(choice1 != choice2):
                        add_filter_rand.append(filter_locations4[choice2])
                        break
                game_state.attempt_spawn(FILTER,add_filter_rand)



        #secondary_filter_locations = [x + 1 for x in filter_locations[1]]
        #game_state.attempt_spawn(FILTER, secondary_filter_locations)


    def build_reactive_defense(self, game_state):
        """
        This function builds reactive defenses based on where the enemy scored on us from.
        We can track where the opponent scored by looking at events in action frames
        as shown in the on_action_frame function
        """
        for location in self.scored_on_locations:
            # Build destructor one space above so that it doesn't block our own edge spawn locations
            build_location = [location[0], location[1]+1]
            game_state.attempt_spawn(DESTRUCTOR, build_location)

    def build_wall_from_left(self, game_state):
        filter_locations = [[i, 13] for i in range(28)]
        game_state.attempt_spawn(FILTER, filter_locations)

    # def check_left_hall_hole(self, game_state):
    #     start_location = [15,1]
    #     path = game_state.find_path_to_edge(start_location)
    #     count = 0
    #     for path_location in path:
    #         count += 1
    #         if(count > 3):
    #             return False
    #         if(path_location[0] <= 13):
    #             return True
    #     return False

    def stall_with_scramblers(self, game_state):
        """
        Send out Scramblers at random locations to defend our base from enemy moving units.
        """
        # We can spawn moving units on our edges so a list of all our edge locations
        # friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)

        # # Remove locations that are blocked by our own firewalls
        # # since we can't deploy units there.
        # deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)

        deploy_locations = [[19,5]]
        num_scramblers = 1
        opp_bits = game_state.get_resource(game_state.BITS,1)
        if(opp_bits >= 7 and opp_bits < 9):
            num_scramblers = 2
        elif( opp_bits >= 9 and opp_bits < 14):
            num_scramblers = 4
        elif(opp_bits >= 14):
            num_scramblers = 6
        game_state.attempt_spawn(SCRAMBLER, deploy_locations,num_scramblers)




    def emp_line_strategy(self, game_state):
        """
        Build a line of the cheapest stationary unit so our EMP's can attack from long range.
        """
        # First let's figure out the cheapest unit
        # We could just check the game rules, but this demonstrates how to use the GameUnit class
        #stationary_units = [FILTER, DESTRUCTOR, ENCRYPTOR]
        #cheapest_unit = FILTER
        # for unit in stationary_units:
        #     unit_class = gamelib.GameUnit(unit, game_state.config)
        #     if unit_class.cost < gamelib.GameUnit(cheapest_unit, game_state.config).cost:
        #         cheapest_unit = unit

        # Now let's build out a line of stationary units. This will prevent our EMPs from running into the enemy base.
        # Instead they will stay at the perfect distance to attack the front two rows of the enemy base.
        for x in range(27, 5, -1):
            game_state.attempt_spawn(FILTER, [x, 11])

        # Now spawn EMPs next to the line
        # By asking attempt_spawn to spawn 1000 units, it will essentially spawn as many as we have resources for
        game_state.attempt_spawn(EMP, [24, 10], 1000)


        #builds a defensive destruct-filter block
    def build_spot_defense(self,game_state,location):
        filter_deploy_locations = [[location[0]-1,location[1]],[location[0],location[1]+1],[location[0]+1,location[1]]]
        game_state.attempt_spawn(FILTER, filter_deploy_locations)
        destructor_deploy_locations = location
        game_state.attempt_spawn(DESTRUCTOR,destructor_deploy_locations)

    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy destructors that can attack the final location and multiply by destructor damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(DESTRUCTOR, game_state.config).damage
            damages.append(damage)

        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units

    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at: https://docs.c1games.com/json-docs.html
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly,
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
