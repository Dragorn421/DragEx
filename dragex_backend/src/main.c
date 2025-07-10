#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "exporter.h"

#include "../build_id.h"

#ifndef ARRAY_COUNT
#define ARRAY_COUNT(arr) (sizeof(arr) / sizeof(arr[0]))
#endif

/*
 * Given a string in the `var##_name` variable, find the string in the
 * `names` array and store its index into the `var` variable.
 * If the string is not found, raise a Python exception and return.
 */
#define NAME_TO_ENUM(var, names)                                               \
    {                                                                          \
        var = 0;                                                               \
        bool success = false;                                                  \
        for (size_t i = 0; i < ARRAY_COUNT(names); i++) {                      \
            if (names[i] == NULL)                                              \
                continue;                                                      \
            if (strcmp(var##_name, names[i]) == 0) {                           \
                success = true;                                                \
                var = i;                                                       \
            }                                                                  \
        }                                                                      \
        if (!success) {                                                        \
            PyErr_Format(PyExc_ValueError, "Bad " #var " name: %s",            \
                         var##_name);                                          \
            return -1;                                                         \
        }                                                                      \
    }

static PyObject *get_build_id(PyObject *self, PyObject *args) {
    return PyLong_FromLong(BUILD_ID);
}

struct MaterialInfoImageObject {
    PyObject_HEAD

        struct MaterialInfoImage image;
};

static void MaterialInfoImage_dealloc(PyObject *_self) {
    struct MaterialInfoImageObject *self =
        (struct MaterialInfoImageObject *)_self;

    printf("MaterialInfoImage_dealloc %s\n", self->image.c_identifier == NULL
                                                 ? "(NULL c_identifier)"
                                                 : self->image.c_identifier);

    free(self->image.c_identifier);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *MaterialInfoImage_new(PyTypeObject *type, PyObject *args,
                                       PyObject *kwds) {
    struct MaterialInfoImageObject *self;

    printf("MaterialInfoImage_new\n");

    self = (struct MaterialInfoImageObject *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->image.c_identifier = NULL;
    }
    return (PyObject *)self;
}

static int MaterialInfoImage_init(PyObject *_self, PyObject *args,
                                  PyObject *kwds) {
    struct MaterialInfoImageObject *self =
        (struct MaterialInfoImageObject *)_self;
    static char *kwlist[] = {
        "c_identifier",
        "width",
        "height",
        NULL,
    };
    char *c_identifier;
    int width;
    int height;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "sii", kwlist, &c_identifier,
                                     &width, &height))
        return -1;

    self->image.c_identifier = strdup(c_identifier);
    self->image.width = width;
    self->image.height = height;

    return 0;
}

static PyTypeObject MaterialInfoImageType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.MaterialInfoImage",
    .tp_doc = PyDoc_STR("material info image"),
    .tp_basicsize = sizeof(struct MaterialInfoImageObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = MaterialInfoImage_new,
    .tp_init = MaterialInfoImage_init,
    .tp_dealloc = MaterialInfoImage_dealloc,
};

struct MaterialInfoOtherModesObject {
    PyObject_HEAD

        struct MaterialInfoOtherModes other_modes;
};

static int MaterialInfoOtherModes_init(PyObject *_self, PyObject *args,
                                       PyObject *kwds) {
    struct MaterialInfoOtherModesObject *self =
        (struct MaterialInfoOtherModesObject *)_self;
    static char *kwlist[] = {
        "atomic_prim",      "cycle_type",
        "persp_tex_en",     "detail_tex_en",
        "sharpen_tex_en",   "tex_lod_en",
        "tlut_en",          "tlut_type",

        "sample_type",      "mid_texel",
        "bi_lerp_0",        "bi_lerp_1",
        "convert_one",      "key_en",
        "rgb_dither_sel",   "alpha_dither_sel",

        "bl_m1a_0",         "bl_m1a_1",
        "bl_m1b_0",         "bl_m1b_1",
        "bl_m2a_0",         "bl_m2a_1",
        "bl_m2b_0",         "bl_m2b_1",

        "force_blend",      "alpha_cvg_select",
        "cvg_x_alpha",      "z_mode",
        "cvg_dest",         "color_on_cvg",

        "image_read_en",    "z_update_en",
        "z_compare_en",     "antialias_en",
        "z_source_sel",     "dither_alpha_en",
        "alpha_compare_en", NULL,
    };
    int atomic_prim;
    char *cycle_type_name;
    int persp_tex_en;
    int detail_tex_en;
    int sharpen_tex_en;
    int tex_lod_en;
    int tlut_en;
    int tlut_type;

    int sample_type;
    int mid_texel;
    int bi_lerp_0;
    int bi_lerp_1;
    int convert_one;
    int key_en;
    char *rgb_dither_sel_name;
    char *alpha_dither_sel_name;

    char *bl_m1a_0_name;
    char *bl_m1a_1_name;
    char *bl_m1b_0_name;
    char *bl_m1b_1_name;
    char *bl_m2a_0_name;
    char *bl_m2a_1_name;
    char *bl_m2b_0_name;
    char *bl_m2b_1_name;

    int force_blend;
    int alpha_cvg_select;
    int cvg_x_alpha;
    char *z_mode_name;
    char *cvg_dest_name;
    int color_on_cvg;

    int image_read_en;
    int z_update_en;
    int z_compare_en;
    int antialias_en;
    int z_source_sel;
    int dither_alpha_en;
    int alpha_compare_en;

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds,
            "pspppppp"
            "ppppppss"
            "ssssssss"
            "pppssp"
            "ppppppp",
            kwlist,

            &atomic_prim, &cycle_type_name, &persp_tex_en, &detail_tex_en,
            &sharpen_tex_en, &tex_lod_en, &tlut_en, &tlut_type,

            &sample_type, &mid_texel, &bi_lerp_0, &bi_lerp_1, &convert_one,
            &key_en, &rgb_dither_sel_name, &alpha_dither_sel_name,

            &bl_m1a_0_name, &bl_m1a_1_name, &bl_m1b_0_name, &bl_m1b_1_name,
            &bl_m2a_0_name, &bl_m2a_1_name, &bl_m2b_0_name, &bl_m2b_1_name,

            &force_blend, &alpha_cvg_select, &cvg_x_alpha, &z_mode_name,
            &cvg_dest_name, &color_on_cvg,

            &image_read_en, &z_update_en, &z_compare_en, &antialias_en,
            &z_source_sel, &dither_alpha_en, &alpha_compare_en))
        return -1;

    static const char *cycle_type_names[] = {
        [RDP_OM_CYCLE_TYPE_1CYCLE] = "1CYCLE",
        [RDP_OM_CYCLE_TYPE_2CYCLE] = "2CYCLE",
        [RDP_OM_CYCLE_TYPE_COPY] = "COPY",
        [RDP_OM_CYCLE_TYPE_FILL] = "FILL",
    };
    enum rdp_om_cycle_type cycle_type;
    NAME_TO_ENUM(cycle_type, cycle_type_names);

    static const char *rgb_dither_sel_names[] = {
        [RDP_OM_RGB_DITHER_MAGIC_SQUARE] = "MAGIC_SQUARE",
        [RDP_OM_RGB_DITHER_BAYER] = "BAYER",
        [RDP_OM_RGB_DITHER_RANDOM_NOISE] = "RANDOM_NOISE",
        [RDP_OM_RGB_DITHER_NONE] = "NONE",
    };
    enum rdp_om_rgb_dither rgb_dither_sel;
    NAME_TO_ENUM(rgb_dither_sel, rgb_dither_sel_names);

    static const char *alpha_dither_sel_names[] = {
        [RDP_OM_ALPHA_DITHER_SAME_AS_RGB] = "SAME_AS_RGB",
        [RDP_OM_ALPHA_DITHER_INVERSE_OF_RGB] = "INVERSE_OF_RGB",
        [RDP_OM_ALPHA_DITHER_RANDOM_NOISE] = "RANDOM_NOISE",
        [RDP_OM_ALPHA_DITHER_NONE] = "NONE",
    };
    enum rdp_om_alpha_dither alpha_dither_sel;
    NAME_TO_ENUM(alpha_dither_sel, alpha_dither_sel_names);

    static const char *blender_P_M_inputs_names[] = {
        [RDP_OM_BLENDER_P_M_INPUTS_INPUT] = "INPUT",
        [RDP_OM_BLENDER_P_M_INPUTS_MEMORY] = "MEMORY",
        [RDP_OM_BLENDER_P_M_INPUTS_BLEND_COLOR] = "BLEND_COLOR",
        [RDP_OM_BLENDER_P_M_INPUTS_FOG_COLOR] = "FOG_COLOR",
    };
    static const char *blender_A_inputs_names[] = {
        [RDP_OM_BLENDER_A_INPUTS_INPUT_ALPHA] = "INPUT_ALPHA",
        [RDP_OM_BLENDER_A_INPUTS_FOG_ALPHA] = "FOG_ALPHA",
        [RDP_OM_BLENDER_A_INPUTS_SHADE_ALPHA] = "SHADE_ALPHA",
        [RDP_OM_BLENDER_A_INPUTS_0] = "0",
    };
    static const char *blender_B_inputs_names[] = {
        [RDP_OM_BLENDER_B_INPUTS_1_MINUS_A] = "1_MINUS_A",
        [RDP_OM_BLENDER_B_INPUTS_MEMORY_COVERAGE] = "MEMORY_COVERAGE",
        [RDP_OM_BLENDER_B_INPUTS_1] = "1",
        [RDP_OM_BLENDER_B_INPUTS_0] = "0",
    };
    enum rdp_om_blender_P_M_inputs bl_m1a_0;
    NAME_TO_ENUM(bl_m1a_0, blender_P_M_inputs_names);
    enum rdp_om_blender_P_M_inputs bl_m1a_1;
    NAME_TO_ENUM(bl_m1a_1, blender_P_M_inputs_names);
    enum rdp_om_blender_A_inputs bl_m1b_0;
    NAME_TO_ENUM(bl_m1b_0, blender_A_inputs_names);
    enum rdp_om_blender_A_inputs bl_m1b_1;
    NAME_TO_ENUM(bl_m1b_1, blender_A_inputs_names);
    enum rdp_om_blender_P_M_inputs bl_m2a_0;
    NAME_TO_ENUM(bl_m2a_0, blender_P_M_inputs_names);
    enum rdp_om_blender_P_M_inputs bl_m2a_1;
    NAME_TO_ENUM(bl_m2a_1, blender_P_M_inputs_names);
    enum rdp_om_blender_B_inputs bl_m2b_0;
    NAME_TO_ENUM(bl_m2b_0, blender_B_inputs_names);
    enum rdp_om_blender_B_inputs bl_m2b_1;
    NAME_TO_ENUM(bl_m2b_1, blender_B_inputs_names);

    static const char *z_mode_names[] = {
        [RDP_OM_Z_MODE_OPAQUE] = "OPAQUE",
        [RDP_OM_Z_MODE_INTERPENETRATING] = "INTERPENETRATING",
        [RDP_OM_Z_MODE_TRANSPARENT] = "TRANSPARENT",
        [RDP_OM_Z_MODE_DECAL] = "DECAL",
    };
    enum rdp_om_z_mode z_mode;
    NAME_TO_ENUM(z_mode, z_mode_names);

    static const char *cvg_dest_names[] = {
        [RDP_OM_CVG_DEST_CLAMP] = "CLAMP",
        [RDP_OM_CVG_DEST_WRAP] = "WRAP",
        [RDP_OM_CVG_DEST_FULL] = "FULL",
        [RDP_OM_CVG_DEST_SAVE] = "SAVE",
    };
    enum rdp_om_cvg_dest cvg_dest;
    NAME_TO_ENUM(cvg_dest, cvg_dest_names);

    self->other_modes.atomic_prim = atomic_prim;
    self->other_modes.cycle_type = cycle_type;
    self->other_modes.persp_tex_en = persp_tex_en;
    self->other_modes.detail_tex_en = detail_tex_en;
    self->other_modes.sharpen_tex_en = sharpen_tex_en;
    self->other_modes.tex_lod_en = tex_lod_en;
    self->other_modes.tlut_en = tlut_en;
    self->other_modes.tlut_type = tlut_type;

    self->other_modes.sample_type = sample_type;
    self->other_modes.mid_texel = mid_texel;
    self->other_modes.bi_lerp_0 = bi_lerp_0;
    self->other_modes.bi_lerp_1 = bi_lerp_1;
    self->other_modes.convert_one = convert_one;
    self->other_modes.key_en = key_en;
    self->other_modes.rgb_dither_sel = rgb_dither_sel;
    self->other_modes.alpha_dither_sel = alpha_dither_sel;

    self->other_modes.bl_m1a_0 = bl_m1a_0;
    self->other_modes.bl_m1a_1 = bl_m1a_1;
    self->other_modes.bl_m1b_0 = bl_m1b_0;
    self->other_modes.bl_m1b_1 = bl_m1b_1;
    self->other_modes.bl_m2a_0 = bl_m2a_0;
    self->other_modes.bl_m2a_1 = bl_m2a_1;
    self->other_modes.bl_m2b_0 = bl_m2b_0;
    self->other_modes.bl_m2b_1 = bl_m2b_1;

    self->other_modes.force_blend = force_blend;
    self->other_modes.alpha_cvg_select = alpha_cvg_select;
    self->other_modes.cvg_x_alpha = cvg_x_alpha;
    self->other_modes.z_mode = z_mode;
    self->other_modes.cvg_dest = cvg_dest;
    self->other_modes.color_on_cvg = color_on_cvg;

    self->other_modes.image_read_en = image_read_en;
    self->other_modes.z_update_en = z_update_en;
    self->other_modes.z_compare_en = z_compare_en;
    self->other_modes.antialias_en = antialias_en;
    self->other_modes.z_source_sel = z_source_sel;
    self->other_modes.dither_alpha_en = dither_alpha_en;
    self->other_modes.alpha_compare_en = alpha_compare_en;

    return 0;
}

static PyTypeObject MaterialInfoOtherModesType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.MaterialInfoOtherModes",
    .tp_doc = PyDoc_STR("material info other modes"),
    .tp_basicsize = sizeof(struct MaterialInfoOtherModesObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = MaterialInfoOtherModes_init,
};

struct MaterialInfoTileObject {
    PyObject_HEAD

        struct MaterialInfoImageObject *image_object;
    struct MaterialInfoTile tile;
};

static void MaterialInfoTile_dealloc(PyObject *_self) {
    struct MaterialInfoTileObject *self =
        (struct MaterialInfoTileObject *)_self;

    printf("MaterialInfoTile_dealloc\n");

    Py_XDECREF(self->image_object);
}

static PyObject *MaterialInfoTile_new(PyTypeObject *type, PyObject *args,
                                      PyObject *kwds) {
    struct MaterialInfoTileObject *self;

    printf("MaterialInfoTile_new\n");

    self = (struct MaterialInfoTileObject *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->image_object = NULL;
    }
    return (PyObject *)self;
}

static int converter_MaterialInfoImage_or_None(PyObject *obj, void *_result) {
    struct MaterialInfoImageObject **result =
        (struct MaterialInfoImageObject **)_result;

    if (obj == Py_None) {
        *result = NULL;
        return 1;
    }

    if (PyObject_TypeCheck(obj, &MaterialInfoImageType)) {
        *result = (struct MaterialInfoImageObject *)obj;
        return 1;
    } else {
        PyErr_Format(PyExc_TypeError, "Object is not None or a %s",
                     MaterialInfoImageType.tp_name);
        return 0;
    }
}

static int MaterialInfoTile_init(PyObject *_self, PyObject *args,
                                 PyObject *kwds) {
    struct MaterialInfoTileObject *self =
        (struct MaterialInfoTileObject *)_self;
    static char *kwlist[] = {
        "image",         "format",        "size",         "line",
        "address",       "palette",       "clamp_T",      "mirror_T",
        "mask_T",        "shift_T",       "clamp_S",      "mirror_S",
        "mask_S",        "shift_S",       "upper_left_S", "upper_left_T",
        "lower_right_S", "lower_right_T", NULL,
    };
    struct MaterialInfoImageObject *image;
    char *format_name;
    char *size_name;
    int line;
    int address;
    int palette;
    int clamp_T;
    int mirror_T;
    int mask_T;
    int shift_T;
    int clamp_S;
    int mirror_S;
    int mask_S;
    int shift_S;

    float upper_left_S;
    float upper_left_T;
    float lower_right_S;
    float lower_right_T;

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds,
            "O&"
            "ssiiippiippii"
            "ffff",
            kwlist,

            converter_MaterialInfoImage_or_None, &image,

            &format_name, &size_name, &line, &address, &palette, &clamp_T,
            &mirror_T, &mask_T, &shift_T, &clamp_S, &mirror_S, &mask_S,
            &shift_S,

            &upper_left_S, &upper_left_T, &lower_right_S, &lower_right_T))
        return -1;

    static const char *format_names[] = {
        [RDP_TILE_FORMAT_RGBA] = "RGBA", [RDP_TILE_FORMAT_YUV] = "YUV",
        [RDP_TILE_FORMAT_CI] = "CI",     [RDP_TILE_FORMAT_IA] = "IA",
        [RDP_TILE_FORMAT_I] = "I",
    };
    enum rdp_tile_format format;
    NAME_TO_ENUM(format, format_names);

    static const char *size_names[] = {
        [RDP_TILE_SIZE_4] = "4",
        [RDP_TILE_SIZE_8] = "8",
        [RDP_TILE_SIZE_16] = "16",
        [RDP_TILE_SIZE_32] = "32",
    };
    enum rdp_tile_size size;
    NAME_TO_ENUM(size, size_names);

    if (image == NULL) {
        self->tile.image = NULL;
    } else {
        Py_INCREF(image);
        self->image_object = image;

        self->tile.image = &image->image;
    }

    self->tile.format = format;
    self->tile.size = size;
    self->tile.line = line;
    self->tile.address = address;
    self->tile.palette = palette;
    self->tile.clamp_T = clamp_T;
    self->tile.mirror_T = mirror_T;
    self->tile.mask_T = mask_T;
    self->tile.shift_T = shift_T;
    self->tile.clamp_S = clamp_S;
    self->tile.mirror_S = mirror_S;
    self->tile.mask_S = mask_S;
    self->tile.shift_S = shift_S;

    self->tile.upper_left_S = upper_left_S;
    self->tile.upper_left_T = upper_left_T;
    self->tile.lower_right_S = lower_right_S;
    self->tile.lower_right_T = lower_right_T;

    return 0;
}

static PyTypeObject MaterialInfoTileType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.MaterialInfoTile",
    .tp_doc = PyDoc_STR("material info tile"),
    .tp_basicsize = sizeof(struct MaterialInfoTileObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = MaterialInfoTile_new,
    .tp_init = MaterialInfoTile_init,
    .tp_dealloc = MaterialInfoTile_dealloc,
};

struct MaterialInfoCombinerObject {
    PyObject_HEAD

        struct MaterialInfoCombiner combiner;
};

static int MaterialInfoCombiner_init(PyObject *_self, PyObject *args,
                                     PyObject *kwds) {
    struct MaterialInfoCombinerObject *self =
        (struct MaterialInfoCombinerObject *)_self;
    static char *kwlist[] = {
        "rgb_A_0",   "rgb_B_0",   "rgb_C_0",   "rgb_D_0",   "alpha_A_0",
        "alpha_B_0", "alpha_C_0", "alpha_D_0", "rgb_A_1",   "rgb_B_1",
        "rgb_C_1",   "rgb_D_1",   "alpha_A_1", "alpha_B_1", "alpha_C_1",
        "alpha_D_1", NULL,
    };
    char *rgb_A_0_name;
    char *rgb_B_0_name;
    char *rgb_C_0_name;
    char *rgb_D_0_name;
    char *alpha_A_0_name;
    char *alpha_B_0_name;
    char *alpha_C_0_name;
    char *alpha_D_0_name;
    char *rgb_A_1_name;
    char *rgb_B_1_name;
    char *rgb_C_1_name;
    char *rgb_D_1_name;
    char *alpha_A_1_name;
    char *alpha_B_1_name;
    char *alpha_C_1_name;
    char *alpha_D_1_name;

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds,
            "ssss"
            "ssss"
            "ssss"
            "ssss",
            kwlist,

            &rgb_A_0_name, &rgb_B_0_name, &rgb_C_0_name, &rgb_D_0_name,
            &alpha_A_0_name, &alpha_B_0_name, &alpha_C_0_name, &alpha_D_0_name,
            &rgb_A_1_name, &rgb_B_1_name, &rgb_C_1_name, &rgb_D_1_name,
            &alpha_A_1_name, &alpha_B_1_name, &alpha_C_1_name, &alpha_D_1_name))
        return -1;

    static const char *rgb_A_names[] = {
        [RDP_COMBINER_RGB_A_INPUTS_COMBINED] = "COMBINED",
        [RDP_COMBINER_RGB_A_INPUTS_TEX0] = "TEX0",
        [RDP_COMBINER_RGB_A_INPUTS_TEX1] = "TEX1",
        [RDP_COMBINER_RGB_A_INPUTS_PRIMITIVE] = "PRIMITIVE",
        [RDP_COMBINER_RGB_A_INPUTS_SHADE] = "SHADE",
        [RDP_COMBINER_RGB_A_INPUTS_ENVIRONMENT] = "ENVIRONMENT",
        [RDP_COMBINER_RGB_A_INPUTS_1] = "1",
        [RDP_COMBINER_RGB_A_INPUTS_NOISE] = "NOISE",
        [RDP_COMBINER_RGB_A_INPUTS_0] = "0",
    };
    static const char *rgb_B_names[] = {
        [RDP_COMBINER_RGB_B_INPUTS_COMBINED] = "COMBINED",
        [RDP_COMBINER_RGB_B_INPUTS_TEX0] = "TEX0",
        [RDP_COMBINER_RGB_B_INPUTS_TEX1] = "TEX1",
        [RDP_COMBINER_RGB_B_INPUTS_PRIMITIVE] = "PRIMITIVE",
        [RDP_COMBINER_RGB_B_INPUTS_SHADE] = "SHADE",
        [RDP_COMBINER_RGB_B_INPUTS_ENVIRONMENT] = "ENVIRONMENT",
        [RDP_COMBINER_RGB_B_INPUTS_CENTER] = "CENTER",
        [RDP_COMBINER_RGB_B_INPUTS_K4] = "K4",
        [RDP_COMBINER_RGB_B_INPUTS_0] = "0",
    };
    static const char *rgb_C_names[] = {
        [RDP_COMBINER_RGB_C_INPUTS_COMBINED] = "COMBINED",
        [RDP_COMBINER_RGB_C_INPUTS_TEX0] = "TEX0",
        [RDP_COMBINER_RGB_C_INPUTS_TEX1] = "TEX1",
        [RDP_COMBINER_RGB_C_INPUTS_PRIMITIVE] = "PRIMITIVE",
        [RDP_COMBINER_RGB_C_INPUTS_SHADE] = "SHADE",
        [RDP_COMBINER_RGB_C_INPUTS_ENVIRONMENT] = "ENVIRONMENT",
        [RDP_COMBINER_RGB_C_INPUTS_SCALE] = "SCALE",
        [RDP_COMBINER_RGB_C_INPUTS_COMBINED_ALPHA] = "COMBINED_ALPHA",
        [RDP_COMBINER_RGB_C_INPUTS_TEX0_ALPHA] = "TEX0_ALPHA",
        [RDP_COMBINER_RGB_C_INPUTS_TEX1_ALPHA] = "TEX1_ALPHA",
        [RDP_COMBINER_RGB_C_INPUTS_PRIMITIVE_ALPHA] = "PRIMITIVE_ALPHA",
        [RDP_COMBINER_RGB_C_INPUTS_SHADE_ALPHA] = "SHADE_ALPHA",
        [RDP_COMBINER_RGB_C_INPUTS_ENVIRONMENT_ALPHA] = "ENVIRONMENT_ALPHA",
        [RDP_COMBINER_RGB_C_INPUTS_LOD_FRACTION] = "LOD_FRACTION",
        [RDP_COMBINER_RGB_C_INPUTS_PRIM_LOD_FRAC] = "PRIM_LOD_FRAC",
        [RDP_COMBINER_RGB_C_INPUTS_K5] = "K5",
        [RDP_COMBINER_RGB_C_INPUTS_0] = "0",
    };
    static const char *rgb_D_names[] = {
        [RDP_COMBINER_RGB_D_INPUTS_COMBINED] = "COMBINED",
        [RDP_COMBINER_RGB_D_INPUTS_TEX0] = "TEX0",
        [RDP_COMBINER_RGB_D_INPUTS_TEX1] = "TEX1",
        [RDP_COMBINER_RGB_D_INPUTS_PRIMITIVE] = "PRIMITIVE",
        [RDP_COMBINER_RGB_D_INPUTS_SHADE] = "SHADE",
        [RDP_COMBINER_RGB_D_INPUTS_ENVIRONMENT] = "ENVIRONMENT",
        [RDP_COMBINER_RGB_D_INPUTS_1] = "1",
        [RDP_COMBINER_RGB_D_INPUTS_0] = "0",
    };

    static const char *alpha_A_names[] = {
        [RDP_COMBINER_ALPHA_A_INPUTS_COMBINED] = "COMBINED",
        [RDP_COMBINER_ALPHA_A_INPUTS_TEX0] = "TEX0",
        [RDP_COMBINER_ALPHA_A_INPUTS_TEX1] = "TEX1",
        [RDP_COMBINER_ALPHA_A_INPUTS_PRIMITIVE] = "PRIMITIVE",
        [RDP_COMBINER_ALPHA_A_INPUTS_SHADE] = "SHADE",
        [RDP_COMBINER_ALPHA_A_INPUTS_ENVIRONMENT] = "ENVIRONMENT",
        [RDP_COMBINER_ALPHA_A_INPUTS_1] = "1",
        [RDP_COMBINER_ALPHA_A_INPUTS_0] = "0",
    };
    static const char *alpha_B_names[] = {
        [RDP_COMBINER_ALPHA_B_INPUTS_COMBINED] = "COMBINED",
        [RDP_COMBINER_ALPHA_B_INPUTS_TEX0] = "TEX0",
        [RDP_COMBINER_ALPHA_B_INPUTS_TEX1] = "TEX1",
        [RDP_COMBINER_ALPHA_B_INPUTS_PRIMITIVE] = "PRIMITIVE",
        [RDP_COMBINER_ALPHA_B_INPUTS_SHADE] = "SHADE",
        [RDP_COMBINER_ALPHA_B_INPUTS_ENVIRONMENT] = "ENVIRONMENT",
        [RDP_COMBINER_ALPHA_B_INPUTS_1] = "1",
        [RDP_COMBINER_ALPHA_B_INPUTS_0] = "0",
    };
    static const char *alpha_C_names[] = {
        [RDP_COMBINER_ALPHA_C_INPUTS_LOD_FRACTION] = "LOD_FRACTION",
        [RDP_COMBINER_ALPHA_C_INPUTS_TEX0] = "TEX0",
        [RDP_COMBINER_ALPHA_C_INPUTS_TEX1] = "TEX1",
        [RDP_COMBINER_ALPHA_C_INPUTS_PRIMITIVE] = "PRIMITIVE",
        [RDP_COMBINER_ALPHA_C_INPUTS_SHADE] = "SHADE",
        [RDP_COMBINER_ALPHA_C_INPUTS_ENVIRONMENT] = "ENVIRONMENT",
        [RDP_COMBINER_ALPHA_C_INPUTS_PRIM_LOD_FRAC] = "PRIM_LOD_FRAC",
        [RDP_COMBINER_ALPHA_C_INPUTS_0] = "0",
    };
    static const char *alpha_D_names[] = {
        [RDP_COMBINER_ALPHA_D_INPUTS_COMBINED] = "COMBINED",
        [RDP_COMBINER_ALPHA_D_INPUTS_TEX0] = "TEX0",
        [RDP_COMBINER_ALPHA_D_INPUTS_TEX1] = "TEX1",
        [RDP_COMBINER_ALPHA_D_INPUTS_PRIMITIVE] = "PRIMITIVE",
        [RDP_COMBINER_ALPHA_D_INPUTS_SHADE] = "SHADE",
        [RDP_COMBINER_ALPHA_D_INPUTS_ENVIRONMENT] = "ENVIRONMENT",
        [RDP_COMBINER_ALPHA_D_INPUTS_1] = "1",
        [RDP_COMBINER_ALPHA_D_INPUTS_0] = "0",
    };

    enum rdp_combiner_rgb_A_inputs rgb_A_0;
    NAME_TO_ENUM(rgb_A_0, rgb_A_names);
    enum rdp_combiner_rgb_B_inputs rgb_B_0;
    NAME_TO_ENUM(rgb_B_0, rgb_B_names);
    enum rdp_combiner_rgb_C_inputs rgb_C_0;
    NAME_TO_ENUM(rgb_C_0, rgb_C_names);
    enum rdp_combiner_rgb_D_inputs rgb_D_0;
    NAME_TO_ENUM(rgb_D_0, rgb_D_names);
    enum rdp_combiner_alpha_A_inputs alpha_A_0;
    NAME_TO_ENUM(alpha_A_0, alpha_A_names);
    enum rdp_combiner_alpha_B_inputs alpha_B_0;
    NAME_TO_ENUM(alpha_B_0, alpha_B_names);
    enum rdp_combiner_alpha_C_inputs alpha_C_0;
    NAME_TO_ENUM(alpha_C_0, alpha_C_names);
    enum rdp_combiner_alpha_D_inputs alpha_D_0;
    NAME_TO_ENUM(alpha_D_0, alpha_D_names);
    enum rdp_combiner_rgb_A_inputs rgb_A_1;
    NAME_TO_ENUM(rgb_A_1, rgb_A_names);
    enum rdp_combiner_rgb_B_inputs rgb_B_1;
    NAME_TO_ENUM(rgb_B_1, rgb_B_names);
    enum rdp_combiner_rgb_C_inputs rgb_C_1;
    NAME_TO_ENUM(rgb_C_1, rgb_C_names);
    enum rdp_combiner_rgb_D_inputs rgb_D_1;
    NAME_TO_ENUM(rgb_D_1, rgb_D_names);
    enum rdp_combiner_alpha_A_inputs alpha_A_1;
    NAME_TO_ENUM(alpha_A_1, alpha_A_names);
    enum rdp_combiner_alpha_B_inputs alpha_B_1;
    NAME_TO_ENUM(alpha_B_1, alpha_B_names);
    enum rdp_combiner_alpha_C_inputs alpha_C_1;
    NAME_TO_ENUM(alpha_C_1, alpha_C_names);
    enum rdp_combiner_alpha_D_inputs alpha_D_1;
    NAME_TO_ENUM(alpha_D_1, alpha_D_names);

    self->combiner.rgb_A_0 = rgb_A_0;
    self->combiner.rgb_B_0 = rgb_B_0;
    self->combiner.rgb_C_0 = rgb_C_0;
    self->combiner.rgb_D_0 = rgb_D_0;
    self->combiner.alpha_A_0 = alpha_A_0;
    self->combiner.alpha_B_0 = alpha_B_0;
    self->combiner.alpha_C_0 = alpha_C_0;
    self->combiner.alpha_D_0 = alpha_D_0;
    self->combiner.rgb_A_1 = rgb_A_1;
    self->combiner.rgb_B_1 = rgb_B_1;
    self->combiner.rgb_C_1 = rgb_C_1;
    self->combiner.rgb_D_1 = rgb_D_1;
    self->combiner.alpha_A_1 = alpha_A_1;
    self->combiner.alpha_B_1 = alpha_B_1;
    self->combiner.alpha_C_1 = alpha_C_1;
    self->combiner.alpha_D_1 = alpha_D_1;

    return 0;
}

static PyTypeObject MaterialInfoCombinerType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.MaterialInfoCombiner",
    .tp_doc = PyDoc_STR("material info geometry mode"),
    .tp_basicsize = sizeof(struct MaterialInfoCombinerObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = MaterialInfoCombiner_init,
};

struct MaterialInfoValsObject {
    PyObject_HEAD

        struct MaterialInfoVals vals;
};

static int MaterialInfoVals_init(PyObject *_self, PyObject *args,
                                 PyObject *kwds) {
    struct MaterialInfoValsObject *self =
        (struct MaterialInfoValsObject *)_self;
    static char *kwlist[] = {
        "primitive_depth_z", "primitive_depth_dz", "fog_color",
        "blend_color",       "min_level",          "prim_lod_frac",
        "primitive_color",   "environment_color",  NULL,
    };
    int primitive_depth_z;
    int primitive_depth_dz;
    struct rgbaf fog_color;
    struct rgbaf blend_color;
    int min_level;
    int prim_lod_frac;
    struct rgbaf primitive_color;
    struct rgbaf environment_color;

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds,
            "ii"
            "(ffff)"
            "(ffff)"
            "ii"
            "(ffff)"
            "(ffff)",
            kwlist,

            &primitive_depth_z, &primitive_depth_dz,

            &fog_color.r, &fog_color.g, &fog_color.b, &fog_color.a,

            &blend_color.r, &blend_color.g, &blend_color.b, &blend_color.a,

            &min_level, &prim_lod_frac,

            &primitive_color.r, &primitive_color.g, &primitive_color.b,
            &primitive_color.a,

            &environment_color.r, &environment_color.g, &environment_color.b,
            &environment_color.a))
        return -1;

    self->vals.primitive_depth_z = primitive_depth_z;
    self->vals.primitive_depth_dz = primitive_depth_dz;
    self->vals.fog_color = fog_color;
    self->vals.blend_color = blend_color;
    self->vals.min_level = min_level;
    self->vals.prim_lod_frac = prim_lod_frac;
    self->vals.primitive_color = primitive_color;
    self->vals.environment_color = environment_color;

    return 0;
}

static PyTypeObject MaterialInfoValsType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.MaterialInfoVals",
    .tp_doc = PyDoc_STR("material info vals"),
    .tp_basicsize = sizeof(struct MaterialInfoValsObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = MaterialInfoVals_init,
};

struct MaterialInfoGeometryModeObject {
    PyObject_HEAD

        struct MaterialInfoGeometryMode geometry_mode;
};

static int MaterialInfoGeometryMode_init(PyObject *_self, PyObject *args,
                                         PyObject *kwds) {
    struct MaterialInfoGeometryModeObject *self =
        (struct MaterialInfoGeometryModeObject *)_self;
    static char *kwlist[] = {
        "lighting",
        NULL,
    };
    int lighting;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "p", kwlist, &lighting))
        return -1;

    self->geometry_mode.lighting = !!lighting;
    return 0;
}

static PyTypeObject MaterialInfoGeometryModeType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.MaterialInfoGeometryMode",
    .tp_doc = PyDoc_STR("material info geometry mode"),
    .tp_basicsize = sizeof(struct MaterialInfoGeometryModeObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = MaterialInfoGeometryMode_init,
};

struct MaterialInfoObject {
    PyObject_HEAD

        struct MaterialInfoImageObject *image_objects[8];
    struct MaterialInfo mat_info;
};

static void MaterialInfo_dealloc(PyObject *_self) {
    struct MaterialInfoObject *self = (struct MaterialInfoObject *)_self;

    for (int i = 0; i < 8; i++)
        Py_XDECREF(self->image_objects[i]);

    free(self->mat_info.name);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *MaterialInfo_new(PyTypeObject *type, PyObject *args,
                                  PyObject *kwds) {
    struct MaterialInfoObject *self;
    self = (struct MaterialInfoObject *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->mat_info.name = NULL;
    }
    return (PyObject *)self;
}

struct MaterialInfoTileObjectSequenceInfo {
    struct MaterialInfoTileObject **buffer;
    Py_ssize_t len;
};

void free_MaterialInfoTileSequenceInfo(
    struct MaterialInfoTileObjectSequenceInfo *tile_infos) {

    for (Py_ssize_t i = 0; i < tile_infos->len; i++)
        Py_DECREF(tile_infos->buffer[i]);

    free(tile_infos->buffer);
}

int converter_MaterialInfoTileObject_sequence_len8(PyObject *obj,
                                                   void *_result) {
    Py_ssize_t len = PySequence_Length(obj);
    if (len < 0)
        return 0;
    if (len != 8) {
        PyErr_Format(PyExc_IndexError,
                     "Expected a sequence of length 8, not %ld", (long)len);
        return 0;
    }

    struct MaterialInfoTileObject **buffer =
        malloc(sizeof(struct MaterialInfoTileObject *[len]));
    // TODO check malloc
    for (Py_ssize_t i = 0; i < len; i++) {
        PyObject *item = PySequence_GetItem(obj, i);
        if (item == NULL) {
            for (Py_ssize_t j = 0; j < i; j++)
                Py_DECREF(buffer[j]);
            free(buffer);
            return 0;
        }

        if (PyObject_TypeCheck(item, &MaterialInfoTileType)) {
            buffer[i] = (struct MaterialInfoTileObject *)item;
        } else {
            PyErr_Format(PyExc_TypeError,
                         "Object in sequence at index %ld is not a %s", (long)i,
                         MaterialInfoTileType.tp_name);
            for (Py_ssize_t j = 0; j < i; j++)
                Py_DECREF(buffer[j]);
            free(buffer);
            return 0;
        }
    }

    struct MaterialInfoTileObjectSequenceInfo *result =
        (struct MaterialInfoTileObjectSequenceInfo *)_result;
    result->buffer = buffer;
    result->len = len;
    return 1;
}

static int MaterialInfo_init(PyObject *_self, PyObject *args, PyObject *kwds) {
    struct MaterialInfoObject *self = (struct MaterialInfoObject *)_self;
    static char *kwlist[] = {
        "name",     "uv_basis_s", "uv_basis_t",    "other_modes", "tiles",
        "combiner", "vals",       "geometry_mode", NULL,
    };
    char *name;
    int uv_basis_s, uv_basis_t;
    PyObject *_other_modes, *_combiner, *_geometry_mode, *_vals;
    struct MaterialInfoTileObjectSequenceInfo tile_infos;

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds,
            "sii"
            "O!O&O!O!O!",
            kwlist,

            &name, &uv_basis_s, &uv_basis_t,

            &MaterialInfoOtherModesType, &_other_modes,
            converter_MaterialInfoTileObject_sequence_len8, &tile_infos,
            &MaterialInfoCombinerType, &_combiner, //
            &MaterialInfoValsType, &_vals,         //
            &MaterialInfoGeometryModeType, &_geometry_mode))
        return -1;

    struct MaterialInfoOtherModesObject *other_modes =
        (struct MaterialInfoOtherModesObject *)_other_modes;

    struct MaterialInfoCombinerObject *combiner =
        (struct MaterialInfoCombinerObject *)_combiner;

    struct MaterialInfoValsObject *vals =
        (struct MaterialInfoValsObject *)_vals;

    struct MaterialInfoGeometryModeObject *geometry_mode =
        (struct MaterialInfoGeometryModeObject *)_geometry_mode;

    if (self->mat_info.name != NULL) {
        free(self->mat_info.name);
    }
    self->mat_info.name = strdup(name);
    self->mat_info.uv_basis_s = uv_basis_s;
    self->mat_info.uv_basis_t = uv_basis_t;
    self->mat_info.other_modes = other_modes->other_modes;
    assert(tile_infos.len == 8);
    for (int i = 0; i < 8; i++) {
        Py_XINCREF(tile_infos.buffer[i]->image_object);
        self->image_objects[i] = tile_infos.buffer[i]->image_object;
        self->mat_info.tiles[i] = tile_infos.buffer[i]->tile;
    }
    self->mat_info.combiner = combiner->combiner;
    self->mat_info.vals = vals->vals;
    self->mat_info.geometry_mode = geometry_mode->geometry_mode;

    free_MaterialInfoTileSequenceInfo(&tile_infos);

    return 0;
}

static PyTypeObject MaterialInfoType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.MaterialInfo",
    .tp_doc = PyDoc_STR("material info"),
    .tp_basicsize = sizeof(struct MaterialInfoObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = MaterialInfo_new,
    .tp_init = MaterialInfo_init,
    .tp_dealloc = MaterialInfo_dealloc,
};

struct MeshInfoObject {
    PyObject_HEAD

        struct MaterialInfoImageObject **image_objects;
    size_t len_image_objects;
    struct MeshInfo *mesh;
};

static void MeshInfo_dealloc(PyObject *_self) {
    struct MeshInfoObject *self = (struct MeshInfoObject *)_self;

    printf("MeshInfo_dealloc\n");

    if (self->image_objects != NULL) {
        for (size_t i = 0; i < self->len_image_objects; i++) {
            Py_XDECREF(self->image_objects[i]);
        }
        free(self->image_objects);
    }

    if (self->mesh != NULL) {
        free_create_MeshInfo_from_buffers(self->mesh);
    }

    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *MeshInfo_new(PyTypeObject *type, PyObject *args,
                              PyObject *kwds) {
    struct MeshInfoObject *self;

    printf("MeshInfo_new\n");

    self = (struct MeshInfoObject *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->image_objects = NULL;
        self->mesh = NULL;
    }
    return (PyObject *)self;
}

static PyObject *MeshInfo_write_c(PyObject *_self, PyObject *args) {
    struct MeshInfoObject *self = (struct MeshInfoObject *)_self;
    PyObject *path_bytes_object;

    if (!PyArg_ParseTuple(args, "O&", PyUnicode_FSConverter,
                          &path_bytes_object))
        return NULL;

    char *path = PyBytes_AsString(path_bytes_object);
    if (path == NULL)
        return NULL;

    int res = write_mesh_info_to_f3d_c(self->mesh, path);

    Py_DECREF(path_bytes_object);

    if (res != 0) {
        PyErr_SetString(PyExc_Exception, "write_mesh_info_to_f3d_c failed");
        return NULL;
    }

    return Py_None;
}

static PyMethodDef MeshInfo_methods[] = {
    {"write_c", MeshInfo_write_c, METH_VARARGS, "Write mesh to a .c file"},
    {NULL} /* Sentinel */
};

static PyTypeObject MeshInfoType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.MeshInfo",
    .tp_doc = PyDoc_STR("mesh info"),
    .tp_basicsize = sizeof(struct MeshInfoObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = MeshInfo_new,
    .tp_dealloc = MeshInfo_dealloc,
    .tp_methods = MeshInfo_methods,
};

int converter_contiguous_buffer_impl(PyObject *obj, void *result,
                                     const char *required_format,
                                     size_t expected_itemsize) {
    if (obj == NULL) {
        PyBuffer_Release(result);
        return 0;
    }

    Py_buffer view;

    if (PyObject_GetBuffer(obj, &view, PyBUF_ND | PyBUF_FORMAT) < 0)
        return 0;
    if (strcmp(view.format, required_format) != 0) {
        PyBuffer_Release(&view);
        PyErr_Format(PyExc_TypeError, "view.format != %s", required_format);
        return 0;
    }
    if (view.ndim != 1) {
        PyBuffer_Release(&view);
        PyErr_SetString(PyExc_TypeError, "view.ndim != 1");
        return 0;
    }
    assert(view.itemsize == sizeof(unsigned int));
    assert(view.len == view.itemsize * view.shape[0]);

    *(Py_buffer *)result = view;

    return Py_CLEANUP_SUPPORTED;
}

int converter_contiguous_uint_buffer(PyObject *obj, void *result) {
    return converter_contiguous_buffer_impl(obj, result, "I",
                                            sizeof(unsigned int));
}

int converter_contiguous_float_buffer(PyObject *obj, void *result) {
    return converter_contiguous_buffer_impl(obj, result, "f", sizeof(float));
}

int converter_contiguous_float_buffer_optional(PyObject *obj, void *result) {
    if (obj == Py_None) {
        ((Py_buffer *)result)->buf = NULL;
        return 1;
    }
    return converter_contiguous_buffer_impl(obj, result, "f", sizeof(float));
}

struct MaterialInfoObjectSequenceInfo {
    struct MaterialInfoObject **buffer;
    Py_ssize_t len;
};

void free_MaterialInfoSequenceInfo(
    struct MaterialInfoObjectSequenceInfo *material_infos) {

    for (Py_ssize_t i = 0; i < material_infos->len; i++)
        Py_XDECREF(material_infos->buffer[i]);

    free(material_infos->buffer);
}

int converter_MaterialInfoObject_or_None_sequence(PyObject *obj,
                                                  void *_result) {
    Py_ssize_t len = PySequence_Length(obj);
    if (len < 0)
        return 0;

    struct MaterialInfoObject **buffer =
        malloc(sizeof(struct MaterialInfoObject *[len]));
    // TODO check malloc
    for (Py_ssize_t i = 0; i < len; i++) {
        PyObject *item = PySequence_GetItem(obj, i);
        if (item == NULL) {
            for (Py_ssize_t j = 0; j < i; j++)
                Py_XDECREF(buffer[j]);
            free(buffer);
            return 0;
        }

        if (item == Py_None) {
            buffer[i] = NULL;
        } else if (PyObject_TypeCheck(item, &MaterialInfoType)) {
            buffer[i] = (struct MaterialInfoObject *)item;
        } else {
            PyErr_Format(PyExc_TypeError,
                         "Object in sequence at index %ld is not None or a %s",
                         (long)i, MaterialInfoType.tp_name);
            for (Py_ssize_t j = 0; j < i; j++)
                Py_XDECREF(buffer[j]);
            free(buffer);
            return 0;
        }
    }

    struct MaterialInfoObjectSequenceInfo *result =
        (struct MaterialInfoObjectSequenceInfo *)_result;
    result->buffer = buffer;
    result->len = len;
    return 1;
}

static PyObject *create_MeshInfo(PyObject *self, PyObject *args) {
    Py_buffer buf_vertices_co_view, buf_triangles_loops_view,
        buf_triangles_material_index_view, buf_loops_vertex_index_view,
        buf_loops_normal_view, buf_corners_color_view, buf_loops_uv_view;
    struct MaterialInfoObjectSequenceInfo material_info_objects;
    PyObject *_default_material_info;

    if (!PyArg_ParseTuple(
            args, "O&O&O&O&O&O&O&O&O!",                                  //
            converter_contiguous_float_buffer, &buf_vertices_co_view,    //
            converter_contiguous_uint_buffer, &buf_triangles_loops_view, //
            converter_contiguous_uint_buffer,
            &buf_triangles_material_index_view,
            converter_contiguous_uint_buffer, &buf_loops_vertex_index_view, //
            converter_contiguous_float_buffer, &buf_loops_normal_view,      //
            converter_contiguous_float_buffer_optional,
            &buf_corners_color_view,                                        //
            converter_contiguous_float_buffer_optional, &buf_loops_uv_view, //
            converter_MaterialInfoObject_or_None_sequence,
            &material_info_objects, //
            &MaterialInfoType, &_default_material_info))
        return NULL;

    struct MaterialInfoObject *default_material_info =
        (struct MaterialInfoObject *)_default_material_info;

    struct MaterialInfoImageObject **image_objects;
    size_t len_image_objects;

    struct MaterialInfo **material_infos;
    size_t n_material_infos = material_info_objects.len;

    // + 1 for default_material_info
    len_image_objects = (n_material_infos + 1) * 8;
    image_objects =
        malloc(sizeof(struct MaterialInfoImageObject *[len_image_objects]));
    material_infos = malloc(sizeof(struct MaterialInfo *[n_material_infos]));
    // TODO check malloc

    for (Py_ssize_t i = 0; i < material_info_objects.len; i++) {
        material_infos[i] = &material_info_objects.buffer[i]->mat_info;
        for (int j = 0; j < 8; j++) {
            assert((size_t)(i * 8 + j) < len_image_objects);
            image_objects[i * 8 + j] =
                material_info_objects.buffer[i]->image_objects[j];
        }
    }

    for (int j = 0; j < 8; j++) {
        assert((size_t)(n_material_infos * 8 + j) < len_image_objects);
        image_objects[n_material_infos * 8 + j] =
            default_material_info->image_objects[j];
    }

    // This also decreases the reference counts of the image_objects before we
    // increase it below, but that's fine as the objects are still referenced
    // elsewhere due to being passed as arguments.
    free_MaterialInfoSequenceInfo(&material_info_objects);

    struct MeshInfo *mesh;

    mesh = create_MeshInfo_from_buffers(
        buf_vertices_co_view.buf, buf_vertices_co_view.shape[0],         //
        buf_triangles_loops_view.buf, buf_triangles_loops_view.shape[0], //
        buf_triangles_material_index_view.buf,
        buf_triangles_material_index_view.shape[0], //
        buf_loops_vertex_index_view.buf,
        buf_loops_vertex_index_view.shape[0],                      //
        buf_loops_normal_view.buf, buf_loops_normal_view.shape[0], //
        buf_corners_color_view.buf,
        buf_corners_color_view.buf == NULL ? 0
                                           : buf_corners_color_view.shape[0], //
        buf_loops_uv_view.buf,
        buf_loops_uv_view.buf == NULL ? 0 : buf_loops_uv_view.shape[0], //
        material_infos, n_material_infos,                               //
        &default_material_info->mat_info);

    PyBuffer_Release(&buf_vertices_co_view);
    PyBuffer_Release(&buf_triangles_loops_view);
    PyBuffer_Release(&buf_triangles_material_index_view);
    PyBuffer_Release(&buf_loops_vertex_index_view);
    PyBuffer_Release(&buf_loops_normal_view);
    if (buf_corners_color_view.buf != NULL)
        PyBuffer_Release(&buf_corners_color_view);
    if (buf_loops_uv_view.buf != NULL)
        PyBuffer_Release(&buf_loops_uv_view);
    free(material_infos);

    if (mesh == NULL) {
        PyErr_SetString(PyExc_MemoryError,
                        "create_MeshInfo_from_buffers failed");
        free(image_objects);
        return NULL;
    }

    struct MeshInfoObject *mesh_info_object;

    // TODO is this how to create objects?
    printf("%s: PyObject_New...\n", __FUNCTION__);
    // FIXME PyObject_New does not call MeshInfo_new so must be wrong (no it's
    // not necessarily wrong)
    mesh_info_object = PyObject_New(struct MeshInfoObject, &MeshInfoType);
    if (mesh_info_object == NULL) {
        PyErr_SetString(PyExc_MemoryError, "PyObject_New failed");
        free(image_objects);
        return NULL;
    }
    printf("%s: PyObject_Init...\n", __FUNCTION__);
    if (PyObject_Init((PyObject *)mesh_info_object,
                      Py_TYPE(mesh_info_object)) == NULL) {
        // ? (can init even return NULL?) (no it can't)
        Py_DECREF(mesh_info_object);
        free(image_objects);
        return NULL;
    }

    for (size_t i = 0; i < len_image_objects; i++)
        Py_XINCREF(image_objects[i]);

    mesh_info_object->image_objects = image_objects;
    mesh_info_object->len_image_objects = len_image_objects;
    mesh_info_object->mesh = mesh;

    return (PyObject *)mesh_info_object;
}

static int dragex_backend_exec(PyObject *m) {
    if (PyType_Ready(&MaterialInfoImageType) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(m, "MaterialInfoImage",
                              (PyObject *)&MaterialInfoImageType) < 0) {
        return -1;
    }

    if (PyType_Ready(&MaterialInfoOtherModesType) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(m, "MaterialInfoOtherModes",
                              (PyObject *)&MaterialInfoOtherModesType) < 0) {
        return -1;
    }

    if (PyType_Ready(&MaterialInfoTileType) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(m, "MaterialInfoTile",
                              (PyObject *)&MaterialInfoTileType) < 0) {
        return -1;
    }

    if (PyType_Ready(&MaterialInfoCombinerType) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(m, "MaterialInfoCombiner",
                              (PyObject *)&MaterialInfoCombinerType) < 0) {
        return -1;
    }

    if (PyType_Ready(&MaterialInfoValsType) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(m, "MaterialInfoVals",
                              (PyObject *)&MaterialInfoValsType) < 0) {
        return -1;
    }

    if (PyType_Ready(&MaterialInfoGeometryModeType) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(m, "MaterialInfoGeometryMode",
                              (PyObject *)&MaterialInfoGeometryModeType) < 0) {
        return -1;
    }

    if (PyType_Ready(&MaterialInfoType) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(m, "MaterialInfo",
                              (PyObject *)&MaterialInfoType) < 0) {
        return -1;
    }

    if (PyType_Ready(&MeshInfoType) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(m, "MeshInfo", (PyObject *)&MeshInfoType) < 0) {
        return -1;
    }

    return 0;
}

static PyModuleDef_Slot dragex_backend_slots[] = {
    {Py_mod_exec, dragex_backend_exec},
    // Just use this while using static types
    // Note: added in Python 3.12
    /*
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_NOT_SUPPORTED},
    */
    {0, NULL},
};

static PyMethodDef dragex_backend_methods[] = {
    {"get_build_id", get_build_id, METH_NOARGS, "get build_id"},
    {"create_MeshInfo", create_MeshInfo, METH_VARARGS,
     "create MeshInfo from buffers"},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static struct PyModuleDef dragex_backend_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    // No idea what m_name does. It is *not* the name for importing.
    // Be safe and set it to the same value as that anyway.
    .m_name = "dragex_backend",
    .m_methods = dragex_backend_methods,
    .m_slots = dragex_backend_slots,
};

PyMODINIT_FUNC PyInit_dragex_backend(void) {
    printf("%s: compiled %s %s\n", __FUNCTION__, __DATE__, __TIME__);
    return PyModuleDef_Init(&dragex_backend_module);
}
