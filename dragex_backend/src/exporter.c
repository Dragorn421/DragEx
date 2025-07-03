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

void free_create_MeshInfo_from_buffers(struct MeshInfo *mesh) {
  if (mesh != NULL) {
    free(mesh->name);
    free(mesh->verts);
    free(mesh->faces);
    if (mesh->materials != NULL) {
      for (int i = 0; i < mesh->n_materials; i++) {
        free(mesh->materials[i].name);
      }
      free(mesh->materials);
    }
    free(mesh);
  }
}

struct MeshInfo *create_MeshInfo_from_buffers(
    float *buf_vertices_co, size_t buf_vertices_co_len,
    unsigned int *buf_triangles_loops, size_t buf_triangles_loops_len,
    unsigned int *buf_loops_vertex_index, size_t buf_loops_vertex_index_len,
    float *buf_loops_normal, size_t buf_loops_normal_len) {
  unsigned int n_loops = buf_loops_vertex_index_len;
  if (buf_loops_normal_len != n_loops * 3)
    return NULL;

  struct MeshInfo *mesh = malloc(sizeof(struct MeshInfo));
  if (mesh == NULL)
    return NULL;
  mesh->name = strdup("mesh");

  mesh->n_verts = n_loops;
  mesh->verts = malloc(sizeof(struct VertexInfo[n_loops]));

  int n_faces = (int)(buf_triangles_loops_len / 3);
  mesh->n_faces = n_faces;
  mesh->faces = malloc(sizeof(struct VertexInfo[n_faces]));

  mesh->n_materials = 1;
  mesh->materials = malloc(sizeof(struct MaterialInfo[1]));

  mesh->materials[0].name = strdup("material");

  if (mesh->name == NULL || mesh->verts == NULL || mesh->faces == NULL ||
      mesh->materials == NULL || mesh->materials[0].name == NULL) {
    free_create_MeshInfo_from_buffers(mesh);
    return NULL;
  }

  for (unsigned int i_loop = 0; i_loop < n_loops; i_loop++) {
    for (int j = 0; j < 3; j++) {
      int v = buf_loops_vertex_index[i_loop] * 3 + j;
      if (v >= buf_vertices_co_len) {
        free_create_MeshInfo_from_buffers(mesh);
        return NULL;
      }
      mesh->verts[i_loop].coords[j] = buf_vertices_co[v];
    }

    for (int j = 0; j < 3; j++)
      mesh->verts[i_loop].normal[j] = buf_loops_normal[i_loop * 3 + j];

    mesh->verts[i_loop].alpha = 255;
  }

  for (int i = 0; i < n_faces; i++) {
    for (int j = 0; j < 3; j++) {
      unsigned int loop = buf_triangles_loops[i * 3 + j];
      if (loop >= n_loops) {
        free_create_MeshInfo_from_buffers(mesh);
        return NULL;
      }
      mesh->faces[i].verts[j] = loop;
    }
    mesh->faces[i].material = 0;
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

  for (int i_mat = 0; i_mat < in_mesh->n_materials; i_mat++) {
    struct MeshInfo *m = malloc(sizeof(struct MeshInfo));
    if (m == NULL) {
      free_split_mesh_by_material(out_meshes, in_mesh->n_materials);
      return NULL;
    }
    out_meshes[i_mat] = m;

    int n_faces_used = 0;
    uint8_t vertices_used[in_mesh->n_verts];

    memset(vertices_used, 0, in_mesh->n_verts);

    for (int i_face = 0; i_face < in_mesh->n_faces; i_face++) {
      struct TriInfo *f = &in_mesh->faces[i_face];

      if (f->material == i_mat) {
        n_faces_used++;
        for (int i = 0; i < 3; i++) {
          vertices_used[f->verts[i]] = 1;
        }
      }
    }

    int n_vertices_used = 0;
    for (int i_vert = 0; i_vert < in_mesh->n_verts; i_vert++) {
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

    int i_face_new = 0;
    int i_vert_new = 0;
    memset(vertices_used, 0, in_mesh->n_verts);

    for (int i_face = 0; i_face < in_mesh->n_faces; i_face++) {
      struct TriInfo *f = &in_mesh->faces[i_face];

      if (f->material == i_mat) {
        m->faces[i_face_new] = *f;
        i_face_new++;
        for (int i = 0; i < 3; i++) {
          int v = f->verts[i];

          if (!vertices_used[v]) {
            m->verts[i_vert_new] = in_mesh->verts[v];
            i_vert_new++;
            vertices_used[v] = 1;
          }
        }
      }
    }

    m->materials[0] = in_mesh->materials[i_mat];
    m->materials[0].name = strdup(m->materials[0].name);
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

struct f3d_mesh *mesh_to_f3d_mesh(struct MeshInfo *mesh) {
  unsigned int indices[mesh->n_faces * 3];
  unsigned int remap[mesh->n_verts];

  for (int i_face = 0; i_face < mesh->n_faces; i_face++) {
    for (int j = 0; j < 3; j++)
      indices[i_face * 3 + j] = mesh->faces[i_face].verts[j];
  }

  // TODO convert VertexInfo.coords to int16_t somewhere before doing the remap

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
  int i_tri = 0;
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
                f3d_vertices, sizeof(struct f3d_vertex[f3d_vertices_buf_len]));
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
          f3d_v->st[0] = 0;
          f3d_v->st[1] = 0;
          f3d_v->cn[0] = (uint8_t)(int)(vi->normal[0] * 0x7F);
          f3d_v->cn[1] = (uint8_t)(int)(vi->normal[1] * 0x7F);
          f3d_v->cn[2] = (uint8_t)(int)(vi->normal[2] * 0x7F);
          f3d_v->alpha = vi->alpha;
          i_f3d_vertices++;
        }
      }

      // append tri to tris
      if (f3d_entries[i_f3d_entries].n_tris >= cur_entry_tris_buf_len) {
        cur_entry_tris_buf_len *= 2;
        void *tmp = realloc(
            f3d_entries[i_f3d_entries].tris,
            sizeof(struct f3d_mesh_load_entry_tri[cur_entry_tris_buf_len]));
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
            realloc(f3d_entries,
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

int write_f3d_mesh(FILE *f, struct f3d_mesh *mesh, const char *name) {
  fprintf(f, "Vtx %s_vtx[] = {\n", name);
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

  fprintf(f, "Gfx %s_dl[] = {\n", name);
  for (int i = 0; i < mesh->n_entries; i++) {
    struct f3d_mesh_load_entry *e = &mesh->entries[i];

    fprintf(f,
            "    gsSPVertex("
            "&%s_vtx[%d], %" PRIu8 ", %" PRIu8 "),\n",
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
  for (int i_mesh = 0; i_mesh < mesh_info->n_materials; i_mesh++) {
    struct MeshInfo *mesh = meshes[i_mesh];
    struct f3d_mesh *f3d_mesh = mesh_to_f3d_mesh(mesh);
    write_f3d_mesh(f, f3d_mesh, mesh->name);
    free_mesh_to_f3d_mesh(f3d_mesh);
  }
  free_split_mesh_by_material(meshes, mesh_info->n_materials);
  fclose(f);
  return 0;
}
