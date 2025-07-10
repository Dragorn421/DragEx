#ifndef DRAGEX_OBJS_H
#define DRAGEX_OBJS_H

#ifndef PY_SSIZE_T_CLEAN
#define PY_SSIZE_T_CLEAN
#endif
#include <Python.h>

#include "../exporter.h"

struct MaterialInfoImageObject {
    PyObject_HEAD

        struct MaterialInfoImage image;
};

extern PyTypeObject MaterialInfoImageType;

struct MaterialInfoOtherModesObject {
    PyObject_HEAD

        struct MaterialInfoOtherModes other_modes;
};

extern PyTypeObject MaterialInfoOtherModesType;

struct MaterialInfoTileObject {
    PyObject_HEAD

        struct MaterialInfoImageObject *image_object;
    struct MaterialInfoTile tile;
};

extern PyTypeObject MaterialInfoTileType;

struct MaterialInfoCombinerObject {
    PyObject_HEAD

        struct MaterialInfoCombiner combiner;
};

extern PyTypeObject MaterialInfoCombinerType;

struct MaterialInfoValsObject {
    PyObject_HEAD

        struct MaterialInfoVals vals;
};

extern PyTypeObject MaterialInfoValsType;

struct MaterialInfoGeometryModeObject {
    PyObject_HEAD

        struct MaterialInfoGeometryMode geometry_mode;
};

extern PyTypeObject MaterialInfoGeometryModeType;

struct MaterialInfoObject {
    PyObject_HEAD

        struct MaterialInfoImageObject *image_objects[8];
    struct MaterialInfo mat_info;
};

extern PyTypeObject MaterialInfoType;

struct MeshInfoObject {
    PyObject_HEAD

        struct MaterialInfoImageObject **image_objects;
    size_t len_image_objects;
    struct MeshInfo *mesh;
};

extern PyTypeObject MeshInfoType;

PyObject *create_MeshInfo(PyObject *self, PyObject *args);

#endif
