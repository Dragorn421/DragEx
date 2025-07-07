// Hi from write_mesh_info_to_f3d_c
Gfx mesh_mymaterial_mat_dl[] = {
    gsSPClearGeometryMode(G_LIGHTING),
    gsSPEndDisplayList(),
};
Vtx mesh_mymaterial_mesh_vtx[] = {
    {{ { 0, 0, 0 }, 0, { 0, 0 }, { 0x0, 0xFF, 0x0, 0 } }},
    {{ { 0, 0, 0 }, 0, { 0, 0 }, { 0x0, 0x0, 0x0, 0 } }},
    {{ { 0, 0, 0 }, 0, { 0, 0 }, { 0x0, 0x0, 0x0, 0 } }},
};
Gfx mesh_mymaterial_mesh_dl[] = {
    gsSPVertex(&mesh_mymaterial_mesh_vtx[0], 3, 0),
    gsSP1Triangle(0, 1, 2, 0),
    gsSPEndDisplayList(),
};
Gfx mesh_dl[] = {
    gsSPDisplayList(mesh_mymaterial_mat_dl),
    gsSPDisplayList(mesh_mymaterial_mesh_dl),
    gsSPEndDisplayList(),
};
