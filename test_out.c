// Hi from write_mesh_info_to_f3d_c
Vtx mesh_material_vtx[] = {
    {{ { 0, 0, 0 }, 0, { 0, 0 }, { 0xff, 0xff, 0xff, 255 } }},
    {{ { 0, 0, 0 }, 0, { 0, 0 }, { 0xff, 0xff, 0xff, 255 } }},
    {{ { 0, 0, 0 }, 0, { 0, 0 }, { 0xff, 0xff, 0xff, 255 } }},
};
Gfx mesh_material_dl[] = {
    gsSPVertex(&mesh_material_vtx[0], 3, 0),
    gsSP1Triangle(0, 1, 2, 0),
};
