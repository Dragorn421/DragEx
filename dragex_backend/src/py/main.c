#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stddef.h>
#include <stdio.h>

#include "objs.h"

#include "../logging/logging.h"
#include "../logging/py_logging.h"

#include "../../build_id.h"

static PyObject *get_build_id(PyObject *self, PyObject *args) {
    return PyLong_FromLong(BUILD_ID);
}

static int dragex_backend_exec(PyObject *m) {
    if (PyType_Ready(&MaterialInfoImageType) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(m, "MaterialInfoImage",
                              (PyObject *)&MaterialInfoImageType) < 0) {
        return -1;
    }

    if (PyType_Ready(&MaterialInfoOtherModesType) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(m, "MaterialInfoOtherModes",
                              (PyObject *)&MaterialInfoOtherModesType) < 0) {
        return -1;
    }

    if (PyType_Ready(&MaterialInfoTileType) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(m, "MaterialInfoTile",
                              (PyObject *)&MaterialInfoTileType) < 0) {
        return -1;
    }

    if (PyType_Ready(&MaterialInfoCombinerType) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(m, "MaterialInfoCombiner",
                              (PyObject *)&MaterialInfoCombinerType) < 0) {
        return -1;
    }

    if (PyType_Ready(&MaterialInfoValsType) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(m, "MaterialInfoVals",
                              (PyObject *)&MaterialInfoValsType) < 0) {
        return -1;
    }

    if (PyType_Ready(&MaterialInfoGeometryModeType) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(m, "MaterialInfoGeometryMode",
                              (PyObject *)&MaterialInfoGeometryModeType) < 0) {
        return -1;
    }

    if (PyType_Ready(&MaterialInfoType) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(m, "MaterialInfo",
                              (PyObject *)&MaterialInfoType) < 0) {
        return -1;
    }

    if (PyType_Ready(&MeshInfoType) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(m, "MeshInfo", (PyObject *)&MeshInfoType) < 0) {
        return -1;
    }

    PyObject *logging_module_obj =
        PyModule_Create(&dragex_backend_logging_module);
    if (logging_module_obj == NULL) {
        return -1;
    }
    if (PyModule_AddObject(m, "logging", logging_module_obj) < 0) {
        Py_DECREF(logging_module_obj);
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
    {"create_MeshInfo", create_MeshInfo, METH_VARARGS,
     "create MeshInfo from buffers"},
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
    log_info("compiled %s %s", __DATE__, __TIME__);
    return PyModuleDef_Init(&dragex_backend_module);
}
