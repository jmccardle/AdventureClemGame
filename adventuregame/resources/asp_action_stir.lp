{ action_t(TURN,stir,THING,STIRRER):at_t(TURN,THING,ROOM),at_t(TURN,STIRRER,ROOM) } 1 :- turn(TURN), at_t(TURN,player1,ROOM), not turn_limit(TURN).
ladlestirred_t(TURN+1,THING) :- action_t(TURN,stir,THING,STIRRER), type(STIRRER,ladle).
whisked_t(TURN+1,THING) :- action_t(TURN,stir,THING,STIRRER), type(STIRRER,whisk).
spoonstirred_t(TURN+1,THING) :- action_t(TURN,stir,THING,STIRRER), type(STIRRER,spoon).
borpulusstirred_t(TURN+1,THING) :- action_t(TURN,stir,THING,STIRRER), type(STIRRER,borpulus).
ladlestirred_t(TURN+1,THING) :- turn(TURN), ladlestirred_t(TURN,THING), not action_t(TURN,stir,THING,STIRRER), type(STIRRER,whisk).
ladlestirred_t(TURN+1,THING) :- turn(TURN), ladlestirred_t(TURN,THING), not action_t(TURN,stir,THING,STIRRER), type(STIRRER,spoon).
ladlestirred_t(TURN+1,THING) :- turn(TURN), ladlestirred_t(TURN,THING), not action_t(TURN,stir,THING,STIRRER), type(STIRRER,borpulus).
whisked_t(TURN+1,THING) :- turn(TURN), whisked_t(TURN,THING), not action_t(TURN,stir,THING,STIRRER), type(STIRRER,ladle).
whisked_t(TURN+1,THING) :- turn(TURN), whisked_t(TURN,THING), not action_t(TURN,stir,THING,STIRRER), type(STIRRER,spoon).
whisked_t(TURN+1,THING) :- turn(TURN), whisked_t(TURN,THING), not action_t(TURN,stir,THING,STIRRER), type(STIRRER,borpulus).
spoonstirred_t(TURN+1,THING) :- turn(TURN), spoonstirred_t(TURN,THING), not action_t(TURN,stir,THING,STIRRER), type(STIRRER,ladle).
spoonstirred_t(TURN+1,THING) :- turn(TURN), spoonstirred_t(TURN,THING), not action_t(TURN,stir,THING,STIRRER), type(STIRRER,spoon).
spoonstirred_t(TURN+1,THING) :- turn(TURN), spoonstirred_t(TURN,THING), not action_t(TURN,stir,THING,STIRRER), type(STIRRER,whisk).
borpulusstirred_t(TURN+1,THING) :- turn(TURN), borpulusstirred_t(TURN,THING), not action_t(TURN,stir,THING,STIRRER), type(STIRRER,ladle).
borpulusstirred_t(TURN+1,THING) :- turn(TURN), borpulusstirred_t(TURN,THING), not action_t(TURN,stir,THING,STIRRER), type(STIRRER,spoon).
borpulusstirred_t(TURN+1,THING) :- turn(TURN), borpulusstirred_t(TURN,THING), not action_t(TURN,stir,THING,STIRRER), type(STIRRER,whisk).