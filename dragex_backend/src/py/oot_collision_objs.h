#ifndef DRAGEX_OOT_COLLISION_OBJS_H
#define DRAGEX_OOT_COLLISION_OBJS_H

#ifndef PY_SSIZE_T_CLEAN
#define PY_SSIZE_T_CLEAN
#endif
#include <Python.h>

#include <stddef.h>

#include "../exporter.h"

struct OoTCollisionMaterialObject {
    PyObject_HEAD

        struct OoTCollisionMaterial mat;
};

extern PyTypeObject OoTCollisionMaterialType;

struct OoTCollisionMeshObject {
    PyObject_HEAD

        struct OoTCollisionMesh *mesh;
};

extern PyTypeObject OoTCollisionMeshType;

PyObject *create_OoTCollisionMesh(PyObject *self, PyObject *args);

PyObject *join_OoTCollisionMeshes(PyObject *self, PyObject *args);

struct OoTCollisionBoundsObject {
    PyObject_HEAD

        struct OoTCollisionBounds bounds;
};

extern PyTypeObject OoTCollisionBoundsType;

#endif
