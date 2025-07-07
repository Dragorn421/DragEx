#ifndef DRAGEX_BACKEND_EXPORTER_H
#define DRAGEX_BACKEND_EXPORTER_H

#include "stdbool.h"
#include "stddef.h"
#include "stdint.h"

// info

struct VertexInfo {
    float coords[3];
    float normal[3];
    uint8_t color[4]; // RGBA
};

struct TriInfo {
    unsigned int verts[3];
    unsigned int material;
};

struct MaterialInfo {
    char *name;
    bool lighting;
};

struct MeshInfo {
    char *name;
    struct VertexInfo *verts;
    struct TriInfo *faces;
    struct MaterialInfo *materials;
    unsigned int n_verts, n_faces, n_materials;
};

void free_create_MeshInfo_from_buffers(struct MeshInfo *mesh);

struct MeshInfo *create_MeshInfo_from_buffers(
    float *buf_vertices_co, size_t buf_vertices_co_len,                //
    unsigned int *buf_triangles_loops, size_t buf_triangles_loops_len, //
    unsigned int *buf_triangles_material_index,
    size_t buf_triangles_material_index_len,                                 //
    unsigned int *buf_loops_vertex_index, size_t buf_loops_vertex_index_len, //
    float *buf_loops_normal, size_t buf_loops_normal_len,                    //
    float *buf_corners_color, size_t buf_corners_color_len,                  //
    struct MaterialInfo **material_infos, size_t n_material_infos,           //
    struct MaterialInfo *default_material);

// f3d

struct f3d_vertex {
    int16_t coords[3];
    int16_t st[2];
    uint8_t cn[3]; // color/normal
    uint8_t alpha;
};

struct f3d_mesh_load_entry_tri {
    uint8_t indices[3];
};

struct f3d_mesh_load_entry {
    struct f3d_mesh_load_entry_tri *tris;
    int buffer_i;  // index into vertex buffer to load from
    uint8_t n, v0; // arguments to SPVertex
    uint8_t n_tris;
};

struct f3d_mesh {
    struct f3d_vertex *vertices;
    struct f3d_mesh_load_entry *entries;
    int n_vertices;
    int n_entries;
};

//

int write_mesh_info_to_f3d_c(struct MeshInfo *mesh_info, const char *path);

#endif
