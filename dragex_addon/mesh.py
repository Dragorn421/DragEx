import dataclasses
from typing import TYPE_CHECKING, Optional, Sequence

import numpy as np

import bpy
import mathutils

from . import util

if TYPE_CHECKING:
    from ..dragex_backend import dragex_backend
else:
    try:
        import dragex_backend
    except ModuleNotFoundError:
        dragex_backend = None


@dataclasses.dataclass(frozen=True)
class ImageKey:
    image: bpy.types.Image
    format: str
    size: str


@dataclasses.dataclass
class ImageInfos:
    info_by_key: dict[ImageKey, "dragex_backend.MaterialInfoImage"] = dataclasses.field(
        default_factory=dict
    )
    key_by_c_identifier: dict[str, ImageKey] = dataclasses.field(default_factory=dict)


def material_to_MaterialInfo(
    c_identifiers_prefix: str,
    mat: bpy.types.Material,
    image_infos: ImageInfos,
):
    mat_dragex = util.DRAGEX(mat)
    other_modes = mat_dragex.rdp.other_modes
    tiles = mat_dragex.rdp.tiles
    combiner = mat_dragex.rdp.combiner
    vals = mat_dragex.rdp.vals
    mat_geomode = mat_dragex.rsp

    mat_info_tiles = list[dragex_backend.MaterialInfoTile]()
    for tile in tiles.tiles:
        image: bpy.types.Image | None = tile.image
        if image is None:
            image_info = None
        else:
            image_key = ImageKey(image, tile.format, tile.size)
            image_info = image_infos.info_by_key.get(image_key)
            if image_info is None:
                c_identifier = c_identifiers_prefix + util.make_c_identifier(image.name)
                if c_identifier in image_infos.key_by_c_identifier:
                    c_identifier = c_identifiers_prefix + util.make_c_identifier(
                        f"{image.name}_{tile.format}{tile.size}"
                    )
                    c_identifier_candidate = c_identifier
                    i = 2
                    while c_identifier_candidate in image_infos.key_by_c_identifier:
                        c_identifier_candidate = f"{c_identifier}_{i}"
                        i += 1
                    c_identifier = c_identifier_candidate

                width, height = image.size
                image_info = dragex_backend.MaterialInfoImage(
                    c_identifier=c_identifier,
                    width=width,
                    height=height,
                )
                image_infos.info_by_key[image_key] = image_info
                image_infos.key_by_c_identifier[c_identifier] = image_key
        mat_info_tiles.append(
            dragex_backend.MaterialInfoTile(
                image=image_info,
                format=tile.format,
                size=tile.size,
                line=tile.line,
                address=tile.address,
                palette=tile.palette,
                clamp_T=tile.clamp_T,
                mirror_T=tile.mirror_T,
                mask_T=tile.mask_T,
                shift_T=tile.shift_T,
                clamp_S=tile.clamp_S,
                mirror_S=tile.mirror_S,
                mask_S=tile.mask_S,
                shift_S=tile.shift_S,
                upper_left_S=tile.upper_left_S,
                upper_left_T=tile.upper_left_T,
                lower_right_S=tile.lower_right_S,
                lower_right_T=tile.lower_right_T,
            )
        )

    mat_info = dragex_backend.MaterialInfo(
        name=c_identifiers_prefix + util.make_c_identifier(mat.name),
        uv_basis_s=mat_dragex.uv_basis_s,
        uv_basis_t=mat_dragex.uv_basis_t,
        other_modes=dragex_backend.MaterialInfoOtherModes(
            atomic_prim=other_modes.atomic_prim,
            cycle_type=other_modes.cycle_type,
            persp_tex_en=other_modes.persp_tex_en,
            detail_tex_en=other_modes.detail_tex_en,
            sharpen_tex_en=other_modes.sharpen_tex_en,
            tex_lod_en=other_modes.tex_lod_en,
            tlut_en=other_modes.tlut_en,
            tlut_type=other_modes.tlut_type,
            #
            sample_type=other_modes.sample_type,
            mid_texel=other_modes.mid_texel,
            bi_lerp_0=other_modes.bi_lerp_0,
            bi_lerp_1=other_modes.bi_lerp_1,
            convert_one=other_modes.convert_one,
            key_en=other_modes.key_en,
            rgb_dither_sel=other_modes.rgb_dither_sel,
            alpha_dither_sel=other_modes.alpha_dither_sel,
            #
            bl_m1a_0=other_modes.bl_m1a_0,
            bl_m1a_1=other_modes.bl_m1a_1,
            bl_m1b_0=other_modes.bl_m1b_0,
            bl_m1b_1=other_modes.bl_m1b_1,
            bl_m2a_0=other_modes.bl_m2a_0,
            bl_m2a_1=other_modes.bl_m2a_1,
            bl_m2b_0=other_modes.bl_m2b_0,
            bl_m2b_1=other_modes.bl_m2b_1,
            #
            force_blend=other_modes.force_blend,
            alpha_cvg_select=other_modes.alpha_cvg_select,
            cvg_x_alpha=other_modes.cvg_x_alpha,
            z_mode=other_modes.z_mode,
            cvg_dest=other_modes.cvg_dest,
            color_on_cvg=other_modes.color_on_cvg,
            #
            image_read_en=other_modes.image_read_en,
            z_update_en=other_modes.z_update_en,
            z_compare_en=other_modes.z_compare_en,
            antialias_en=other_modes.antialias_en,
            z_source_sel=other_modes.z_source_sel,
            dither_alpha_en=other_modes.dither_alpha_en,
            alpha_compare_en=other_modes.alpha_compare_en,
        ),
        tiles=mat_info_tiles,
        combiner=dragex_backend.MaterialInfoCombiner(
            combiner.rgb_A_0,
            combiner.rgb_B_0,
            combiner.rgb_C_0,
            combiner.rgb_D_0,
            combiner.alpha_A_0,
            combiner.alpha_B_0,
            combiner.alpha_C_0,
            combiner.alpha_D_0,
            combiner.rgb_A_1,
            combiner.rgb_B_1,
            combiner.rgb_C_1,
            combiner.rgb_D_1,
            combiner.alpha_A_1,
            combiner.alpha_B_1,
            combiner.alpha_C_1,
            combiner.alpha_D_1,
        ),
        vals=dragex_backend.MaterialInfoVals(
            primitive_depth_z=vals.primitive_depth_z,
            primitive_depth_dz=vals.primitive_depth_dz,
            fog_color=vals.fog_color,
            blend_color=vals.blend_color,
            min_level=vals.min_level,
            prim_lod_frac=vals.prim_lod_frac,
            primitive_color=vals.primitive_color,
            environment_color=vals.environment_color,
        ),
        geometry_mode=dragex_backend.MaterialInfoGeometryMode(
            zbuffer=mat_geomode.zbuffer,
            lighting=mat_geomode.lighting,
            vertex_colors=mat_geomode.vertex_colors,
            cull_front=mat_geomode.cull_front,
            cull_back=mat_geomode.cull_back,
            fog=mat_geomode.fog,
            uv_gen_spherical=mat_geomode.uv_gen_spherical,
            uv_gen_linear=mat_geomode.uv_gen_linear,
            shade_smooth=mat_geomode.shade_smooth,
        ),
    )

    return mat_info


def mesh_to_mesh_info(
    obj: bpy.types.Object,
    mesh: bpy.types.Mesh,
    transform: mathutils.Matrix,
    image_infos: ImageInfos,
    c_identifiers_prefix: str,
):
    transform_per_vertex = np.zeros(len(mesh.vertices), dtype=np.uint)
    transforms = (transform,)

    mesh.calc_loop_triangles()  # TODO is this costly? we call it twice

    submeshes = (
        SubMeshInfo(
            tris_mask=np.ones(len(mesh.loop_triangles), dtype=bool),
            c_identifiers_suffix="",
        ),
    )

    buf_corners_material_index = util.new_uint_buf(len(mesh.loops))
    buf_corners_material_index[:] = 0

    corner_material_infos = ()
    default_corner_material_info = dragex_backend.CornerMaterialInfo(
        limb_index=0,
    )

    mesh_infos = mesh_to_mesh_infos_general(
        obj,
        mesh,
        transform_per_vertex,
        transforms,
        image_infos,
        c_identifiers_prefix,
        submeshes,
        buf_corners_material_index,
        corner_material_infos,
        default_corner_material_info,
    )

    assert len(mesh_infos) == 1, mesh_infos

    return mesh_infos[0]


@dataclasses.dataclass
class SubMeshInfo:
    tris_mask: np.ndarray
    c_identifiers_suffix: str


def mesh_to_mesh_infos_general(
    obj: bpy.types.Object,
    mesh: bpy.types.Mesh,
    transform_per_vertex: np.ndarray,
    transforms: Sequence[mathutils.Matrix],
    image_infos: ImageInfos,
    c_identifiers_prefix: str,
    submeshes: Sequence[SubMeshInfo],
    buf_corners_material_index: np.ndarray,
    corner_material_infos: Sequence["dragex_backend.CornerMaterialInfo"],
    default_corner_material_info: "dragex_backend.CornerMaterialInfo",
):
    # note: if size is too small, error is undescriptive:
    # "RuntimeError: internal error setting the array"
    buf_vertices_co = util.new_float_buf(3 * len(mesh.vertices))
    mesh.vertices.foreach_get("co", buf_vertices_co)
    mesh.calc_loop_triangles()
    buf_triangles_loops = util.new_uint_buf(3 * len(mesh.loop_triangles))
    buf_triangles_loops_Nx3 = buf_triangles_loops.reshape((len(mesh.loop_triangles), 3))
    buf_triangles_material_index = util.new_uint_buf(len(mesh.loop_triangles))
    mesh.loop_triangles[0].loops
    mesh.loop_triangles[0].material_index
    mesh.loop_triangles.foreach_get("loops", buf_triangles_loops)
    mesh.loop_triangles.foreach_get("material_index", buf_triangles_material_index)
    mesh.loops[0].vertex_index
    mesh.loops[0].normal
    buf_loops_vertex_index = util.new_uint_buf(len(mesh.loops))
    buf_loops_normal = util.new_float_buf(3 * len(mesh.loops))
    mesh.loops.foreach_get("vertex_index", buf_loops_vertex_index)
    mesh.loops.foreach_get("normal", buf_loops_normal)

    buf_vertices_co_Nx3 = buf_vertices_co.reshape((len(mesh.vertices), 3))
    buf_vertices_co_3xN = buf_vertices_co_Nx3.T

    buf_loops_normal_3xN = buf_loops_normal.reshape((len(mesh.loops), 3)).T

    if not set(transform_per_vertex).issubset(range(len(transforms))):
        raise Exception("There are vertices for which no transform is provided")

    for i_transform, transform in enumerate(transforms):
        transform = transform.to_4x4()
        if transform[3] != mathutils.Vector((0, 0, 0, 1)):
            raise Exception("Unexpected transform", i_transform, transform)
        transform3 = transform.to_3x3()
        transform3_np = np.array(transform3)
        transform_translation = transform.translation
        transform_translation_np = np.array(transform_translation)

        # TODO make faster using np.matmul(out=) and np.add(out=)
        buf_vertices_co_3xN[:, transform_per_vertex == i_transform] = (
            (
                transform3_np
                @ buf_vertices_co_3xN[:, transform_per_vertex == i_transform]
            ).T
            + transform_translation_np
        ).T

    active_color_attribute = mesh.color_attributes.active_color
    if active_color_attribute is None:
        buf_corners_color = None
        buf_points_color = None
    else:
        if active_color_attribute.data_type in {"FLOAT_COLOR", "BYTE_COLOR"}:
            assert isinstance(
                active_color_attribute,
                (
                    bpy.types.FloatColorAttribute,
                    bpy.types.ByteColorAttribute,
                ),
            )
            # Note: for ByteColorAttribute too the color uses floats
            if active_color_attribute.domain == "CORNER":
                buf_corners_color = util.new_float_buf(4 * len(mesh.loops))
                active_color_attribute.data.foreach_get("color", buf_corners_color)
                buf_points_color = None
            elif active_color_attribute.domain == "POINT":
                buf_corners_color = None
                buf_points_color = util.new_float_buf(4 * len(mesh.vertices))
                active_color_attribute.data.foreach_get("color", buf_points_color)
            else:
                raise NotImplementedError(active_color_attribute.domain)
        else:
            raise NotImplementedError(active_color_attribute.data_type)

    active_uv_layer = mesh.uv_layers.active
    if active_uv_layer is None:
        buf_loops_uv = None
    else:
        buf_loops_uv = util.new_float_buf(2 * len(mesh.loops))
        active_uv_layer.uv.foreach_get("vector", buf_loops_uv)

    material_infos = list[dragex_backend.MaterialInfo | None]()
    for mat_index in range(len(obj.material_slots)):
        mat = obj.material_slots[mat_index].material
        if mat is None:
            mat_info = None
        else:
            mat_dragex = util.DRAGEX(mat)
            if mat_dragex.mode == "NONE":
                mat_info = None
            else:
                mat_info = material_to_MaterialInfo(
                    c_identifiers_prefix, mat, image_infos
                )
        material_infos.append(mat_info)
    default_material_info = dragex_backend.MaterialInfo(
        name="DEFAULT_MATERIAL",
        uv_basis_s=1,
        uv_basis_t=1,
        other_modes=dragex_backend.MaterialInfoOtherModes(
            # TODO put more thought into default material
            atomic_prim=False,
            cycle_type="1CYCLE",
            persp_tex_en=False,
            detail_tex_en=False,
            sharpen_tex_en=False,
            tex_lod_en=False,
            tlut_en=False,
            tlut_type=False,
            #
            sample_type=False,
            mid_texel=False,
            bi_lerp_0=False,
            bi_lerp_1=False,
            convert_one=False,
            key_en=False,
            rgb_dither_sel="MAGIC_SQUARE",
            alpha_dither_sel="NONE",
            #
            bl_m1a_0="INPUT",
            bl_m1a_1="INPUT",
            bl_m1b_0="0",
            bl_m1b_1="0",
            bl_m2a_0="INPUT",
            bl_m2a_1="INPUT",
            bl_m2b_0="1",
            bl_m2b_1="1",
            #
            force_blend=False,
            alpha_cvg_select=False,
            cvg_x_alpha=False,
            z_mode="OPAQUE",
            cvg_dest="CLAMP",
            color_on_cvg=False,
            #
            image_read_en=False,
            z_update_en=False,
            z_compare_en=False,
            antialias_en=False,
            z_source_sel=False,
            dither_alpha_en=False,
            alpha_compare_en=False,
        ),
        tiles=(
            [
                dragex_backend.MaterialInfoTile(
                    image=None,
                    format="RGBA",
                    size="16",
                    line=0,
                    address=0,
                    palette=0,
                    clamp_T=False,
                    mirror_T=False,
                    mask_T=0,
                    shift_T=0,
                    clamp_S=False,
                    mirror_S=False,
                    mask_S=0,
                    shift_S=0,
                    upper_left_S=0,
                    upper_left_T=0,
                    lower_right_S=0,
                    lower_right_T=0,
                )
            ]
            * 8
        ),
        combiner=dragex_backend.MaterialInfoCombiner(
            "0",
            "0",
            "0",
            "PRIMITIVE",
            "0",
            "0",
            "0",
            "1",
            "0",
            "0",
            "0",
            "PRIMITIVE",
            "0",
            "0",
            "0",
            "1",
        ),
        vals=dragex_backend.MaterialInfoVals(
            primitive_depth_z=0,
            primitive_depth_dz=0,
            fog_color=(1, 1, 1, 1),
            blend_color=(1, 1, 1, 1),
            min_level=0,
            prim_lod_frac=0,
            primitive_color=(1, 1, 1, 1),
            environment_color=(1, 1, 1, 1),
        ),
        geometry_mode=dragex_backend.MaterialInfoGeometryMode(
            zbuffer=True,
            lighting=False,
            vertex_colors=False,
            cull_front=False,
            cull_back=True,
            fog=False,
            uv_gen_spherical=False,
            uv_gen_linear=False,
            shade_smooth=False,
        ),
    )

    mesh_infos_list: list[dragex_backend.MeshInfo] = []

    for submesh_info in submeshes:
        mesh_info = dragex_backend.create_MeshInfo(
            (
                c_identifiers_prefix
                + util.make_c_identifier(obj.name)
                + submesh_info.c_identifiers_suffix
            ),
            buf_vertices_co,
            buf_triangles_loops_Nx3[submesh_info.tris_mask, :].ravel(),
            buf_triangles_material_index[submesh_info.tris_mask],
            buf_loops_vertex_index,
            buf_loops_normal,
            buf_corners_color,
            buf_points_color,
            buf_loops_uv,
            buf_corners_material_index,
            material_infos,
            default_material_info,
            corner_material_infos,
            default_corner_material_info,
        )
        mesh_infos_list.append(mesh_info)
    return mesh_infos_list
