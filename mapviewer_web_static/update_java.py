import os

# Directory containing your HTML files
html_dir = os.getcwd()

# Function to extract unique values of modules, magtypes, and percentiles
def extract_values(files):

    modules = []
    module_magtypes = {}
    percentiles = []

    for filename in files:


        parts = os.path.splitext(filename)[0].split("_")

        if len(parts) >= 4 and parts[0].startswith("galinspec"):


            module, magtype = parts[1], parts[2]
            if len(parts) > 4:
                magtype += "_" + "_".join(parts[3:-1])
            percentile = parts[-1]

            if module not in modules:
                modules.append(module)
            if module not in module_magtypes:
                module_magtypes[module] = []
            if magtype not in module_magtypes[module]:
                module_magtypes[module].append(magtype)
            if percentile not in percentiles:
                percentiles.append(percentile)


    return list(modules), {module: list(magtypes) for module, magtypes in module_magtypes.items()}, list(percentiles)




# Function to generate JavaScript code
def generate_js_code(modules, module_magtypes, percentiles):
    js_code = f"""
    document.addEventListener("DOMContentLoaded", function() {{
        const modules = {str(modules)};
        const moduleMagtypes = {module_magtypes};
        const percentileOptions = {str(percentiles)};

        const buttonsDiv = document.getElementById("buttons");
        const magtypeSelect = document.getElementById("magtypeSelect");
        const percentileSelect = document.getElementById("percentileSelect");

        let selectedModule = modules[0];
        let selectedMagtype = moduleMagtypes[selectedModule][0];
        let selectedPercentile = percentileOptions[0];

        const updateMagtypeOptions = (module) => {{
            const magtypeOptionsHTML = moduleMagtypes[module].map(magtype => `
                <option value="${{magtype}}">${{magtype}}</option>
            `).join("");
            magtypeSelect.innerHTML = magtypeOptionsHTML;
        }};

        const updatePercentileOptions = () => {{
            const percentileOptionsHTML = percentileOptions.map(percentile => `
                <option value="${{percentile}}">${{percentile}}</option>
            `).join("");
            percentileSelect.innerHTML = percentileOptionsHTML;
        }};

        window.changeModule = function(module) {{
            selectedModule = module;
            selectedMagtype = moduleMagtypes[module][0];
            selectedPercentile = percentileOptions[0];
            updateMagtypeOptions(module);
            updatePercentileOptions();
            updateContent(selectedModule, selectedMagtype, selectedPercentile);
        }};

        // Event listener for changes in the "magtype" dropdown
        magtypeSelect.addEventListener("change", function() {{
            selectedMagtype = magtypeSelect.value;
            updateContent(selectedModule, selectedMagtype, selectedPercentile);
        }});

        // Event listener for changes in the "percentile" dropdown
        percentileSelect.addEventListener("change", function() {{
            selectedPercentile = percentileSelect.value;
            updateContent(selectedModule, selectedMagtype, selectedPercentile);
        }});

        function updateContent(module, magtype, percentile) {{
            const src = `galinspec_${{module}}_${{magtype}}_${{percentile}}.html`;
            const iframe = document.getElementById("iframe");
            iframe.src = src;
        }}

        // Populate the buttons for selecting modules
        buttonsDiv.innerHTML = modules.map(module => `
            <button onclick="changeModule('${{module}}')">${{module}}</button>
        `).join("");

        updateMagtypeOptions(selectedModule);
        updatePercentileOptions();
        updateContent(selectedModule, selectedMagtype, selectedPercentile);
    }});
    """

    return js_code


# List HTML files in the directory
html_files = os.listdir(html_dir)

# Sort the list by last modified time
html_files = sorted(html_files, key=lambda x: os.path.getmtime(os.path.join(html_dir, x)))


# Extract unique modules, magtypes, and percentiles
modules, module_magtypes, percentiles = extract_values(html_files)
print(modules)
print(module_magtypes)
print(percentiles)



# Write the JavaScript code to the JavaScript file
with open("main.js", "w") as js_file:
    js_code = generate_js_code(modules, module_magtypes, percentiles)
    js_file.write(js_code)
