#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stddef.h>

#include "objs.h"

static void CornerMaterialInfo_dealloc(PyObject *_self) {
    struct CornerMaterialInfoObject *self =
        (struct CornerMaterialInfoObject *)_self;

    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *CornerMaterialInfo_new(PyTypeObject *type, PyObject *args,
                                        PyObject *kwds) {
    struct CornerMaterialInfoObject *self;

    self = (struct CornerMaterialInfoObject *)type->tp_alloc(type, 0);
    return (PyObject *)self;
}

static int CornerMaterialInfo_init(PyObject *_self, PyObject *args,
                                   PyObject *kwds) {
    struct CornerMaterialInfoObject *self =
        (struct CornerMaterialInfoObject *)_self;
    static char *kwlist[] = {
        "limb_index",
        NULL,
    };
    int limb_index;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "i", kwlist, &limb_index))
        return -1;

    self->corner_mat_info.limb_index = limb_index;

    return 0;
}

PyTypeObject CornerMaterialInfoType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.CornerMaterialInfo",
    .tp_doc = PyDoc_STR("corner material info"),
    .tp_basicsize = sizeof(struct CornerMaterialInfoObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = CornerMaterialInfo_new,
    .tp_init = CornerMaterialInfo_init,
    .tp_dealloc = CornerMaterialInfo_dealloc,
};
