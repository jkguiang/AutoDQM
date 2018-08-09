import React, {Component} from 'react';
import ApiSelect from './ApiSelect.js';
import {Row, Col, Button} from 'reactstrap';
import {css} from 'react-emotion';
import {Link} from 'react-router-dom';

export default class InputForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      subsystem: null,
      refSeries: null,
      refSample: null,
      refRun: null,
      dataSeries: null,
      dataSample: null,
      dataRun: null,
    };
  }

  componentWillMount = () => {
    const recentQuery = localStorage.getItem('recentQuery');
    if (recentQuery) {
      const q = JSON.parse(recentQuery);
      this.setState(q);
    }
  };

  handleSubsystemChange = opt => {
    this.setState({subsystem: opt.value});
  };

  handleDataChange = (type, opt) => {
    if (type === 'series')
      this.setState({dataSeries: opt.value, dataSample: null, dataRun: null});
    else if (type === 'sample')
      this.setState({dataSample: opt.value, dataRun: null});
    else if (type === 'run') this.setState({dataRun: opt.value});

    const s = this.state;
    const data = {series: s.dataSeries, sample: s.dataSample, run: s.dataRun};
    const ref = {series: s.refSeries, sample: s.refSample, run: s.refRun};

    if (type === 'series' && !ref.series) {
      this.handleRefChange('series', opt);
    } else if (type === 'sample' && !ref.sample && ref.series === data.series) {
      this.handleRefChange('sample', opt);
    } else if (
      type === 'run' &&
      !ref.run &&
      ref.sample === data.sample &&
      ref.series === data.series
    ) {
      this.handleRefChange('run', opt);
    }
  };

  handleRefChange = (type, opt) => {
    if (type === 'series')
      this.setState({refSeries: opt.value, refSample: null, refRun: null});
    else if (type === 'sample')
      this.setState({refSample: opt.value, refRun: null});
    else if (type === 'run') this.setState({refRun: opt.value});
  };

  queryParams = () => {
    return [
      this.state.subsystem,
      this.state.refSeries,
      this.state.refSample,
      this.state.refRun,
      this.state.dataSeries,
      this.state.dataSample,
      this.state.dataRun,
    ];
  };

  inputIsValid = () => {
    return this.queryParams().every(o => o);
  };

  queryPath = () => {
    const params = this.queryParams();
    return `/plots/${params.join('/')}`;
  };

  render() {
    const s = this.state;
    const data = {series: s.dataSeries, sample: s.dataSample, run: s.dataRun};
    const ref = {series: s.refSeries, sample: s.refSample, run: s.refRun};

    return (
      <React.Fragment>
        <Row className="mt-3">
          <Col>
            <h3>Subsystem</h3>
            <ApiSelect
              placeholder="Select subsystem..."
              type="get_subsystems"
              value={option(this.state.subsystem)}
              onChange={this.handleSubsystemChange}
            />
          </Col>
        </Row>
        <Row className="mt-3">
          <Col md="6">
            <h3>Data Run</h3>
            <RunSelectForm {...data} onChange={this.handleDataChange} />
          </Col>
          <Col md="6">
            <h3>Ref Run</h3>
            <RunSelectForm {...ref} onChange={this.handleRefChange} />
          </Col>
        </Row>
        <Row className="mt-3">
          <Col>
            <Button
              color="success"
              disabled={!this.inputIsValid()}
              className={css`
                width: 100%;
                margin-top: 10px;
              `}
              tag={Link}
              to={this.queryPath()}>
              Submit
            </Button>
          </Col>
        </Row>
      </React.Fragment>
    );
  }
}

function RunSelectForm(props) {
  return (
    <React.Fragment>
      <span>Series</span>
      <ApiSelect
        placeholder="Select series..."
        type="get_series"
        value={option(props.series)}
        onChange={c => props.onChange('series', c)}
      />
      <span>Sample</span>
      <ApiSelect
        placeholder="Select sample..."
        type="get_samples"
        series={props.series}
        value={option(props.sample)}
        onChange={c => props.onChange('sample', c)}
      />
      <span>Run</span>
      <ApiSelect
        placeholder="Select run..."
        type="get_runs"
        series={props.series}
        sample={props.sample}
        value={option(props.run)}
        onChange={c => props.onChange('run', c)}
      />
    </React.Fragment>
  );
}

function option(val) {
  if (val === null || val === undefined) return null;
  return {value: val, label: val};
}
