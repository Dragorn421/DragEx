#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stddef.h>

#include "objs.h"

#include "../exporter.h"

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

PyTypeObject MaterialInfoValsType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.MaterialInfoVals",
    .tp_doc = PyDoc_STR("material info vals"),
    .tp_basicsize = sizeof(struct MaterialInfoValsObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = MaterialInfoVals_init,
};
