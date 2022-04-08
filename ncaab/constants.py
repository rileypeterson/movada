import os

BOVADA_COLUMNS = [
    "scrape_datetime",
    "game_datetime",
    "top_team",
    "top_final",
    "bottom_final",
    "bottom_team",
    "top_spread",
    "top_spread_odds",
    "top_ml_odds",
    "top_total",
    "top_total_odds",
    "bottom_spread",
    "bottom_spread_odds",
    "bottom_ml_odds",
    "bottom_total",
    "bottom_total_odds",
]
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
IS_PROD = True
if ROOT_DIR.startswith("/Users/riley"):
    IS_PROD = False
OUTLAWED_TEAMS = {
    "Chaminade",
    "AlaskaAnchorage",
    "ConcordiaSt.Paul",
    "TXPanAmerican",
    "Texas-PanAmerican",
}


SRCBB_COLUMNS = [
    "top_s_G_1",
    "top_s_Date_1",
    "top_s_H/A_1",
    "top_s_Op_1",
    "top_s_W/L_1",
    "top_s_Tm_1",
    "top_s_Opp_1",
    "top_s_FG_1",
    "top_s_FGA_1",
    "top_s_FG%_1",
    "top_s_3P_1",
    "top_s_3PA_1",
    "top_s_3P%_1",
    "top_s_FT_1",
    "top_s_FTA_1",
    "top_s_FT%_1",
    "top_s_ORB_1",
    "top_s_TRB_1",
    "top_s_AST_1",
    "top_s_STL_1",
    "top_s_BLK_1",
    "top_s_TOV_1",
    "top_s_PF_1",
    "top_s_Opp_FG_1",
    "top_s_Opp_FGA_1",
    "top_s_Opp_FG%_1",
    "top_s_Opp_3P_1",
    "top_s_Opp_3PA_1",
    "top_s_Opp_3P%_1",
    "top_s_Opp_FT_1",
    "top_s_Opp_FTA_1",
    "top_s_Opp_FT%_1",
    "top_s_Opp_ORB_1",
    "top_s_Opp_TRB_1",
    "top_s_Opp_AST_1",
    "top_s_Opp_STL_1",
    "top_s_Opp_BLK_1",
    "top_s_Opp_TOV_1",
    "top_s_Opp_PF_1",
    "top_s_G_2",
    "top_s_Date_2",
    "top_s_H/A_2",
    "top_s_Op_2",
    "top_s_W/L_2",
    "top_s_Tm_2",
    "top_s_Opp_2",
    "top_s_FG_2",
    "top_s_FGA_2",
    "top_s_FG%_2",
    "top_s_3P_2",
    "top_s_3PA_2",
    "top_s_3P%_2",
    "top_s_FT_2",
    "top_s_FTA_2",
    "top_s_FT%_2",
    "top_s_ORB_2",
    "top_s_TRB_2",
    "top_s_AST_2",
    "top_s_STL_2",
    "top_s_BLK_2",
    "top_s_TOV_2",
    "top_s_PF_2",
    "top_s_Opp_FG_2",
    "top_s_Opp_FGA_2",
    "top_s_Opp_FG%_2",
    "top_s_Opp_3P_2",
    "top_s_Opp_3PA_2",
    "top_s_Opp_3P%_2",
    "top_s_Opp_FT_2",
    "top_s_Opp_FTA_2",
    "top_s_Opp_FT%_2",
    "top_s_Opp_ORB_2",
    "top_s_Opp_TRB_2",
    "top_s_Opp_AST_2",
    "top_s_Opp_STL_2",
    "top_s_Opp_BLK_2",
    "top_s_Opp_TOV_2",
    "top_s_Opp_PF_2",
    "top_s_G_3",
    "top_s_Date_3",
    "top_s_H/A_3",
    "top_s_Op_3",
    "top_s_W/L_3",
    "top_s_Tm_3",
    "top_s_Opp_3",
    "top_s_FG_3",
    "top_s_FGA_3",
    "top_s_FG%_3",
    "top_s_3P_3",
    "top_s_3PA_3",
    "top_s_3P%_3",
    "top_s_FT_3",
    "top_s_FTA_3",
    "top_s_FT%_3",
    "top_s_ORB_3",
    "top_s_TRB_3",
    "top_s_AST_3",
    "top_s_STL_3",
    "top_s_BLK_3",
    "top_s_TOV_3",
    "top_s_PF_3",
    "top_s_Opp_FG_3",
    "top_s_Opp_FGA_3",
    "top_s_Opp_FG%_3",
    "top_s_Opp_3P_3",
    "top_s_Opp_3PA_3",
    "top_s_Opp_3P%_3",
    "top_s_Opp_FT_3",
    "top_s_Opp_FTA_3",
    "top_s_Opp_FT%_3",
    "top_s_Opp_ORB_3",
    "top_s_Opp_TRB_3",
    "top_s_Opp_AST_3",
    "top_s_Opp_STL_3",
    "top_s_Opp_BLK_3",
    "top_s_Opp_TOV_3",
    "top_s_Opp_PF_3",
    "top_s_G_4",
    "top_s_Date_4",
    "top_s_H/A_4",
    "top_s_Op_4",
    "top_s_W/L_4",
    "top_s_Tm_4",
    "top_s_Opp_4",
    "top_s_FG_4",
    "top_s_FGA_4",
    "top_s_FG%_4",
    "top_s_3P_4",
    "top_s_3PA_4",
    "top_s_3P%_4",
    "top_s_FT_4",
    "top_s_FTA_4",
    "top_s_FT%_4",
    "top_s_ORB_4",
    "top_s_TRB_4",
    "top_s_AST_4",
    "top_s_STL_4",
    "top_s_BLK_4",
    "top_s_TOV_4",
    "top_s_PF_4",
    "top_s_Opp_FG_4",
    "top_s_Opp_FGA_4",
    "top_s_Opp_FG%_4",
    "top_s_Opp_3P_4",
    "top_s_Opp_3PA_4",
    "top_s_Opp_3P%_4",
    "top_s_Opp_FT_4",
    "top_s_Opp_FTA_4",
    "top_s_Opp_FT%_4",
    "top_s_Opp_ORB_4",
    "top_s_Opp_TRB_4",
    "top_s_Opp_AST_4",
    "top_s_Opp_STL_4",
    "top_s_Opp_BLK_4",
    "top_s_Opp_TOV_4",
    "top_s_Opp_PF_4",
    "top_s_G_5",
    "top_s_Date_5",
    "top_s_H/A_5",
    "top_s_Op_5",
    "top_s_W/L_5",
    "top_s_Tm_5",
    "top_s_Opp_5",
    "top_s_FG_5",
    "top_s_FGA_5",
    "top_s_FG%_5",
    "top_s_3P_5",
    "top_s_3PA_5",
    "top_s_3P%_5",
    "top_s_FT_5",
    "top_s_FTA_5",
    "top_s_FT%_5",
    "top_s_ORB_5",
    "top_s_TRB_5",
    "top_s_AST_5",
    "top_s_STL_5",
    "top_s_BLK_5",
    "top_s_TOV_5",
    "top_s_PF_5",
    "top_s_Opp_FG_5",
    "top_s_Opp_FGA_5",
    "top_s_Opp_FG%_5",
    "top_s_Opp_3P_5",
    "top_s_Opp_3PA_5",
    "top_s_Opp_3P%_5",
    "top_s_Opp_FT_5",
    "top_s_Opp_FTA_5",
    "top_s_Opp_FT%_5",
    "top_s_Opp_ORB_5",
    "top_s_Opp_TRB_5",
    "top_s_Opp_AST_5",
    "top_s_Opp_STL_5",
    "top_s_Opp_BLK_5",
    "top_s_Opp_TOV_5",
    "top_s_Opp_PF_5",
    "top_s_G_6",
    "top_s_Date_6",
    "top_s_H/A_6",
    "top_s_Op_6",
    "top_s_W/L_6",
    "top_s_Tm_6",
    "top_s_Opp_6",
    "top_s_FG_6",
    "top_s_FGA_6",
    "top_s_FG%_6",
    "top_s_3P_6",
    "top_s_3PA_6",
    "top_s_3P%_6",
    "top_s_FT_6",
    "top_s_FTA_6",
    "top_s_FT%_6",
    "top_s_ORB_6",
    "top_s_TRB_6",
    "top_s_AST_6",
    "top_s_STL_6",
    "top_s_BLK_6",
    "top_s_TOV_6",
    "top_s_PF_6",
    "top_s_Opp_FG_6",
    "top_s_Opp_FGA_6",
    "top_s_Opp_FG%_6",
    "top_s_Opp_3P_6",
    "top_s_Opp_3PA_6",
    "top_s_Opp_3P%_6",
    "top_s_Opp_FT_6",
    "top_s_Opp_FTA_6",
    "top_s_Opp_FT%_6",
    "top_s_Opp_ORB_6",
    "top_s_Opp_TRB_6",
    "top_s_Opp_AST_6",
    "top_s_Opp_STL_6",
    "top_s_Opp_BLK_6",
    "top_s_Opp_TOV_6",
    "top_s_Opp_PF_6",
    "top_s_G_7",
    "top_s_Date_7",
    "top_s_H/A_7",
    "top_s_Op_7",
    "top_s_W/L_7",
    "top_s_Tm_7",
    "top_s_Opp_7",
    "top_s_FG_7",
    "top_s_FGA_7",
    "top_s_FG%_7",
    "top_s_3P_7",
    "top_s_3PA_7",
    "top_s_3P%_7",
    "top_s_FT_7",
    "top_s_FTA_7",
    "top_s_FT%_7",
    "top_s_ORB_7",
    "top_s_TRB_7",
    "top_s_AST_7",
    "top_s_STL_7",
    "top_s_BLK_7",
    "top_s_TOV_7",
    "top_s_PF_7",
    "top_s_Opp_FG_7",
    "top_s_Opp_FGA_7",
    "top_s_Opp_FG%_7",
    "top_s_Opp_3P_7",
    "top_s_Opp_3PA_7",
    "top_s_Opp_3P%_7",
    "top_s_Opp_FT_7",
    "top_s_Opp_FTA_7",
    "top_s_Opp_FT%_7",
    "top_s_Opp_ORB_7",
    "top_s_Opp_TRB_7",
    "top_s_Opp_AST_7",
    "top_s_Opp_STL_7",
    "top_s_Opp_BLK_7",
    "top_s_Opp_TOV_7",
    "top_s_Opp_PF_7",
    "bottom_s_G_1",
    "bottom_s_Date_1",
    "bottom_s_H/A_1",
    "bottom_s_Op_1",
    "bottom_s_W/L_1",
    "bottom_s_Tm_1",
    "bottom_s_Opp_1",
    "bottom_s_FG_1",
    "bottom_s_FGA_1",
    "bottom_s_FG%_1",
    "bottom_s_3P_1",
    "bottom_s_3PA_1",
    "bottom_s_3P%_1",
    "bottom_s_FT_1",
    "bottom_s_FTA_1",
    "bottom_s_FT%_1",
    "bottom_s_ORB_1",
    "bottom_s_TRB_1",
    "bottom_s_AST_1",
    "bottom_s_STL_1",
    "bottom_s_BLK_1",
    "bottom_s_TOV_1",
    "bottom_s_PF_1",
    "bottom_s_Opp_FG_1",
    "bottom_s_Opp_FGA_1",
    "bottom_s_Opp_FG%_1",
    "bottom_s_Opp_3P_1",
    "bottom_s_Opp_3PA_1",
    "bottom_s_Opp_3P%_1",
    "bottom_s_Opp_FT_1",
    "bottom_s_Opp_FTA_1",
    "bottom_s_Opp_FT%_1",
    "bottom_s_Opp_ORB_1",
    "bottom_s_Opp_TRB_1",
    "bottom_s_Opp_AST_1",
    "bottom_s_Opp_STL_1",
    "bottom_s_Opp_BLK_1",
    "bottom_s_Opp_TOV_1",
    "bottom_s_Opp_PF_1",
    "bottom_s_G_2",
    "bottom_s_Date_2",
    "bottom_s_H/A_2",
    "bottom_s_Op_2",
    "bottom_s_W/L_2",
    "bottom_s_Tm_2",
    "bottom_s_Opp_2",
    "bottom_s_FG_2",
    "bottom_s_FGA_2",
    "bottom_s_FG%_2",
    "bottom_s_3P_2",
    "bottom_s_3PA_2",
    "bottom_s_3P%_2",
    "bottom_s_FT_2",
    "bottom_s_FTA_2",
    "bottom_s_FT%_2",
    "bottom_s_ORB_2",
    "bottom_s_TRB_2",
    "bottom_s_AST_2",
    "bottom_s_STL_2",
    "bottom_s_BLK_2",
    "bottom_s_TOV_2",
    "bottom_s_PF_2",
    "bottom_s_Opp_FG_2",
    "bottom_s_Opp_FGA_2",
    "bottom_s_Opp_FG%_2",
    "bottom_s_Opp_3P_2",
    "bottom_s_Opp_3PA_2",
    "bottom_s_Opp_3P%_2",
    "bottom_s_Opp_FT_2",
    "bottom_s_Opp_FTA_2",
    "bottom_s_Opp_FT%_2",
    "bottom_s_Opp_ORB_2",
    "bottom_s_Opp_TRB_2",
    "bottom_s_Opp_AST_2",
    "bottom_s_Opp_STL_2",
    "bottom_s_Opp_BLK_2",
    "bottom_s_Opp_TOV_2",
    "bottom_s_Opp_PF_2",
    "bottom_s_G_3",
    "bottom_s_Date_3",
    "bottom_s_H/A_3",
    "bottom_s_Op_3",
    "bottom_s_W/L_3",
    "bottom_s_Tm_3",
    "bottom_s_Opp_3",
    "bottom_s_FG_3",
    "bottom_s_FGA_3",
    "bottom_s_FG%_3",
    "bottom_s_3P_3",
    "bottom_s_3PA_3",
    "bottom_s_3P%_3",
    "bottom_s_FT_3",
    "bottom_s_FTA_3",
    "bottom_s_FT%_3",
    "bottom_s_ORB_3",
    "bottom_s_TRB_3",
    "bottom_s_AST_3",
    "bottom_s_STL_3",
    "bottom_s_BLK_3",
    "bottom_s_TOV_3",
    "bottom_s_PF_3",
    "bottom_s_Opp_FG_3",
    "bottom_s_Opp_FGA_3",
    "bottom_s_Opp_FG%_3",
    "bottom_s_Opp_3P_3",
    "bottom_s_Opp_3PA_3",
    "bottom_s_Opp_3P%_3",
    "bottom_s_Opp_FT_3",
    "bottom_s_Opp_FTA_3",
    "bottom_s_Opp_FT%_3",
    "bottom_s_Opp_ORB_3",
    "bottom_s_Opp_TRB_3",
    "bottom_s_Opp_AST_3",
    "bottom_s_Opp_STL_3",
    "bottom_s_Opp_BLK_3",
    "bottom_s_Opp_TOV_3",
    "bottom_s_Opp_PF_3",
    "bottom_s_G_4",
    "bottom_s_Date_4",
    "bottom_s_H/A_4",
    "bottom_s_Op_4",
    "bottom_s_W/L_4",
    "bottom_s_Tm_4",
    "bottom_s_Opp_4",
    "bottom_s_FG_4",
    "bottom_s_FGA_4",
    "bottom_s_FG%_4",
    "bottom_s_3P_4",
    "bottom_s_3PA_4",
    "bottom_s_3P%_4",
    "bottom_s_FT_4",
    "bottom_s_FTA_4",
    "bottom_s_FT%_4",
    "bottom_s_ORB_4",
    "bottom_s_TRB_4",
    "bottom_s_AST_4",
    "bottom_s_STL_4",
    "bottom_s_BLK_4",
    "bottom_s_TOV_4",
    "bottom_s_PF_4",
    "bottom_s_Opp_FG_4",
    "bottom_s_Opp_FGA_4",
    "bottom_s_Opp_FG%_4",
    "bottom_s_Opp_3P_4",
    "bottom_s_Opp_3PA_4",
    "bottom_s_Opp_3P%_4",
    "bottom_s_Opp_FT_4",
    "bottom_s_Opp_FTA_4",
    "bottom_s_Opp_FT%_4",
    "bottom_s_Opp_ORB_4",
    "bottom_s_Opp_TRB_4",
    "bottom_s_Opp_AST_4",
    "bottom_s_Opp_STL_4",
    "bottom_s_Opp_BLK_4",
    "bottom_s_Opp_TOV_4",
    "bottom_s_Opp_PF_4",
    "bottom_s_G_5",
    "bottom_s_Date_5",
    "bottom_s_H/A_5",
    "bottom_s_Op_5",
    "bottom_s_W/L_5",
    "bottom_s_Tm_5",
    "bottom_s_Opp_5",
    "bottom_s_FG_5",
    "bottom_s_FGA_5",
    "bottom_s_FG%_5",
    "bottom_s_3P_5",
    "bottom_s_3PA_5",
    "bottom_s_3P%_5",
    "bottom_s_FT_5",
    "bottom_s_FTA_5",
    "bottom_s_FT%_5",
    "bottom_s_ORB_5",
    "bottom_s_TRB_5",
    "bottom_s_AST_5",
    "bottom_s_STL_5",
    "bottom_s_BLK_5",
    "bottom_s_TOV_5",
    "bottom_s_PF_5",
    "bottom_s_Opp_FG_5",
    "bottom_s_Opp_FGA_5",
    "bottom_s_Opp_FG%_5",
    "bottom_s_Opp_3P_5",
    "bottom_s_Opp_3PA_5",
    "bottom_s_Opp_3P%_5",
    "bottom_s_Opp_FT_5",
    "bottom_s_Opp_FTA_5",
    "bottom_s_Opp_FT%_5",
    "bottom_s_Opp_ORB_5",
    "bottom_s_Opp_TRB_5",
    "bottom_s_Opp_AST_5",
    "bottom_s_Opp_STL_5",
    "bottom_s_Opp_BLK_5",
    "bottom_s_Opp_TOV_5",
    "bottom_s_Opp_PF_5",
    "bottom_s_G_6",
    "bottom_s_Date_6",
    "bottom_s_H/A_6",
    "bottom_s_Op_6",
    "bottom_s_W/L_6",
    "bottom_s_Tm_6",
    "bottom_s_Opp_6",
    "bottom_s_FG_6",
    "bottom_s_FGA_6",
    "bottom_s_FG%_6",
    "bottom_s_3P_6",
    "bottom_s_3PA_6",
    "bottom_s_3P%_6",
    "bottom_s_FT_6",
    "bottom_s_FTA_6",
    "bottom_s_FT%_6",
    "bottom_s_ORB_6",
    "bottom_s_TRB_6",
    "bottom_s_AST_6",
    "bottom_s_STL_6",
    "bottom_s_BLK_6",
    "bottom_s_TOV_6",
    "bottom_s_PF_6",
    "bottom_s_Opp_FG_6",
    "bottom_s_Opp_FGA_6",
    "bottom_s_Opp_FG%_6",
    "bottom_s_Opp_3P_6",
    "bottom_s_Opp_3PA_6",
    "bottom_s_Opp_3P%_6",
    "bottom_s_Opp_FT_6",
    "bottom_s_Opp_FTA_6",
    "bottom_s_Opp_FT%_6",
    "bottom_s_Opp_ORB_6",
    "bottom_s_Opp_TRB_6",
    "bottom_s_Opp_AST_6",
    "bottom_s_Opp_STL_6",
    "bottom_s_Opp_BLK_6",
    "bottom_s_Opp_TOV_6",
    "bottom_s_Opp_PF_6",
    "bottom_s_G_7",
    "bottom_s_Date_7",
    "bottom_s_H/A_7",
    "bottom_s_Op_7",
    "bottom_s_W/L_7",
    "bottom_s_Tm_7",
    "bottom_s_Opp_7",
    "bottom_s_FG_7",
    "bottom_s_FGA_7",
    "bottom_s_FG%_7",
    "bottom_s_3P_7",
    "bottom_s_3PA_7",
    "bottom_s_3P%_7",
    "bottom_s_FT_7",
    "bottom_s_FTA_7",
    "bottom_s_FT%_7",
    "bottom_s_ORB_7",
    "bottom_s_TRB_7",
    "bottom_s_AST_7",
    "bottom_s_STL_7",
    "bottom_s_BLK_7",
    "bottom_s_TOV_7",
    "bottom_s_PF_7",
    "bottom_s_Opp_FG_7",
    "bottom_s_Opp_FGA_7",
    "bottom_s_Opp_FG%_7",
    "bottom_s_Opp_3P_7",
    "bottom_s_Opp_3PA_7",
    "bottom_s_Opp_3P%_7",
    "bottom_s_Opp_FT_7",
    "bottom_s_Opp_FTA_7",
    "bottom_s_Opp_FT%_7",
    "bottom_s_Opp_ORB_7",
    "bottom_s_Opp_TRB_7",
    "bottom_s_Opp_AST_7",
    "bottom_s_Opp_STL_7",
    "bottom_s_Opp_BLK_7",
    "bottom_s_Opp_TOV_7",
    "bottom_s_Opp_PF_7",
]
