#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stddef.h>
#include <stdio.h>

#include "name_to_enum.h"
#include "objs.h"

#include "../logging/logging.h"

#include "../exporter.h"

static void MaterialInfoTile_dealloc(PyObject *_self) {
    struct MaterialInfoTileObject *self =
        (struct MaterialInfoTileObject *)_self;

    log_trace("entry");

    Py_XDECREF(self->image_object);
}

static PyObject *MaterialInfoTile_new(PyTypeObject *type, PyObject *args,
                                      PyObject *kwds) {
    struct MaterialInfoTileObject *self;

    log_trace("entry");

    self = (struct MaterialInfoTileObject *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->image_object = NULL;
    }
    return (PyObject *)self;
}

static int converter_MaterialInfoImage_or_None(PyObject *obj, void *_result) {
    struct MaterialInfoImageObject **result =
        (struct MaterialInfoImageObject **)_result;

    if (obj == Py_None) {
        *result = NULL;
        return 1;
    }

    if (PyObject_TypeCheck(obj, &MaterialInfoImageType)) {
        *result = (struct MaterialInfoImageObject *)obj;
        return 1;
    } else {
        PyErr_Format(PyExc_TypeError, "Object is not None or a %s",
                     MaterialInfoImageType.tp_name);
        return 0;
    }
}

static int MaterialInfoTile_init(PyObject *_self, PyObject *args,
                                 PyObject *kwds) {
    struct MaterialInfoTileObject *self =
        (struct MaterialInfoTileObject *)_self;
    static char *kwlist[] = {
        "image",         "format",        "size",         "line",
        "address",       "palette",       "clamp_T",      "mirror_T",
        "mask_T",        "shift_T",       "clamp_S",      "mirror_S",
        "mask_S",        "shift_S",       "upper_left_S", "upper_left_T",
        "lower_right_S", "lower_right_T", NULL,
    };
    struct MaterialInfoImageObject *image;
    char *format_name;
    char *size_name;
    int line;
    int address;
    int palette;
    int clamp_T;
    int mirror_T;
    int mask_T;
    int shift_T;
    int clamp_S;
    int mirror_S;
    int mask_S;
    int shift_S;

    float upper_left_S;
    float upper_left_T;
    float lower_right_S;
    float lower_right_T;

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds,
            "O&"
            "ssiiippiippii"
            "ffff",
            kwlist,

            converter_MaterialInfoImage_or_None, &image,

            &format_name, &size_name, &line, &address, &palette, &clamp_T,
            &mirror_T, &mask_T, &shift_T, &clamp_S, &mirror_S, &mask_S,
            &shift_S,

            &upper_left_S, &upper_left_T, &lower_right_S, &lower_right_T))
        return -1;

    static const char *format_names[] = {
        [RDP_TILE_FORMAT_RGBA] = "RGBA", [RDP_TILE_FORMAT_YUV] = "YUV",
        [RDP_TILE_FORMAT_CI] = "CI",     [RDP_TILE_FORMAT_IA] = "IA",
        [RDP_TILE_FORMAT_I] = "I",
    };
    enum rdp_tile_format format;
    NAME_TO_ENUM(format, format_names);

    static const char *size_names[] = {
        [RDP_TILE_SIZE_4] = "4",
        [RDP_TILE_SIZE_8] = "8",
        [RDP_TILE_SIZE_16] = "16",
        [RDP_TILE_SIZE_32] = "32",
    };
    enum rdp_tile_size size;
    NAME_TO_ENUM(size, size_names);

    if (image == NULL) {
        self->tile.image = NULL;
    } else {
        Py_INCREF(image);
        self->image_object = image;

        self->tile.image = &image->image;
    }

    self->tile.format = format;
    self->tile.size = size;
    self->tile.line = line;
    self->tile.address = address;
    self->tile.palette = palette;
    self->tile.clamp_T = clamp_T;
    self->tile.mirror_T = mirror_T;
    self->tile.mask_T = mask_T;
    self->tile.shift_T = shift_T;
    self->tile.clamp_S = clamp_S;
    self->tile.mirror_S = mirror_S;
    self->tile.mask_S = mask_S;
    self->tile.shift_S = shift_S;

    self->tile.upper_left_S = upper_left_S;
    self->tile.upper_left_T = upper_left_T;
    self->tile.lower_right_S = lower_right_S;
    self->tile.lower_right_T = lower_right_T;

    return 0;
}

PyTypeObject MaterialInfoTileType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)

                   .tp_name = "dragex_backend.MaterialInfoTile",
    .tp_doc = PyDoc_STR("material info tile"),
    .tp_basicsize = sizeof(struct MaterialInfoTileObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = MaterialInfoTile_new,
    .tp_init = MaterialInfoTile_init,
    .tp_dealloc = MaterialInfoTile_dealloc,
};
