/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface MatchModel {
  code: string;
  public: boolean;
  white_player: string | null;
  black_player: string | null;
  time: number;
  bonus: number;
  connected: string[];
  moves: string[];
  game_over?: boolean;
  result?: string | null;
  time_created?: number;
  time_ended?: number | null;
}
