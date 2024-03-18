import { c as create_ssr_component } from "../../chunks/ssr.js";
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  return `<div class="flex flex-row min-h-screen justify-center items-center" data-svelte-h="svelte-1uy0fey"><div class="space-y-5"><button class="btn variant-filled-secondary">Hello world!</button></div></div>`;
});
export {
  Page as default
};
