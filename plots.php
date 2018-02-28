<html>
    <head>
        <title>AutoPlotter</title>

        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
        <script src="//code.jquery.com/ui/1.11.4/jquery-ui.js"></script>

        <!-- Latest compiled and minified Boostrap CSS and Javascript -->
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
 
        <!-- My Code -->
        
        <!-- CSS -->
        <style>
            img:hover {
                border: 1px solid #cecece;
            }
            
            .well-image .bg {
                pointer-events: none;
                margin-bottom: 0px;
                opacity: 0.2;
                color: #fff;
                background: #fff url("") no-repeat center top;
                background-color: #ffffff !important;
                background-size: contain !important;

                -webkit-filter: blur(5px);
                -moz-filter: blur(5px);
                -o-filter: blur(5px);
                -ms-filter: blur(5px);
                filter: blur(5px);

                overflow: hidden;
                width: 115%;
                height: 100%;

                position: absolute;
                top:0;left:0;
                z-index:auto;
            }
            
            .well {
                overflow: hidden;
                width: 115%;
            }
            
            .tooltip-txt {
                white-space: pre;
            }

        </style>

        <!-- PHP -->
        <?php
            $url_array = explode(",", $_REQUEST["query"]);
            $user_id = $url_array[2];

            $images = array();

            function newImage($new_png, $new_pdf, $new_txt, $new_width, $new_height) {
                global $images;
                $new_image = array(
                    "png_path" => $new_png,
                    "pdf_path" => $new_pdf,
                    "txt_path" => $new_txt,
                    "width" => $new_width,
                    "height" => $new_height,
                );

                $images[] = $new_image;
            
            }

            if ($user_id != "") {

                $cwd = getcwd();

                $pdf_path = ("data/pdfs/" . $user_id . "/");
                $png_path = ("data/pngs/" . $user_id . "/");
                $txt_path = ("data/txts/" . $user_id . "/");

                $pdfs = scandir($cwd . "/" . $pdf_path);
                $pngs = scandir($cwd . "/" . $png_path);
                $txts = scandir($cwd . "/" . $txt_path);
                
                // Fill JSON
                $txt_offset = 0;
                for ($i = 0; $i < count($pngs); $i++) {
                    $png_name = explode(".", $pngs[$i]);
                    $pdf_name = explode(".", $pdfs[$i]);
                    $txt_name = explode(".", $txts[$i - $txt_offset]);
                    if ($png_name[0] != $pdf_name[0]) continue;
                    if ($pngs[$i] == '.' || $pngs[$i] == '..') continue;
                    list($width, $height) = getimagesize($cwd . "/" . $png_path . "/" . $pngs[$i]);
                    if ($png_name[0] != $txt_name[0]) {
                        newImage($png_path . $pngs[$i], $pdf_path . $pdfs[$i], "None", $width, $height);
                        $txt_offset++;
                        continue;
                    }
                    newImage($png_path . $pngs[$i], $pdf_path . $pdfs[$i], $txt_path . $txts[$i - $txt_offset], $width, $height);
                }

            }

        ?>

        <!-- pass php values to js vars -->
        <script type="text/javascript">
            var php_out = <?php echo json_encode($images); ?>;
        </script>

        <!-- load jquery after php runs -->
        <script src="src/js/plots.js"></script>

    </head>

    <body>
        <ul class="nav nav-tabs" id="navbar" role="tablist">
            <li role="presentation"><a href="./">AutoDQM</a></li>
            <li role="presentation"><a href="search.php">Search</a></li>
            <li role="presentation"><a href="database.php">Database</a></li>
            <li role="presentation" class="active"><a href="plots.php">Plots</a></li>
        </ul>

        <p><br /><br /></p>

        <div class="container-fluid">
            <div class="row">
                <!-- Side Navbar -->
                <div class="col-md-3">
                    <div class="sidebar-nav-fixed sidebar-nav-fixed affix">
                        <div class="well well-image">
                            <h4>AutoPlotter</h4>
                            <div class="text-center">
                                <form>
                                    <div class="form-group">
                                        <input type="text" id="search" onkeyup="refresh()" placeholder="Search" class="form-control">
                                    </div>
                                </form>
                                <a style="z-index: auto; position: relative;" class="btn btn-primary btn-sm" href="http://github.com/jkguiang/AutoDQM" role="button">Github &raquo;</a>
                            </div>
                        </div>
                        <div class="well">
                            <div class="text-center">
                                <img id="preview" class="img-thumbnail" src="" alt="Hover over a thumbnail to get preview here" width=200 height=300>
                            </div>
                        </div>
                        <div class="well">
                            <div id="tooltip" class="tooltip-txt"></div>
                        </div>
                    </div>
                </div>

                <div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
                    <div class="row">
                        <div class="col-sm-2"></div>
                        <div class="col-sm-8" id="title_wells">
                            <label for="data_well">Data</label>
                            <div class="alert alert-success" id="data_well"><p id="data_title"></p></div>
                            <label for="ref_well">Reference</label>
                            <div class="alert alert-info" id="ref_well"><p id="ref_title" ></p></div>
                            <hr>
                        </div>
                        <div class="col-sm-2"></div>
                    </div>
                    <!-- Images -->
                    <div id="section_1" class="container">
                    </div><!-- /.container -->

                    <!-- Footer -->
                    <div class="container">
                        <hr> <!-- thin, grey horizontal line -->
                    </div>
                </div>
            </div>
        </div>
    </body>
</html>
