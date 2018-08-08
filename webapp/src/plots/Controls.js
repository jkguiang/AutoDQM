import React, {Component} from 'react';
import {Card, CardBody, Input, Button, Col, Row, UncontrolledTooltip} from 'reactstrap';
import Select from 'react-select';
import Switch from 'react-switch';
import {css} from 'react-emotion';
import axios from 'axios';
import {Redirect} from 'react-router-dom';

export default class Controls extends Component {
  constructor(props) {
    super(props);
    this.state = {
      runReq: null,
      runOpts: [],
      newRun: null,
    };
  }

  componentWillMount = () => {
    this.loadRunControls();
  };

  componentDidUpdate = () => {
    if (this.state.newRun) this.setState({newRun: null});
  };

  handleSearchChange = e => {
    this.props.onSearchChange(e.target.value);
    e.preventDefault();
  };

  switchRun = run => {
    if (!run) return;
    console.log(run);

    let q = this.props.query;
    const params = [
      q.subsystem,
      q.refSeries,
      q.refSample,
      q.refRun,
      q.dataSeries,
      q.dataSample,
      run,
    ];

    this.setState({newRun: `/plots/${params.join('/')}`});
  };

  nextRun = () => {
    const runOpts = this.state.runOpts;
    if (runOpts.length === 0) return null;

    const curRun = this.props.query.dataRun;
    const idx = runOpts.map(r => r.value).indexOf(curRun);
    if (idx + 1 === runOpts.length || idx === -1) return null;
    return runOpts[idx + 1].value;
  };

  prevRun = () => {
    const runOpts = this.state.runOpts;
    if (runOpts.length === 0) return null;

    const curRun = this.props.query.dataRun;
    const idx = runOpts.map(r => r.value).indexOf(curRun);
    if (idx === 0 || idx === -1) return null;
    return runOpts[idx - 1].value;
  };

  loadRunControls = () => {
    const params = this.props.query;
    const runReq = cancellableQuery('/cgi-bin/index.py', {
      type: 'get_runs',
      series: params.dataSeries,
      sample: params.dataSample,
    });
    this.setState({runReq});
    runReq
      .then(res => {
        const seen = {};
        const sorted = res.data.items
          .map(r => ({value: r.name, label: r.name}))
          .filter(r => !seen.hasOwnProperty(r.value) && (seen[r.value] = true))
          .sort((a, b) => parseInt(a.value, 10) - parseInt(b.value, 10));

        this.setState({runReq: null, runOpts: sorted});
      })
      .catch(err => {
        if (!axios.isCancel(err)) this.setState({runReq: null, runOpts: []});
      });
  };

  render() {
    if (this.state.newRun) return <Redirect to={this.state.newRun} />;
    return (
      <Card className={this.props.className}>
        <CardBody className="p-2">
          <div>
            <small className="text-muted">Filter plots</small>
            <Input
              onChange={this.handleSearchChange}
              value={this.props.search}
            />
          </div>
          <div className="mt-2">
            <small className="text-muted mt-3">
              Select a different data run
            </small>
            <Row>
              <Col xs="4">
                <Button
                  outline
                  color="primary"
                  className={css`
                    width: 100%;
                  `}
                  onClick={() => this.switchRun(this.prevRun())}
                  disabled={this.state.runOpts.length === 0}
                  id="prevButton">
                  Prev
                </Button>
                <UncontrolledTooltip placement="top" target="prevButton">
                  {this.prevRun()}
                </UncontrolledTooltip>
              </Col>
              <Col xs="4" className="p-0">
                <Select
                  options={this.state.runOpts}
                  onChange={r => this.switchRun(r.value)}
                  isLoading={this.state.runReq}
                  isDisabled={this.state.runOpts.length === 0}
                />
              </Col>
              <Col xs="4">
                <Button
                  outline
                  color="primary"
                  className={css`
                    width: 100%;
                  `}
                  onClick={() => this.switchRun(this.nextRun())}
                  disabled={this.state.runOpts.length === 0}
                  id="nextButton">
                  Next
                </Button>
                <UncontrolledTooltip placement="top" target="nextButton">
                  {this.nextRun()}
                </UncontrolledTooltip>
              </Col>
            </Row>
          </div>
          <div className="mt-3">
            <span>Show hidden plots</span>
            <Switch
              className={css`
                vertical-align: middle;
                margin-left: 4px;
                float: right;
              `}
              checked={this.props.showAll}
              onChange={this.props.onShowAllChange}
            />
          </div>
        </CardBody>
      </Card>
    );
  }
}

const cancellableQuery = (endpoint, query) => {
  const source = axios.CancelToken.source();
  const p = axios
    .get(endpoint, {params: query, cancelToken: source.token})
    .then(res => {
      if (res.data.error) throw res.data.error;
      return res.data;
    })
    .catch(err => {
      console.log(err);
      throw err;
    });
  p.cancel = () => source.cancel(`Cancelled request of type ${query.type}`);
  return p;
};
