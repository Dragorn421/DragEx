#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stddef.h>

#include "objs.h"

#include "../exporter.h"

static int MaterialInfoGeometryMode_init(PyObject *_self, PyObject *args,
                                         PyObject *kwds) {
    struct MaterialInfoGeometryModeObject *self =
        (struct MaterialInfoGeometryModeObject *)_self;
    static char *kwlist[] = {
        "zbuffer",      "lighting", "vertex_colors",    "cull_front",
        "cull_back",    "fog",      "uv_gen_spherical", "uv_gen_linear",
        "shade_smooth", NULL,
    };
    int zbuffer, lighting, vertex_colors, cull_front, cull_back, fog,
        uv_gen_spherical, uv_gen_linear, shade_smooth;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "ppppppppp", kwlist, &zbuffer,
                                     &lighting, &vertex_colors, &cull_front,
                                     &cull_back, &fog, &uv_gen_spherical,
                                     &uv_gen_linear, &shade_smooth))
        return -1;

    self->geometry_mode.zbuffer = !!zbuffer;
    self->geometry_mode.lighting = !!lighting;
    self->geometry_mode.vertex_colors = !!vertex_colors;
    self->geometry_mode.cull_front = !!cull_front;
    self->geometry_mode.cull_back = !!cull_back;
    self->geometry_mode.fog = !!fog;
    self->geometry_mode.uv_gen_spherical = !!uv_gen_spherical;
    self->geometry_mode.uv_gen_linear = !!uv_gen_linear;
    self->geometry_mode.shade_smooth = !!shade_smooth;
    return 0;
}

PyTypeObject MaterialInfoGeometryModeType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.MaterialInfoGeometryMode",
    .tp_doc = PyDoc_STR("material info geometry mode"),
    .tp_basicsize = sizeof(struct MaterialInfoGeometryModeObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = MaterialInfoGeometryMode_init,
};
