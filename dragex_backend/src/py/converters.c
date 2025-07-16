#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <assert.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

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
