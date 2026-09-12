"""Serves the interactive API documentation.

"""

from flask import Blueprint, render_template_string, url_for

docs_bp = Blueprint("docs", __name__)

SWAGGER_UI_VERSION = "5.17.14"

DOCS_PAGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Tamatem Commerce API</title>
    <link
      rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/{{ version }}/swagger-ui.min.css"
    />
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script
      src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/{{ version }}/swagger-ui-bundle.min.js"
      crossorigin
    ></script>
    <script>
      window.onload = function () {
        SwaggerUIBundle({
          url: "{{ spec_url }}",
          dom_id: "#swagger-ui",
          // Send requests to the origin serving this page, so "Try it out"
          // works without editing the server list in the spec.
          servers: [{ url: window.location.origin }],
          tryItOutEnabled: true,
          // Keeps the pasted token across page reloads while exploring.
          persistAuthorization: true,
        });
      };
    </script>
  </body>
</html>
"""


@docs_bp.get("/docs")
def api_docs():
    """Render the Swagger UI page for the OpenAPI specification."""
    return render_template_string(
        DOCS_PAGE,
        version=SWAGGER_UI_VERSION,
        spec_url=url_for("static", filename="openapi.json"),
    )
