#ifndef DRAGEX_CONVERTERS_H
#define DRAGEX_CONVERTERS_H

#ifndef PY_SSIZE_T_CLEAN
#define PY_SSIZE_T_CLEAN
#endif
#include <Python.h>

int converter_contiguous_uint_buffer(PyObject *obj, void *result);

int converter_contiguous_float_buffer(PyObject *obj, void *result);

int converter_contiguous_float_buffer_optional(PyObject *obj, void *result);

//

struct GenericObjectSequenceInfo {
    PyObject **buffer;
    Py_ssize_t len;
};

int converter_Object_or_None_sequence_impl(
    PyObject *obj, struct GenericObjectSequenceInfo *result,
    PyTypeObject *forType);

//

struct StringSequenceInfo {
    PyObject **buffer;
    Py_ssize_t len;
};

void free_StringSequenceInfo(struct StringSequenceInfo *strings);

int converter_string_or_None_sequence(PyObject *obj, void *result);

#endif
