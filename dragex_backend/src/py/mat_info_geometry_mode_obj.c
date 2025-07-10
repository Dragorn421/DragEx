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
        "lighting",
        NULL,
    };
    int lighting;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "p", kwlist, &lighting))
        return -1;

    self->geometry_mode.lighting = !!lighting;
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
