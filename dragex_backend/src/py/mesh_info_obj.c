#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <assert.h>
#include <errno.h>
#include <stddef.h>
#include <stdlib.h>

#include "converters.h"
#include "objs.h"

#include "../logging/logging.h"

#include "../exporter.h"

static void MeshInfo_dealloc(PyObject *_self) {
    struct MeshInfoObject *self = (struct MeshInfoObject *)_self;

    log_trace("entry");

    if (self->image_objects != NULL) {
        for (size_t i = 0; i < self->len_image_objects; i++) {
            Py_XDECREF(self->image_objects[i]);
        }
        free(self->image_objects);
    }

    if (self->mesh != NULL) {
        free_create_MeshInfo_from_buffers(self->mesh);
    }

    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *MeshInfo_new(PyTypeObject *type, PyObject *args,
                              PyObject *kwds) {
    struct MeshInfoObject *self;

    log_trace("entry");

    self = (struct MeshInfoObject *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->image_objects = NULL;
        self->mesh = NULL;
    }
    return (PyObject *)self;
}

static PyObject *MeshInfo_write_c(PyObject *_self, PyObject *args) {
    struct MeshInfoObject *self = (struct MeshInfoObject *)_self;
    int fd;

    if (!PyArg_ParseTuple(args, "i", &fd))
        return NULL;

    FILE *f = fdopen(dup(fd), "w");
    if (f == NULL) {
        PyErr_Format(PyExc_IOError, "Failed to open fd for writing. fdopen: %s",
                     strerror(errno));
        return NULL;
    }

    char *dl_name = NULL;
    int res = write_mesh_info_to_f3d_c(self->mesh, f, &dl_name);

    fclose(f);

    if (res != 0) {
        PyErr_SetString(PyExc_Exception, "write_mesh_info_to_f3d_c failed");
        free(dl_name);
        return NULL;
    }

    PyObject *dl_name_obj = PyUnicode_FromString(dl_name);

    free(dl_name);

    if (dl_name_obj == NULL) {
        return NULL;
    }

    return dl_name_obj;
}

static PyMethodDef MeshInfo_methods[] = {
    {"write_c", MeshInfo_write_c, METH_VARARGS, "Write mesh to a .c file"},
    {NULL} /* Sentinel */
};

PyTypeObject MeshInfoType = {
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

struct MaterialInfoObjectSequenceInfo {
    struct MaterialInfoObject **buffer;
    Py_ssize_t len;
};

void free_MaterialInfoSequenceInfo(
    struct MaterialInfoObjectSequenceInfo *material_infos) {

    for (Py_ssize_t i = 0; i < material_infos->len; i++)
        Py_XDECREF(material_infos->buffer[i]);

    free(material_infos->buffer);
}

int converter_MaterialInfoObject_or_None_sequence(PyObject *obj,
                                                  void *_result) {
    Py_ssize_t len = PySequence_Length(obj);
    if (len < 0)
        return 0;

    struct MaterialInfoObject **buffer =
        malloc(sizeof(struct MaterialInfoObject *) * len);
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
        } else if (PyObject_TypeCheck(item, &MaterialInfoType)) {
            buffer[i] = (struct MaterialInfoObject *)item;
        } else {
            PyErr_Format(PyExc_TypeError,
                         "Object in sequence at index %ld is not None or a %s",
                         (long)i, MaterialInfoType.tp_name);
            for (Py_ssize_t j = 0; j < i; j++)
                Py_XDECREF(buffer[j]);
            free(buffer);
            return 0;
        }
    }

    struct MaterialInfoObjectSequenceInfo *result =
        (struct MaterialInfoObjectSequenceInfo *)_result;
    result->buffer = buffer;
    result->len = len;
    return 1;
}

PyObject *create_MeshInfo(PyObject *self, PyObject *args) {
    Py_buffer buf_vertices_co_view, buf_triangles_loops_view,
        buf_triangles_material_index_view, buf_loops_vertex_index_view,
        buf_loops_normal_view, buf_corners_color_view, buf_points_color_view,
        buf_loops_uv_view;
    struct MaterialInfoObjectSequenceInfo material_info_objects;
    PyObject *_default_material_info;

    if (!PyArg_ParseTuple(
            args, "O&O&O&O&O&O&O&O&O&O!",                                //
            converter_contiguous_float_buffer, &buf_vertices_co_view,    //
            converter_contiguous_uint_buffer, &buf_triangles_loops_view, //
            converter_contiguous_uint_buffer,
            &buf_triangles_material_index_view,
            converter_contiguous_uint_buffer, &buf_loops_vertex_index_view, //
            converter_contiguous_float_buffer, &buf_loops_normal_view,      //
            converter_contiguous_float_buffer_optional,
            &buf_corners_color_view, //
            converter_contiguous_float_buffer_optional,
            &buf_points_color_view,                                         //
            converter_contiguous_float_buffer_optional, &buf_loops_uv_view, //
            converter_MaterialInfoObject_or_None_sequence,
            &material_info_objects, //
            &MaterialInfoType, &_default_material_info))
        return NULL;

    struct MaterialInfoObject *default_material_info =
        (struct MaterialInfoObject *)_default_material_info;

    struct MaterialInfoImageObject **image_objects;
    size_t len_image_objects;

    struct MaterialInfo **material_infos;
    size_t n_material_infos = material_info_objects.len;

    // + 1 for default_material_info
    len_image_objects = (n_material_infos + 1) * 8;
    image_objects =
        malloc(sizeof(struct MaterialInfoImageObject *) * len_image_objects);
    material_infos = malloc(sizeof(struct MaterialInfo *) * n_material_infos);
    // TODO check malloc

    for (Py_ssize_t i = 0; i < material_info_objects.len; i++) {
        material_infos[i] = &material_info_objects.buffer[i]->mat_info;
        for (int j = 0; j < 8; j++) {
            assert((size_t)(i * 8 + j) < len_image_objects);
            image_objects[i * 8 + j] =
                material_info_objects.buffer[i]->image_objects[j];
        }
    }

    for (int j = 0; j < 8; j++) {
        assert((size_t)(n_material_infos * 8 + j) < len_image_objects);
        image_objects[n_material_infos * 8 + j] =
            default_material_info->image_objects[j];
    }

    // This also decreases the reference counts of the image_objects before we
    // increase it below, but that's fine as the objects are still referenced
    // elsewhere due to being passed as arguments.
    free_MaterialInfoSequenceInfo(&material_info_objects);

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
        buf_points_color_view.buf,
        buf_points_color_view.buf == NULL ? 0
                                          : buf_points_color_view.shape[0], //
        buf_loops_uv_view.buf,
        buf_loops_uv_view.buf == NULL ? 0 : buf_loops_uv_view.shape[0], //
        material_infos, n_material_infos,                               //
        &default_material_info->mat_info);

    PyBuffer_Release(&buf_vertices_co_view);
    PyBuffer_Release(&buf_triangles_loops_view);
    PyBuffer_Release(&buf_triangles_material_index_view);
    PyBuffer_Release(&buf_loops_vertex_index_view);
    PyBuffer_Release(&buf_loops_normal_view);
    if (buf_corners_color_view.buf != NULL)
        PyBuffer_Release(&buf_corners_color_view);
    if (buf_points_color_view.buf != NULL)
        PyBuffer_Release(&buf_points_color_view);
    if (buf_loops_uv_view.buf != NULL)
        PyBuffer_Release(&buf_loops_uv_view);
    free(material_infos);

    if (mesh == NULL) {
        PyErr_SetString(PyExc_MemoryError,
                        "create_MeshInfo_from_buffers failed");
        free(image_objects);
        return NULL;
    }

    struct MeshInfoObject *mesh_info_object;

    // TODO is this how to create objects?
    log_debug("PyObject_New...");
    // FIXME PyObject_New does not call MeshInfo_new so must be wrong (no it's
    // not necessarily wrong)
    mesh_info_object = PyObject_New(struct MeshInfoObject, &MeshInfoType);
    if (mesh_info_object == NULL) {
        PyErr_SetString(PyExc_MemoryError, "PyObject_New failed");
        free(image_objects);
        return NULL;
    }
    log_debug("PyObject_Init...");
    if (PyObject_Init((PyObject *)mesh_info_object,
                      Py_TYPE(mesh_info_object)) == NULL) {
        // ? (can init even return NULL?) (no it can't)
        Py_DECREF(mesh_info_object);
        free(image_objects);
        return NULL;
    }

    for (size_t i = 0; i < len_image_objects; i++)
        Py_XINCREF(image_objects[i]);

    mesh_info_object->image_objects = image_objects;
    mesh_info_object->len_image_objects = len_image_objects;
    mesh_info_object->mesh = mesh;

    return (PyObject *)mesh_info_object;
}
