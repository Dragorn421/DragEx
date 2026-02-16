#include "stdbool.h"
#include "room.h"
#include "scene.h"

#include "exported/room_ROOM_NUMBER_shape.h"

SceneCmd map_prefix_lower_room_ROOM_NUMBER[] = {
    SCENE_CMD_ECHO_SETTINGS(10),
    SCENE_CMD_ROOM_BEHAVIOR(ROOM_TYPE_NORMAL, ROOM_ENV_DEFAULT, LENS_MODE_SHOW_ACTORS, false),
    SCENE_CMD_SKYBOX_DISABLES(false, false),
    SCENE_CMD_TIME_SETTINGS(0xFF, 0xFF, 0),
    SCENE_CMD_ROOM_SHAPE(&map_prefix_lower_room_ROOM_NUMBER_RoomShape),
    SCENE_CMD_END(),
};
