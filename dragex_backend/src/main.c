#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject *get_value(PyObject *self, PyObject *args) {
  if (!PyArg_ParseTuple(args, ""))
    return NULL;
  return PyLong_FromLong(421);
}

static PyMethodDef dragex_backend_methods[] = {
    {"get_value", get_value, METH_VARARGS, "get 421"},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static struct PyModuleDef dragex_backend_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    // No idea what m_name does. It is *not* the name for importing.
    // Be safe and set it to the same value as that anyway.
    .m_name = "dragex_backend",
    .m_methods = dragex_backend_methods,
};

PyMODINIT_FUNC PyInit_dragex_backend(void) {
  return PyModuleDef_Init(&dragex_backend_module);
}
