#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stddef.h>
#include <stdlib.h>

#include "converters.h"
#include "oot_collision_objs.h"

#include "../logging/logging.h"

#include "../exporter.h"

static void OoTCollisionMaterial_dealloc(PyObject *_self) {
    struct OoTCollisionMaterialObject *self =
        (struct OoTCollisionMaterialObject *)_self;

    free(self->mat.surface_type_0);
    free(self->mat.surface_type_1);
    free(self->mat.flags_a);
    free(self->mat.flags_b);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *OoTCollisionMaterial_new(PyTypeObject *type, PyObject *args,
                                          PyObject *kwds) {
    struct OoTCollisionMaterialObject *self;
    self = (struct OoTCollisionMaterialObject *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->mat.surface_type_0 = NULL;
        self->mat.surface_type_1 = NULL;
        self->mat.flags_a = NULL;
        self->mat.flags_b = NULL;
    }
    return (PyObject *)self;
}

static int OoTCollisionMaterial_init(PyObject *_self, PyObject *args,
                                     PyObject *kwds) {
    struct OoTCollisionMaterialObject *self =
        (struct OoTCollisionMaterialObject *)_self;
    static char *kwlist[] = {
        "surface_type_0", "surface_type_1", "flags_a", "flags_b", NULL,
    };
    char *surface_type_0, *surface_type_1, *flags_a, *flags_b;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "ssss", kwlist,
                                     &surface_type_0, &surface_type_1, &flags_a,
                                     &flags_b))
        return -1;

    if (self->mat.surface_type_0 != NULL) {
        free(self->mat.surface_type_0);
    }
    self->mat.surface_type_0 = strdup(surface_type_0);

    if (self->mat.surface_type_1 != NULL) {
        free(self->mat.surface_type_1);
    }
    self->mat.surface_type_1 = strdup(surface_type_1);

    if (self->mat.flags_a != NULL) {
        free(self->mat.flags_a);
    }
    self->mat.flags_a = strdup(flags_a);

    if (self->mat.flags_b != NULL) {
        free(self->mat.flags_b);
    }
    self->mat.flags_b = strdup(flags_b);

    return 0;
}

PyTypeObject OoTCollisionMaterialType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.OoTCollisionMaterial",
    .tp_doc = PyDoc_STR("OoT collision material"),
    .tp_basicsize = sizeof(struct OoTCollisionMaterialObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = OoTCollisionMaterial_new,
    .tp_init = OoTCollisionMaterial_init,
    .tp_dealloc = OoTCollisionMaterial_dealloc,
};

static void OoTCollisionMesh_dealloc(PyObject *_self) {
    struct OoTCollisionMeshObject *self =
        (struct OoTCollisionMeshObject *)_self;

    log_trace("entry");

    if (self->mesh != NULL) {
        free_create_OoTCollisionMesh_from_buffers(self->mesh);
    }

    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *OoTCollisionMesh_new(PyTypeObject *type, PyObject *args,
                                      PyObject *kwds) {
    struct OoTCollisionMeshObject *self;

    log_trace("entry");

    self = (struct OoTCollisionMeshObject *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->mesh = NULL;
    }
    return (PyObject *)self;
}

static PyObject *OoTCollisionMesh_write_c(PyObject *_self, PyObject *args) {
    struct OoTCollisionMeshObject *self =
        (struct OoTCollisionMeshObject *)_self;
    int fd;
    const char *vtx_list_name, *poly_list_name, *surface_types_name;

    if (!PyArg_ParseTuple(args, "isss", &fd, &vtx_list_name, &poly_list_name,
                          &surface_types_name))
        return NULL;

    FILE *f = fdopen(dup(fd), "w");
    if (f == NULL) {
        PyErr_Format(PyExc_IOError, "Failed to open fd for writing. fdopen: %s",
                     strerror(errno));
        return NULL;
    }

    struct OoTCollisionBounds bounds;
    int res =
        write_OoTCollisionMesh_to_c(self->mesh, vtx_list_name, poly_list_name,
                                    surface_types_name, f, &bounds);

    fclose(f);

    if (res != 0) {
        PyErr_SetString(PyExc_Exception, "write_OoTCollisionMesh_to_c failed");
        return NULL;
    }

    struct OoTCollisionBoundsObject *bounds_obj =
        PyObject_New(struct OoTCollisionBoundsObject, &OoTCollisionBoundsType);
    if (bounds_obj == NULL) {
        PyErr_SetString(PyExc_MemoryError, "PyObject_New failed");
        return NULL;
    }

    bounds_obj->bounds = bounds;

    return (PyObject *)bounds_obj;
}

static PyMethodDef OoTCollisionMesh_methods[] = {
    {"write_c", OoTCollisionMesh_write_c, METH_VARARGS,
     "Write mesh to a .c file"},
    {NULL} /* Sentinel */
};

PyTypeObject OoTCollisionMeshType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.OoTCollisionMesh",
    .tp_doc = PyDoc_STR("OoT collision mesh"),
    .tp_basicsize = sizeof(struct OoTCollisionMeshObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = OoTCollisionMesh_new,
    .tp_dealloc = OoTCollisionMesh_dealloc,
    .tp_methods = OoTCollisionMesh_methods,
};

struct OoTCollisionMaterialObjectSequenceInfo {
    struct OoTCollisionMaterialObject **buffer;
    Py_ssize_t len;
};

void free_OoTCollisionMaterialSequenceInfo(
    struct OoTCollisionMaterialObjectSequenceInfo *materials) {

    for (Py_ssize_t i = 0; i < materials->len; i++)
        Py_XDECREF(materials->buffer[i]);

    free(materials->buffer);
}

int converter_OoTCollisionMaterialObject_or_None_sequence(PyObject *obj,
                                                          void *_result) {
    Py_ssize_t len = PySequence_Length(obj);
    if (len < 0)
        return 0;

    struct OoTCollisionMaterialObject **buffer =
        malloc(sizeof(struct OoTCollisionMaterialObject *) * len);
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
        } else if (PyObject_TypeCheck(item, &OoTCollisionMaterialType)) {
            buffer[i] = (struct OoTCollisionMaterialObject *)item;
        } else {
            PyErr_Format(PyExc_TypeError,
                         "Object in sequence at index %ld is not None or a %s",
                         (long)i, OoTCollisionMaterialType.tp_name);
            for (Py_ssize_t j = 0; j < i; j++)
                Py_XDECREF(buffer[j]);
            free(buffer);
            return 0;
        }
    }

    struct OoTCollisionMaterialObjectSequenceInfo *result =
        (struct OoTCollisionMaterialObjectSequenceInfo *)_result;
    result->buffer = buffer;
    result->len = len;
    return 1;
}

PyObject *create_OoTCollisionMesh(PyObject *self, PyObject *args) {
    Py_buffer buf_vertices_co_view, buf_triangles_loops_view,
        buf_triangles_material_index_view, buf_loops_vertex_index_view;
    struct OoTCollisionMaterialObjectSequenceInfo materials_objects;
    PyObject *_default_material_info;

    if (!PyArg_ParseTuple(
            args, "O&O&O&O&O&O!",                                        //
            converter_contiguous_float_buffer, &buf_vertices_co_view,    //
            converter_contiguous_uint_buffer, &buf_triangles_loops_view, //
            converter_contiguous_uint_buffer,
            &buf_triangles_material_index_view,                             //
            converter_contiguous_uint_buffer, &buf_loops_vertex_index_view, //
            converter_OoTCollisionMaterialObject_or_None_sequence,
            &materials_objects, //
            &OoTCollisionMaterialType, &_default_material_info))
        return NULL;

    struct OoTCollisionMaterialObject *default_material_info =
        (struct OoTCollisionMaterialObject *)_default_material_info;

    struct OoTCollisionMaterial **materials;
    size_t n_materials = materials_objects.len;

    materials = malloc(sizeof(struct OoTCollisionMaterial *) * n_materials);
    // TODO check malloc

    for (Py_ssize_t i = 0; i < materials_objects.len; i++) {
        materials[i] = &materials_objects.buffer[i]->mat;
    }

    // This also decreases the reference counts of the strings we keep pointers
    // to in the materials array, but that's fine as the objects are still
    // referenced elsewhere due to being passed as arguments.
    free_OoTCollisionMaterialSequenceInfo(&materials_objects);

    struct OoTCollisionMesh *mesh;

    mesh = create_OoTCollisionMesh_from_buffers(
        buf_vertices_co_view.buf, buf_vertices_co_view.shape[0],         //
        buf_triangles_loops_view.buf, buf_triangles_loops_view.shape[0], //
        buf_triangles_material_index_view.buf,
        buf_triangles_material_index_view.shape[0], //
        buf_loops_vertex_index_view.buf, buf_loops_vertex_index_view.shape[0],
        materials, n_materials, //
        &default_material_info->mat);

    PyBuffer_Release(&buf_vertices_co_view);
    PyBuffer_Release(&buf_triangles_loops_view);
    PyBuffer_Release(&buf_triangles_material_index_view);
    PyBuffer_Release(&buf_loops_vertex_index_view);
    free(materials);

    if (mesh == NULL) {
        PyErr_SetString(PyExc_MemoryError,
                        "create_OoTCollisionMesh_from_buffers failed");
        return NULL;
    }

    struct OoTCollisionMeshObject *mesh_object;

    // TODO is this how to create objects?
    log_debug("PyObject_New...");
    // FIXME PyObject_New does not call OoTCollisionMesh_new so must be wrong
    // (no it's not necessarily wrong)
    mesh_object =
        PyObject_New(struct OoTCollisionMeshObject, &OoTCollisionMeshType);
    if (mesh_object == NULL) {
        PyErr_SetString(PyExc_MemoryError, "PyObject_New failed");
        return NULL;
    }
    log_debug("PyObject_Init...");
    if (PyObject_Init((PyObject *)mesh_object, Py_TYPE(mesh_object)) == NULL) {
        // ? (can init even return NULL?) (no it can't)
        Py_DECREF(mesh_object);
        return NULL;
    }

    mesh_object->mesh = mesh;

    return (PyObject *)mesh_object;
}

struct OoTCollisionMeshObjectSequenceInfo {
    struct OoTCollisionMeshObject **buffer;
    Py_ssize_t len;
};

void free_OoTCollisionMeshSequenceInfo(
    struct OoTCollisionMeshObjectSequenceInfo *materials) {

    for (Py_ssize_t i = 0; i < materials->len; i++)
        Py_XDECREF(materials->buffer[i]);

    free(materials->buffer);
}

int converter_OoTCollisionMeshObject_sequence(PyObject *obj, void *_result) {
    Py_ssize_t len = PySequence_Length(obj);
    if (len < 0)
        return 0;

    struct OoTCollisionMeshObject **buffer =
        malloc(sizeof(struct OoTCollisionMeshObject *) * len);
    // TODO check malloc
    for (Py_ssize_t i = 0; i < len; i++) {
        PyObject *item = PySequence_GetItem(obj, i);
        if (item == NULL) {
            for (Py_ssize_t j = 0; j < i; j++)
                Py_XDECREF(buffer[j]);
            free(buffer);
            return 0;
        }

        if (PyObject_TypeCheck(item, &OoTCollisionMeshType)) {
            buffer[i] = (struct OoTCollisionMeshObject *)item;
        } else {
            PyErr_Format(PyExc_TypeError,
                         "Object in sequence at index %ld is not a %s", (long)i,
                         OoTCollisionMeshType.tp_name);
            for (Py_ssize_t j = 0; j < i; j++)
                Py_XDECREF(buffer[j]);
            free(buffer);
            return 0;
        }
    }

    struct OoTCollisionMeshObjectSequenceInfo *result =
        (struct OoTCollisionMeshObjectSequenceInfo *)_result;
    result->buffer = buffer;
    result->len = len;
    return 1;
}

PyObject *join_OoTCollisionMeshes(PyObject *self, PyObject *args) {
    struct OoTCollisionMeshObjectSequenceInfo meshes_objects;

    if (!PyArg_ParseTuple(args, "O&", converter_OoTCollisionMeshObject_sequence,
                          &meshes_objects))
        return NULL;

    struct OoTCollisionMesh **meshes =
        malloc(sizeof(struct OoTCollisionMesh *) * meshes_objects.len);
    if (meshes == NULL) {
        PyErr_SetString(PyExc_MemoryError, "malloc meshes failed");
        return NULL;
    }
    for (Py_ssize_t i = 0; i < meshes_objects.len; i++)
        meshes[i] = meshes_objects.buffer[i]->mesh;

    struct OoTCollisionMesh *mesh =
        join_OoTCollisionMeshes_impl(meshes, (size_t)meshes_objects.len);

    struct OoTCollisionMeshObject *mesh_object;

    // TODO is this how to create objects?
    log_debug("PyObject_New...");
    // FIXME PyObject_New does not call OoTCollisionMesh_new so must be wrong
    // (no it's not necessarily wrong)
    mesh_object =
        PyObject_New(struct OoTCollisionMeshObject, &OoTCollisionMeshType);
    if (mesh_object == NULL) {
        PyErr_SetString(PyExc_MemoryError, "PyObject_New failed");
        return NULL;
    }
    log_debug("PyObject_Init...");
    if (PyObject_Init((PyObject *)mesh_object, Py_TYPE(mesh_object)) == NULL) {
        // ? (can init even return NULL?) (no it can't)
        Py_DECREF(mesh_object);
        return NULL;
    }

    mesh_object->mesh = mesh;

    return (PyObject *)mesh_object;
}

static PyObject *OoTCollisionBounds_getmin(PyObject *_self, void *closure) {
    struct OoTCollisionBoundsObject *self =
        (struct OoTCollisionBoundsObject *)_self;
    static_assert(sizeof(self->bounds.min[0]) == sizeof(short),
                  "int16_t != short");
    return Py_BuildValue("(hhh)", self->bounds.min[0], self->bounds.min[1],
                         self->bounds.min[2]);
}

static PyObject *OoTCollisionBounds_getmax(PyObject *_self, void *closure) {
    struct OoTCollisionBoundsObject *self =
        (struct OoTCollisionBoundsObject *)_self;
    static_assert(sizeof(self->bounds.max[0]) == sizeof(short),
                  "int16_t != short");
    return Py_BuildValue("(hhh)", self->bounds.max[0], self->bounds.max[1],
                         self->bounds.max[2]);
}

static PyGetSetDef Custom_getsetters[] = {
    {"min", OoTCollisionBounds_getmin, NULL, "bounds minimum", NULL},
    {"max", OoTCollisionBounds_getmax, NULL, "bounds maximum", NULL},
    {NULL} /* Sentinel */
};

PyTypeObject OoTCollisionBoundsType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name =
        "dragex_backend.OoTCollisionBounds",
    .tp_doc = PyDoc_STR("OoT collision bounds"),
    .tp_basicsize = sizeof(struct OoTCollisionBoundsObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_getset = Custom_getsetters,
};
