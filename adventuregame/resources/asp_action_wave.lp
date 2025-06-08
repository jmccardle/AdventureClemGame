{ action_t(TURN,wave,THING,WAND):at_t(TURN,THING,ROOM),at_t(TURN,WAND,ROOM) } 1 :- turn(TURN), at_t(TURN,player1,ROOM), not turn_limit(TURN).
hot_t(TURN+1,THING) :- action_t(TURN,wave,THING,WAND), type(WAND,firewand).
cold_t(TURN+1,THING) :- action_t(TURN,wave,THING,WAND), type(WAND,iceewand).
glittery_t(TURN+1,THING) :- action_t(TURN,wave,THING,WAND), type(WAND,firewand).
zulponated_t(TURN+1,THING) :- action_t(TURN,wave,THING,WAND), type(WAND,firewand).
hot_t(TURN+1,THING) :- turn(TURN), hot_t(TURN,THING), not action_t(TURN,wave,THING,WAND), type(WAND,icewand).
cold_t(TURN+1,THING) :- turn(TURN), cold_t(TURN,THING), not action_t(TURN,wave,THING,WAND), type(WAND,firewand).
glittery_t(TURN+1,THING) :- turn(TURN), glittery_t(TURN,THING).
zulponated_t(TURN+1,THING) :- turn(TURN), zulponated_t(TURN,THING).


{ action_t(TURN,wave,WAND,cauldron1):at_t(TURN,cauldron1,ROOM),at_t(TURN,WAND,ROOM) } 1 :- turn(TURN), at_t(TURN,player1,ROOM), not turn_limit(TURN).
hot_t(TURN+1,cauldron1) :- action_t(TURN,wave,WAND,cauldron1), type(WAND,firewand).
cold_t(TURN+1,cauldron1) :- action_t(TURN,wave,WAND,cauldron1), type(WAND,icewand).
glittery_t(TURN+1,cauldron1) :- action_t(TURN,wave,WAND,cauldron1), type(WAND,fairywand).
zulponated_t(TURN+1,cauldron1) :- action_t(TURN,wave,WAND,cauldron1), type(WAND,zulpowand).
hot_t(TURN+1,cauldron1) :- turn(TURN), hot_t(TURN,cauldron1), not action_t(TURN,wave,WAND,cauldron1), type(WAND,icewand).
cold_t(TURN+1,cauldron1) :- turn(TURN), cold_t(TURN,cauldron1), not action_t(TURN,wave,WAND,cauldron1), type(WAND,firewand).
glittery_t(TURN+1,cauldron1) :- turn(TURN), glittery_t(TURN,cauldron1).
zulponated_t(TURN+1,cauldron1) :- turn(TURN), zulponated_t(TURN,cauldron1).