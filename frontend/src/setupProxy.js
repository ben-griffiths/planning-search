const { createProxyMiddleware } = require("http-proxy-middleware");

module.exports = function (app) {
  app.use(
    "/api",
    createProxyMiddleware({
      target:
        "https://tln7h57trpgrz7wdidyewispzq0tlqwy.lambda-url.eu-west-2.on.aws",
      changeOrigin: true,
      secure: false,
    })
  );
  app.use(
    "/maps",
    createProxyMiddleware({
      target:
        "https://tln7h57trpgrz7wdidyewispzq0tlqwy.lambda-url.eu-west-2.on.aws/maps",
      changeOrigin: true,
      secure: false,
    })
  );
};
