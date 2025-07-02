#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../build_id.h"

static PyObject *get_build_id(PyObject *self, PyObject *args) {
  return PyLong_FromLong(BUILD_ID);
}

struct FloatBufferThingObject {
  PyObject_HEAD

      Py_ssize_t n_exports;
  Py_ssize_t sz;
  float *vals;
};

static void FloatBufferThing_dealloc(PyObject *_self) {
  struct FloatBufferThingObject *self = (struct FloatBufferThingObject *)_self;

  free(self->vals);
  Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *FloatBufferThing_new(PyTypeObject *type, PyObject *args,
                                      PyObject *kwds) {
  struct FloatBufferThingObject *self;

  self = (struct FloatBufferThingObject *)type->tp_alloc(type, 0);
  if (self != NULL) {
    self->n_exports = 0;
    self->sz = -1;
    self->vals = NULL;
  }
  return (PyObject *)self;
}

static int FloatBufferThing_init(PyObject *_self, PyObject *args,
                                 PyObject *kwds) {
  static char *kwlist[] = {
      "length",
      "value",
      NULL,
  };

  struct FloatBufferThingObject *self = (struct FloatBufferThingObject *)_self;
  Py_ssize_t length;
  float value = 0.0f;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "n|f", kwlist, &length, &value))
    return -1;

  printf("%s: length = %zd\n", __FUNCTION__, length);

  if (self->n_exports != 0) {
    PyErr_SetString(PyExc_BufferError,
                    "Existing exports of data, cannot re-init");
    return -1;
  }

  if (self->vals != NULL) {

    free(self->vals);
  }

  self->sz = length;
  self->vals = malloc(sizeof(float[length]));
  if (self->vals == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Could not allocate buffer");
    return -1;
  }

  // TODO initializing values is potentially slow and useless
  for (Py_ssize_t i = 0; i < length; i++)
    self->vals[i] = value;

  return 0;
}

int FloatBufferThing_getbuffer(PyObject *exporter, Py_buffer *view, int flags) {
  struct FloatBufferThingObject *self =
      (struct FloatBufferThingObject *)exporter;

  // we want to set format="f" but are only allowed so if PyBUF_FORMAT is
  // passed?
  if (!(flags & PyBUF_FORMAT)) {
    PyErr_SetString(PyExc_BufferError, "PyBUF_FORMAT required.");
    return -1; // failure?
  }

  self->n_exports++;

  view->buf = self->vals;
  Py_INCREF(exporter);  // ?
  view->obj = exporter; // ?
  view->len = self->sz * sizeof(self->vals[0]);
  view->readonly = false; // ignore flags & PyBUF_WRITABLE ?
  view->itemsize = sizeof(self->vals[0]);
  view->format = "f";
  view->ndim = 1;
  view->shape = malloc(sizeof(Py_ssize_t[1]));
  view->shape[0] = self->sz;
  view->strides = &view->itemsize;

  // Note: required to not segfault in bytes() conversion
  view->suboffsets = NULL;

  view->internal = NULL;

  return 0;
}

void FloatBufferThing_releasebuffer(PyObject *exporter, Py_buffer *view) {
  struct FloatBufferThingObject *self =
      (struct FloatBufferThingObject *)exporter;

  free(view->shape);
  self->n_exports--;
  assert(self->n_exports >= 0);
}

static PyBufferProcs FloatBufferThing_bufferprocs = {
    .bf_getbuffer = FloatBufferThing_getbuffer,
    .bf_releasebuffer = FloatBufferThing_releasebuffer,
};

static PyTypeObject FloatBufferThingType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.FloatBufferThing",
    .tp_doc = PyDoc_STR("float buffer thing"),
    .tp_basicsize = sizeof(struct FloatBufferThingObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = FloatBufferThing_new,
    .tp_init = FloatBufferThing_init,
    .tp_dealloc = FloatBufferThing_dealloc,
    .tp_as_buffer = &FloatBufferThing_bufferprocs,
};

static int dragex_backend_exec(PyObject *m) {
  if (PyType_Ready(&FloatBufferThingType) < 0) {
    return -1;
  }

  if (PyModule_AddObjectRef(m, "FloatBufferThing",
                            (PyObject *)&FloatBufferThingType) < 0) {
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
