#include "glue_room_ROOM_NUMBER.h"

#include "ultra64.h"
#include "scene.h"

// Room header

#include "../header_room_ROOM_NUMBER.inc.c"

// Objects

s16 map_prefix_lower_room_ROOM_NUMBER_ObjectList[] = {
#define DEF_OBJECT(objectName) (objectName),
#include "../table_objects_room_ROOM_NUMBER.h"
#undef DEF_OBJECT
};

// Actors

ActorEntry map_prefix_lower_room_ROOM_NUMBER_ActorEntryList[] = {
#define DEF_ACTOR(actorName, pos, rot, params)                                 \
  {(actorName), {pos}, {rot}, (params)},
#include "../table_actors_room_ROOM_NUMBER.h"
#undef DEF_ACTOR
};

// Room shape

#include "../exported/room_ROOM_NUMBER_shape.inc.c"
