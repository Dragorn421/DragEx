#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stddef.h>

#include "name_to_enum.h"
#include "objs.h"

#include "../exporter.h"

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

PyTypeObject MaterialInfoOtherModesType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.MaterialInfoOtherModes",
    .tp_doc = PyDoc_STR("material info other modes"),
    .tp_basicsize = sizeof(struct MaterialInfoOtherModesObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = MaterialInfoOtherModes_init,
};
