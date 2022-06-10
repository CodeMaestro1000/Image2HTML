def generate_output_html(data, filename):
    rendering_data = {
        "rectangle": {
            "input_type": """<input type="text" class="form-control" placeholder="rectangle" aria-label="" aria-describedby="">""", 
            "name":"Text Input"
            },
        
        "square"   : {
            'input_type': """<input class="form-check-input" type="checkbox" value="" id="">""",
            'name':'Checkbox'
            },
        
        "circle"   : {'input_type': """<input class="form-check-input" type="radio" name="" id="">""", 'name':'Radio Button'} 
    }

    form_data = ''

    ext = filename.split(".")[-1]
    if ext != "html":
        filename += ".html"

    for keys in data.keys():
        for element in data[keys]:
            input_data = rendering_data[element['shape']]['input_type']
        form_data += f"""\n
            <div class="row mb-3">
                <label for="" class="form-label">{rendering_data[element['shape']]['name']}</label>
                <div class="col-12">
                    {input_data}
                </div>
            </div>
    """

    html = f"""
        <!doctype html>
        <html lang="en">
        <head>
            <!-- Required meta tags -->
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">

            <!-- Bootstrap CSS -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">

            <title>Image2HTML</title>
        </head>
        <body>
            <div class="container-sm mt-4">
                <form class="d-block mx-auto border p-4">
                    {form_data}
                </form>
            </div>

            <style>
                form {{
                    width: 85%;
                    background-color: #FFFF;
                    border-radius: 15px;
                }}

                body {{
                    background-color: #F5F5F5;
                }}
            </style>
        
            <!-- Option 1: Bootstrap Bundle with Popper -->
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>
        </body>
        </html>

    """

    with open(f"{filename}", "w") as out_file:
        out_file.write(html)
    


"""data = {
    'row0': [{'shape': 'rectangle', 'centroid': (185, 36), 'width': 334, 'height': 34}], 
    'row1': [{'shape': 'square', 'centroid': (58, 98), 'width': 55, 'height': 39}], 
    'row2': [{'shape': 'rectangle', 'centroid': (109, 173), 'width': 177, 'height': 39}], 
    'row3': [{'shape': 'rectangle', 'centroid': (75, 238), 'width': 106, 'height': 33}], 
    'row4': [{'shape': 'circle', 'centroid': (48, 299), 'width': None, 'height': None}], 
    'row5': [{'shape': 'circle', 'centroid': (41, 350), 'width': None, 'height': None}], 
    'row6': [{'shape': 'circle', 'centroid': (40, 380), 'width': None, 'height': None}], 
    'row7': [{'shape': 'circle', 'centroid': (43, 422), 'width': None, 'height': None}]
}

data2 = {
    'row0': [{'shape': 'rectangle', 'centroid': (147, 57), 'width': 184, 'height': 38}], 
    'row1': [{'shape': 'square', 'centroid': (124, 168), 'width': 138, 'height': 111}], 
    'row2': [{'shape': 'circle', 'centroid': (107, 301), 'width': None, 'height': None}]
}

generate_output_html(data, "output")"""

