Display adapters for framework runtime modules (Next.js here). Alias them in
integration.config.mjs only when the mounted components import them. They are static:
the film never navigates, optimises images or lazy-loads panels. Write the equivalent for
other frameworks (router hooks, i18n loaders, IPC bridges) as the components require.
