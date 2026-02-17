#ifndef MAP_PREFIX_UPPER_GLUE_ROOM_ROOM_NUMBER_H
#define MAP_PREFIX_UPPER_GLUE_ROOM_ROOM_NUMBER_H

#include "ultra64.h"
#include "scene.h"

// Objects

#define DEF_OBJECT(objectName)
#include "../table_objects_room_ROOM_NUMBER.h"
#undef DEF_OBJECT

extern s16 map_prefix_lower_room_ROOM_NUMBER_ObjectList[0
#define DEF_OBJECT(objectName) +1
#include "../table_objects_room_ROOM_NUMBER.h"
#undef DEF_OBJECT
];

// Actors

#define DEF_ACTOR(actorName, pos, rot, params)
#include "../table_actors_room_ROOM_NUMBER.h"
#undef DEF_ACTOR

extern ActorEntry map_prefix_lower_room_ROOM_NUMBER_ActorEntryList[0
#define DEF_ACTOR(actorName, pos, rot, params) +1
#include "../table_actors_room_ROOM_NUMBER.h"
#undef DEF_ACTOR
];

#endif
