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
    gsDPLoadMultiBlock(image_c_identifier, 0x000, 0, G_IM_FMT_RGBA, G_IM_SIZ_16b, 32, 32, 0, G_TX_NOMIRROR | G_TX_WRAP, G_TX_NOMIRROR | G_TX_WRAP, 5, 5, 0, 0),
    gsDPLoadMultiBlock(image_c_identifier, 0x000, 1, G_IM_FMT_RGBA, G_IM_SIZ_16b, 32, 32, 0, G_TX_NOMIRROR | G_TX_WRAP, G_TX_NOMIRROR | G_TX_WRAP, 5, 5, 0, 0),
    gsDPLoadMultiBlock(image_c_identifier, 0x000, 2, G_IM_FMT_RGBA, G_IM_SIZ_16b, 32, 32, 0, G_TX_NOMIRROR | G_TX_WRAP, G_TX_NOMIRROR | G_TX_WRAP, 5, 5, 0, 0),
    gsDPLoadMultiBlock(image_c_identifier, 0x000, 3, G_IM_FMT_RGBA, G_IM_SIZ_16b, 32, 32, 0, G_TX_NOMIRROR | G_TX_WRAP, G_TX_NOMIRROR | G_TX_WRAP, 5, 5, 0, 0),
    gsDPLoadMultiBlock(image_c_identifier, 0x000, 4, G_IM_FMT_RGBA, G_IM_SIZ_16b, 32, 32, 0, G_TX_NOMIRROR | G_TX_WRAP, G_TX_NOMIRROR | G_TX_WRAP, 5, 5, 0, 0),
    gsDPLoadMultiBlock(image_c_identifier, 0x000, 5, G_IM_FMT_RGBA, G_IM_SIZ_16b, 32, 32, 0, G_TX_NOMIRROR | G_TX_WRAP, G_TX_NOMIRROR | G_TX_WRAP, 5, 5, 0, 0),
    gsDPLoadMultiBlock(image_c_identifier, 0x000, 6, G_IM_FMT_RGBA, G_IM_SIZ_16b, 32, 32, 0, G_TX_NOMIRROR | G_TX_WRAP, G_TX_NOMIRROR | G_TX_WRAP, 5, 5, 0, 0),
    gsDPLoadMultiBlock(image_c_identifier, 0x000, 7, G_IM_FMT_RGBA, G_IM_SIZ_16b, 32, 32, 0, G_TX_NOMIRROR | G_TX_WRAP, G_TX_NOMIRROR | G_TX_WRAP, 5, 5, 0, 0),
    gsDPSetTile(G_IM_FMT_RGBA, G_IM_SIZ_16b, 0x40, 0x000, 0, 0, G_TX_NOMIRROR | G_TX_WRAP, 5, 0, G_TX_NOMIRROR | G_TX_WRAP, 5, 0),
    gsDPSetTileSize(0, (int)(0.00 * 4), (int)(0.00 * 4), (int)(31.00 * 4), (int)(31.00 * 4)),
    gsDPSetTile(G_IM_FMT_RGBA, G_IM_SIZ_16b, 0x40, 0x000, 1, 0, G_TX_NOMIRROR | G_TX_WRAP, 5, 0, G_TX_NOMIRROR | G_TX_WRAP, 5, 0),
    gsDPSetTileSize(1, (int)(0.00 * 4), (int)(0.00 * 4), (int)(31.00 * 4), (int)(31.00 * 4)),
    gsDPSetTile(G_IM_FMT_RGBA, G_IM_SIZ_16b, 0x40, 0x000, 2, 0, G_TX_NOMIRROR | G_TX_WRAP, 5, 0, G_TX_NOMIRROR | G_TX_WRAP, 5, 0),
    gsDPSetTileSize(2, (int)(0.00 * 4), (int)(0.00 * 4), (int)(31.00 * 4), (int)(31.00 * 4)),
    gsDPSetTile(G_IM_FMT_RGBA, G_IM_SIZ_16b, 0x40, 0x000, 3, 0, G_TX_NOMIRROR | G_TX_WRAP, 5, 0, G_TX_NOMIRROR | G_TX_WRAP, 5, 0),
    gsDPSetTileSize(3, (int)(0.00 * 4), (int)(0.00 * 4), (int)(31.00 * 4), (int)(31.00 * 4)),
    gsDPSetTile(G_IM_FMT_RGBA, G_IM_SIZ_16b, 0x40, 0x000, 4, 0, G_TX_NOMIRROR | G_TX_WRAP, 5, 0, G_TX_NOMIRROR | G_TX_WRAP, 5, 0),
    gsDPSetTileSize(4, (int)(0.00 * 4), (int)(0.00 * 4), (int)(31.00 * 4), (int)(31.00 * 4)),
    gsDPSetTile(G_IM_FMT_RGBA, G_IM_SIZ_16b, 0x40, 0x000, 5, 0, G_TX_NOMIRROR | G_TX_WRAP, 5, 0, G_TX_NOMIRROR | G_TX_WRAP, 5, 0),
    gsDPSetTileSize(5, (int)(0.00 * 4), (int)(0.00 * 4), (int)(31.00 * 4), (int)(31.00 * 4)),
    gsDPSetTile(G_IM_FMT_RGBA, G_IM_SIZ_16b, 0x40, 0x000, 6, 0, G_TX_NOMIRROR | G_TX_WRAP, 5, 0, G_TX_NOMIRROR | G_TX_WRAP, 5, 0),
    gsDPSetTileSize(6, (int)(0.00 * 4), (int)(0.00 * 4), (int)(31.00 * 4), (int)(31.00 * 4)),
    gsDPSetTile(G_IM_FMT_RGBA, G_IM_SIZ_16b, 0x40, 0x000, 7, 0, G_TX_NOMIRROR | G_TX_WRAP, 5, 0, G_TX_NOMIRROR | G_TX_WRAP, 5, 0),
    gsDPSetTileSize(7, (int)(0.00 * 4), (int)(0.00 * 4), (int)(31.00 * 4), (int)(31.00 * 4)),
    gsDPSetCombineLERP(0, 0, 0, TEXEL0, 0, 0, 0, 1, 0, 0, 0, TEXEL0, 0, 0, 0, 1),
    gsDPSetPrimDepth(0, 0),
    gsDPSetFogColor(255, 255, 255, 255),
    gsDPSetBlendColor(255, 255, 255, 255),
    gsDPSetPrimColor(0, 0, 255, 255, 255, 255),
    gsDPSetEnvColor(255, 255, 255, 255),
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
// oot_collision_mesh.write_c
// Hi from write_OoTCollisionMesh_to_c
Vec3s magicVtxList[] = {
    { 0, 0, 0 },
};
CollisionPoly magicPolyList[] = {
/*
  0 = 0.000000 0.000000 0.000000
  1 = 0.000000 0.000000 0.000000
  2 = 0.000000 0.000000 0.000000
  u = 0.000000 0.000000 0.000000
  v = 0.000000 0.000000 0.000000
  n = 0.000000 0.000000 0.000000
  nn = 0.000000
 */
    {
        0,
        {
            COLPOLY_VTX(0, FLAGSA),
            COLPOLY_VTX(0, FLAGSB),
            COLPOLY_VTX(0, 0),
        },
        {
            COLPOLY_SNORMAL(1.000000),
            COLPOLY_SNORMAL(0.000000),
            COLPOLY_SNORMAL(0.000000),
        },
        0,
    },
};
SurfaceType magicSurfaceTypes[] = {
    {
        {
            SURFTYPE0,
            SURFTYPE1,
        },
    },
};
// oot_collision_mesh_joined.write_c
// Hi from write_OoTCollisionMesh_to_c
Vec3s magicJoinedVtxList[] = {
    { 0, 0, 0 },
};
CollisionPoly magicJoinedPolyList[] = {
/*
  0 = 0.000000 0.000000 0.000000
  1 = 0.000000 0.000000 0.000000
  2 = 0.000000 0.000000 0.000000
  u = 0.000000 0.000000 0.000000
  v = 0.000000 0.000000 0.000000
  n = 0.000000 0.000000 0.000000
  nn = 0.000000
 */
    {
        0,
        {
            COLPOLY_VTX(0, FLAGSA),
            COLPOLY_VTX(0, FLAGSB),
            COLPOLY_VTX(0, 0),
        },
        {
            COLPOLY_SNORMAL(1.000000),
            COLPOLY_SNORMAL(0.000000),
            COLPOLY_SNORMAL(0.000000),
        },
        0,
    },
/*
  0 = 0.000000 0.000000 0.000000
  1 = 0.000000 0.000000 0.000000
  2 = 0.000000 0.000000 0.000000
  u = 0.000000 0.000000 0.000000
  v = 0.000000 0.000000 0.000000
  n = 0.000000 0.000000 0.000000
  nn = 0.000000
 */
    {
        1,
        {
            COLPOLY_VTX(0, FLAGSA),
            COLPOLY_VTX(0, FLAGSB),
            COLPOLY_VTX(0, 0),
        },
        {
            COLPOLY_SNORMAL(1.000000),
            COLPOLY_SNORMAL(0.000000),
            COLPOLY_SNORMAL(0.000000),
        },
        0,
    },
};
SurfaceType magicJoinedSurfaceTypes[] = {
    {
        {
            SURFTYPE0,
            SURFTYPE1,
        },
    },
    {
        {
            SURFTYPE0,
            SURFTYPE1,
        },
    },
};
