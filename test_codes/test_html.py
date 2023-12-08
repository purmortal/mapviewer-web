# from jinja2 import Template
#
# # Load the HTML template from the file
# with open('template.html') as template_file:
#     template = Template(template_file.read())
#
# # Define the dynamic data
# data = {
#     'title': 'Dynamic HTML',
#     'heading': 'Hello, World!',
#     'content': 'This content is dynamically generated with Python.'
# }
#
# # Render the template with the dynamic data
# rendered_html = template.render(data)
#
# # Save the rendered HTML to a file or use it as needed
# with open('output.html', 'w') as output_file:
#     output_file.write(rendered_html)

import os

working_dir = os.getcwd()

# List of HTML files you want to include
html_files = os.listdir(working_dir)
html_files = [x for x in html_files if 'galinspec' in x]


# Create the main HTML file content
main_html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Main HTML Page</title>
</head>
<body>
    <h1>Main Page</h1>
    
    <!-- Buttons to switch between HTML files (positioned below the h1 title) -->
    <div id="buttons">
        {}
    </div>
    
    <div id="content">
        <!-- Initial content -->
        <iframe id="iframe" src="{}" width="100%" height="600"></iframe>
    </div>

    <script>
        function changeContent(file) {{
            // Change the source of the iframe to the selected HTML file
            document.getElementById("iframe").src = file;
        }}
    </script>
</body>
</html>
""".format(
    ' '.join([f'<button onclick="changeContent(\'{file}\')">{file.replace(".html", "").replace("galinspec_", "")}</button>' for file in html_files]),
    html_files[0]
)

# Save the main HTML content to a file
with open("main_old.html", "w") as main_html_file:
    main_html_file.write(main_html_content)
