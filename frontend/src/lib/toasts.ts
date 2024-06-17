import { type ToastSettings } from "@skeletonlabs/skeleton";

export const loginSuccess: ToastSettings = {
    message: "Logged in successfully!",
    background: "variant-filled-success",
    timeout: 2000,
};

export const alreadyLoggedIn: ToastSettings = {
    message: "You are already logged in!",
    background: "variant-filled-error",
    timeout: 2000,
};

export const tooManyRequests: ToastSettings = {
    message: "You are sending too many requests!",
    background: "variant-filled-error",
    timeout: 2000,
};

export const loginFailed: ToastSettings = {
    message: "Failed to login!",
    background: "variant-filled-error",
    timeout: 2000,
};

export const registerSuccess: ToastSettings = {
    message: "Created an account successfully!",
    background: "variant-filled-success",
    timeout: 3000,
};

export const registerCancelled: ToastSettings = {
    message: "Cancelled account creation!",
    background: "variant-filled-success",
    timeout: 3000,
};

export const differentPasswords: ToastSettings = {
    message: "Passwords do not match",
    background: "variant-filled-error",
    timeout: 3000,
};

export const insecurePassword: ToastSettings = {
    message: "Passwords is not strong enough",
    background: "variant-filled-error",
    timeout: 3000,
};

export const registerFailed: ToastSettings = {
    message: "Failed to sign up!",
    background: "variant-filled-error",
    timeout: 3000,
};

export const emptyFields: ToastSettings = {
    message: "Empty fields",
    background: "variant-filled-error",
    timeout: 3000,
}