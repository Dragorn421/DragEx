#ifndef DRAGEX_CONVERTERS_H
#define DRAGEX_CONVERTERS_H

#ifndef PY_SSIZE_T_CLEAN
#define PY_SSIZE_T_CLEAN
#endif
#include <Python.h>

int converter_contiguous_uint_buffer(PyObject *obj, void *result);

int converter_contiguous_float_buffer(PyObject *obj, void *result);

int converter_contiguous_float_buffer_optional(PyObject *obj, void *result);

#endif
