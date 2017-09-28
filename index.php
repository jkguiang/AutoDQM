<html>
        <head>
                <title>AutoDQM</title>

                <!-- Latest compiled and minified Boostrap CSS and Javascript -->
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
                <script src="//code.jquery.com/ui/1.11.4/jquery-ui.js"></script>

                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
                <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>

                <!-- Slider -->
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-slider/9.8.1/css/bootstrap-slider.min.css">
                <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-slider/9.8.1/bootstrap-slider.min.js"></script>
 
                <!-- My Code -->
                
                <!-- CSS -->
                <style>
                    .container-wide {
                        padding: 0 50px !important;
                    }
                    .loader {
                        text-align: center;
                        margin: auto;
                        border: 16px solid #f3f3f3; /* Light grey */
                        border-top: 16px solid #3498db; /* Blue */
                        border-radius: 50%;
                        width: 120px;
                        height: 120px;
                        animation: spin 2s linear infinite;
                    }
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                </style>

                <!-- JQuery -->
                <script>
                    // Global variables
                    var t0 = 0;
                    var cur_sample = "none"; // So script knows what sample is selected
                    var data_info = ""; // To be sent with query
                    var ref_info = ""; // To be sent with query
                    var prefix = ""; // Sample name that is placed in front of dataset name

                    // Form functions: mostly for updating 'preview' wells
                    function updt_data() {
                        var path = document.getElementById("path").value;

                        $('#preview').text("");
                        $('#preview').text("/" + prefix + "/" + path);
                        check_input();
                    }

                    function updt_ref() {
                        var ref_path = document.getElementById("ref_path").value;

                        $('#ref_preview').text("");
                        $('#ref_preview').text("/" + prefix + "/" + ref_path);
                        check_input();
                    }

                    function updt_sample() {

                        if (cur_sample == "RelVal") {
                            var sample_input = document.getElementById(cur_sample + "_input").value;
                            prefix = cur_sample + sample_input;
                            data_info = sample_input;
                            ref_info = sample_input;
                            $("#data_sample").attr('placeholder', "/"+ prefix +"/");
                            $("#ref_sample").attr('placeholder', "/"+ prefix +"/");
                        }
                        else if (cur_sample == "SingleMuon") {
                            data_info = document.getElementById(cur_sample + "_dataInput").value;
                            ref_info = document.getElementById(cur_sample + "_refInput").value;
                            prefix = cur_sample;
                        }
                        updt_data();
                        updt_ref();
                        check_input();
                    }

                    function check_input() {
                        var passed = true;

                        data_inp = document.getElementById("path").value;
                        ref_inp = document.getElementById("ref_path").value;
                        data_split = data_inp.split("/");
                        ref_split = ref_inp.split("/");

                        // Sample form filled
                        if (cur_sample == "SingleMuon") {
                            if  (document.getElementById(cur_sample + "_dataInput").value != "" || document.getElementById(cur_sample + "_refInput").value != "") {
                                $("#sample_chk").attr('class', 'list-group-item list-group-item-success')
                            }

                            else {
                                $("#sample_chk").attr('class', 'list-group-item list-group-item-danger');
                                passed = false;
                            }
                        }
                        if (cur_sample == "RelVal") {
                            if  (document.getElementById(cur_sample + "_input").value != "") {
                                $("#sample_chk").attr('class', 'list-group-item list-group-item-success')
                            }

                            else {
                                $("#sample_chk").attr('class', 'list-group-item list-group-item-danger');
                                passed = false;
                            }
                        }
                        // One slash
                        if ( (data_split.length - 1) == 1 && (ref_split.length - 1) == 1 ) {
                            var passed_slash = true;
                            $("#slash_chk").attr('class', 'list-group-item list-group-item-success');
                        }
                        else {
                            $("#slash_chk").attr('class', 'list-group-item list-group-item-danger');
                            passed = false;
                        }
                        // Text on both sides of slash
                        if ( passed_slash && data_split.indexOf("") <= -1 && ref_split.indexOf("") <= -1 ) {
                            $("#form_chk").attr('class', 'list-group-item list-group-item-success');
                        }
                        else {
                            $("#form_chk").attr('class', 'list-group-item list-group-item-danger');
                            passed = false;
                        }
                        // Ends with DQMIO
                        if (data_split[data_split.length - 1] == "DQMIO" && ref_split[ref_split.length - 1] == "DQMIO") {
                            $("#dqmio_chk").attr('class', 'list-group-item list-group-item-success');
                        }
                        else {
                            $("#dqmio_chk").attr('class', 'list-group-item list-group-item-danger');
                            passed = false;
                        }

                        if (passed) {
                            $("#submit").removeAttr('disabled');
                        }
                        else {
                            $("#submit").attr('disabled', 'disabled');
                        }
                    }

                    // End form functions

                    // Query handlers
                    function pass_object(new_object) {
                        url = (window.location.href + "plots.php?query=" + encodeURIComponent(new_object));
                        document.location.href = url;
                    }

                    function handle_response(response) {
                        console.log(response); 
                        console.log("Run time: " + String(Math.floor(Date.now() / 1000) - t0));
                        try {
                            // Handle output from main.py
                            console.log(response["response"]["payload"]);
                            var resp = response["response"];

                            if (resp["status"] == "failed") {
                                $("#internal_err").text(resp["fail_reason"]);
                                $("#submit").show();
                                $("#internal_err").show();
                            }                            

                            else {
                                localStorage["data"] = response["query"][3];
                                localStorage["ref"] = response["query"][5];
                                pass_object(response["query"]);
                                $("#finished").show();
                            }
                        }
                        catch(TypeError) {
                            // Handle crashes, system error, timeouts, etc.
                            console.log(response["responseText"]);
                            var resp = response["responseText"];
                            var err_msg = "";
                            
                            if (resp.indexOf("504") !== 1) {
                                err_msg = "Error: Gateway timed out. Could not reach server."
                            }
                            else {
                                err_msg = "Error: An internal error occured."
                            }

                            $("#internal_err").text(err_msg);

                            $("#submit").show();
                            $("#internal_err").show();
                        }
                        finally {
                            $("#load").hide();
                        }
                    }

                    function submit(query) {
                        console.log("submitting query");
                        console.log(query);
                        $("#load").show();
                        $("#submit").hide();
                        t0 = Math.floor(Date.now() / 1000);
                        console.log(t0);

                        $.ajaxSetup({timeout:300000}); // Set timeout to 5 minutes
                        $.get("handler.py", query)
                            .done(function(response) {})
                            .always(handle_response);
                    }

                    function check_query(query) {
                        var fail = false;

                        var path = document.getElementById("path").value;
                        var ref_path = document.getElementById("ref_path").value;
                        if (path == "" || ref_path == "")   {
                            fail = true;
                        }
                        if (fail) {
                            $("#input_err").show();
                        }

                        else {
                            $("#input_err").hide();
                            console.log(query);
                            submit(query);
                        }
                    }
                    // End query handlers

                    // Main function
                    $(function() {
                        // Initital hides
                        $("#load").hide();
                        $("#finished").hide();
                        $("#input_err").hide();
                        $("#internal_err").hide();
                        $("#SingleMuon").hide();
                        $("#RelVal").hide();

                        // Initial Disables
                        $("#path").attr('disabled', 'disabled');
                        $("#ref_path").attr('disabled', 'disabled');
                        $("#submit").attr('disabled', 'disabled');

                        // Prevent 'enter' key from submitting forms (gives 404 error with full data set name form)
                        $(window).keydown(function(event) {
                            if (event.keyCode == 13) {
                                event.preventDefault();
                                return false;
                            }
                        });

                        // Select menu functions
                        $("#sample_list").val("none");
                        var relval_ex = "e.g. CMSSW_9_1_1_patch1-91X_upgrade2023_realistic_v1_D17-v1/DQMIO";
                        var singlemu_ex = "e.g. Run2017C-PromptReco-v1/DQMIO";
                        var none_ex = "Please select a sample."
                        $("#sample_list").on('change', function() {
                            // Store current sample (global variable)
                            cur_sample = this.value;
                            prefix = this.value;

                            // Reset fields
                            if (cur_sample != "none"){
                                $("#" + cur_sample)[0].reset();
                                updt_data();
                                updt_ref();
                                updt_sample();
                            }

                            // Disable data set name input if no sample selected
                            if (this.value == "none") {
                                $("#path").attr('disabled', 'disabled');
                                $("#ref_path").attr('disabled', 'disabled');
                                $("#path").attr('placeholder', none_ex);
                                $("#ref_path").attr('placeholder', none_ex);
                                $("#data_sample").attr('placeholder', "/sample/");
                                $("#ref_sample").attr('placeholder', "/sample/");
                            }
                            else {
                                $("#path").removeAttr('disabled');
                                $("#ref_path").removeAttr('disabled');
                                if (this.value == "RelVal") {
                                    $("#path").attr('placeholder', relval_ex);
                                    $("#ref_path").attr('placeholder', relval_ex);
                                    $("#data_sample").attr('placeholder', "/" + prefix + "/");
                                    $("#ref_sample").attr('placeholder', "/" + prefix + "/");
                                }
                                if (this.value == "SingleMuon") {
                                    $("#path").attr('placeholder', singlemu_ex);
                                    $("#ref_path").attr('placeholder', singlemu_ex);
                                    $("#data_sample").attr('placeholder', "/" + prefix + "/");
                                    $("#ref_sample").attr('placeholder', "/" + prefix + "/");
                                }
                            }

                            // Show proper input for selected sample
                            var opts = document.getElementById("sample_list").options;
                            for ( var i = 0; i < opts.length; i++ ) {
                                if (opts[i].value == this.value) {
                                    $("#" + this.value).show();
                                }
                                else {
                                    $("#" + opts[i].value).hide();
                                }
                            }
                        });

                        // Main query handler
                        $("#submit").click(function(){
                            var query = {
                                "data_query": $("#preview").text(),
                                "ref_query": $("#ref_preview").text(),
                                "sample": cur_sample,
                                "data_info": data_info,
                                "ref_info": ref_info,
                            }
                            check_query(query);
                        });
                    
                    });

                </script>

        </head>

        <body>
            <ul class="nav nav-tabs" id="navbar" role="tablist">
                <li role="presentation" class="active"><a href="./">AutoDQM</a></li>
                <li role="presentation"><a href="search.php">Search</a></li>
                <li role="presentation"><a href="plots.php">Plots</a></li>
            </ul>


            <div class="container-wide">

                <div class="row">
                    <div class="col-lg-6">
                        <div class="row"><h2>Sample</h2><hr></div>
                        <div class="row">
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label for="sample_list">Name</label>
                                    <select class="form-control" id="sample_list">
                                        <option value="none">Select Sample</option>
                                        <option value="RelVal">RelVal</option>
                                        <option value="SingleMuon">SingleMuon</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <!-- RelVal Sample Entry -->
                                <div class="form-group row">
                                    <form id="RelVal" action="/" method="post" role="form">
                                        <div class="form-group">
                                            <label for="RelVal_input">RelVal Sample</label>
                                            <input type="text" class="form-control" id="RelVal_input" onkeyup="updt_sample()" placeholder="e.g. ZMM_14">
                                        </div>
                                    </form>
                                <!-- SingleMuon Run Entry -->
                                    <form id="SingleMuon" action="/" method="post" role="form">
                                        <div class="form-group">
                                            <label for="SingleMuon_dataInput">Data Run Number</label>
                                            <input type="text" class="form-control" id="SingleMuon_dataInput" onkeyup="updt_sample()" placeholder="e.g. 30016">
                                            <hr style="margin:0px; height:10px; visibility:hidden;" />
                                            <label for="SingleMuon_refInput">Reference Run Number</label>
                                            <input type="text" class="form-control" id="SingleMuon_refInput" onkeyup="updt_sample()" placeholder="e.g. 29916">
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div> <!-- End top left column -->
                    <div class="col-lg-6">
                        <p><br /></p>
                        <div class="list-group">
                            <li class="list-group-item">Requirements</li>
                            <li class="list-group-item list-group-item-danger" id="sample_chk">Sample form filled</li>
                            <li class="list-group-item list-group-item-danger" id="slash_chk">One slash</li>
                            <li class="list-group-item list-group-item-danger" id="form_chk">Text on both sides of slash</li>
                            <li class="list-group-item list-group-item-danger" id="dqmio_chk">Ends with DQMIO</li>
                        </div>
                    </div>
                </div>
                <hr>
                <div class="row">
                    <div class="col-lg-6">
                        <h2>Data</h2>
                        <hr>

                        <div class="row">
                            <div class="col-sm-2" style="padding: 0px">
                                <div class="form-group">
                                    <label for="data_sample">Sample</label>
                                    <input type="text" class="form-control" id="data_sample" placeholder="/sample/" style="text-align: right" disabled>
                                </div>
                            </div>
                            <div class="col-md-9">
                                <form id="full" action="./" method="post" role="form">
                                    <div class="form-group row">
                                        <label for="path">Dataset Name</label>
                                        <input type="text" class="form-control" id="path" onkeyup="updt_data()" name="path" placeholder="Please select a sample.">
                                    </div>
                                </form>
                            </div>
                        </div>

                    </div> <!-- end left col -->

                    <div class="col-lg-6">
                        <h2>Reference</h2>
                        <hr>

                        <div class="row">
                            <div class="col-md-2" style="padding: 0px">
                                <div class="form-group">
                                    <label for="ref_sample">Sample</label>
                                    <input type="text" class="form-control" id="ref_sample" placeholder="/sample/" style="text-align: right" disabled>
                                </div>
                            </div>
                            <div class="col-md-9">
                                <form id="ref_full" action="./" method="post" role="form">
                                    <div class="form-group row">
                                        <label for="ref_path">Dataset Name</label>
                                        <input type="text" class="form-control" id="ref_path" onkeyup="updt_ref()" name="ref_path" placeholder="Please select a sample.">
                                    </div>
                                </form>
                            </div>
                        </div>

                    </div > <!-- end right col -->

                </div> <!-- end main row -->

                <p><br /></p>

                <hr>
                <div class="row">
                    <div class="col-lg-3">
                    </div> <!-- end secondary row left padding -->
                    <div class="col-lg-6">
                        <div class="row">
                            <div class="col-md-12">
                                <label for="preview_well">Data Preview</label>
                                <div class="alert alert-success" id="preview_well">
                                    <p id="preview">Please enter a data set name.</p>
                                </div>
                            </div>
                        </div> <!-- end preview row -->
                        <div class="row">
                            <div class="col-md-12">
                                <label for="ref_preview_well">Reference Preview</label>
                                <div class="alert alert-info" id="ref_preview_well">
                                    <p id="ref_preview">Please enter a reference data set name.</p>
                                </div>
                            </div>
                        </div> <!-- end ref_preview row -->
                        <div class="text-center">
                            <button id="submit" type="submit" class="btn btn-lg btn-success">Submit</button>
                            <p><br /></p>
                            <a href="plots.php"><div class="alert alert-success" id="finished">Success! Please navigate to the 'Plots' page to view the results.</div></a>
                            <div class="alert alert-danger" id="input_err">Error: Incomplete input.</div>
                            <div class="alert alert-danger" id="internal_err">Error: Internal error.</div>
                        </div>
                        <div class="loader" id="load"></div>
                    </div> <!-- end secondary row middle col -->
                    <div class="col-lg-3">
                    </div> <!-- end secondary row right padding -->
                </div> <!-- end secondary row -->

            </div> <!-- end container -->
        </body>
</html>
