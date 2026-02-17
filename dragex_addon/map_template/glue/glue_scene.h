#ifndef MAP_PREFIX_UPPER_GLUE_SCENE_H
#define MAP_PREFIX_UPPER_GLUE_SCENE_H

#include "environment.h"
#include "romfile.h"
#include "scene.h"

// Rooms

enum {
#define DEF_ROOM(enumName, segmentName) enumName,
#include "../table_rooms.h"
#undef DEF_ROOM
    MAP_PREFIX_UPPER_ROOM_MAX
};

extern RomFile map_prefix_lower_RoomList[0
#define DEF_ROOM(enumName, segmentName) +1
#include "../table_rooms.h"
#undef DEF_ROOM
];

// Spawns

enum {
#define DEF_SPAWN(spawnEnumName, roomEnumName, pos, rotY, params) spawnEnumName,
#include "../table_spawns.h"
#undef DEF_SPAWN
    MAP_PREFIX_UPPER_SPAWN_MAX
};

extern Spawn map_prefix_lower_SpawnList[MAP_PREFIX_UPPER_SPAWN_MAX];
extern ActorEntry map_prefix_lower_PlayerEntryList[MAP_PREFIX_UPPER_SPAWN_MAX];

// Environment light settings

enum {
#define DEF_ENV_LIGHT_SETTINGS(enumName, data) enumName,
#include "../table_envlightsettings.h"
#undef DEF_ENV_LIGHT_SETTINGS
    MAP_PREFIX_UPPER_ENV_LIGHT_SETTINGS_MAX
};

extern EnvLightSettings map_prefix_lower_EnvLightSettingsList[MAP_PREFIX_UPPER_ENV_LIGHT_SETTINGS_MAX];

// Cameras

enum {
#define DEF_CAMERA(enumName, camSetting) enumName,
#include "../table_cameras.h"
#undef DEF_CAMERA
    MAP_PREFIX_UPPER_CAMERA_MAX
};

#endif
