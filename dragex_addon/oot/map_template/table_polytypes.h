#include "bgcheck.h"
#include "glue/glue_scene.h"

/*
 * DEF_SURFACETYPE(name, surfaceType0, surfaceType1, flagsA, flagsB)
 * - `name` is the name of the surface type: it can be used in the DragEx OoT
 *   Collision panel in the material properties.
 * - `surfaceType0` and `surfaceType1` are the surface type properties
 * - `flagsA` can be set to a combination of `COLPOLY_IGNORE_*` flags
 * - `flagsB` can be set to 0 or the `COLPOLY_IS_FLOOR_CONVEYOR` flag
 */

DEF_SURFACETYPE(DEFAULT,
                SURFACETYPE0(MAP_PREFIX_UPPER_CAMERA_DEFAULT, 0, FLOOR_TYPE_0,
                             0, WALL_TYPE_0, FLOOR_PROPERTY_0, false, false),
                SURFACETYPE1(SURFACE_MATERIAL_DIRT, FLOOR_EFFECT_0, 31, 1,
                             false, CONVEYOR_SPEED_DISABLED, 0, false),
                COLPOLY_IGNORE_NONE, 0)
