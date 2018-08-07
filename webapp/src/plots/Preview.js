import React, {Component} from 'react';
import {Card, CardBody, CardTitle, CardText, ListGroup} from 'reactstrap';

export default class Preview extends Component {
  render() {
    let inner;
    if (this.props.plot) {
      inner = (
        <React.Fragment>
          <img
            src={this.props.plot.png_path}
            alt="Plot Preview"
            className="card-img-top img-fluid"
          />
          <CardBody>
            <ListGroup flush />
          </CardBody>
        </React.Fragment>
      );
    } else {
      inner = (
        <CardBody>
          <CardTitle>Preview</CardTitle>
          <CardText>Hover over a plot to show more details.</CardText>
        </CardBody>
      );
    }
    return <Card className={this.props.className}>{inner}</Card>;
  }
}
