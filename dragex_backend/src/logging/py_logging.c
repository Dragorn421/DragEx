#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "py_logging.h"

#include <string.h>

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

static PyObject *py_log_impl(enum log_level level, PyObject *self,
                             PyObject *args) {
    char *message;

    if (!PyArg_ParseTuple(args, "s", &message))
        return NULL;

    PyFrameObject *frame = PyEval_GetFrame();
    PyCodeObject *code = PyFrame_GetCode(frame);
    const char *file_path = PyUnicode_AsUTF8AndSize(code->co_filename, NULL);
    const char *function = PyUnicode_AsUTF8AndSize(code->co_name, NULL);
    int line = PyFrame_GetLineNumber(frame);

    // file_path is an absolute path,
    // trim it by looking for a dragex folder and only keep the parts after

    const char path_sep =
#ifdef _WIN32
        '\\';
#else
        '/';
#endif

    size_t len_file_path = strlen(file_path);
    char *file_path_buf = strdup(file_path);
    if (file_path_buf == NULL) {
        PyErr_SetString(PyExc_MemoryError, "strdup file_path_buf failed");
        return NULL;
    }
    size_t n_file_path_parts = 1;
    for (size_t i = 0; i < len_file_path; i++) {
        if (file_path_buf[i] == path_sep) {
            n_file_path_parts++;
        }
    }

    char **file_path_parts = malloc(sizeof(char *) * n_file_path_parts);
    if (file_path_parts == NULL) {
        free(file_path_buf);
        PyErr_SetString(PyExc_MemoryError, "malloc file_path_parts failed");
        return NULL;
    }
    file_path_parts[0] = file_path_buf;
    size_t i_file_path_part = 1;
    for (size_t i = 0; i < len_file_path; i++) {
        if (file_path_buf[i] == path_sep) {
            assert(i_file_path_part < n_file_path_parts);
            file_path_buf[i] = '\0';
            file_path_parts[i_file_path_part] = &file_path_buf[i + 1];
            i_file_path_part++;
        }
    }
    assert(i_file_path_part == n_file_path_parts);

    size_t i_first_part;

    // default to only the final part (file name)
    i_first_part = n_file_path_parts - 1;

    for (size_t i = 0; i < n_file_path_parts; i++) {
        if (strcasecmp(file_path_parts[i], "dragex") == 0) {
            i_first_part = i + 1;
        }
    }

    char *file;

    if (i_first_part == n_file_path_parts) {
        // Somehow the last part in the path is "dragex"
        file = strdup("dragex");
    } else {
        assert(i_first_part < n_file_path_parts);
        file = malloc(len_file_path); // over-allocate for simplicity
        if (file == NULL) {
            free(file_path_parts);
            free(file_path_buf);
            PyErr_SetString(PyExc_MemoryError, "malloc file failed");
            return NULL;
        }
        file[0] = '\0';
        char path_sep_str[2] = {path_sep, '\0'};
        for (size_t i = i_first_part; i < n_file_path_parts; i++) {
            if (i != i_first_part)
                strcat(file, path_sep_str);
            strcat(file, file_path_parts[i]);
        }
    }

    // Log and cleanup

    free(file_path_parts);
    free(file_path_buf);

    _log(file, line, function, level, "%s", message);

    free(file);

    return Py_None;
}

static PyObject *py_trace(PyObject *self, PyObject *args) {
    return py_log_impl(LOG_LEVEL_TRACE, self, args);
}

static PyObject *py_debug(PyObject *self, PyObject *args) {
    return py_log_impl(LOG_LEVEL_DEBUG, self, args);
}

static PyObject *py_info(PyObject *self, PyObject *args) {
    return py_log_impl(LOG_LEVEL_INFO, self, args);
}

static PyObject *py_warn(PyObject *self, PyObject *args) {
    return py_log_impl(LOG_LEVEL_WARN, self, args);
}

static PyObject *py_error(PyObject *self, PyObject *args) {
    return py_log_impl(LOG_LEVEL_ERROR, self, args);
}

static PyObject *py_fatal(PyObject *self, PyObject *args) {
    return py_log_impl(LOG_LEVEL_FATAL, self, args);
}

static PyMethodDef logging_methods[] = {
    {"set_log_file", py_set_log_file, METH_VARARGS, "Set output log file"},
    {"clear_log_file", py_clear_log_file, METH_NOARGS,
     "Clear output log file (no longer log to file)"},
    {"flush", py_flush, METH_NOARGS, "Flush log file"},
    {"trace", py_trace, METH_VARARGS, "Log a message at the TRACE level"},
    {"debug", py_debug, METH_VARARGS, "Log a message at the DEBUG level"},
    {"info", py_info, METH_VARARGS, "Log a message at the INFO level"},
    {"warn", py_warn, METH_VARARGS, "Log a message at the WARN level"},
    {"error", py_error, METH_VARARGS, "Log a message at the ERROR level"},
    {"fatal", py_fatal, METH_VARARGS, "Log a message at the FATAL level"},
    {NULL, NULL, 0, NULL}};

struct PyModuleDef dragex_backend_logging_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "dragex_backend.logging",
    .m_methods = logging_methods,
};
