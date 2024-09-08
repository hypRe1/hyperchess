/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface MatchListingRequestForm {
  public: boolean;
  colour: boolean | null;
  time: number;
  bonus: number | null;
}
export interface MatchRequest {
  white: string;
  black: string;
  moves: string[];
  winner: boolean;
  result: number;
  time: number;
  bonus: number;
  time_started?: string;
}
export interface MatchResponse {
  white: string;
  black: string;
  moves: string[];
  winner: boolean;
  result: number;
  time: number;
  bonus: number;
  time_started?: string;
  id: number;
  hyperchess: boolean;
}
export interface MatchesResponse {
  id: number;
  white: string;
  black: string;
  n_moves: number;
  fen: string;
  winner: boolean;
  result: number;
  time: number;
  bonus: number;
  time_started?: string;
  hyperchess: boolean;
}
