import React, {Component} from 'react';
import {Container, Row, Col} from 'reactstrap';
import InputForm from './InputForm.js';

export default class InputPage extends Component {
  render() {
    return (
      <Container fluid>
        <Row>
          <Col md="6">
            <InputForm recentQuery={this.props.recentQuery}/>
          </Col>
          <Col md="6" />
        </Row>
      </Container>
    );
  }
}
