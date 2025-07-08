#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "exporter.h"

#include "../build_id.h"

static PyObject *get_build_id(PyObject *self, PyObject *args) {
    return PyLong_FromLong(BUILD_ID);
}

struct MaterialInfoGeometryModeObject {
    PyObject_HEAD

        struct MaterialInfoGeometryMode geometry_mode;
};

static int MaterialInfoGeometryMode_init(PyObject *_self, PyObject *args,
                                         PyObject *kwds) {
    struct MaterialInfoGeometryModeObject *self =
        (struct MaterialInfoGeometryModeObject *)_self;
    static char *kwlist[] = {
        "lighting",
        NULL,
    };
    int lighting;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "p", kwlist, &lighting))
        return -1;

    self->geometry_mode.lighting = !!lighting;
    return 0;
}

static PyTypeObject MaterialInfoGeometryModeType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.MaterialInfoGeometryMode",
    .tp_doc = PyDoc_STR("material info geometry mode"),
    .tp_basicsize = sizeof(struct MaterialInfoGeometryModeObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = MaterialInfoGeometryMode_init,
};

struct MaterialInfoObject {
    PyObject_HEAD

        struct MaterialInfo mat_info;
};

static void MaterialInfo_dealloc(PyObject *_self) {
    struct MaterialInfoObject *self = (struct MaterialInfoObject *)_self;
    free(self->mat_info.name);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *MaterialInfo_new(PyTypeObject *type, PyObject *args,
                                  PyObject *kwds) {
    struct MaterialInfoObject *self;
    self = (struct MaterialInfoObject *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->mat_info.name = NULL;
    }
    return (PyObject *)self;
}

static int MaterialInfo_init(PyObject *_self, PyObject *args, PyObject *kwds) {
    struct MaterialInfoObject *self = (struct MaterialInfoObject *)_self;
    static char *kwlist[] = {
        "name", "uv_basis_s", "uv_basis_t", "geometry_mode", NULL,
    };
    char *name;
    int uv_basis_s, uv_basis_t;
    PyObject *_geometry_mode;

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "siiO!", kwlist, &name, &uv_basis_s, &uv_basis_t,
            &MaterialInfoGeometryModeType, &_geometry_mode))
        return -1;

    struct MaterialInfoGeometryModeObject *geometry_mode =
        (struct MaterialInfoGeometryModeObject *)_geometry_mode;

    if (self->mat_info.name != NULL) {
        free(self->mat_info.name);
    }
    self->mat_info.name = strdup(name);
    self->mat_info.uv_basis_s = uv_basis_s;
    self->mat_info.uv_basis_t = uv_basis_t;
    self->mat_info.geometry_mode = geometry_mode->geometry_mode;
    return 0;
}

static PyTypeObject MaterialInfoType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.MaterialInfo",
    .tp_doc = PyDoc_STR("material info"),
    .tp_basicsize = sizeof(struct MaterialInfoObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = MaterialInfo_new,
    .tp_init = MaterialInfo_init,
    .tp_dealloc = MaterialInfo_dealloc,
};

struct MeshInfoObject {
    PyObject_HEAD

        struct MeshInfo *mesh;
};

static void MeshInfo_dealloc(PyObject *_self) {
    struct MeshInfoObject *self = (struct MeshInfoObject *)_self;

    printf("MeshInfo_dealloc\n");

    if (self->mesh != NULL) {
        free_create_MeshInfo_from_buffers(self->mesh);
    }

    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *MeshInfo_new(PyTypeObject *type, PyObject *args,
                              PyObject *kwds) {
    struct MeshInfoObject *self;

    printf("MeshInfo_new\n");

    self = (struct MeshInfoObject *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->mesh = NULL;
    }
    return (PyObject *)self;
}

static PyObject *MeshInfo_write_c(PyObject *_self, PyObject *args) {
    struct MeshInfoObject *self = (struct MeshInfoObject *)_self;
    PyObject *path_bytes_object;

    if (!PyArg_ParseTuple(args, "O&", PyUnicode_FSConverter,
                          &path_bytes_object))
        return NULL;

    char *path = PyBytes_AsString(path_bytes_object);
    if (path == NULL)
        return NULL;

    int res = write_mesh_info_to_f3d_c(self->mesh, path);

    Py_DECREF(path_bytes_object);

    if (res != 0) {
        PyErr_SetString(PyExc_Exception, "write_mesh_info_to_f3d_c failed");
        return NULL;
    }

    return Py_None;
}

static PyMethodDef MeshInfo_methods[] = {
    {"write_c", MeshInfo_write_c, METH_VARARGS, "Write mesh to a .c file"},
    {NULL} /* Sentinel */
};

static PyTypeObject MeshInfoType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.MeshInfo",
    .tp_doc = PyDoc_STR("mesh info"),
    .tp_basicsize = sizeof(struct MeshInfoObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = MeshInfo_new,
    .tp_dealloc = MeshInfo_dealloc,
    .tp_methods = MeshInfo_methods,
};

int converter_contiguous_buffer_impl(PyObject *obj, void *result,
                                     const char *required_format,
                                     size_t expected_itemsize) {
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
    assert(view.itemsize == sizeof(unsigned int));
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

struct MaterialInfoSequenceInfo {
    struct MaterialInfo **buffer;
    Py_ssize_t len;
};

void free_MaterialInfoSequenceInfo(
    struct MaterialInfoSequenceInfo *material_infos) {
    free(material_infos->buffer);
}

int converter_MaterialInfo_or_None_sequence(PyObject *obj, void *_result) {
    Py_ssize_t len = PySequence_Length(obj);
    if (len < 0)
        return 0;

    struct MaterialInfo **buffer = malloc(sizeof(struct MaterialInfo *[len]));
    for (Py_ssize_t i = 0; i < len; i++) {
        PyObject *item = PySequence_GetItem(obj, i);
        if (item == NULL) {
            free(buffer);
            return 0;
        }

        if (item == Py_None) {
            buffer[i] = NULL;
        } else if (PyObject_TypeCheck(item, &MaterialInfoType)) {
            buffer[i] = &((struct MaterialInfoObject *)item)->mat_info;
        } else {
            PyErr_Format(PyExc_TypeError,
                         "Object in sequence at index %ld is not None or a %s",
                         (long)i, MaterialInfoType.tp_name);
            free(buffer);
            return 0;
        }
    }

    struct MaterialInfoSequenceInfo *result =
        (struct MaterialInfoSequenceInfo *)_result;
    result->buffer = buffer;
    result->len = len;
    return 1;
}

static PyObject *create_MeshInfo(PyObject *self, PyObject *args) {
    Py_buffer buf_vertices_co_view, buf_triangles_loops_view,
        buf_triangles_material_index_view, buf_loops_vertex_index_view,
        buf_loops_normal_view, buf_corners_color_view, buf_loops_uv_view;
    struct MaterialInfoSequenceInfo material_infos;
    PyObject *default_material_info;

    if (!PyArg_ParseTuple(
            args, "O&O&O&O&O&O&O&O&O!",                                  //
            converter_contiguous_float_buffer, &buf_vertices_co_view,    //
            converter_contiguous_uint_buffer, &buf_triangles_loops_view, //
            converter_contiguous_uint_buffer,
            &buf_triangles_material_index_view,
            converter_contiguous_uint_buffer, &buf_loops_vertex_index_view, //
            converter_contiguous_float_buffer, &buf_loops_normal_view,      //
            converter_contiguous_float_buffer_optional,
            &buf_corners_color_view,                                        //
            converter_contiguous_float_buffer_optional, &buf_loops_uv_view, //
            converter_MaterialInfo_or_None_sequence, &material_infos,       //
            &MaterialInfoType, &default_material_info))
        return NULL;

    struct MeshInfo *mesh;

    mesh = create_MeshInfo_from_buffers(
        buf_vertices_co_view.buf, buf_vertices_co_view.shape[0],         //
        buf_triangles_loops_view.buf, buf_triangles_loops_view.shape[0], //
        buf_triangles_material_index_view.buf,
        buf_triangles_material_index_view.shape[0], //
        buf_loops_vertex_index_view.buf,
        buf_loops_vertex_index_view.shape[0],                      //
        buf_loops_normal_view.buf, buf_loops_normal_view.shape[0], //
        buf_corners_color_view.buf,
        buf_corners_color_view.buf == NULL ? 0
                                           : buf_corners_color_view.shape[0], //
        buf_loops_uv_view.buf,
        buf_loops_uv_view.buf == NULL ? 0 : buf_loops_uv_view.shape[0], //
        material_infos.buffer, material_infos.len,                      //
        &((struct MaterialInfoObject *)default_material_info)->mat_info);

    PyBuffer_Release(&buf_vertices_co_view);
    PyBuffer_Release(&buf_triangles_loops_view);
    PyBuffer_Release(&buf_triangles_material_index_view);
    PyBuffer_Release(&buf_loops_vertex_index_view);
    PyBuffer_Release(&buf_loops_normal_view);
    if (buf_corners_color_view.buf != NULL)
        PyBuffer_Release(&buf_corners_color_view);
    if (buf_loops_uv_view.buf != NULL)
        PyBuffer_Release(&buf_loops_uv_view);
    free_MaterialInfoSequenceInfo(&material_infos);

    if (mesh == NULL) {
        PyErr_SetString(PyExc_MemoryError,
                        "create_MeshInfo_from_buffers failed");
        return NULL;
    }

    struct MeshInfoObject *mesh_info_object;

    // TODO is this how to create objects?
    printf("%s: PyObject_New...\n", __FUNCTION__);
    // FIXME PyObject_New does not call MeshInfo_new so must be wrong (no it's
    // not necessarily wrong)
    mesh_info_object = PyObject_New(struct MeshInfoObject, &MeshInfoType);
    if (mesh_info_object == NULL) {
        PyErr_SetString(PyExc_MemoryError, "PyObject_New failed");
        return NULL;
    }
    printf("%s: PyObject_Init...\n", __FUNCTION__);
    if (PyObject_Init((PyObject *)mesh_info_object,
                      Py_TYPE(mesh_info_object)) == NULL) {
        // ? (can init even return NULL?) (no it can't)
        Py_DECREF(mesh_info_object);
        return NULL;
    }

    mesh_info_object->mesh = mesh;

    return (PyObject *)mesh_info_object;
}

static int dragex_backend_exec(PyObject *m) {
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
    printf("%s: compiled %s %s\n", __FUNCTION__, __DATE__, __TIME__);
    return PyModuleDef_Init(&dragex_backend_module);
}
