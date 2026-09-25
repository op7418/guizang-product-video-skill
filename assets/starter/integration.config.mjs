// Product integration for the video project (never edit the product repo).
// repoDir defaults to plan.repo. Point '@' (or the repo's own alias) at its source; map
// framework runtime modules (next/image, next/navigation, …) to display adapters in src/adapters/.
export default {
  repoDir: null,
  // aliases: {'@': '/abs/repo/src', 'next/image': new URL('./src/adapters/next-image.jsx', import.meta.url).pathname},
  aliases: {},
  // Bare imports to leave external must resolve from the video project at runtime.
  external: [],
  loaders: {},
  define: {},
};
