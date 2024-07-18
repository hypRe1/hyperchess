/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type Themes =
  | "skeleton"
  | "wintry"
  | "modern"
  | "rocket"
  | "seafoam"
  | "vintage"
  | "sahara"
  | "hamlindigo"
  | "gold-nouveau"
  | "crimson"
  | "hypertheme";
export type Boards =
  | "canvas2"
  | "metal"
  | "horsey"
  | "blue3"
  | "blue2"
  | "wood"
  | "green-plastic"
  | "pink-pyramid"
  | "blue-marble"
  | "wood4"
  | "olive"
  | "purple-diag"
  | "maple"
  | "wood3"
  | "wood2"
  | "leather"
  | "maple2"
  | "grey"
  | "ncf-board"
  | "marble"
  | "blue"
  | "newspaper"
  | "purple"
  | "brown"
  | "ic"
  | "green";
export type Pieces =
  | "kosal"
  | "riohacha"
  | "governor"
  | "neo"
  | "horsey"
  | "cardinal"
  | "kiwen-suwi"
  | "maestro"
  | "disguised"
  | "fresca"
  | "gioco"
  | "caliente"
  | "icpieces"
  | "letter"
  | "shapes"
  | "reillycraig"
  | "prmi"
  | "anarcandy"
  | "staunty"
  | "dubrovny"
  | "tatiana"
  | "pixel"
  | "merida"
  | "mpchess"
  | "chessnut"
  | "celtic"
  | "leipzig"
  | "libra"
  | "chess7"
  | "pirouetti"
  | "spatial"
  | "skulls"
  | "alpha"
  | "eyes"
  | "california"
  | "freak"
  | "fantasy"
  | "cburnett"
  | "cooke"
  | "companion";

export interface UserAppearance {
  theme: Themes;
  board: Boards;
  piece: Pieces;
  dark: boolean;
}
