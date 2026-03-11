#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <assert.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#include "converters.h"

int converter_contiguous_buffer_impl(PyObject *obj, void *result,
                                     const char *required_format,
                                     Py_ssize_t expected_itemsize) {
    if (obj == NULL) {
        PyBuffer_Release(result);
        return 0;
    }

    Py_buffer view;

    if (PyObject_GetBuffer(obj, &view, PyBUF_ND | PyBUF_FORMAT) < 0)
        return 0;
    if (strcmp(view.format, required_format) != 0) {
        PyBuffer_Release(&view);
        PyErr_Format(PyExc_TypeError, "view.format != %s", required_format);
        return 0;
    }
    if (view.ndim != 1) {
        PyBuffer_Release(&view);
        PyErr_SetString(PyExc_TypeError, "view.ndim != 1");
        return 0;
    }
    assert(view.itemsize == expected_itemsize);
    assert(view.len == view.itemsize * view.shape[0]);

    *(Py_buffer *)result = view;

    return Py_CLEANUP_SUPPORTED;
}

int converter_contiguous_uint_buffer(PyObject *obj, void *result) {
    return converter_contiguous_buffer_impl(obj, result, "I",
                                            sizeof(unsigned int));
}

int converter_contiguous_float_buffer(PyObject *obj, void *result) {
    return converter_contiguous_buffer_impl(obj, result, "f", sizeof(float));
}

int converter_contiguous_float_buffer_optional(PyObject *obj, void *result) {
    if (obj == Py_None) {
        ((Py_buffer *)result)->buf = NULL;
        return 1;
    }
    return converter_contiguous_buffer_impl(obj, result, "f", sizeof(float));
}

int converter_Object_or_None_sequence_impl(
    PyObject *obj, struct GenericObjectSequenceInfo *result,
    PyTypeObject *forType) {
    Py_ssize_t len = PySequence_Length(obj);
    if (len < 0)
        return 0;

    PyObject **buffer = malloc(sizeof(PyObject *) * len);
    // TODO check malloc
    for (Py_ssize_t i = 0; i < len; i++) {
        PyObject *item = PySequence_GetItem(obj, i);
        if (item == NULL) {
            for (Py_ssize_t j = 0; j < i; j++)
                Py_XDECREF(buffer[j]);
            free(buffer);
            return 0;
        }

        if (item == Py_None) {
            buffer[i] = NULL;
        } else if (PyObject_TypeCheck(item, forType)) {
            buffer[i] = item;
        } else {
            PyErr_Format(PyExc_TypeError,
                         "Object in sequence at index %ld is not None or a %s",
                         (long)i, forType->tp_name);
            for (Py_ssize_t j = 0; j < i; j++)
                Py_XDECREF(buffer[j]);
            free(buffer);
            return 0;
        }
    }

    result->buffer = buffer;
    result->len = len;
    return 1;
}

void free_StringSequenceInfo(struct StringSequenceInfo *strings) {

    for (Py_ssize_t i = 0; i < strings->len; i++)
        Py_XDECREF(strings->buffer[i]);

    free(strings->buffer);
}

int converter_string_or_None_sequence(PyObject *obj, void *_result) {
    struct GenericObjectSequenceInfo genericResult;
    int res = converter_Object_or_None_sequence_impl(obj, &genericResult,
                                                     &PyUnicode_Type);
    if (res == 1) {
        struct StringSequenceInfo *result = _result;
        result->buffer = genericResult.buffer;
        result->len = genericResult.len;
    }
    return res;
}
