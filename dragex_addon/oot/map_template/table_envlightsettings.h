#ifndef ENV_LIGHT_SETTINGS_DEFAULT
#define ENV_LIGHT_SETTINGS_DEFAULT                                             \
  {                                                                            \
    {255, 255, 255}, {127, 0, 0}, {0, 0, 0}, {127, 0, 0}, {0, 0, 0},           \
        {255, 255, 255}, BLEND_RATE_AND_FOG_NEAR(4, ENV_FOGNEAR_MAX), 12800,   \
  }
#endif

DEF_ENV_LIGHT_SETTINGS(MAP_PREFIX_UPPER_ENV_LIGHT_SETTINGS_0,
                       ENV_LIGHT_SETTINGS_DEFAULT)
DEF_ENV_LIGHT_SETTINGS(MAP_PREFIX_UPPER_ENV_LIGHT_SETTINGS_1,
                       ENV_LIGHT_SETTINGS_DEFAULT)
DEF_ENV_LIGHT_SETTINGS(MAP_PREFIX_UPPER_ENV_LIGHT_SETTINGS_2,
                       ENV_LIGHT_SETTINGS_DEFAULT)
DEF_ENV_LIGHT_SETTINGS(MAP_PREFIX_UPPER_ENV_LIGHT_SETTINGS_3,
                       ENV_LIGHT_SETTINGS_DEFAULT)
