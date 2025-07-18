#ifndef DRAGEX_BACKEND_EXPORTER_H
#define DRAGEX_BACKEND_EXPORTER_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

// info

struct VertexInfo {
    float coords[3];
    float uv[2];
    float normal[3];
    uint8_t color[4]; // RGBA
};

struct TriInfo {
    unsigned int verts[3];
    unsigned int material;
};

struct MaterialInfoImage {
    char *c_identifier;
    int width, height;
};

enum rdp_om_cycle_type {
    RDP_OM_CYCLE_TYPE_1CYCLE,
    RDP_OM_CYCLE_TYPE_2CYCLE,
    RDP_OM_CYCLE_TYPE_COPY,
    RDP_OM_CYCLE_TYPE_FILL
};

enum rdp_om_rgb_dither {
    RDP_OM_RGB_DITHER_MAGIC_SQUARE,
    RDP_OM_RGB_DITHER_BAYER,
    RDP_OM_RGB_DITHER_RANDOM_NOISE,
    RDP_OM_RGB_DITHER_NONE
};

enum rdp_om_alpha_dither {
    RDP_OM_ALPHA_DITHER_SAME_AS_RGB,
    RDP_OM_ALPHA_DITHER_INVERSE_OF_RGB,
    RDP_OM_ALPHA_DITHER_RANDOM_NOISE,
    RDP_OM_ALPHA_DITHER_NONE
};

enum rdp_om_blender_P_M_inputs {
    RDP_OM_BLENDER_P_M_INPUTS_INPUT,
    RDP_OM_BLENDER_P_M_INPUTS_MEMORY,
    RDP_OM_BLENDER_P_M_INPUTS_BLEND_COLOR,
    RDP_OM_BLENDER_P_M_INPUTS_FOG_COLOR
};

enum rdp_om_blender_A_inputs {
    RDP_OM_BLENDER_A_INPUTS_INPUT_ALPHA,
    RDP_OM_BLENDER_A_INPUTS_FOG_ALPHA,
    RDP_OM_BLENDER_A_INPUTS_SHADE_ALPHA,
    RDP_OM_BLENDER_A_INPUTS_0
};

enum rdp_om_blender_B_inputs {
    RDP_OM_BLENDER_B_INPUTS_1_MINUS_A,
    RDP_OM_BLENDER_B_INPUTS_MEMORY_COVERAGE,
    RDP_OM_BLENDER_B_INPUTS_1,
    RDP_OM_BLENDER_B_INPUTS_0
};

enum rdp_om_z_mode {
    RDP_OM_Z_MODE_OPAQUE,
    RDP_OM_Z_MODE_INTERPENETRATING,
    RDP_OM_Z_MODE_TRANSPARENT,
    RDP_OM_Z_MODE_DECAL
};

enum rdp_om_cvg_dest {
    RDP_OM_CVG_DEST_CLAMP,
    RDP_OM_CVG_DEST_WRAP,
    RDP_OM_CVG_DEST_FULL,
    RDP_OM_CVG_DEST_SAVE
};

struct MaterialInfoOtherModes {
    bool atomic_prim;
    enum rdp_om_cycle_type cycle_type;
    bool persp_tex_en;
    bool detail_tex_en;
    bool sharpen_tex_en;
    bool tex_lod_en;
    bool tlut_en;
    bool tlut_type;

    bool sample_type;
    bool mid_texel;
    bool bi_lerp_0;
    bool bi_lerp_1;
    bool convert_one;
    bool key_en;
    enum rdp_om_rgb_dither rgb_dither_sel;
    enum rdp_om_alpha_dither alpha_dither_sel;

    enum rdp_om_blender_P_M_inputs bl_m1a_0;
    enum rdp_om_blender_P_M_inputs bl_m1a_1;
    enum rdp_om_blender_A_inputs bl_m1b_0;
    enum rdp_om_blender_A_inputs bl_m1b_1;
    enum rdp_om_blender_P_M_inputs bl_m2a_0;
    enum rdp_om_blender_P_M_inputs bl_m2a_1;
    enum rdp_om_blender_B_inputs bl_m2b_0;
    enum rdp_om_blender_B_inputs bl_m2b_1;

    bool force_blend;
    bool alpha_cvg_select;
    bool cvg_x_alpha;
    enum rdp_om_z_mode z_mode;
    enum rdp_om_cvg_dest cvg_dest;
    bool color_on_cvg;

    bool image_read_en;
    bool z_update_en;
    bool z_compare_en;
    bool antialias_en;
    bool z_source_sel;
    bool dither_alpha_en;
    bool alpha_compare_en;
};

enum rdp_tile_format {
    RDP_TILE_FORMAT_RGBA,
    RDP_TILE_FORMAT_YUV,
    RDP_TILE_FORMAT_CI,
    RDP_TILE_FORMAT_IA,
    RDP_TILE_FORMAT_I
};

enum rdp_tile_size {
    RDP_TILE_SIZE_4,
    RDP_TILE_SIZE_8,
    RDP_TILE_SIZE_16,
    RDP_TILE_SIZE_32
};

struct MaterialInfoTile {
    // this is a pointer instead of a sub-struct because it can be NULL or
    // shared with other tiles/materials
    struct MaterialInfoImage *image;

    enum rdp_tile_format format;
    enum rdp_tile_size size;
    int line;
    int address;
    int palette;
    bool clamp_T;
    bool mirror_T;
    int mask_T;
    int shift_T;
    bool clamp_S;
    bool mirror_S;
    int mask_S;
    int shift_S;

    float upper_left_S;
    float upper_left_T;
    float lower_right_S;
    float lower_right_T;
};

enum rdp_combiner_rgb_A_inputs {
    RDP_COMBINER_RGB_A_INPUTS_COMBINED,
    RDP_COMBINER_RGB_A_INPUTS_TEX0,
    RDP_COMBINER_RGB_A_INPUTS_TEX1,
    RDP_COMBINER_RGB_A_INPUTS_PRIMITIVE,
    RDP_COMBINER_RGB_A_INPUTS_SHADE,
    RDP_COMBINER_RGB_A_INPUTS_ENVIRONMENT,
    RDP_COMBINER_RGB_A_INPUTS_1,
    RDP_COMBINER_RGB_A_INPUTS_NOISE,
    RDP_COMBINER_RGB_A_INPUTS_0
};
enum rdp_combiner_rgb_B_inputs {
    RDP_COMBINER_RGB_B_INPUTS_COMBINED,
    RDP_COMBINER_RGB_B_INPUTS_TEX0,
    RDP_COMBINER_RGB_B_INPUTS_TEX1,
    RDP_COMBINER_RGB_B_INPUTS_PRIMITIVE,
    RDP_COMBINER_RGB_B_INPUTS_SHADE,
    RDP_COMBINER_RGB_B_INPUTS_ENVIRONMENT,
    RDP_COMBINER_RGB_B_INPUTS_CENTER,
    RDP_COMBINER_RGB_B_INPUTS_K4,
    RDP_COMBINER_RGB_B_INPUTS_0
};
enum rdp_combiner_rgb_C_inputs {
    RDP_COMBINER_RGB_C_INPUTS_COMBINED,
    RDP_COMBINER_RGB_C_INPUTS_TEX0,
    RDP_COMBINER_RGB_C_INPUTS_TEX1,
    RDP_COMBINER_RGB_C_INPUTS_PRIMITIVE,
    RDP_COMBINER_RGB_C_INPUTS_SHADE,
    RDP_COMBINER_RGB_C_INPUTS_ENVIRONMENT,
    RDP_COMBINER_RGB_C_INPUTS_SCALE,
    RDP_COMBINER_RGB_C_INPUTS_COMBINED_ALPHA,
    RDP_COMBINER_RGB_C_INPUTS_TEX0_ALPHA,
    RDP_COMBINER_RGB_C_INPUTS_TEX1_ALPHA,
    RDP_COMBINER_RGB_C_INPUTS_PRIMITIVE_ALPHA,
    RDP_COMBINER_RGB_C_INPUTS_SHADE_ALPHA,
    RDP_COMBINER_RGB_C_INPUTS_ENVIRONMENT_ALPHA,
    RDP_COMBINER_RGB_C_INPUTS_LOD_FRACTION,
    RDP_COMBINER_RGB_C_INPUTS_PRIM_LOD_FRAC,
    RDP_COMBINER_RGB_C_INPUTS_K5,
    RDP_COMBINER_RGB_C_INPUTS_0
};
enum rdp_combiner_rgb_D_inputs {
    RDP_COMBINER_RGB_D_INPUTS_COMBINED,
    RDP_COMBINER_RGB_D_INPUTS_TEX0,
    RDP_COMBINER_RGB_D_INPUTS_TEX1,
    RDP_COMBINER_RGB_D_INPUTS_PRIMITIVE,
    RDP_COMBINER_RGB_D_INPUTS_SHADE,
    RDP_COMBINER_RGB_D_INPUTS_ENVIRONMENT,
    RDP_COMBINER_RGB_D_INPUTS_1,
    RDP_COMBINER_RGB_D_INPUTS_0
};

enum rdp_combiner_alpha_A_inputs {
    RDP_COMBINER_ALPHA_A_INPUTS_COMBINED,
    RDP_COMBINER_ALPHA_A_INPUTS_TEX0,
    RDP_COMBINER_ALPHA_A_INPUTS_TEX1,
    RDP_COMBINER_ALPHA_A_INPUTS_PRIMITIVE,
    RDP_COMBINER_ALPHA_A_INPUTS_SHADE,
    RDP_COMBINER_ALPHA_A_INPUTS_ENVIRONMENT,
    RDP_COMBINER_ALPHA_A_INPUTS_1,
    RDP_COMBINER_ALPHA_A_INPUTS_0
};
enum rdp_combiner_alpha_B_inputs {
    RDP_COMBINER_ALPHA_B_INPUTS_COMBINED,
    RDP_COMBINER_ALPHA_B_INPUTS_TEX0,
    RDP_COMBINER_ALPHA_B_INPUTS_TEX1,
    RDP_COMBINER_ALPHA_B_INPUTS_PRIMITIVE,
    RDP_COMBINER_ALPHA_B_INPUTS_SHADE,
    RDP_COMBINER_ALPHA_B_INPUTS_ENVIRONMENT,
    RDP_COMBINER_ALPHA_B_INPUTS_1,
    RDP_COMBINER_ALPHA_B_INPUTS_0
};
enum rdp_combiner_alpha_C_inputs {
    RDP_COMBINER_ALPHA_C_INPUTS_LOD_FRACTION,
    RDP_COMBINER_ALPHA_C_INPUTS_TEX0,
    RDP_COMBINER_ALPHA_C_INPUTS_TEX1,
    RDP_COMBINER_ALPHA_C_INPUTS_PRIMITIVE,
    RDP_COMBINER_ALPHA_C_INPUTS_SHADE,
    RDP_COMBINER_ALPHA_C_INPUTS_ENVIRONMENT,
    RDP_COMBINER_ALPHA_C_INPUTS_PRIM_LOD_FRAC,
    RDP_COMBINER_ALPHA_C_INPUTS_0
};
enum rdp_combiner_alpha_D_inputs {
    RDP_COMBINER_ALPHA_D_INPUTS_COMBINED,
    RDP_COMBINER_ALPHA_D_INPUTS_TEX0,
    RDP_COMBINER_ALPHA_D_INPUTS_TEX1,
    RDP_COMBINER_ALPHA_D_INPUTS_PRIMITIVE,
    RDP_COMBINER_ALPHA_D_INPUTS_SHADE,
    RDP_COMBINER_ALPHA_D_INPUTS_ENVIRONMENT,
    RDP_COMBINER_ALPHA_D_INPUTS_1,
    RDP_COMBINER_ALPHA_D_INPUTS_0
};

struct MaterialInfoCombiner {
    enum rdp_combiner_rgb_A_inputs rgb_A_0;
    enum rdp_combiner_rgb_B_inputs rgb_B_0;
    enum rdp_combiner_rgb_C_inputs rgb_C_0;
    enum rdp_combiner_rgb_D_inputs rgb_D_0;
    enum rdp_combiner_alpha_A_inputs alpha_A_0;
    enum rdp_combiner_alpha_B_inputs alpha_B_0;
    enum rdp_combiner_alpha_C_inputs alpha_C_0;
    enum rdp_combiner_alpha_D_inputs alpha_D_0;
    enum rdp_combiner_rgb_A_inputs rgb_A_1;
    enum rdp_combiner_rgb_B_inputs rgb_B_1;
    enum rdp_combiner_rgb_C_inputs rgb_C_1;
    enum rdp_combiner_rgb_D_inputs rgb_D_1;
    enum rdp_combiner_alpha_A_inputs alpha_A_1;
    enum rdp_combiner_alpha_B_inputs alpha_B_1;
    enum rdp_combiner_alpha_C_inputs alpha_C_1;
    enum rdp_combiner_alpha_D_inputs alpha_D_1;
};

struct rgbaf {
    float r, g, b, a;
};

struct rgbau8 {
    uint8_t r, g, b, a;
};

struct MaterialInfoVals {
    int primitive_depth_z;
    int primitive_depth_dz;
    struct rgbaf fog_color;
    struct rgbaf blend_color;
    int min_level;
    int prim_lod_frac;
    struct rgbaf primitive_color;
    struct rgbaf environment_color;
};

struct MaterialInfoGeometryMode {
    bool lighting;
};

struct MaterialInfo {
    char *name;
    int uv_basis_s;
    int uv_basis_t;
    struct MaterialInfoOtherModes other_modes;
    struct MaterialInfoTile tiles[8];
    struct MaterialInfoCombiner combiner;
    struct MaterialInfoVals vals;
    struct MaterialInfoGeometryMode geometry_mode;
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
    float *buf_points_color, size_t buf_points_color_len,                    //
    float *buf_loops_uv, size_t buf_loops_uv_len,                            //
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

int write_mesh_info_to_f3d_c(struct MeshInfo *mesh_info, FILE *f,
                             char **dl_name);

//

struct OoTCollisionVertex {
    float coords[3];
};

struct OoTCollisionTri {
    unsigned int verts[3];
    unsigned int material;
};

struct OoTCollisionMaterial {
    char *surface_type_0, *surface_type_1, *flags_a, *flags_b;
};

struct OoTCollisionMesh {
    struct OoTCollisionVertex *verts;
    struct OoTCollisionTri *faces;
    struct OoTCollisionMaterial *materials;
    unsigned int n_verts, n_faces, n_materials;
};

void free_create_OoTCollisionMesh_from_buffers(struct OoTCollisionMesh *mesh);

struct OoTCollisionMesh *create_OoTCollisionMesh_from_buffers(
    float *buf_vertices_co, size_t buf_vertices_co_len,                //
    unsigned int *buf_triangles_loops, size_t buf_triangles_loops_len, //
    unsigned int *buf_triangles_material_index,
    size_t buf_triangles_material_index_len,                                 //
    unsigned int *buf_loops_vertex_index, size_t buf_loops_vertex_index_len, //
    struct OoTCollisionMaterial **materials, size_t n_materials,             //
    struct OoTCollisionMaterial *default_material);

struct OoTCollisionMesh *
join_OoTCollisionMeshes_impl(struct OoTCollisionMesh **meshes, size_t n_meshes);

struct OoTCollisionBounds {
    int16_t min[3];
    int16_t max[3];
};

int write_OoTCollisionMesh_to_c(struct OoTCollisionMesh *mesh,
                                const char *vtx_list_name,
                                const char *poly_list_name,
                                const char *surface_types_name, FILE *f,
                                struct OoTCollisionBounds *out_bounds);

#endif
