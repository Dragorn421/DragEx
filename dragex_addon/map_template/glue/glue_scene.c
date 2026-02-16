#include "glue_scene.h"

#include "actor.h"
#include "environment.h"
#include "player.h" // for PLAYER_PARAMS in spawns_table.h
#include "romfile.h"
#include "scene.h"
#include "segment_symbols.h"

// Scene header

#include "../header_scene.inc.c"

// Rooms

#define DEF_ROOM(enumName, segmentName) DECLARE_ROM_SEGMENT(segmentName)
#include "../table_rooms.h"
#undef DEF_ROOM

RomFile map_prefix_lower_RoomList[] = {
#define DEF_ROOM(enumName, segmentName) ROM_FILE(segmentName),
#include "../table_rooms.h"
#undef DEF_ROOM
};

// Spawns

Spawn map_prefix_lower_SpawnList[] = {
#define DEF_SPAWN(spawnEnumName, roomEnumName, pos, rotY, params)              \
  {(spawnEnumName), (roomEnumName)},
#include "../table_spawns.h"
#undef DEF_SPAWN
};

ActorEntry map_prefix_lower_PlayerEntryList[] = {
#define DEF_SPAWN(spawnEnumName, roomEnumName, pos, rotY, params)              \
  {ACTOR_PLAYER, {pos}, {0, (rotY), 0}, params},
#include "../table_spawns.h"
#undef DEF_SPAWN
};

// Environment light settings

EnvLightSettings map_prefix_lower_EnvLightSettingsList[] = {
#define DEF_ENV_LIGHT_SETTINGS(enumName, data) data,
#include "../table_envlightsettings.h"
#undef DEF_ENV_LIGHT_SETTINGS
};

// Collision

enum {
#define DEF_SURFACETYPE(name, st0, st1, flagsA, flagsB)                        \
  MAP_PREFIX_UPPER_COL_##name##_FLAGS_A = (flagsA),                            \
  MAP_PREFIX_UPPER_COL_##name##_FLAGS_B = (flagsB),
#include "../table_polytypes.h"
#undef DEF_SURFACETYPE
  MAP_PREFIX_UPPER_COL_FLAGS_LAST
};

enum {
#define DEF_SURFACETYPE(name, st0, st1, flagsA, flagsB)                        \
  MAP_PREFIX_UPPER_SURFACETYPE_##name,
#include "../table_polytypes.h"
#undef DEF_SURFACETYPE
  MY_MAP_SURFACETYPE_MAX
};

SurfaceType map_prefix_lower_SurfaceTypes[] = {
#define DEF_SURFACETYPE(name, st0, st1, flagsA, flagsB) {{st0, st1}},
#include "../table_polytypes.h"
#undef DEF_SURFACETYPE
};

#include "../exported/collision.inc.c"
