#include "py_logging.h"

#ifndef PY_SSIZE_T_CLEAN
#define PY_SSIZE_T_CLEAN
#endif
#include <Python.h>

#include "logging.h"

static PyObject *py_set_log_file(PyObject *self, PyObject *args) {
    PyObject *path_bytes_object;

    if (!PyArg_ParseTuple(args, "O&", PyUnicode_FSConverter,
                          &path_bytes_object))
        return NULL;

    char *path = PyBytes_AsString(path_bytes_object);
    if (path == NULL)
        return NULL;

    if (!set_log_file(path)) {
        PyErr_SetString(PyExc_Exception, "set_log_file failed");
        return NULL;
    }

    return Py_None;
}

static PyObject *py_clear_log_file(PyObject *self, PyObject *args) {
    if (!set_log_file(NULL)) {
        PyErr_SetString(PyExc_Exception, "set_log_file failed");
        return NULL;
    }
    return Py_None;
}

static PyObject *py_flush(PyObject *self, PyObject *args) {
    log_flush();
    return Py_None;
}

static PyMethodDef logging_methods[] = {
    {"set_log_file", py_set_log_file, METH_VARARGS, "Set output log file"},
    {"clear_log_file", py_clear_log_file, METH_NOARGS,
     "Clear output log file (no longer log to file)"},
    {"flush", py_flush, METH_NOARGS, "Flush log file"},
    {NULL, NULL, 0, NULL}};

struct PyModuleDef dragex_backend_logging_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "dragex_backend.logging",
    .m_methods = logging_methods,
};
