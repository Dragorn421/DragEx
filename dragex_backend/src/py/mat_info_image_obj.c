#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#include "objs.h"

#include "../logging/logging.h"

#include "../exporter.h"

static void MaterialInfoImage_dealloc(PyObject *_self) {
    struct MaterialInfoImageObject *self =
        (struct MaterialInfoImageObject *)_self;

    log_trace("entry %s", self->image.c_identifier == NULL
                              ? "(NULL c_identifier)"
                              : self->image.c_identifier);

    free(self->image.c_identifier);
    free(self->image.tlut_c_identifier);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *MaterialInfoImage_new(PyTypeObject *type, PyObject *args,
                                       PyObject *kwds) {
    struct MaterialInfoImageObject *self;

    log_trace("entry");

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
        "c_identifier", "width", "height", "tlut_c_identifier", NULL,
    };
    char *c_identifier;
    int width;
    int height;
    char *tlut_c_identifier;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "siiz", kwlist, &c_identifier,
                                     &width, &height, &tlut_c_identifier))
        return -1;

    self->image.c_identifier = strdup(c_identifier);
    self->image.width = width;
    self->image.height = height;
    self->image.tlut_c_identifier =
        tlut_c_identifier == NULL ? NULL : strdup(tlut_c_identifier);

    return 0;
}

static PyObject *MaterialInfoImage_get_c_identifier(PyObject *_self,
                                                    PyObject *args) {
    struct MaterialInfoImageObject *self =
        (struct MaterialInfoImageObject *)_self;

    PyObject *c_identifier_obj = PyUnicode_FromString(self->image.c_identifier);

    if (c_identifier_obj == NULL) {
        return NULL;
    }

    return c_identifier_obj;
}

static PyMethodDef MaterialInfoImage_methods[] = {
    {"get_c_identifier", MaterialInfoImage_get_c_identifier, METH_NOARGS,
     "c_identifier getter"},
    {NULL} /* Sentinel */
};

PyTypeObject MaterialInfoImageType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.MaterialInfoImage",
    .tp_doc = PyDoc_STR("material info image"),
    .tp_basicsize = sizeof(struct MaterialInfoImageObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = MaterialInfoImage_new,
    .tp_init = MaterialInfoImage_init,
    .tp_dealloc = MaterialInfoImage_dealloc,
    .tp_methods = MaterialInfoImage_methods,
};
