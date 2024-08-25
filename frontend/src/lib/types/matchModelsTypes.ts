/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type Result = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7;

export interface MatchModel {
  code: string;
  public: boolean;
  white_player: string;
  black_player: string;
  time: number;
  bonus: number;
  connected: string[];
  moves: string[];
  game_over?: boolean;
  result?: Result & number;
  winner?: boolean | null;
  time_created?: number;
  timings?: number[];
}
