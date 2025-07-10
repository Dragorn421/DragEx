#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stddef.h>

#include "name_to_enum.h"
#include "objs.h"

#include "../exporter.h"

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

PyTypeObject MaterialInfoCombinerType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.MaterialInfoCombiner",
    .tp_doc = PyDoc_STR("material info geometry mode"),
    .tp_basicsize = sizeof(struct MaterialInfoCombinerObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = MaterialInfoCombiner_init,
};
