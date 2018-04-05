
var indexMap = {"thumbnails":{"width": 0, "height": 0}, "search":""};
var page_loads = 0;
response = {};

// Fetch object pased from index
function fetch_object() {
    var url = document.location.href.split("#")[0],
        params = url.split('?')[1].split('&'), 
        tmp;
    for (var i = 0, l = params.length; i < l; i++) {
        tmp = params[i].split('=');
        response[tmp[0]] = tmp[1];
    }
    response["query"] = unescape(response["query"]).split(",");
    console.log(response);
}

$(function() {
    page_loads++;
    console.log(localStorage);
    load_page(php_out);
});

function load_page(php_out) {
    var data = make_json(php_out);
    filter(data);
    fill_sections(data);
    if (page_loads == 1) {
        try {
            fetch_object();
            localStorage["data"] = response["query"][0];
            localStorage["ref"] = response["query"][1];
            localStorage["user_id"] = response["query"][2];
            console.log(localStorage);
            $("#data_title").text(response["query"][0]);
            $("#ref_title").text(response["query"][1]);
            $("#title_wells").show();
            if (response["query"][0] == "" || response["query"][1] == "") {
                $("#title_wells").hide();
            }
        }
        catch(TypeError) {
            if (localStorage.hasOwnProperty("data")) {
                $("#data_title").text(localStorage["data"]);
                $("#ref_title").text(localStorage["ref"]);
                $("#title_wells").show();
            }
            else {
                $("#title_wells").hide();
            }
        }
    }
    $('[id^=img_]').mouseenter(
        function() {
            // Dynamic Well Preview
            $("#preview").attr("src", $(this).attr("src"));

            // Dynamic Well Tooltip
            new_txt = data[Number($(this).attr('id').split("_")[1])]["txt_path"];
            if (new_txt != "None"){
                $("#tooltip").show();
                $("#tooltip").load(new_txt);
            }
            else {
                $("#tooltip").hide();
            }
        } 
    );

}

function make_json(php_out) {
    var new_json = [];
    
    for (var i = 0; i < php_out.length; i++) {
        var img_obj = php_out[i];
        var png_path = img_obj["png_path"];
        var pdf_path = img_obj["pdf_path"];
        var txt_path = img_obj["txt_path"];
        var width = img_obj["width"];
        var height = img_obj["height"];
        var name = png_path.split('/').reverse()[0].split('.')[0];

        // Get divisor for image dimensions
        var div = get_div(Math.max(width, height));
        indexMap["thumbnails"]["width"] = width/div;
        indexMap["thumbnails"]["height"] = height/div;

        new_json.push({
            "name": name,
            "png_path": png_path,
            "pdf_path": pdf_path,
            "txt_path": txt_path,
            "width": indexMap["thumbnails"]["width"],
            "height": indexMap["thumbnails"]["height"],
            "hidden": false,
        });

    }                
    
    return new_json;
}

function get_div(max_length) {
    var divisor = 1;
    while (true) {
        if (max_length/divisor <= 250) {
            return divisor;
        }
        divisor+=0.5;
    }
}

function refresh() {
    page_loads++;
    load_page(php_out);
}

function filter(data) {

    var input = document.getElementById('search');
    if (page_loads == 1 && window.location.hash != "") {
        var search = window.location.hash.split("#")[1];
    }
    else{
        if (input == "") {
            window.location.hash = "";
        }
        var search = input.value;
        window.location.hash = search;
    }
    indexMap["search"] = search;
    for (var i = 0; i < data.length; i++) {
        if (data[i]["name"].indexOf(search) < 0) {
            data[i]["hidden"] = true;
        }
    }

    return data;
}

function set_grid(data) {
    var container = $("#section_1");
    var counter = 0;

    container.html("");

    for (var i = 0; i < (data.length + data.length % 3); i+=3) {
        var toappend = "";

        //Draw thumbnails
        toappend += "<div class='row'>";
        toappend += "   <div class='text-center'>"
        for (var j = 0; j < 3; j++){
            toappend +=     ("<div id=grid_" + (i + j) + " class='col-lg-4'></div>");
            counter++;
        }
        toappend += "   </div>"
        toappend += "</div>";
        container.append(toappend);
    }
}

function fill_grid(data) {

    var counter = 0;
    var new_search = "";

    var true_count = 0;
    for (var i = 0; i < data.length; i++) {
        if (data[i]["hidden"]) {
            true_count++;
            continue;
        }

        var new_split = "";
        var html_name = "";

        if (indexMap["search"] != "") {
            new_search = indexMap["search"];
            new_split = data[i]["name"].split(new_search);
            new_name = "";

            for (var j = 0; j < new_split.length; j++) {
                new_name += new_split[j];
                html_name += new_split[j];
                if (data[i]["name"].indexOf(new_name + new_search) != -1) {
                    new_name += new_search;
                    html_name += "<font class='bg-success'>"+new_search+"</font>";
                }
            }
        }

        else {
            html_name = data[i]["name"];
        }


        $("#grid_" + counter).append("<a href="+data[i]["pdf_path"]+"><h4>"+html_name+"</h4></a><a href="+data[i]["pdf_path"]+"><img id=img_"+true_count+" src="+data[i]["png_path"]+" width="+data[i]["width"]+" height="+data[i]["height"]+"></a>");
        true_count++;
        counter++;
    }
}

function fill_sections(data) {
    set_grid(data);
    fill_grid(data);
}
