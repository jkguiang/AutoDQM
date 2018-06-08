// Global variables
var t0 = 0;

function submit() {
    let query = getQuery();
    localStorage["recent_query"] = JSON.stringify(query);

    $("#submit").hide();
    $("#finished").hide();
    $("#input_err").hide();
    $("#internal_err").hide();
    $("#load_msg").text("Loading...");
    $("#load").show();
    $("#load_msg").show();

    // TODO this does fetching sequentially, but it could be done in parallel
    $.Deferred().resolve()
        .then(() => {
            $("#load_msg").text("Loading data...")
            return fetchRun(query.data_series, query.data_sample, query.data_run);
        })
        .then(res => {
            $("#load_msg").text("Loading reference...")
            return fetchRun(query.ref_series, query.ref_sample, query.ref_run);
        })
        .then(res => {
            $("#load_msg").text("Processing...")
            return process(query.subsystem,
                query.data_series, query.data_sample, query.data_run,
                query.ref_series, query.ref_sample, query.ref_run);
        })
        .then(res => {
            console.log(res);
            load_plots(query);
            $("#load").hide()
            $("#load_msg").hide()
            $("#finished").show();
        })
        .fail(res => {
            console.log("Error:", res);
            res.error.traceback && console.log(res.error.traceback);
            $("#load").hide();
            $("#load_msg").hide();
            $("#internal_err").text(res.error.message);
            $("#internal_err").show();
            $("#submit").show();
        });
}

/** 
 * Wraps a $.getJson call to the api so that ajax errors and api errors are
 * sent homogenously to the .fail callback.
 */
function wrapApiCall(p) {
    let defer = $.Deferred();
    p.done(res => {
            if (res.error) {
                defer.reject(res);
            } else {
                defer.resolve(res);
            }
        })
        .fail(res => {
            defer.reject({
                error: {
                    message: res.statusText,
                    jqXHR: res
                }
            });
        })
    defer.abort = p.abort;
    return defer;
}

function fetchRun(series, sample, run) {
    return wrapApiCall($.getJSON('cgi-bin/index.py', {
        type: 'fetch_run',
        series: series,
        sample: sample,
        run: run
    }));
}

function process(subsystem,
    data_series, data_sample, data_run,
    ref_series, ref_sample, ref_run) {
    return wrapApiCall($.getJSON('cgi-bin/index.py', {
        type: 'process',
        subsystem: subsystem,
        data_series: data_series,
        data_sample: data_sample,
        data_run: data_run,
        ref_series: ref_series,
        ref_sample: ref_sample,
        ref_run: ref_run
    }));
}

function getSubsystems() {
    return wrapApiCall($.getJSON('cgi-bin/index.py', {
        type: 'get_subsystems'
    }));
}

function getSeries() {
    return wrapApiCall($.getJSON('cgi-bin/index.py', {
        type: 'get_series'
    }));
}

function getSamples(series) {
    return wrapApiCall($.getJSON('cgi-bin/index.py', {
        type: 'get_samples',
        series: series
    }));
}

function getRuns(series, sample) {
    return wrapApiCall($.getJSON('cgi-bin/index.py', {
        type: 'get_runs',
        series: series,
        sample: sample
    }));
}

function checkInput() {
    let query = getQuery();
    let filled = true;

    // Check that each option has a value (not "")
    for (let key in query) {
        filled = filled && query[key];
    }

    if (filled) {
        $("#sample_chk").attr('class', 'list-group-item list-group-item-success');
        $("#submit").removeAttr('disabled');
    } else {
        $("#sample_chk").attr('class', 'list-group-item list-group-item-danger');
        $("#submit").attr('disabled', 'disabled');
    }
}

function getQuery() {
    return {
        subsystem: $("#select-subsystem").val(),
        data_series: $("#data-select-series").val(),
        data_sample: $("#data-select-sample").val(),
        data_run: $("#data-select-run").val(),
        ref_series: $("#ref-select-series").val(),
        ref_sample: $("#ref-select-sample").val(),
        ref_run: $("#ref-select-run").val(),
    };
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

    checkInput();
}

function load_plots(query) {
    url = (window.location.href + "plots.php?" + $.param(query));
    document.location.href = url;
}

function load_samples(saSelect, series) {
    saSelect.load(function(callback) {
        saSelect.req = getSamples(series)
            .done(res => callback(res.data.items))
            .fail(res => {
                console.log("Samples could not be loaded", res)
                callback();
            });
    });
}

function load_runs(rSelect, series, sample) {
    rSelect.load(function(callback) {
        rSelect.req = getRuns(series, sample)
            .done(res => {
                let runs = res.data.items;
                let seen = {}
                // Filter entries with duplicate run number
                runs = runs.filter(r => {
                    return seen.hasOwnProperty(r.name) ? false : (seen[r.name] = true);
                });
                callback(runs);
            })
            .fail(res => {
                console.log(res.error.message, res)
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
        onChange: checkInput,
        load: function(query, callback) {
            this.settings.load = null; // prevent reloading on user input
            getSubsystems()
                .done(res => callback(res.data.items));
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
                this.req = getSeries()
                    .done(res => callback(res.data.items))
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
                checkInput();
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
                checkInput();
            }
        }, selectizeDefaults));

        $rSelect = $(`#${colType}-select-run`).selectize(Object.assign({
            onChange: checkInput,
        }, selectizeDefaults));

        seSelect = $seSelect[0].selectize;
        saSelect = $saSelect[0].selectize;
        rSelect = $rSelect[0].selectize;
    }
}

function main() {
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
    checkInput();

    // Main query handler
    $("#submit").click(submit);

    // Recent query handler
    if (localStorage.hasOwnProperty("recent_query")) {
        // Update plots link if search stored in local storage
        let query = JSON.parse(localStorage["recent_query"]);
        $("#plots_url").attr('href', window.location.href + "plots.php?" + $.param(query));
        load_query(query);
    }

    // External query handler
    if (localStorage.hasOwnProperty("external_query")) {
        // Submit external query
        let query = JSON.parse(localStorage["external_query"]);
        localStorage.removeItem("external_query");
        console.log("External query detected:", query);
        load_query(query);
        submit();
    }
}

$(main);
