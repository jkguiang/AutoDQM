import React, {Component} from 'react';
import {Container, Row as BSRow, Col, Button} from 'reactstrap';
import Select from 'react-select';
import styled, {css} from 'react-emotion';
import RunSelectForm from './RunSelectForm.js';
import SubsystemSelect from './SubsystemSelect.js';

// Give RSRow some bottom margin
const Row = styled(BSRow)`
  margin-bottom: 1rem;
`;

export default class InputPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      subsystem: null,
      data: {series: null, sample: null, run: null},
      ref: {series: null, sample: null, run: null},
    };
  }

  handleSubsysChange = subsystem => {
    this.setState({subsystem});
  };

  handleDataChange = dataState => {
    const other = {...this.state.ref};
    if (!other.series) other.series = dataState.series;
    if (!other.sample && other.series === dataState.series) {
      other.sample = dataState.sample;
    }
    if (
      !other.run &&
      other.series === dataState.series &&
      other.sample === dataState.sample
    ) {
      other.run = dataState.run;
    }
    this.setState({data: dataState, ref: other});
  };
  handleRefChange = refState => this.setState({ref: refState});

  inputIsValid = () => {
    const check = o => [o.series, o.sample, o.run].every(e => e);
    const data = this.state.data;
    const ref = this.state.ref;
    return this.state.subsystem && check(data) && check(ref);
  };

  render() {
    return (
      <Container fluid>
        <Row>
          <Col md="6">
            <Row>
              <Col>
                <h3>Subsystem</h3>
                <SubsystemSelect
                  subsystem={this.state.subsystem}
                  onChange={this.handleSubsysChange}
                />
              </Col>
            </Row>
            <Row>
              <Col md="6">
                <h3>Data Run</h3>
                <RunSelectForm
                  {...this.state.data}
                  onChange={this.handleDataChange}
                />
              </Col>
              <Col md="6">
                <h3>Ref Run</h3>
                <RunSelectForm
                  {...this.state.ref}
                  onChange={this.handleRefChange}
                />
              </Col>
            </Row>
            <Row>
              <Col>
                <Button
                  color="success"
                  disabled={!this.inputIsValid()}
                  className={css`
                    width: 100%;
                    margin-top: 10px;
                  `}>
                  Submit
                </Button>
              </Col>
            </Row>
          </Col>
          <Col md="6" />
        </Row>
      </Container>
    );
  }
}
