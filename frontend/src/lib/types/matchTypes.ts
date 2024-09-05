/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface Match {
  white: string;
  black: string;
  moves: string[];
  winner: boolean;
  result: number;
  time_started?: string;
}
export interface MatchListingRequestForm {
  public: boolean;
  colour: boolean | null;
  time: number;
  bonus: number | null;
}
