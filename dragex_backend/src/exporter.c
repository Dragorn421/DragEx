#include "exporter.h"

#include <assert.h>
#include <errno.h>
#include <inttypes.h>
#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../meshoptimizer/src/meshoptimizer.h"

#include "logging/logging.h"

#ifndef MIN
#define MIN(a, b) (((a) < (b)) ? (a) : (b))
#endif
#ifndef MAX
#define MAX(a, b) (((a) > (b)) ? (a) : (b))
#endif

float clampf(float f, float min, float max) {
    return f < min ? min : f > max ? max : f;
}

struct rgbau8 rgbaf_to_rgbau8(struct rgbaf *rgbaf) {
    struct rgbau8 rgbau8;
    rgbau8.r = (uint8_t)clampf(rgbaf->r * 255, 0, 255);
    rgbau8.g = (uint8_t)clampf(rgbaf->g * 255, 0, 255);
    rgbau8.b = (uint8_t)clampf(rgbaf->b * 255, 0, 255);
    rgbau8.a = (uint8_t)clampf(rgbaf->a * 255, 0, 255);
    return rgbau8;
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

/**
 * Generate a mapping from input material indices to new material indices such
 * that the new material indices are all used and contiguous.
 * If a material is unused, its index maps to ~0u in the returned mapping.
 * Invalid material indices and indices for which the material is NULL are
 * mapped to the special returned material index `*default_material_index_out`.
 * There are such indices only if `*use_default_material_out` is true.
 */
unsigned int *remap_materials(unsigned int *buf_triangles_material_index,
                              unsigned int n_faces, void **materials_in,
                              size_t n_materials_in,
                              unsigned int *n_materials_out,
                              bool *use_default_material_out,
                              unsigned int *default_material_index_out) {
    unsigned int n_materials = 0;
    bool use_default_material = false;
    unsigned int default_material_index = ~0u;
    unsigned int material_index_map_len = n_materials_in;
    unsigned int *material_index_map =
        malloc(sizeof(unsigned int) * material_index_map_len);
    if (material_index_map_len != 0 && material_index_map == NULL) {
        log_error("malloc material_index_map failed");
        return NULL;
    }
    for (unsigned int i = 0; i < material_index_map_len; i++) {
        material_index_map[i] = ~0u;
    }
    for (unsigned int i_face = 0; i_face < n_faces; i_face++) {
        unsigned int mat_index = buf_triangles_material_index[i_face];

        if (mat_index >= material_index_map_len) {
            unsigned int prev_material_index_map_len = material_index_map_len;
            material_index_map_len = mat_index + 1;
            void *tmp = realloc(material_index_map,
                                sizeof(unsigned int) * material_index_map_len);
            if (tmp == NULL) {
                log_error("realloc material_index_map failed");
                free(material_index_map);
                return NULL;
            }
            material_index_map = tmp;
            for (unsigned int i = prev_material_index_map_len;
                 i < material_index_map_len; i++) {
                material_index_map[i] = ~0u;
            }
        }

        if (mat_index >= n_materials_in || materials_in[mat_index] == NULL) {
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
    *n_materials_out = n_materials;
    *use_default_material_out = use_default_material;
    *default_material_index_out = default_material_index;
    return material_index_map;
}

struct MeshInfo *create_MeshInfo_from_buffers(
    float *buf_vertices_co, size_t buf_vertices_co_len,                //
    unsigned int *buf_triangles_loops, size_t buf_triangles_loops_len, //
    unsigned int *buf_triangles_material_index,
    size_t buf_triangles_material_index_len,                                 //
    unsigned int *buf_loops_vertex_index, size_t buf_loops_vertex_index_len, //
    float *buf_loops_normal, size_t buf_loops_normal_len,                    //
    float *buf_corners_color, size_t buf_corners_color_len,                  //
    float *buf_points_color, size_t buf_points_color_len,                    //
    float *buf_loops_uv, size_t buf_loops_uv_len,                            //
    struct MaterialInfo **material_infos, size_t n_material_infos,           //
    struct MaterialInfo *default_material) {

    if (buf_corners_color != NULL && buf_points_color != NULL) {
        log_error("Can't provide both buf_corners_color and "
                  "buf_points_color");
        return NULL;
    }

    unsigned int n_loops = buf_loops_vertex_index_len;
    if (buf_loops_normal_len != n_loops * 3) {
        log_error("buf_loops_normal_len=%zd and n_loops=%u mismatch",
                  buf_loops_normal_len, n_loops);
        return NULL;
    }
    if (buf_corners_color != NULL && buf_corners_color_len != n_loops * 4) {
        log_error("buf_corners_color_len=%zd and n_loops=%u mismatch",
                  buf_corners_color_len, n_loops);
        return NULL;
    }
    if (buf_points_color != NULL &&
        buf_points_color_len != buf_vertices_co_len * 4 / 3) {
        log_error(
            "buf_points_color_len=%zd and buf_vertices_co_len=%zd mismatch",
            buf_points_color_len, buf_vertices_co_len);
        return NULL;
    }
    if (buf_loops_uv != NULL && buf_loops_uv_len != n_loops * 2) {
        log_error("buf_loops_uv_len=%zd and n_loops=%u mismatch",
                  buf_loops_uv_len, n_loops);
        return NULL;
    }

    unsigned int n_faces = (unsigned int)(buf_triangles_loops_len / 3);
    if (buf_triangles_material_index_len != n_faces) {
        log_error(
            "buf_triangles_material_index_len=%zd and n_faces=%u mismatch",
            buf_triangles_material_index_len, n_faces);
        return NULL;
    }

    unsigned int n_materials;
    bool use_default_material;
    unsigned int default_material_index;
    unsigned int *material_index_map =
        remap_materials(buf_triangles_material_index, n_faces,
                        (void **)material_infos, n_material_infos, &n_materials,
                        &use_default_material, &default_material_index);
    if (material_index_map == NULL) {
        log_error("remap_materials failed");
        return NULL;
    }

    struct MeshInfo *mesh = malloc(sizeof(struct MeshInfo));
    if (mesh == NULL) {
        log_error("malloc mesh failed");
        return NULL;
    }
    mesh->name = strdup("mesh");

    mesh->n_verts = n_loops;
    mesh->verts = malloc(sizeof(struct VertexInfo) * n_loops);

    mesh->n_faces = n_faces;
    mesh->faces = malloc(sizeof(struct TriInfo) * n_faces);

    mesh->n_materials = n_materials;
    mesh->materials = malloc(sizeof(struct MaterialInfo) * n_materials);

    if (mesh->materials != NULL) {
        // for free_create_MeshInfo_from_buffers
        for (unsigned int i = 0; i < n_materials; i++) {
            mesh->materials[i].name = NULL;
        }
    }

    if (mesh->name == NULL || mesh->verts == NULL || mesh->faces == NULL ||
        mesh->materials == NULL) {
        log_error("malloc name, verts, faces or materials failed");
        free_create_MeshInfo_from_buffers(mesh);
        return NULL;
    }

    for (unsigned int i_loop = 0; i_loop < n_loops; i_loop++) {
        for (int j = 0; j < 3; j++) {
            unsigned int v = buf_loops_vertex_index[i_loop] * 3 + j;
            if (v >= buf_vertices_co_len) {
                log_error(
                    "i_loop=%u: v=%u out of bounds (buf_vertices_co_len=%zd)",
                    i_loop, v, buf_vertices_co_len);
                free_create_MeshInfo_from_buffers(mesh);
                return NULL;
            }
            mesh->verts[i_loop].coords[j] = buf_vertices_co[v];
        }

        for (int j = 0; j < 2; j++)
            mesh->verts[i_loop].uv[j] =
                buf_loops_uv == NULL ? 0.0f : buf_loops_uv[i_loop * 2 + j];

        for (int j = 0; j < 3; j++)
            mesh->verts[i_loop].normal[j] = buf_loops_normal[i_loop * 3 + j];

        for (int j = 0; j < 4; j++) {
            if (buf_corners_color != NULL) {
                mesh->verts[i_loop].color[j] = (uint8_t)clampf(
                    buf_corners_color[i_loop * 4 + j] * 255, 0, 255);
            } else if (buf_points_color != NULL) {
                unsigned int v = buf_loops_vertex_index[i_loop] * 4 + j;
                if (v >= buf_points_color_len) {
                    log_error("i_loop=%u: v=%u out of bounds "
                              "(buf_points_color_len=%zd)",
                              i_loop, v, buf_points_color_len);
                    free_create_MeshInfo_from_buffers(mesh);
                    return NULL;
                }
                mesh->verts[i_loop].color[j] =
                    (uint8_t)clampf(buf_points_color[v] * 255, 0, 255);
            } else {
                mesh->verts[i_loop].color[j] = 255;
            }
        }
    }

    for (unsigned int i = 0; i < n_faces; i++) {
        for (int j = 0; j < 3; j++) {
            unsigned int loop = buf_triangles_loops[i * 3 + j];
            if (loop >= n_loops) {
                log_error("face %u: loop=%u out of bounds (n_loops=%u)", i,
                          loop, n_loops);
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

    free(material_index_map);

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

    out_meshes = malloc(sizeof(struct MeshInfo *) * in_mesh->n_materials);
    if (out_meshes == NULL) {
        log_error("malloc out_meshes failed");
        return NULL;
    }

    for (unsigned int i_mat = 0; i_mat < in_mesh->n_materials; i_mat++) {
        struct MeshInfo *m = malloc(sizeof(struct MeshInfo));
        if (m == NULL) {
            log_error("malloc m failed");
            free_split_mesh_by_material(out_meshes, in_mesh->n_materials);
            return NULL;
        }
        out_meshes[i_mat] = m;

        int n_faces_used = 0;
        uint8_t *vertices_used = calloc(in_mesh->n_verts, sizeof(uint8_t));

        if (vertices_used == NULL) {
            log_error("calloc vertices_used failed");
            m->name = NULL;
            m->verts = NULL;
            m->faces = NULL;
            m->materials = NULL;
            free_split_mesh_by_material(out_meshes, in_mesh->n_materials);
            return NULL;
        }

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
        m->verts = malloc(sizeof(struct VertexInfo) * n_vertices_used);
        m->faces = malloc(sizeof(struct TriInfo) * n_faces_used);
        m->materials = malloc(sizeof(struct MaterialInfo[1]));
        if (m->name == NULL || m->verts == NULL || m->faces == NULL ||
            m->materials == NULL) {
            log_error("malloc name, verts, faces or materials failed");
            free(vertices_used);
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

        unsigned int *verts_remap =
            malloc(sizeof(unsigned int) * in_mesh->n_verts);
        if (verts_remap == NULL) {
            log_error("malloc verts_remap failed");
            free(vertices_used);
            free_split_mesh_by_material(out_meshes, in_mesh->n_materials);
            return NULL;
        }

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

        free(verts_remap);
        free(vertices_used);

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
    unsigned int *indices = malloc(sizeof(unsigned int) * mesh->n_faces * 3);
    unsigned int *remap = malloc(sizeof(unsigned int) * mesh->n_verts);

    if (indices == NULL || remap == NULL) {
        log_error("malloc indices or remap failed");
        free(indices);
        free(remap);
        return NULL;
    }

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

    struct VertexInfo *vertices =
        malloc(sizeof(struct VertexInfo) * n_unique_verts);
    if (vertices == NULL) {
        log_error("malloc vertices failed");
        free(indices);
        free(remap);
        return NULL;
    }
    meshopt_remapIndexBuffer(indices, indices, mesh->n_faces * 3, remap);
    meshopt_remapVertexBuffer(vertices, mesh->verts, mesh->n_verts,
                              sizeof(struct VertexInfo), remap);

    free(remap);

    meshopt_optimizeVertexCache(indices, indices, mesh->n_faces * 3,
                                n_unique_verts);

    // TODO check malloc results

    size_t f3d_vertices_buf_len = n_unique_verts * 2;
    struct f3d_vertex *f3d_vertices =
        malloc(sizeof(struct f3d_vertex) * f3d_vertices_buf_len);
#define VERTEX_CACHE 32
    size_t f3d_entries_buf_len = 1 + 2 * mesh->n_faces / VERTEX_CACHE;
    struct f3d_mesh_load_entry *f3d_entries =
        malloc(sizeof(struct f3d_mesh_load_entry) * f3d_entries_buf_len);
    size_t i_f3d_vertices = 0;
    size_t i_f3d_entries = 0;
    size_t cur_entry_tris_buf_len = VERTEX_CACHE;
    f3d_entries[0].tris =
        malloc(sizeof(struct f3d_mesh_load_entry_tri) * cur_entry_tris_buf_len);
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
                        void *tmp =
                            realloc(f3d_vertices, sizeof(struct f3d_vertex) *
                                                      f3d_vertices_buf_len);
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
                                    sizeof(struct f3d_mesh_load_entry_tri) *
                                        cur_entry_tris_buf_len);
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
                void *tmp =
                    realloc(f3d_entries, sizeof(struct f3d_mesh_load_entry) *
                                             f3d_entries_buf_len);
                if (tmp == NULL) {
                    // TODO
                }
                f3d_entries = tmp;
            }
            i_f3d_entries++;
            cur_entry_tris_buf_len = VERTEX_CACHE;
            f3d_entries[i_f3d_entries].tris =
                malloc(sizeof(struct f3d_mesh_load_entry_tri) *
                       cur_entry_tris_buf_len);
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

    free(vertices);
    free(indices);

    struct f3d_mesh *f3d_mesh = malloc(sizeof(struct f3d_mesh));
    f3d_mesh->vertices = f3d_vertices;
    f3d_mesh->entries = f3d_entries;
    f3d_mesh->n_vertices = i_f3d_vertices;
    f3d_mesh->n_entries = i_f3d_entries + 1;
    return f3d_mesh;
}

int write_f3d_mat(FILE *f, struct MaterialInfo *mat_info, const char *name) {
    struct MaterialInfoOtherModes *om = &mat_info->other_modes;

    fprintf(f, "Gfx %s_mat_dl[] = {\n", name);

    fprintf(f, "    gsDPPipelineMode(%s),\n",
            om->atomic_prim ? "G_PM_1PRIMITIVE" : "G_PM_NPRIMITIVE");

    static const char *cycle_type_names[] = {
        [RDP_OM_CYCLE_TYPE_1CYCLE] = "G_CYC_1CYCLE",
        [RDP_OM_CYCLE_TYPE_2CYCLE] = "G_CYC_2CYCLE",
        [RDP_OM_CYCLE_TYPE_COPY] = "G_CYC_COPY",
        [RDP_OM_CYCLE_TYPE_FILL] = "G_CYC_FILL",
    };
    fprintf(f, "    gsDPSetCycleType(%s),\n", cycle_type_names[om->cycle_type]);

    fprintf(f, "    gsDPSetTexturePersp(%s),\n",
            om->persp_tex_en ? "G_TP_PERSP" : "G_TP_NONE");

    // Note: having both detail and sharpen at once is invalid
    // N64brew discord:
    // https://discord.com/channels/205520502922543113/205520502922543113/1392399686819774575
    fprintf(f, "    gsDPSetTextureDetail(%s),\n",
            om->detail_tex_en    ? "G_TD_DETAIL"
            : om->sharpen_tex_en ? "G_TD_SHARPEN"
                                 : "G_TD_CLAMP");

    fprintf(f, "    gsDPSetTextureLOD(%s),\n",
            om->tex_lod_en ? "G_TL_LOD" : "G_TL_TILE");

    fprintf(f, "    gsDPSetTextureLUT(%s),\n",
            om->tlut_en ? (om->tlut_type ? "G_TT_IA16" : "G_TT_RGBA16")
                        : "G_TT_NONE");

    fprintf(f, "    gsDPSetTextureFilter(%s),\n",
            om->sample_type ? (om->mid_texel ? "G_TF_AVERAGE" : "G_TF_BILERP")
                            : "G_TF_POINT");

    const char *textConv;
    // Note: this is approximate
    if (om->bi_lerp_0 && om->bi_lerp_1)
        textConv = "G_TC_FILT";
    else if (om->bi_lerp_0 && om->convert_one)
        textConv = "G_TC_FILTCONV";
    else
        textConv = "G_TC_CONV";
    fprintf(f, "    gsDPSetTextureConvert(%s),\n", textConv);

    fprintf(f, "    gsDPSetCombineKey(%s),\n",
            om->key_en ? "G_CK_KEY" : "G_CK_NONE");

    static const char *rgb_dither_sel_names[] = {
        [RDP_OM_RGB_DITHER_MAGIC_SQUARE] = "G_CD_MAGICSQ",
        [RDP_OM_RGB_DITHER_BAYER] = "G_CD_BAYER",
        [RDP_OM_RGB_DITHER_RANDOM_NOISE] = "G_CD_NOISE",
        [RDP_OM_RGB_DITHER_NONE] = "G_CD_DISABLE",
    };
    fprintf(f, "    gsDPSetColorDither(%s),\n",
            rgb_dither_sel_names[om->rgb_dither_sel]);

    static const char *alpha_dither_sel_names[] = {
        [RDP_OM_ALPHA_DITHER_SAME_AS_RGB] = "G_AD_PATTERN",
        [RDP_OM_ALPHA_DITHER_INVERSE_OF_RGB] = "G_AD_NOTPATTERN",
        [RDP_OM_ALPHA_DITHER_RANDOM_NOISE] = "G_AD_NOISE",
        [RDP_OM_ALPHA_DITHER_NONE] = "G_AD_DISABLE",
    };
    fprintf(f, "    gsDPSetAlphaDither(%s),\n",
            alpha_dither_sel_names[om->alpha_dither_sel]);

    const char *blender_P_M_inputs_names[] = {
        [RDP_OM_BLENDER_P_M_INPUTS_INPUT] = "G_BL_CLR_IN",
        [RDP_OM_BLENDER_P_M_INPUTS_MEMORY] = "G_BL_CLR_MEM",
        [RDP_OM_BLENDER_P_M_INPUTS_BLEND_COLOR] = "G_BL_CLR_BL",
        [RDP_OM_BLENDER_P_M_INPUTS_FOG_COLOR] = "G_BL_CLR_FOG",
    };
    const char *blender_A_inputs_names[] = {
        [RDP_OM_BLENDER_A_INPUTS_INPUT_ALPHA] = "G_BL_A_IN",
        [RDP_OM_BLENDER_A_INPUTS_FOG_ALPHA] = "G_BL_A_FOG",
        [RDP_OM_BLENDER_A_INPUTS_SHADE_ALPHA] = "G_BL_A_SHADE",
        [RDP_OM_BLENDER_A_INPUTS_0] = "G_BL_0",
    };
    const char *blender_B_inputs_names[] = {
        [RDP_OM_BLENDER_B_INPUTS_1_MINUS_A] = "G_BL_1MA",
        [RDP_OM_BLENDER_B_INPUTS_MEMORY_COVERAGE] = "G_BL_A_MEM",
        [RDP_OM_BLENDER_B_INPUTS_1] = "G_BL_1",
        [RDP_OM_BLENDER_B_INPUTS_0] = "G_BL_0",
    };

    const char *z_mode_names[] = {
        [RDP_OM_Z_MODE_OPAQUE] = "ZMODE_OPA",
        [RDP_OM_Z_MODE_INTERPENETRATING] = "ZMODE_INTER",
        [RDP_OM_Z_MODE_TRANSPARENT] = "ZMODE_XLU",
        [RDP_OM_Z_MODE_DECAL] = "ZMODE_DEC",
    };

    const char *cvg_dest_names[] = {
        [RDP_OM_CVG_DEST_CLAMP] = "CVG_DST_CLAMP",
        [RDP_OM_CVG_DEST_WRAP] = "CVG_DST_WRAP",
        [RDP_OM_CVG_DEST_FULL] = "CVG_DST_FULL",
        [RDP_OM_CVG_DEST_SAVE] = "CVG_DST_SAVE",
    };

    fprintf(
        f,
        "    gsDPSetRenderMode("
        "%s%s%s%s%s"
        "%s | %s | "
        "%s%s%s"
        "GBL_c1(%s, %s, %s, %s), GBL_c2(%s, %s, %s, %s)"
        "),\n",

        om->antialias_en ? "AA_EN | " : "", om->z_compare_en ? "Z_CMP | " : "",
        om->z_update_en ? "Z_UPD | " : "", om->image_read_en ? "IM_RD | " : "",
        om->color_on_cvg ? "CLR_ON_CVG | " : "",

        cvg_dest_names[om->cvg_dest], z_mode_names[om->z_mode],

        om->cvg_x_alpha ? "CVG_X_ALPHA | " : "",
        om->alpha_cvg_select ? "ALPHA_CVG_SEL | " : "",
        om->force_blend ? "FORCE_BL | " : "",

        blender_P_M_inputs_names[om->bl_m1a_0],
        blender_A_inputs_names[om->bl_m1b_0],
        blender_P_M_inputs_names[om->bl_m2a_0],
        blender_B_inputs_names[om->bl_m2b_0],

        blender_P_M_inputs_names[om->bl_m1a_1],
        blender_A_inputs_names[om->bl_m1b_1],
        blender_P_M_inputs_names[om->bl_m2a_1],
        blender_B_inputs_names[om->bl_m2b_1]);

    fprintf(f, "    gsDPSetDepthSource(%s),\n",
            om->z_source_sel ? "G_ZS_PRIM" : "G_ZS_PIXEL");
    fprintf(f, "    gsDPSetAlphaCompare(%s),\n",
            om->alpha_compare_en
                ? om->dither_alpha_en ? "G_AC_DITHER" : "G_AC_THRESHOLD"
                : "G_AC_NONE");

    static const char *tile_format_names[] = {
        [RDP_TILE_FORMAT_RGBA] = "G_IM_FMT_RGBA",
        [RDP_TILE_FORMAT_YUV] = "G_IM_FMT_YUV",
        [RDP_TILE_FORMAT_CI] = "G_IM_FMT_CI",
        [RDP_TILE_FORMAT_IA] = "G_IM_FMT_IA",
        [RDP_TILE_FORMAT_I] = "G_IM_FMT_I",
    };
    static const char *tile_size_names[] = {
        [RDP_TILE_SIZE_4] = "G_IM_SIZ_4b",
        [RDP_TILE_SIZE_8] = "G_IM_SIZ_8b",
        [RDP_TILE_SIZE_16] = "G_IM_SIZ_16b",
        [RDP_TILE_SIZE_32] = "G_IM_SIZ_32b",
    };

    for (int i_tile = 0; i_tile < 8; i_tile++) {
        struct MaterialInfoTile *tile = &mat_info->tiles[i_tile];

        struct MaterialInfoImage *image = tile->image;
        if (image != NULL) {
            // TODO use gsDPLoadMultiTile for textures with line%8!=0 ?
            // TODO use gsDPLoadMultiBlock_4b for RDP_TILE_SIZE_4 images
            fprintf(f,
                    "    gsDPLoadMultiBlock("
                    "%s, 0x%03X, %d, "
                    "%s, %s, %d, %d, %d, "
                    "%s | %s, %s | %s, "
                    "%d, %d, %d, %d),\n",
                    image->c_identifier, tile->address, i_tile,

                    tile_format_names[tile->format],
                    tile_size_names[tile->size], image->width, image->height,
                    tile->palette,

                    tile->mirror_S ? "G_TX_MIRROR" : "G_TX_NOMIRROR",
                    tile->clamp_S ? "G_TX_CLAMP" : "G_TX_WRAP",
                    tile->mirror_T ? "G_TX_MIRROR" : "G_TX_NOMIRROR",
                    tile->clamp_T ? "G_TX_CLAMP" : "G_TX_WRAP",

                    tile->mask_S, tile->mask_T, tile->shift_S, tile->shift_T);
        }
    }

    for (int i_tile = 0; i_tile < 8; i_tile++) {
        struct MaterialInfoTile *tile = &mat_info->tiles[i_tile];

        fprintf(f,
                "    gsDPSetTile("
                "%s, %s, 0x%X, 0x%03X, %d, %d, "
                "%s | %s, %d, %d, "
                "%s | %s, %d, %d),\n",
                tile_format_names[tile->format], tile_size_names[tile->size],
                tile->line, tile->address, i_tile, tile->palette,

                tile->mirror_T ? "G_TX_MIRROR" : "G_TX_NOMIRROR",
                tile->clamp_T ? "G_TX_CLAMP" : "G_TX_WRAP", tile->mask_T,
                tile->shift_T,

                tile->mirror_S ? "G_TX_MIRROR" : "G_TX_NOMIRROR",
                tile->clamp_S ? "G_TX_CLAMP" : "G_TX_WRAP", tile->mask_S,
                tile->shift_S);
        fprintf(f,
                "    gsDPSetTileSize("
                "%d, "
                "(int)(%.2f * 4), (int)(%.2f * 4), "
                "(int)(%.2f * 4), (int)(%.2f * 4)),\n",
                i_tile, tile->upper_left_S, tile->upper_left_T,
                tile->lower_right_S, tile->lower_right_T);
    }

    static const char *combiner_rgb_A_names[] = {
        [RDP_COMBINER_RGB_A_INPUTS_COMBINED] = "COMBINED",
        [RDP_COMBINER_RGB_A_INPUTS_TEX0] = "TEXEL0",
        [RDP_COMBINER_RGB_A_INPUTS_TEX1] = "TEXEL1",
        [RDP_COMBINER_RGB_A_INPUTS_PRIMITIVE] = "PRIMITIVE",
        [RDP_COMBINER_RGB_A_INPUTS_SHADE] = "SHADE",
        [RDP_COMBINER_RGB_A_INPUTS_ENVIRONMENT] = "ENVIRONMENT",
        [RDP_COMBINER_RGB_A_INPUTS_1] = "1",
        [RDP_COMBINER_RGB_A_INPUTS_NOISE] = "NOISE",
        [RDP_COMBINER_RGB_A_INPUTS_0] = "0",
    };
    static const char *combiner_rgb_B_names[] = {
        [RDP_COMBINER_RGB_B_INPUTS_COMBINED] = "COMBINED",
        [RDP_COMBINER_RGB_B_INPUTS_TEX0] = "TEXEL0",
        [RDP_COMBINER_RGB_B_INPUTS_TEX1] = "TEXEL1",
        [RDP_COMBINER_RGB_B_INPUTS_PRIMITIVE] = "PRIMITIVE",
        [RDP_COMBINER_RGB_B_INPUTS_SHADE] = "SHADE",
        [RDP_COMBINER_RGB_B_INPUTS_ENVIRONMENT] = "ENVIRONMENT",
        [RDP_COMBINER_RGB_B_INPUTS_CENTER] = "CENTER",
        [RDP_COMBINER_RGB_B_INPUTS_K4] = "K4",
        [RDP_COMBINER_RGB_B_INPUTS_0] = "0",
    };
    static const char *combiner_rgb_C_names[] = {
        [RDP_COMBINER_RGB_C_INPUTS_COMBINED] = "COMBINED",
        [RDP_COMBINER_RGB_C_INPUTS_TEX0] = "TEXEL0",
        [RDP_COMBINER_RGB_C_INPUTS_TEX1] = "TEXEL1",
        [RDP_COMBINER_RGB_C_INPUTS_PRIMITIVE] = "PRIMITIVE",
        [RDP_COMBINER_RGB_C_INPUTS_SHADE] = "SHADE",
        [RDP_COMBINER_RGB_C_INPUTS_ENVIRONMENT] = "ENVIRONMENT",
        [RDP_COMBINER_RGB_C_INPUTS_SCALE] = "SCALE",
        [RDP_COMBINER_RGB_C_INPUTS_COMBINED_ALPHA] = "COMBINED_ALPHA",
        [RDP_COMBINER_RGB_C_INPUTS_TEX0_ALPHA] = "TEXEL0_ALPHA",
        [RDP_COMBINER_RGB_C_INPUTS_TEX1_ALPHA] = "TEXEL1_ALPHA",
        [RDP_COMBINER_RGB_C_INPUTS_PRIMITIVE_ALPHA] = "PRIMITIVE_ALPHA",
        [RDP_COMBINER_RGB_C_INPUTS_SHADE_ALPHA] = "SHADE_ALPHA",
        [RDP_COMBINER_RGB_C_INPUTS_ENVIRONMENT_ALPHA] = "ENVIRONMENT_ALPHA",
        [RDP_COMBINER_RGB_C_INPUTS_LOD_FRACTION] = "LOD_FRACTION",
        [RDP_COMBINER_RGB_C_INPUTS_PRIM_LOD_FRAC] = "PRIM_LOD_FRAC",
        [RDP_COMBINER_RGB_C_INPUTS_K5] = "K5",
        [RDP_COMBINER_RGB_C_INPUTS_0] = "0",
    };
    static const char *combiner_rgb_D_names[] = {
        [RDP_COMBINER_RGB_D_INPUTS_COMBINED] = "COMBINED",
        [RDP_COMBINER_RGB_D_INPUTS_TEX0] = "TEXEL0",
        [RDP_COMBINER_RGB_D_INPUTS_TEX1] = "TEXEL1",
        [RDP_COMBINER_RGB_D_INPUTS_PRIMITIVE] = "PRIMITIVE",
        [RDP_COMBINER_RGB_D_INPUTS_SHADE] = "SHADE",
        [RDP_COMBINER_RGB_D_INPUTS_ENVIRONMENT] = "ENVIRONMENT",
        [RDP_COMBINER_RGB_D_INPUTS_1] = "1",
        [RDP_COMBINER_RGB_D_INPUTS_0] = "0",
    };

    static const char *combiner_alpha_A_names[] = {
        [RDP_COMBINER_ALPHA_A_INPUTS_COMBINED] = "COMBINED",
        [RDP_COMBINER_ALPHA_A_INPUTS_TEX0] = "TEXEL0",
        [RDP_COMBINER_ALPHA_A_INPUTS_TEX1] = "TEXEL1",
        [RDP_COMBINER_ALPHA_A_INPUTS_PRIMITIVE] = "PRIMITIVE",
        [RDP_COMBINER_ALPHA_A_INPUTS_SHADE] = "SHADE",
        [RDP_COMBINER_ALPHA_A_INPUTS_ENVIRONMENT] = "ENVIRONMENT",
        [RDP_COMBINER_ALPHA_A_INPUTS_1] = "1",
        [RDP_COMBINER_ALPHA_A_INPUTS_0] = "0",
    };
    static const char *combiner_alpha_B_names[] = {
        [RDP_COMBINER_ALPHA_B_INPUTS_COMBINED] = "COMBINED",
        [RDP_COMBINER_ALPHA_B_INPUTS_TEX0] = "TEXEL0",
        [RDP_COMBINER_ALPHA_B_INPUTS_TEX1] = "TEXEL1",
        [RDP_COMBINER_ALPHA_B_INPUTS_PRIMITIVE] = "PRIMITIVE",
        [RDP_COMBINER_ALPHA_B_INPUTS_SHADE] = "SHADE",
        [RDP_COMBINER_ALPHA_B_INPUTS_ENVIRONMENT] = "ENVIRONMENT",
        [RDP_COMBINER_ALPHA_B_INPUTS_1] = "1",
        [RDP_COMBINER_ALPHA_B_INPUTS_0] = "0",
    };
    static const char *combiner_alpha_C_names[] = {
        [RDP_COMBINER_ALPHA_C_INPUTS_LOD_FRACTION] = "LOD_FRACTION",
        [RDP_COMBINER_ALPHA_C_INPUTS_TEX0] = "TEXEL0",
        [RDP_COMBINER_ALPHA_C_INPUTS_TEX1] = "TEXEL1",
        [RDP_COMBINER_ALPHA_C_INPUTS_PRIMITIVE] = "PRIMITIVE",
        [RDP_COMBINER_ALPHA_C_INPUTS_SHADE] = "SHADE",
        [RDP_COMBINER_ALPHA_C_INPUTS_ENVIRONMENT] = "ENVIRONMENT",
        [RDP_COMBINER_ALPHA_C_INPUTS_PRIM_LOD_FRAC] = "PRIM_LOD_FRAC",
        [RDP_COMBINER_ALPHA_C_INPUTS_0] = "0",
    };
    static const char *combiner_alpha_D_names[] = {
        [RDP_COMBINER_ALPHA_D_INPUTS_COMBINED] = "COMBINED",
        [RDP_COMBINER_ALPHA_D_INPUTS_TEX0] = "TEXEL0",
        [RDP_COMBINER_ALPHA_D_INPUTS_TEX1] = "TEXEL1",
        [RDP_COMBINER_ALPHA_D_INPUTS_PRIMITIVE] = "PRIMITIVE",
        [RDP_COMBINER_ALPHA_D_INPUTS_SHADE] = "SHADE",
        [RDP_COMBINER_ALPHA_D_INPUTS_ENVIRONMENT] = "ENVIRONMENT",
        [RDP_COMBINER_ALPHA_D_INPUTS_1] = "1",
        [RDP_COMBINER_ALPHA_D_INPUTS_0] = "0",
    };

    struct MaterialInfoCombiner *comb = &mat_info->combiner;

    fprintf(f,
            "    gsDPSetCombineLERP("
            "%s, %s, %s, %s, "
            "%s, %s, %s, %s, "
            "%s, %s, %s, %s, "
            "%s, %s, %s, %s"
            "),\n",
            combiner_rgb_A_names[comb->rgb_A_0],
            combiner_rgb_B_names[comb->rgb_B_0],
            combiner_rgb_C_names[comb->rgb_C_0],
            combiner_rgb_D_names[comb->rgb_D_0],
            combiner_alpha_A_names[comb->alpha_A_0],
            combiner_alpha_B_names[comb->alpha_B_0],
            combiner_alpha_C_names[comb->alpha_C_0],
            combiner_alpha_D_names[comb->alpha_D_0],
            combiner_rgb_A_names[comb->rgb_A_1],
            combiner_rgb_B_names[comb->rgb_B_1],
            combiner_rgb_C_names[comb->rgb_C_1],
            combiner_rgb_D_names[comb->rgb_D_1],
            combiner_alpha_A_names[comb->alpha_A_1],
            combiner_alpha_B_names[comb->alpha_B_1],
            combiner_alpha_C_names[comb->alpha_C_1],
            combiner_alpha_D_names[comb->alpha_D_1]);

    struct MaterialInfoVals *vals = &mat_info->vals;

    fprintf(f, "    gsDPSetPrimDepth(%d, %d),\n", vals->primitive_depth_z,
            vals->primitive_depth_dz);

    struct rgbau8 fog_color = rgbaf_to_rgbau8(&vals->fog_color);
    fprintf(f,
            "    gsDPSetFogColor(%" PRId8 ", %" PRId8 ", %" PRId8 ", %" PRId8
            "),\n",
            fog_color.r, fog_color.g, fog_color.b, fog_color.a);

    struct rgbau8 blend_color = rgbaf_to_rgbau8(&vals->blend_color);
    fprintf(f,
            "    gsDPSetBlendColor(%" PRId8 ", %" PRId8 ", %" PRId8 ", %" PRId8
            "),\n",
            blend_color.r, blend_color.g, blend_color.b, blend_color.a);

    struct rgbau8 primitive_color = rgbaf_to_rgbau8(&vals->primitive_color);
    fprintf(f,
            "    gsDPSetPrimColor(%d, %d, %" PRId8 ", %" PRId8 ", %" PRId8
            ", %" PRId8 "),\n",
            vals->min_level, vals->prim_lod_frac, primitive_color.r,
            primitive_color.g, primitive_color.b, primitive_color.a);

    struct rgbau8 environment_color = rgbaf_to_rgbau8(&vals->environment_color);
    fprintf(f,
            "    gsDPSetEnvColor(%" PRId8 ", %" PRId8 ", %" PRId8 ", %" PRId8
            "),\n",
            environment_color.r, environment_color.g, environment_color.b,
            environment_color.a);

    if (mat_info->geometry_mode.lighting)
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

int write_mesh_info_to_f3d_c(struct MeshInfo *mesh_info, FILE *f,
                             char **dl_name) {
    fprintf(f, "// Hi from write_mesh_info_to_f3d_c\n");
    struct MeshInfo **meshes = split_mesh_by_material(mesh_info);
    if (meshes == NULL) {
        log_error("malloc meshes failed");
        return -2;
    }
    for (unsigned int i_mesh = 0; i_mesh < mesh_info->n_materials; i_mesh++) {
        struct MaterialInfo *mat_info = &mesh_info->materials[i_mesh];
        struct MeshInfo *mesh = meshes[i_mesh];
        write_f3d_mat(f, mat_info, mesh->name);
        enum shading_type shading_type =
            mat_info->geometry_mode.lighting ? SHADING_NORMALS : SHADING_COLORS;
        struct f3d_mesh *f3d_mesh = mesh_to_f3d_mesh(
            mesh, mat_info->uv_basis_s, mat_info->uv_basis_t, shading_type);
        write_f3d_mesh(f, f3d_mesh, mesh->name);
        free_mesh_to_f3d_mesh(f3d_mesh);
    }

    if (dl_name != NULL) {
        size_t dl_name_len = strlen(mesh_info->name) + strlen("_dl") + 1;
        *dl_name = malloc(dl_name_len);
        if (*dl_name == NULL) {
            log_error("malloc dl_name failed");
            return -3;
        }
        snprintf(*dl_name, dl_name_len, "%s_dl", mesh_info->name);
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

    return 0;
}

void copy_OoTCollisionMaterial(struct OoTCollisionMaterial *dst,
                               struct OoTCollisionMaterial *src) {
    dst->surface_type_0 = strdup(src->surface_type_0);
    dst->surface_type_1 = strdup(src->surface_type_1);
    dst->flags_a = strdup(src->flags_a);
    dst->flags_b = strdup(src->flags_b);
}

// TODO this is also a free for the result of join_OoTCollisionMeshes_impl
void free_create_OoTCollisionMesh_from_buffers(struct OoTCollisionMesh *mesh) {
    free(mesh->verts);
    free(mesh->faces);
    for (unsigned int i = 0; i < mesh->n_materials; i++) {
        free(mesh->materials[i].surface_type_0);
        free(mesh->materials[i].surface_type_1);
        free(mesh->materials[i].flags_a);
        free(mesh->materials[i].flags_b);
    }
    free(mesh->materials);
}

struct OoTCollisionMesh *create_OoTCollisionMesh_from_buffers(
    float *buf_vertices_co, size_t buf_vertices_co_len,                //
    unsigned int *buf_triangles_loops, size_t buf_triangles_loops_len, //
    unsigned int *buf_triangles_material_index,
    size_t buf_triangles_material_index_len,                                 //
    unsigned int *buf_loops_vertex_index, size_t buf_loops_vertex_index_len, //
    struct OoTCollisionMaterial **materials, size_t n_materials,             //
    struct OoTCollisionMaterial *default_material) {

    unsigned int n_loops = buf_loops_vertex_index_len;

    unsigned int n_faces = (unsigned int)(buf_triangles_loops_len / 3);
    if (buf_triangles_material_index_len != n_faces) {
        log_error(
            "buf_triangles_material_index_len=%zd and n_faces=%u mismatch",
            buf_triangles_material_index_len, n_faces);
        return NULL;
    }

    unsigned int n_materials_used;
    bool use_default_material;
    unsigned int default_material_index;
    unsigned int *material_index_map = remap_materials(
        buf_triangles_material_index, n_faces, (void **)materials, n_materials,
        &n_materials_used, &use_default_material, &default_material_index);
    if (material_index_map == NULL) {
        log_error("remap_materials failed");
        return NULL;
    }

    struct OoTCollisionMesh *mesh = malloc(sizeof(struct OoTCollisionMesh));
    if (mesh == NULL) {
        log_error("malloc mesh failed");
        return NULL;
    }

    mesh->n_verts = n_loops;
    mesh->verts = malloc(sizeof(struct OoTCollisionVertex) * n_loops);

    mesh->n_faces = n_faces;
    mesh->faces = malloc(sizeof(struct OoTCollisionTri) * n_faces);

    mesh->n_materials = n_materials_used;
    mesh->materials =
        malloc(sizeof(struct OoTCollisionMaterial) * n_materials_used);

    if (mesh->materials != NULL) {
        // for free_create_OoTCollisionMesh_from_buffers
        for (unsigned int i = 0; i < n_materials_used; i++) {
            mesh->materials[i].surface_type_0 = NULL;
            mesh->materials[i].surface_type_1 = NULL;
            mesh->materials[i].flags_a = NULL;
            mesh->materials[i].flags_b = NULL;
        }
    }

    if (mesh->verts == NULL || mesh->faces == NULL || mesh->materials == NULL) {
        log_error("malloc verts, faces or materials failed");
        free_create_OoTCollisionMesh_from_buffers(mesh);
        return NULL;
    }

    for (unsigned int i_loop = 0; i_loop < n_loops; i_loop++) {
        for (int j = 0; j < 3; j++) {
            unsigned int v = buf_loops_vertex_index[i_loop] * 3 + j;
            if (v >= buf_vertices_co_len) {
                log_error(
                    "i_loop=%u: v=%u out of bounds (buf_vertices_co_len=%zd)",
                    i_loop, v, buf_vertices_co_len);
                free_create_OoTCollisionMesh_from_buffers(mesh);
                return NULL;
            }
            mesh->verts[i_loop].coords[j] = buf_vertices_co[v];
        }
    }

    for (unsigned int i = 0; i < n_faces; i++) {
        for (int j = 0; j < 3; j++) {
            unsigned int loop = buf_triangles_loops[i * 3 + j];
            if (loop >= n_loops) {
                log_error("face %u: loop=%u out of bounds (n_loops=%u)", i,
                          loop, n_loops);
                free_create_OoTCollisionMesh_from_buffers(mesh);
                return NULL;
            }
            mesh->faces[i].verts[j] = loop;
        }
        mesh->faces[i].material =
            material_index_map[buf_triangles_material_index[i]];
    }

    for (unsigned int i = 0; i < n_materials; i++) {
        if (material_index_map[i] == ~0u ||
            (use_default_material &&
             material_index_map[i] == default_material_index))
            continue;
        struct OoTCollisionMaterial *mat = materials[i];

        // because material_index_map[i] != default_material_index
        assert(mat != NULL);

        copy_OoTCollisionMaterial(&mesh->materials[material_index_map[i]], mat);
    }

    free(material_index_map);

    if (use_default_material) {
        assert(default_material_index != ~0u);
        copy_OoTCollisionMaterial(&mesh->materials[default_material_index],
                                  default_material);
    }

    return mesh;
}

struct OoTCollisionMesh *
join_OoTCollisionMeshes_impl(struct OoTCollisionMesh **meshes,
                             size_t n_meshes) {
    unsigned int n_verts = 0, n_faces = 0, n_materials = 0;
    for (size_t i = 0; i < n_meshes; i++) {
        struct OoTCollisionMesh *m = meshes[i];
        n_verts += m->n_verts;
        n_faces += m->n_faces;
        n_materials += m->n_materials;
    }
    struct OoTCollisionMesh *joined_mesh =
        malloc(sizeof(struct OoTCollisionMesh));
    if (joined_mesh == NULL) {
        log_error("malloc mesh failed");
        return NULL;
    }

    joined_mesh->n_verts = n_verts;
    joined_mesh->verts = malloc(sizeof(struct OoTCollisionVertex) * n_verts);

    joined_mesh->n_faces = n_faces;
    joined_mesh->faces = malloc(sizeof(struct OoTCollisionTri) * n_faces);

    joined_mesh->n_materials = n_materials;
    joined_mesh->materials =
        malloc(sizeof(struct OoTCollisionMaterial) * n_materials);

    if (joined_mesh->materials != NULL) {
        // for free_create_OoTCollisionMesh_from_buffers
        for (unsigned int i = 0; i < n_materials; i++) {
            joined_mesh->materials[i].surface_type_0 = NULL;
            joined_mesh->materials[i].surface_type_1 = NULL;
            joined_mesh->materials[i].flags_a = NULL;
            joined_mesh->materials[i].flags_b = NULL;
        }
    }

    if (joined_mesh->verts == NULL || joined_mesh->faces == NULL ||
        joined_mesh->materials == NULL) {
        log_error("malloc verts, faces or materials failed");
        free_create_OoTCollisionMesh_from_buffers(joined_mesh);
        return NULL;
    }

    // TODO dedupe materials somehow?

    unsigned int off_verts = 0, off_faces = 0, off_materials = 0;
    for (size_t i_mesh = 0; i_mesh < n_meshes; i_mesh++) {
        struct OoTCollisionMesh *m = meshes[i_mesh];
        memcpy(&joined_mesh->verts[off_verts], m->verts,
               sizeof(struct OoTCollisionVertex) * m->n_verts);
        for (unsigned int i_face = 0; i_face < m->n_faces; i_face++) {
            for (int j = 0; j < 3; j++) {
                joined_mesh->faces[off_faces + i_face].verts[j] =
                    off_verts + m->faces[i_face].verts[j];
            }
            joined_mesh->faces[off_faces + i_face].material =
                off_materials + m->faces[i_face].material;
        }
        for (unsigned int i_mat = 0; i_mat < m->n_materials; i_mat++) {
            copy_OoTCollisionMaterial(
                &joined_mesh->materials[off_materials + i_mat],
                &m->materials[i_mat]);
        }
        off_verts += m->n_verts;
        off_faces += m->n_faces;
        off_materials += m->n_materials;
    }

    return joined_mesh;
}

int write_OoTCollisionMesh_to_c(struct OoTCollisionMesh *mesh,
                                const char *vtx_list_name,
                                const char *poly_list_name,
                                const char *surface_types_name, FILE *f,
                                struct OoTCollisionBounds *out_bounds) {
    unsigned int *indices = malloc(sizeof(unsigned int) * mesh->n_faces * 3);
    unsigned int *remap = malloc(sizeof(unsigned int) * mesh->n_verts);

    if (indices == NULL || remap == NULL) {
        log_error("malloc indices or remap failed");
        free(indices);
        free(remap);
        return -1;
    }

    for (unsigned int i_face = 0; i_face < mesh->n_faces; i_face++) {
        for (int j = 0; j < 3; j++) {
            indices[i_face * 3 + j] = mesh->faces[i_face].verts[j];
            assert(indices[i_face * 3 + j] < mesh->n_verts);
        }
    }

    // TODO convert vertex coords to int16_t somewhere before doing the remap

    size_t n_unique_verts = meshopt_generateVertexRemap(
        remap, indices, mesh->n_faces * 3, mesh->verts, mesh->n_verts,
        sizeof(struct OoTCollisionVertex));

    free(indices);

    struct OoTCollisionVertex *vertices =
        malloc(sizeof(struct OoTCollisionVertex) * n_unique_verts);
    if (vertices == NULL) {
        log_error("malloc vertices failed");
        free(remap);
        return -2;
    }
    meshopt_remapVertexBuffer(vertices, mesh->verts, mesh->n_verts,
                              sizeof(struct OoTCollisionVertex), remap);

    fprintf(f, "// Hi from write_OoTCollisionMesh_to_c\n");

    int16_t minX = 0, maxX = 0, minY = 0, maxY = 0, minZ = 0, maxZ = 0;

    if (n_unique_verts != 0) {
        minX = maxX = (int16_t)vertices[0].coords[0];
        minY = maxY = (int16_t)vertices[0].coords[1];
        minZ = maxZ = (int16_t)vertices[0].coords[2];
    }

    fprintf(f, "Vec3s %s[] = {\n", vtx_list_name);
    for (size_t i = 0; i < n_unique_verts; i++) {
        struct OoTCollisionVertex *v = &vertices[i];
        // TODO check coords range for int16_t
        int16_t x, y, z;
        x = (int16_t)v->coords[0];
        y = (int16_t)v->coords[1];
        z = (int16_t)v->coords[2];
        fprintf(f, "    { %" PRId16 ", %" PRId16 ", %" PRId16 " },\n", x, y, z);
        minX = MIN(minX, x);
        maxX = MAX(maxX, x);
        minY = MIN(minY, y);
        maxY = MAX(maxY, y);
        minZ = MIN(minZ, z);
        maxZ = MAX(maxZ, z);
    }
    fprintf(f, "};\n");

    free(vertices);

    fprintf(f, "CollisionPoly %s[] = {\n", poly_list_name);
    for (unsigned int i = 0; i < mesh->n_faces; i++) {
        struct OoTCollisionTri *t = &mesh->faces[i];
        unsigned int v0, v1, v2;
        v0 = t->verts[0];
        v1 = t->verts[1];
        v2 = t->verts[2];
        float x0, y0, z0, x1, y1, z1, x2, y2, z2;

        y0 = mesh->verts[v0].coords[1];
        y1 = mesh->verts[v1].coords[1];
        y2 = mesh->verts[v2].coords[1];
        // cycle v0,v1,v2 such that v0 has the lowest y
        // Circumvents a bug in CollisionPoly_GetMinY
        if (y1 < y0 && y1 < y2) {
            v0 = t->verts[1];
            v1 = t->verts[2];
            v2 = t->verts[0];
        } else if (y2 < y0 && y2 < y1) {
            v0 = t->verts[2];
            v1 = t->verts[0];
            v2 = t->verts[1];
        }

        x0 = mesh->verts[v0].coords[0];
        y0 = mesh->verts[v0].coords[1];
        z0 = mesh->verts[v0].coords[2];
        x1 = mesh->verts[v1].coords[0];
        y1 = mesh->verts[v1].coords[1];
        z1 = mesh->verts[v1].coords[2];
        x2 = mesh->verts[v2].coords[0];
        y2 = mesh->verts[v2].coords[1];
        z2 = mesh->verts[v2].coords[2];
        float nx, ny, nz;
        // n = normalized((v1-v0)x(v2-v0))
        float ux, uy, uz, vx, vy, vz;
        // u = v1-v0  v = v2-v0
        ux = x1 - x0;
        uy = y1 - y0;
        uz = z1 - z0;
        vx = x2 - x0;
        vy = y2 - y0;
        vz = z2 - z0;
        // n = u x v
        nx = uy * vz - uz * vy;
        ny = uz * vx - ux * vz;
        nz = ux * vy - uy * vx;
        // n = normalized(n)
        float nn = sqrtf(nx * nx + ny * ny + nz * nz);
        fprintf(f, "/*\n");
        fprintf(f, "  0 = %f %f %f\n", x0, y0, z0);
        fprintf(f, "  1 = %f %f %f\n", x1, y1, z1);
        fprintf(f, "  2 = %f %f %f\n", x2, y2, z2);
        fprintf(f, "  u = %f %f %f\n", ux, uy, uz);
        fprintf(f, "  v = %f %f %f\n", vx, vy, vz);
        fprintf(f, "  n = %f %f %f\n", nx, ny, nz);
        fprintf(f, "  nn = %f\n", nn);
        fprintf(f, " */\n");
        if (nn == 0.0f) {
            // TODO probably skip writing triangle instead
            nx = 1.0f;
            ny = 0.0f;
            nz = 0.0f;
        } else {
            nx /= nn;
            ny /= nn;
            nz /= nn;
        }
        int16_t dist;
        // TODO check float -> int16 conversion
        dist = -(nx * x0 + ny * y0 + nz * z0);

        fprintf(f,
                "    {\n"
                "        %u,\n"
                "        {\n"
                "            COLPOLY_VTX(%u, %s),\n"
                "            COLPOLY_VTX(%u, %s),\n"
                "            COLPOLY_VTX(%u, 0),\n"
                "        },\n"
                "        {\n"
                "            COLPOLY_SNORMAL(%f),\n"
                "            COLPOLY_SNORMAL(%f),\n"
                "            COLPOLY_SNORMAL(%f),\n"
                "        },\n"
                "        %" PRId16 ",\n"
                "    },\n",
                t->material,                                     //
                remap[v0], mesh->materials[t->material].flags_a, //
                remap[v1], mesh->materials[t->material].flags_b, //
                remap[v2],                                       //
                nx, ny, nz, dist);
    }
    fprintf(f, "};\n");

    free(remap);

    fprintf(f, "SurfaceType %s[] = {\n", surface_types_name);
    for (unsigned int i = 0; i < mesh->n_materials; i++) {
        fprintf(f,
                "    {\n"
                "        {\n"
                "            %s,\n"
                "            %s,\n"
                "        },\n"
                "    },\n",
                mesh->materials[i].surface_type_0,
                mesh->materials[i].surface_type_1);
    }
    fprintf(f, "};\n");

    if (out_bounds != NULL) {
        out_bounds->min[0] = minX;
        out_bounds->min[1] = minY;
        out_bounds->min[2] = minZ;
        out_bounds->max[0] = maxX;
        out_bounds->max[1] = maxY;
        out_bounds->max[2] = maxZ;
    }

    return 0;
}
