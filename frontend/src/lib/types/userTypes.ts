/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface Country {
  name: string;
  emoji: string;
  image: string;
  circular_image: string;
}
export interface CountryResponse {
  countries: {
    [k: string]: Country;
  };
}
export interface EditUserRequest {
  avatar: string | null;
  about_me: string | null;
  country: string | null;
}
export interface PersonalUserResponse {
  username: string;
  admin: boolean;
  avatar: string;
  about_me: string | null;
  country: string | null;
  registration_date: string;
  email: string;
}
export interface PublicUserResponse {
  username: string;
  admin: boolean;
  avatar: string;
  about_me: string | null;
  country: string | null;
  registration_date: string;
}
export interface Token {
  access_token: string;
  token_type: string;
}
