// Hi from write_mesh_info_to_f3d_c
Gfx mesh_mymaterial_mat_dl[] = {
    gsDPPipelineMode(G_PM_NPRIMITIVE),
    gsDPSetCycleType(G_CYC_1CYCLE),
    gsDPSetTexturePersp(G_TP_NONE),
    gsDPSetTextureDetail(G_TD_CLAMP),
    gsDPSetTextureLOD(G_TL_TILE),
    gsDPSetTextureLUT(G_TT_NONE),
    gsDPSetTextureFilter(G_TF_POINT),
    gsDPSetTextureConvert(G_TC_CONV),
    gsDPSetCombineKey(G_CK_NONE),
    gsDPSetColorDither(G_CD_MAGICSQ),
    gsDPSetAlphaDither(G_AD_DISABLE),
    gsDPSetRenderMode(CVG_DST_CLAMP | ZMODE_OPA | GBL_c1(G_BL_CLR_IN, G_BL_0, G_BL_CLR_IN, G_BL_1), GBL_c2(G_BL_CLR_IN, G_BL_0, G_BL_CLR_IN, G_BL_1)),
    gsDPSetDepthSource(G_ZS_PIXEL),
    gsDPSetAlphaCompare(G_AC_NONE),
    gsDPSetCombineLERP(0, 0, 0, TEXEL0, 0, 0, 0, 1, 0, 0, 0, TEXEL0, 0, 0, 0, 1),
    gsSPClearGeometryMode(G_LIGHTING),
    gsSPEndDisplayList(),
};
Vtx mesh_mymaterial_mesh_vtx[] = {
    {{ { 0, 0, 0 }, 0, { 0, 32 }, { 0x0, 0xFF, 0x0, 0 } }},
    {{ { 0, 0, 0 }, 0, { 0, 32 }, { 0x0, 0x0, 0x0, 0 } }},
    {{ { 0, 0, 0 }, 0, { 0, 32 }, { 0x0, 0x0, 0x0, 0 } }},
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
