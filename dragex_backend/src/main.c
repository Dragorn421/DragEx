#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject *get_value(PyObject *self, PyObject *args) {
  if (!PyArg_ParseTuple(args, ""))
    return NULL;
  return PyLong_FromLong(421);
}

static PyMethodDef spam_methods[] = {
    {"get_value", get_value, METH_VARARGS, "get 421"},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static struct PyModuleDef spam_module = {
    .m_name = "mylib_main",
    .m_methods = spam_methods,
};

PyMODINIT_FUNC PyInit_dragex_backend(void) {
  return PyModuleDef_Init(&spam_module);
}
