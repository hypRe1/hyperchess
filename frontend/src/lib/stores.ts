import { localStorageStore } from "@skeletonlabs/skeleton";
import type { Writable } from "svelte/store";

export const tokenStore: Writable<string> = localStorageStore('token', '')