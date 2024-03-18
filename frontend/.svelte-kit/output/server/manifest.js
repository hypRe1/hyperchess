export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set(["favicon.png"]),
	mimeTypes: {".png":"image/png"},
	_: {
		client: {"start":"_app/immutable/entry/start.CzxEpE7b.js","app":"_app/immutable/entry/app.CwXTssYV.js","imports":["_app/immutable/entry/start.CzxEpE7b.js","_app/immutable/chunks/entry.Dk1mJV26.js","_app/immutable/chunks/scheduler.Buelg_V3.js","_app/immutable/chunks/index.CxtP2-do.js","_app/immutable/entry/app.CwXTssYV.js","_app/immutable/chunks/scheduler.Buelg_V3.js","_app/immutable/chunks/index.21b-Zw5m.js"],"stylesheets":[],"fonts":[],"uses_env_dynamic_public":false},
		nodes: [
			__memo(() => import('./nodes/0.js')),
			__memo(() => import('./nodes/1.js')),
			__memo(() => import('./nodes/2.js'))
		],
		routes: [
			{
				id: "/",
				pattern: /^\/$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 2 },
				endpoint: null
			}
		],
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();
