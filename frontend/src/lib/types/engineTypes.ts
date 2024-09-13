/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface BestMoveRequest {
  fen: string;
  engine: string;
  depth?: number;
}
export interface ReviewMatchRequest {
  engine: string;
  match_id: number;
  depth?: number;
}
export interface ReviewMatchResponse {
  time: string;
}
