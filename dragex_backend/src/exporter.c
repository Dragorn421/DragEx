#include "exporter.h"

#include <inttypes.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "../meshoptimizer/src/meshoptimizer.h"

float clampf(float f, float min, float max) {
    return f < min ? min : f > max ? max : f;
}

void copy_MaterialInfo(struct MaterialInfo *dest, struct MaterialInfo *src) {
    *dest = *src;
    dest->name = strdup(dest->name);
}

void free_create_MeshInfo_from_buffers(struct MeshInfo *mesh) {
    if (mesh != NULL) {
        free(mesh->name);
        free(mesh->verts);
        free(mesh->faces);
        if (mesh->materials != NULL) {
            for (unsigned int i = 0; i < mesh->n_materials; i++) {
                free(mesh->materials[i].name);
            }
            free(mesh->materials);
        }
        free(mesh);
    }
}

struct MeshInfo *create_MeshInfo_from_buffers(
    float *buf_vertices_co, size_t buf_vertices_co_len,                //
    unsigned int *buf_triangles_loops, size_t buf_triangles_loops_len, //
    unsigned int *buf_triangles_material_index,
    size_t buf_triangles_material_index_len,                                 //
    unsigned int *buf_loops_vertex_index, size_t buf_loops_vertex_index_len, //
    float *buf_loops_normal, size_t buf_loops_normal_len,                    //
    float *buf_corners_color, size_t buf_corners_color_len,                  //
    float *buf_loops_uv, size_t buf_loops_uv_len,                            //
    struct MaterialInfo **material_infos, size_t n_material_infos,           //
    struct MaterialInfo *default_material) {

    printf("buf_corners_color = %p\n", buf_corners_color);

    unsigned int n_loops = buf_loops_vertex_index_len;
    if (buf_loops_normal_len != n_loops * 3)
        return NULL;
    if (buf_corners_color != NULL && buf_corners_color_len != n_loops * 4)
        return NULL;
    if (buf_loops_uv != NULL && buf_loops_uv_len != n_loops * 2)
        return NULL;

    unsigned int n_faces = (unsigned int)(buf_triangles_loops_len / 3);
    if (buf_triangles_material_index_len != n_faces)
        return NULL;

    unsigned int n_materials = 0;
    bool use_default_material = false;
    unsigned int default_material_index = ~0u;
    unsigned int material_index_map_len = n_material_infos;
    unsigned int *material_index_map =
        malloc(sizeof(unsigned int[material_index_map_len]));
    if (material_index_map_len != 0 && material_index_map == NULL)
        return NULL;
    for (unsigned int i = 0; i < material_index_map_len; i++) {
        material_index_map[i] = ~0u;
    }
    for (unsigned int i_face = 0; i_face < n_faces; i_face++) {
        unsigned int mat_index = buf_triangles_material_index[i_face];

        if (mat_index >= material_index_map_len) {
            unsigned int prev_material_index_map_len = material_index_map_len;
            material_index_map_len = mat_index + 1;
            void *tmp = realloc(material_index_map,
                                sizeof(unsigned int[material_index_map_len]));
            if (tmp == NULL) {
                free(material_index_map);
                return NULL;
            }
            material_index_map = tmp;
            for (unsigned int i = prev_material_index_map_len;
                 i < material_index_map_len; i++) {
                material_index_map[i] = ~0u;
            }
        }

        if (mat_index >= n_material_infos ||
            material_infos[mat_index] == NULL) {
            if (!use_default_material) {
                use_default_material = true;
                default_material_index = n_materials;
                n_materials++;
            }
            assert(default_material_index != ~0u);
            material_index_map[mat_index] = default_material_index;
        } else {
            if (material_index_map[mat_index] == ~0u) {
                material_index_map[mat_index] = n_materials;
                n_materials++;
            }
        }
    }

    struct MeshInfo *mesh = malloc(sizeof(struct MeshInfo));
    if (mesh == NULL)
        return NULL;
    mesh->name = strdup("mesh");

    mesh->n_verts = n_loops;
    mesh->verts = malloc(sizeof(struct VertexInfo[n_loops]));

    mesh->n_faces = n_faces;
    mesh->faces = malloc(sizeof(struct VertexInfo[n_faces]));

    mesh->n_materials = n_materials;
    mesh->materials = malloc(sizeof(struct MaterialInfo[n_materials]));

    if (mesh->materials != NULL) {
        // for free_create_MeshInfo_from_buffers
        for (unsigned int i = 0; i < n_materials; i++) {
            mesh->materials[i].name = NULL;
        }
    }

    if (mesh->name == NULL || mesh->verts == NULL || mesh->faces == NULL ||
        mesh->materials == NULL) {
        free_create_MeshInfo_from_buffers(mesh);
        return NULL;
    }

    for (unsigned int i_loop = 0; i_loop < n_loops; i_loop++) {
        for (int j = 0; j < 3; j++) {
            unsigned int v = buf_loops_vertex_index[i_loop] * 3 + j;
            if (v >= buf_vertices_co_len) {
                free_create_MeshInfo_from_buffers(mesh);
                return NULL;
            }
            mesh->verts[i_loop].coords[j] = buf_vertices_co[v];
        }

        for (int j = 0; j < 2; j++)
            mesh->verts[i_loop].uv[j] = buf_loops_uv[i_loop * 2 + j];

        for (int j = 0; j < 3; j++)
            mesh->verts[i_loop].normal[j] = buf_loops_normal[i_loop * 3 + j];

        for (int j = 0; j < 4; j++) {
            if (buf_corners_color != NULL) {
                mesh->verts[i_loop].color[j] = (uint8_t)clampf(
                    buf_corners_color[i_loop * 4 + j] * 255, 0, 255);
            } else {
                mesh->verts[i_loop].color[j] = 255;
            }
        }
    }

    for (unsigned int i = 0; i < n_faces; i++) {
        for (int j = 0; j < 3; j++) {
            unsigned int loop = buf_triangles_loops[i * 3 + j];
            if (loop >= n_loops) {
                free_create_MeshInfo_from_buffers(mesh);
                return NULL;
            }
            mesh->faces[i].verts[j] = loop;
        }
        mesh->faces[i].material =
            material_index_map[buf_triangles_material_index[i]];
    }

    for (unsigned int i = 0; i < n_material_infos; i++) {
        if (material_index_map[i] == ~0u ||
            (use_default_material &&
             material_index_map[i] == default_material_index))
            continue;
        struct MaterialInfo *mat_info = material_infos[i];

        // because material_index_map[i] != default_material_index
        assert(mat_info != NULL);

        copy_MaterialInfo(&mesh->materials[material_index_map[i]], mat_info);
    }

    if (use_default_material) {
        assert(default_material_index != ~0u);
        copy_MaterialInfo(&mesh->materials[default_material_index],
                          default_material);
    }

    return mesh;
}

void free_split_mesh_by_material(struct MeshInfo **meshes, int n_meshes) {
    if (meshes != NULL) {
        for (int i = 0; i < n_meshes; i++) {
            struct MeshInfo *m = meshes[i];

            if (m != NULL) {
                free(m->name);
                free(m->verts);
                free(m->faces);
                if (m->materials != NULL) {
                    free(m->materials[0].name);
                    free(m->materials);
                }
                free(m);
            }
        }
    }
    free(meshes);
}

/**
 * @return An array of n_materials pointers
 */
struct MeshInfo **split_mesh_by_material(struct MeshInfo *in_mesh) {
    struct MeshInfo **out_meshes;

    out_meshes = malloc(sizeof(struct MeshInfo * [in_mesh->n_materials]));
    if (out_meshes == NULL)
        return NULL;

    for (unsigned int i_mat = 0; i_mat < in_mesh->n_materials; i_mat++) {
        struct MeshInfo *m = malloc(sizeof(struct MeshInfo));
        if (m == NULL) {
            free_split_mesh_by_material(out_meshes, in_mesh->n_materials);
            return NULL;
        }
        out_meshes[i_mat] = m;

        int n_faces_used = 0;
        uint8_t vertices_used[in_mesh->n_verts];

        memset(vertices_used, 0, in_mesh->n_verts);

        for (unsigned int i_face = 0; i_face < in_mesh->n_faces; i_face++) {
            struct TriInfo *f = &in_mesh->faces[i_face];

            if (f->material == i_mat) {
                n_faces_used++;
                for (int i = 0; i < 3; i++) {
                    vertices_used[f->verts[i]] = 1;
                }
            }
        }

        int n_vertices_used = 0;
        for (unsigned int i_vert = 0; i_vert < in_mesh->n_verts; i_vert++) {
            n_vertices_used += vertices_used[i_vert];
        }

        size_t new_name_len = strlen(in_mesh->name) + strlen("_") +
                              strlen(in_mesh->materials[i_mat].name) + 1;
        m->name = malloc(new_name_len);
        m->verts = malloc(sizeof(struct VertexInfo[n_vertices_used]));
        m->faces = malloc(sizeof(struct TriInfo[n_faces_used]));
        m->materials = malloc(sizeof(struct MaterialInfo[1]));
        if (m->name == NULL || m->verts == NULL || m->faces == NULL ||
            m->materials == NULL) {
            free_split_mesh_by_material(out_meshes, in_mesh->n_materials);
            return NULL;
        }

        snprintf(m->name, new_name_len, "%s_%s", in_mesh->name,
                 in_mesh->materials[i_mat].name);

        m->n_verts = n_vertices_used;
        m->n_faces = n_faces_used;
        m->n_materials = 1;

        unsigned int i_face_new = 0;
        unsigned int i_vert_new = 0;
        memset(vertices_used, 0, in_mesh->n_verts);

        unsigned int verts_remap[in_mesh->n_verts];

        for (unsigned int i_face = 0; i_face < in_mesh->n_faces; i_face++) {
            struct TriInfo *f = &in_mesh->faces[i_face];

            if (f->material == i_mat) {
                struct TriInfo *f_new = &m->faces[i_face_new];
                *f_new = *f;
                i_face_new++;
                for (int i = 0; i < 3; i++) {
                    int v = f->verts[i];

                    if (!vertices_used[v]) {
                        m->verts[i_vert_new] = in_mesh->verts[v];
                        verts_remap[v] = i_vert_new;
                        i_vert_new++;
                        vertices_used[v] = 1;
                    }

                    f_new->verts[i] = verts_remap[v];
                    assert(f_new->verts[i] < m->n_verts);
                }
            }
        }

        copy_MaterialInfo(&m->materials[0], &in_mesh->materials[i_mat]);
    }

    return out_meshes;
}

void free_mesh_to_f3d_mesh(struct f3d_mesh *mesh) {
    if (mesh != NULL) {
        free(mesh->vertices);
        if (mesh->entries != NULL) {
            for (int i = 0; i < mesh->n_entries; i++) {
                free(mesh->entries[i].tris);
            }
            free(mesh->entries);
        }
        free(mesh);
    }
}

enum shading_type { SHADING_NULL, SHADING_COLORS, SHADING_NORMALS };

struct f3d_mesh *mesh_to_f3d_mesh(struct MeshInfo *mesh, int uv_basis_s,
                                  int uv_basis_t,
                                  enum shading_type shading_type) {
    unsigned int indices[mesh->n_faces * 3];
    unsigned int remap[mesh->n_verts];

    for (unsigned int i_face = 0; i_face < mesh->n_faces; i_face++) {
        for (int j = 0; j < 3; j++) {
            indices[i_face * 3 + j] = mesh->faces[i_face].verts[j];
            assert(indices[i_face * 3 + j] < mesh->n_verts);
        }
    }

    // TODO convert VertexInfo.coords to int16_t somewhere before doing the
    // remap actually just convert VertexInfo to f3d_vertex entirely before
    // doing the remap as VertexInfo contains more data than is relevant (eg
    // both color and normal)

    size_t n_unique_verts = meshopt_generateVertexRemap(
        remap, indices, mesh->n_faces * 3, mesh->verts, mesh->n_verts,
        sizeof(struct VertexInfo));

    struct VertexInfo vertices[n_unique_verts];
    meshopt_remapIndexBuffer(indices, indices, mesh->n_faces * 3, remap);
    meshopt_remapVertexBuffer(vertices, mesh->verts, mesh->n_verts,
                              sizeof(struct VertexInfo), remap);

    meshopt_optimizeVertexCache(indices, indices, mesh->n_faces * 3,
                                n_unique_verts);

    // TODO check malloc results

    size_t f3d_vertices_buf_len = n_unique_verts * 2;
    struct f3d_vertex *f3d_vertices =
        malloc(sizeof(struct f3d_vertex[f3d_vertices_buf_len]));
#define VERTEX_CACHE 32
    size_t f3d_entries_buf_len = 1 + 2 * mesh->n_faces / VERTEX_CACHE;
    struct f3d_mesh_load_entry *f3d_entries =
        malloc(sizeof(struct f3d_mesh_load_entry[f3d_entries_buf_len]));
    size_t i_f3d_vertices = 0;
    size_t i_f3d_entries = 0;
    size_t cur_entry_tris_buf_len = VERTEX_CACHE;
    f3d_entries[0].tris =
        malloc(sizeof(struct f3d_mesh_load_entry_tri[cur_entry_tris_buf_len]));
    f3d_entries[0].buffer_i = 0;
    f3d_entries[0].n = 0;
    f3d_entries[0].v0 = 0;
    f3d_entries[0].n_tris = 0;
    unsigned int vertex_cache[VERTEX_CACHE];
    int i_vertex_cache_next = 0;
    unsigned int i_tri = 0;
    while (i_tri < mesh->n_faces) {
        // count vertices in tri already in cache
        int in_vertex_cache[3] = {0};
        int cache_index[3];
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < i_vertex_cache_next; j++) {
                if (indices[i_tri * 3 + i] == vertex_cache[j]) {
                    in_vertex_cache[i] = 1;
                    cache_index[i] = j;
                    break;
                }
            }
        }
        int n_in_vertex_cache =
            in_vertex_cache[0] + in_vertex_cache[1] + in_vertex_cache[2];
        // if the vertices in the tri not in cache fit in the cache, add them
        if (f3d_entries[i_f3d_entries].v0 + f3d_entries[i_f3d_entries].n + 3 -
                n_in_vertex_cache <=
            VERTEX_CACHE) {
            for (int i = 0; i < 3; i++) {
                if (!in_vertex_cache[i]) {
                    // update cache
                    cache_index[i] = i_vertex_cache_next;
                    vertex_cache[i_vertex_cache_next] = indices[i_tri * 3 + i];
                    f3d_entries[i_f3d_entries].n++;
                    i_vertex_cache_next++;

                    // append vertex to f3d_vertices
                    if (i_f3d_vertices >= f3d_vertices_buf_len) {
                        f3d_vertices_buf_len *= 2;
                        void *tmp = realloc(
                            f3d_vertices,
                            sizeof(struct f3d_vertex[f3d_vertices_buf_len]));
                        if (tmp == NULL) {
                            // TODO
                        }
                        f3d_vertices = tmp;
                    }
                    struct VertexInfo *vi = &vertices[indices[i_tri * 3 + i]];
                    assert(i_f3d_vertices < f3d_vertices_buf_len);
                    struct f3d_vertex *f3d_v = &f3d_vertices[i_f3d_vertices];
                    f3d_v->coords[0] = (int16_t)vi->coords[0];
                    f3d_v->coords[1] = (int16_t)vi->coords[1];
                    f3d_v->coords[2] = (int16_t)vi->coords[2];

                    // TODO uv -> st conversion
                    // (this seems correct for basic UVing and clamping)
                    f3d_v->st[0] =
                        (int16_t)(int)(vi->uv[0] * uv_basis_s * (1 << 5));
                    f3d_v->st[1] = (int16_t)(int)((1.0f - vi->uv[1]) *
                                                  uv_basis_t * (1 << 5));

                    switch (shading_type) {
                    case SHADING_COLORS:
                        for (int j = 0; j < 3; j++)
                            f3d_v->cn[j] = vi->color[j];
                        break;
                    case SHADING_NORMALS:
                        for (int j = 0; j < 3; j++) {
                            f3d_v->cn[j] = (uint8_t)(int)clampf(
                                vi->normal[j] * 0x7F, -0x7F, 0x7F);
                        }
                        break;
                    case SHADING_NULL:
                    default:
                        f3d_v->cn[0] = f3d_v->cn[1] = f3d_v->cn[2] = 0;
                        break;
                    }
                    f3d_v->alpha = vi->color[3];
                    i_f3d_vertices++;
                }
            }

            // append tri to tris
            if (f3d_entries[i_f3d_entries].n_tris >= cur_entry_tris_buf_len) {
                cur_entry_tris_buf_len *= 2;
                void *tmp = realloc(f3d_entries[i_f3d_entries].tris,
                                    sizeof(struct f3d_mesh_load_entry_tri
                                               [cur_entry_tris_buf_len]));
                if (tmp == NULL) {
                    // TODO
                }
                f3d_entries[i_f3d_entries].tris = tmp;
            }
            for (int i = 0; i < 3; i++) {
                f3d_entries[i_f3d_entries]
                    .tris[f3d_entries[i_f3d_entries].n_tris]
                    .indices[i] = cache_index[i];
            }
            f3d_entries[i_f3d_entries].n_tris++;

            i_tri++;
        }
        // otherwise push the entry
        else {
            // advance f3d entry
            if (i_f3d_entries + 1 >= f3d_entries_buf_len) {
                f3d_entries_buf_len *= 2;
                void *tmp = realloc(
                    f3d_entries,
                    sizeof(struct f3d_mesh_load_entry[f3d_entries_buf_len]));
                if (tmp == NULL) {
                    // TODO
                }
                f3d_entries = tmp;
            }
            i_f3d_entries++;
            cur_entry_tris_buf_len = VERTEX_CACHE;
            f3d_entries[i_f3d_entries].tris = malloc(
                sizeof(struct f3d_mesh_load_entry_tri[cur_entry_tris_buf_len]));
            // TODO check malloc
            f3d_entries[i_f3d_entries].buffer_i = i_f3d_vertices;
            f3d_entries[i_f3d_entries].n = 0;
            f3d_entries[i_f3d_entries].v0 = 0;
            f3d_entries[i_f3d_entries].n_tris = 0;

            // reset the cache state
            i_vertex_cache_next = 0;

            // Note: don't increment i_tri,
            // process the same tri next iteration with the new state
        }
    }

    struct f3d_mesh *f3d_mesh = malloc(sizeof(struct f3d_mesh));
    f3d_mesh->vertices = f3d_vertices;
    f3d_mesh->entries = f3d_entries;
    f3d_mesh->n_vertices = i_f3d_vertices;
    f3d_mesh->n_entries = i_f3d_entries + 1;
    return f3d_mesh;
}

int write_f3d_mat(FILE *f, struct MaterialInfo *mat_info, const char *name) {
    fprintf(f, "Gfx %s_mat_dl[] = {\n", name);

    if (mat_info->lighting)
        fprintf(f, "    gsSPSetGeometryMode(G_LIGHTING),\n");
    else
        fprintf(f, "    gsSPClearGeometryMode(G_LIGHTING),\n");

    fprintf(f, "    gsSPEndDisplayList(),\n");
    fprintf(f, "};\n");

    return 0;
}

int write_f3d_mesh(FILE *f, struct f3d_mesh *mesh, const char *name) {
    fprintf(f, "Vtx %s_mesh_vtx[] = {\n", name);
    for (int i = 0; i < mesh->n_vertices; i++) {
        struct f3d_vertex *v = &mesh->vertices[i];

        fprintf(f,
                "    {{ "
                "{ %" PRId16 ", %" PRId16 ", %" PRId16 " }, "
                "0, "
                "{ %" PRId16 ", %" PRId16 " }, "
                "{ 0x%" PRIX8 ", 0x%" PRIX8 ", 0x%" PRIX8 ", %" PRIu8 " }"
                " }},\n",
                v->coords[0], v->coords[1], v->coords[2], v->st[0], v->st[1],
                v->cn[0], v->cn[1], v->cn[2], v->alpha);
    }
    fprintf(f, "};\n");

    fprintf(f, "Gfx %s_mesh_dl[] = {\n", name);
    for (int i = 0; i < mesh->n_entries; i++) {
        struct f3d_mesh_load_entry *e = &mesh->entries[i];

        fprintf(f,
                "    gsSPVertex("
                "&%s_mesh_vtx[%d], %" PRIu8 ", %" PRIu8 "),\n",
                name, e->buffer_i, e->n, e->v0);

        for (int j = 0; j + 1 < e->n_tris; j += 2) {
            struct f3d_mesh_load_entry_tri *tri1 = &e->tris[j];
            struct f3d_mesh_load_entry_tri *tri2 = &e->tris[j + 1];

            fprintf(f,
                    "    gsSP2Triangles("
                    "%" PRIu8 ", %" PRIu8 ", %" PRIu8 ", 0, "
                    "%" PRIu8 ", %" PRIu8 ", %" PRIu8 ", 0),\n",
                    tri1->indices[0], tri1->indices[1], tri1->indices[2],
                    tri2->indices[0], tri2->indices[1], tri2->indices[2]);
        }

        if (e->n_tris % 2 != 0) {
            struct f3d_mesh_load_entry_tri *tri = &e->tris[e->n_tris - 1];

            fprintf(f,
                    "    gsSP1Triangle("
                    "%" PRIu8 ", %" PRIu8 ", %" PRIu8 ", 0),\n",
                    tri->indices[0], tri->indices[1], tri->indices[2]);
        }
    }
    fprintf(f, "    gsSPEndDisplayList(),\n");
    fprintf(f, "};\n");

    return 0;
}

int write_mesh_info_to_f3d_c(struct MeshInfo *mesh_info, const char *path) {
    FILE *f = fopen(path, "w");
    if (f == NULL) {
        perror("fopen");
        return -1;
    }
    fprintf(f, "// Hi from write_mesh_info_to_f3d_c\n");
    struct MeshInfo **meshes = split_mesh_by_material(mesh_info);
    if (meshes == NULL) {
        return -2;
    }
    for (unsigned int i_mesh = 0; i_mesh < mesh_info->n_materials; i_mesh++) {
        struct MaterialInfo *mat_info = &mesh_info->materials[i_mesh];
        struct MeshInfo *mesh = meshes[i_mesh];
        write_f3d_mat(f, mat_info, mesh->name);
        enum shading_type shading_type =
            mat_info->lighting ? SHADING_NORMALS : SHADING_COLORS;
        struct f3d_mesh *f3d_mesh = mesh_to_f3d_mesh(
            mesh, mat_info->uv_basis_s, mat_info->uv_basis_t, shading_type);
        write_f3d_mesh(f, f3d_mesh, mesh->name);
        free_mesh_to_f3d_mesh(f3d_mesh);
    }

    fprintf(f, "Gfx %s_dl[] = {\n", mesh_info->name);
    for (unsigned int i_mesh = 0; i_mesh < mesh_info->n_materials; i_mesh++) {
        struct MeshInfo *mesh = meshes[i_mesh];
        fprintf(f, "    gsSPDisplayList(%s_mat_dl),\n", mesh->name);
        fprintf(f, "    gsSPDisplayList(%s_mesh_dl),\n", mesh->name);
    }
    fprintf(f, "    gsSPEndDisplayList(),\n");
    fprintf(f, "};\n");

    free_split_mesh_by_material(meshes, mesh_info->n_materials);
    fclose(f);
    return 0;
}
