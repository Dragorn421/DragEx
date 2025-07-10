#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <assert.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#include "objs.h"

#include "../exporter.h"

static void MaterialInfo_dealloc(PyObject *_self) {
    struct MaterialInfoObject *self = (struct MaterialInfoObject *)_self;

    for (int i = 0; i < 8; i++)
        Py_XDECREF(self->image_objects[i]);

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

struct MaterialInfoTileObjectSequenceInfo {
    struct MaterialInfoTileObject **buffer;
    Py_ssize_t len;
};

void free_MaterialInfoTileSequenceInfo(
    struct MaterialInfoTileObjectSequenceInfo *tile_infos) {

    for (Py_ssize_t i = 0; i < tile_infos->len; i++)
        Py_DECREF(tile_infos->buffer[i]);

    free(tile_infos->buffer);
}

int converter_MaterialInfoTileObject_sequence_len8(PyObject *obj,
                                                   void *_result) {
    Py_ssize_t len = PySequence_Length(obj);
    if (len < 0)
        return 0;
    if (len != 8) {
        PyErr_Format(PyExc_IndexError,
                     "Expected a sequence of length 8, not %ld", (long)len);
        return 0;
    }

    struct MaterialInfoTileObject **buffer =
        malloc(sizeof(struct MaterialInfoTileObject *) * len);
    // TODO check malloc
    for (Py_ssize_t i = 0; i < len; i++) {
        PyObject *item = PySequence_GetItem(obj, i);
        if (item == NULL) {
            for (Py_ssize_t j = 0; j < i; j++)
                Py_DECREF(buffer[j]);
            free(buffer);
            return 0;
        }

        if (PyObject_TypeCheck(item, &MaterialInfoTileType)) {
            buffer[i] = (struct MaterialInfoTileObject *)item;
        } else {
            PyErr_Format(PyExc_TypeError,
                         "Object in sequence at index %ld is not a %s", (long)i,
                         MaterialInfoTileType.tp_name);
            for (Py_ssize_t j = 0; j < i; j++)
                Py_DECREF(buffer[j]);
            free(buffer);
            return 0;
        }
    }

    struct MaterialInfoTileObjectSequenceInfo *result =
        (struct MaterialInfoTileObjectSequenceInfo *)_result;
    result->buffer = buffer;
    result->len = len;
    return 1;
}

static int MaterialInfo_init(PyObject *_self, PyObject *args, PyObject *kwds) {
    struct MaterialInfoObject *self = (struct MaterialInfoObject *)_self;
    static char *kwlist[] = {
        "name",     "uv_basis_s", "uv_basis_t",    "other_modes", "tiles",
        "combiner", "vals",       "geometry_mode", NULL,
    };
    char *name;
    int uv_basis_s, uv_basis_t;
    PyObject *_other_modes, *_combiner, *_geometry_mode, *_vals;
    struct MaterialInfoTileObjectSequenceInfo tile_infos;

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds,
            "sii"
            "O!O&O!O!O!",
            kwlist,

            &name, &uv_basis_s, &uv_basis_t,

            &MaterialInfoOtherModesType, &_other_modes,
            converter_MaterialInfoTileObject_sequence_len8, &tile_infos,
            &MaterialInfoCombinerType, &_combiner, //
            &MaterialInfoValsType, &_vals,         //
            &MaterialInfoGeometryModeType, &_geometry_mode))
        return -1;

    struct MaterialInfoOtherModesObject *other_modes =
        (struct MaterialInfoOtherModesObject *)_other_modes;

    struct MaterialInfoCombinerObject *combiner =
        (struct MaterialInfoCombinerObject *)_combiner;

    struct MaterialInfoValsObject *vals =
        (struct MaterialInfoValsObject *)_vals;

    struct MaterialInfoGeometryModeObject *geometry_mode =
        (struct MaterialInfoGeometryModeObject *)_geometry_mode;

    if (self->mat_info.name != NULL) {
        free(self->mat_info.name);
    }
    self->mat_info.name = strdup(name);
    self->mat_info.uv_basis_s = uv_basis_s;
    self->mat_info.uv_basis_t = uv_basis_t;
    self->mat_info.other_modes = other_modes->other_modes;
    assert(tile_infos.len == 8);
    for (int i = 0; i < 8; i++) {
        Py_XINCREF(tile_infos.buffer[i]->image_object);
        self->image_objects[i] = tile_infos.buffer[i]->image_object;
        self->mat_info.tiles[i] = tile_infos.buffer[i]->tile;
    }
    self->mat_info.combiner = combiner->combiner;
    self->mat_info.vals = vals->vals;
    self->mat_info.geometry_mode = geometry_mode->geometry_mode;

    free_MaterialInfoTileSequenceInfo(&tile_infos);

    return 0;
}

PyTypeObject MaterialInfoType = {
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
