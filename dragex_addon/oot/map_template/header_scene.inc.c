#include "array_count.h"
#include "object.h"
#include "scene.h"
#include "sequence.h"
#include "skybox.h"

#include "exported/collision.h"
#include "glue/glue_scene.h"

SceneCmd map_prefix_lower_scene[] = {
    SCENE_CMD_SOUND_SETTINGS(0, NATURE_ID_NONE, NA_BGM_NO_MUSIC),
    SCENE_CMD_ROOM_LIST(ARRAY_COUNT(map_prefix_lower_RoomList), map_prefix_lower_RoomList),
    SCENE_CMD_TRANSITION_ACTOR_LIST(ARRAY_COUNT(map_prefix_lower_TransitionActorList), map_prefix_lower_TransitionActorList),
    SCENE_CMD_COL_HEADER(&map_prefix_lower_Col),
    SCENE_CMD_SPAWN_LIST(map_prefix_lower_SpawnList),
    SCENE_CMD_SPECIAL_FILES(NAVI_QUEST_HINTS_NONE, OBJECT_INVALID),
    SCENE_CMD_PLAYER_ENTRY_LIST(ARRAY_COUNT(map_prefix_lower_PlayerEntryList), map_prefix_lower_PlayerEntryList),
    SCENE_CMD_SKYBOX_SETTINGS(SKYBOX_NORMAL_SKY, 0, LIGHT_MODE_TIME),
    SCENE_CMD_ENV_LIGHT_SETTINGS(ARRAY_COUNT(map_prefix_lower_EnvLightSettingsList), map_prefix_lower_EnvLightSettingsList),
    SCENE_CMD_END(),
};
