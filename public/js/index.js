// Global variables
var t0 = 0;

function check_input() {
    var filled =
        $("#select-subsystem").val() != "" &&
        $("#data-select-series").val() != "" &&
        $("#data-select-sample").val() != "" &&
        $("#data-select-run").val() != "" &&
        $("#ref-select-series").val() != "" &&
        $("#ref-select-sample").val() != "" &&
        $("#ref-select-run").val() != "";

    if (filled) {
        $("#sample_chk").attr('class', 'list-group-item list-group-item-success');
        $("#submit").removeAttr('disabled');
    } else {
        $("#sample_chk").attr('class', 'list-group-item list-group-item-danger');
        $("#submit").attr('disabled', 'disabled');
    }
}

function load_query(query) {
    $("#select-subsystem")[0].selectize.addOption({
        name: query["subsystem"]
    });
    $("#data-select-series")[0].selectize.addOption({
        name: query["data_series"]
    });
    $("#data-select-sample")[0].selectize.addOption({
        name: query["data_sample"]
    });
    $("#data-select-run")[0].selectize.addOption({
        name: query["data_run"]
    });
    $("#ref-select-series")[0].selectize.addOption({
        name: query["ref_series"]
    });
    $("#ref-select-sample")[0].selectize.addOption({
        name: query["ref_sample"]
    });
    $("#ref-select-run")[0].selectize.addOption({
        name: query["ref_run"]
    });

    $("#select-subsystem")[0].selectize.setValue(query["subsystem"], true);
    $("#data-select-series")[0].selectize.setValue(query["data_series"], true);
    $("#data-select-sample")[0].selectize.setValue(query["data_sample"], true);
    $("#data-select-run")[0].selectize.setValue(query["data_run"], true);
    $("#ref-select-series")[0].selectize.setValue(query["ref_series"], true);
    $("#ref-select-sample")[0].selectize.setValue(query["ref_sample"], true);
    $("#ref-select-run")[0].selectize.setValue(query["ref_run"], true);

    load_samples($("#data-select-sample")[0].selectize, query["data_series"]);
    load_runs($("#data-select-run")[0].selectize, query["data_series"], query["data_sample"]);
    load_samples($("#ref-select-sample")[0].selectize, query["ref_series"]);
    load_runs($("#ref-select-run")[0].selectize, query["ref_series"], query["ref_sample"]);

    check_input();
}

function load_plots(new_object) {
    url = (window.location.href + "plots.php?" + $.param(new_object));
    document.location.href = url;
}

function handle_response(response) {
    console.log(response);
    console.log("Run time: " + String(Math.floor(Date.now() / 1000) - t0));
    try {
        // Handle output from main.py
        console.log("query to be stored:");
        console.log(response["query"]);
        console.log("response:");
        console.log(response["response"]["payload"]);
        var resp = response["response"];

        if (resp["status"] == "fail") {
            $("#internal_err").text(resp["fail_reason"]);
            $("#submit").show();
            $("#internal_err").show();
        } else {
            localStorage["recent_query"] = JSON.stringify(response["query"]);
            load_plots(response["query"]);
            $("#finished").show();
        }
    } catch (TypeError) {
        // Handle crashes, system error, timeouts, etc.
        console.log(response["responseText"]);
        var resp_txt = response["responseText"];
        var err_msg = "";

        console.log(resp_txt.indexOf("504"));
        if (resp_txt.indexOf("504") <= -1) {
            err_msg = "Error: Gateway timed out. Could not reach server."
        } else {
            err_msg = "Error: An internal error occured."
        }

        $("#internal_err").text(err_msg);

        $("#submit").show();
        $("#internal_err").show();
    } finally {
        $("#load").hide();
        $("#load_msg").text("Loading...");
        $("#load_msg").hide();
    }
}

function handle_processes(response) {
    console.log(response);
    console.log("Run time: " + String(Math.floor(Date.now() / 1000) - t0));

    try {
        // Handle output from main.py
        console.log("query to be stored:");
        console.log(response["query"]);
        console.log("response:");
        console.log(response["response"]["payload"]);
        var resp = response["response"];

        if (resp["status"] == "fail") {
            $("#load").hide()
            $("#load_msg").hide()
            $("#internal_err").text(resp["fail_reason"]);
            $("#submit").show();
            $("#internal_err").show();
        } else if (response["query"]["type"] == "retrieve_data") {
            console.log("data retrieved");
            $("#load_msg").text("Loading reference...")
            response["query"]["type"] = "retrieve_ref";
            submit(response["query"]);
        } else if (response["query"]["type"] == "retrieve_ref") {
            console.log("processing")
            response["query"]["type"] = "process";
            $("#load_msg").text("Processing...")
            $.ajaxSetup({
                timeout: 0
            });
            $.get("cgi-bin/handler.py", response["query"])
                .done(function(response) {})
                .always(handle_response);
        }
    } catch (TypeError) {
        // Handle crashes, system error, timeouts, etc.
        console.log(response["responseText"]);
        var resp = response["responseText"];
        var err_msg = "";

        console.log(resp.indexOf("504"));
        if (resp.indexOf("504") > -1) {
            err_msg = "Error: Gateway timed out. Could not reach server."
        } else {
            err_msg = "Error: An internal error occured."
        }

        $("#load").hide()
        $("#load_msg").hide()
        $("#internal_err").text(err_msg);

        $("#submit").show();
        $("#internal_err").show();
    }

}

function submit(query) {
    console.log("retrieving");
    console.log(query);
    $("#load").show();
    $("#load_msg").show();
    $("#submit").hide();
    $("#finished").hide();
    $("#input_err").hide();
    $("#internal_err").hide();
    t0 = Math.floor(Date.now() / 1000);
    console.log(t0);

    $.ajaxSetup({
        timeout: 0
    }); // Set timeout to 5 minutes
    $.get("cgi-bin/handler.py", query)
        .done(function(response) {})
        .always(handle_processes);
}

function load_samples(saSelect, series) {
    // Enable the sample selector and request its values
    saSelect.load(function(callback) {
        saSelect.req = $.getJSON("cgi-bin/handler.py", {
                    type: "getSamples",
                    series: series
                },
                res => callback(res.response.samples))
            .fail(res => {
                console.log("Samples could not be loaded", res)
                callback();
            });
    });
}

function load_runs(rSelect, series, sample) {
    // Enable the run selector and request its values
    rSelect.load(function(callback) {
        rSelect.req = $.getJSON("cgi-bin/handler.py", {
                    type: "getRuns",
                    series: series,
                    sample: sample
                },
                res => callback(res.response.runs))
            .fail(res => {
                console.log("Runs could not be loaded", res)
                callback();
            });
    });
}

function initialize_selectors() {
    let selectizeDefaults = {
        create: true,
        createOnBlur: true,
        valueField: 'name',
        labelField: 'name',
        searchField: 'name',
    }

    let suReq;
    let suSelect, $suSelect;

    $suSelect = $("#select-subsystem").selectize(Object.assign({
        preload: true,
        onChange: check_input,
        load: function(query, callback) {
            this.settings.load = null; // prevent reloading on user input
            $.getJSON('cgi-bin/handler.py', {
                    type: "getSubsystems"
                },
                function(res) {
                    callback(res.response.subsystems);
                })
        },
    }, selectizeDefaults));

    let colTypes = ["data", "ref"];
    for (let i in colTypes) {
        let colType = colTypes[i];
        let otherColType = colTypes[(i + 1) % 2];

        let seSelect, $seSelect;
        let saSelect, $saSelect;
        let rSelect, $rSelect;

        $seSelect = $(`#${colType}-select-series`).selectize(Object.assign({
            preload: true,
            load: function(query, callback) {
                this.settings.load = null; // prevent reloading on user input
                this.req && this.req.abort();
                this.req = $.getJSON("cgi-bin/handler.py", {
                            type: "getSeries"
                        },
                        res => callback(res.response.series))
                    .fail(res => {
                        console.log("Series could not be loaded", res);
                        callback();
                    });
            },
            onChange: function(series) {
                // Clear the sample and run options and their ongoing requests
                [saSelect, rSelect].forEach(s => {
                    s.clearOptions();
                    s.req && s.req.abort();
                });

                if (series != "") {
                    // Set the other input to the same value if it's empty
                    let other = $(`#${otherColType}-select-series`)[0].selectize;
                    if (other.getValue() == "") {
                        other.setValue(series, false);
                    }
                    load_samples(saSelect, series);
                }
                check_input();
            }
        }, selectizeDefaults));

        $saSelect = $(`#${colType}-select-sample`).selectize(Object.assign({
            onChange: function(sample) {
                // Clear the run options and their ongoing requests
                [rSelect].forEach(s => {
                    s.clearOptions();
                    s.req && s.req.abort();
                });

                if (sample != "") {
                    // Set the other input to the same value if it's empty
                    let other = $(`#${otherColType}-select-sample`)[0].selectize;
                    if (other.getValue() == "") {
                        other.setValue(sample, false);
                    }
                    load_runs(rSelect, seSelect.getValue(), sample);
                }
                check_input();
            }
        }, selectizeDefaults));

        $rSelect = $(`#${colType}-select-run`).selectize(Object.assign({
            onChange: check_input,
        }, selectizeDefaults));

        seSelect = $seSelect[0].selectize;
        saSelect = $saSelect[0].selectize;
        rSelect = $rSelect[0].selectize;
    }
}

// Main function
$(function() {
    console.log(localStorage);

    // Initital hides
    $("#load").hide();
    $("#load_msg").hide();
    $("#finished").hide();
    $("#input_err").hide();
    $("#internal_err").hide();
    $("#SingleMuon").hide();
    $("#Cosmics").hide();

    // Initial Disables
    $("#submit").attr('disabled', 'disabled');

    // Prevent 'enter' key from submitting forms (gives 404 error with full data set name form)
    $(window).keydown(function(event) {
        if (event.keyCode == 13) {
            event.preventDefault();
            return false;
        }
    });

    initialize_selectors();
    check_input();

    // Main query handler
    $("#submit").click(function() {
        $("#load").hide();
        $("#load_msg").text("Loading data...")
        $("#finished").hide();
        $("#input_err").hide();
        $("#internal_err").hide();
        var query = {
            "type": "retrieve_data",
            "subsystem": $("#select-subsystem").val(),
            "data_series": $("#data-select-series").val(),
            "data_sample": $("#data-select-sample").val(),
            "data_run": $("#data-select-run").val(),
            "ref_series": $("#ref-select-series").val(),
            "ref_sample": $("#ref-select-sample").val(),
            "ref_run": $("#ref-select-run").val(),
            "user_id": Date.now(),
        };
        submit(query);
    });

    // Recent query handler
    if (localStorage.hasOwnProperty("recent_query")) {
        // Update plots link if search stored in local storage
        let query = JSON.parse(localStorage["recent_query"]);
        $("#plots_url").attr('href', window.location.href + "plots.php?query=" + $.param(query));
        load_query(query);
    }

    // External query handler
    if (localStorage.hasOwnProperty("external_query")) {
        // Submit external query
        let query = JSON.parse(localStorage["external_query"]);
        query["type"] = "retrieve_data";
        localStorage.removeItem("external_query");
        console.log("External query detected:", query);
        load_query(query);
        submit(query);
    }
});
