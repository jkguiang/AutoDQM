import React, {Component} from 'react';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  NavLink as RouterNavLink,
} from 'react-router-dom';
import {Nav, NavItem, NavLink} from 'reactstrap';
import InputPage from './input/InputPage.js';
import PlotsPage from './plots/PlotsPage.js';

class App extends Component {
  render() {
    return (
      <Router>
        <React.Fragment>
          <Nav tabs>
            <NavItem>
              <NavLink
                tag={RouterNavLink}
                exact={true}
                to="/"
                activeClassName="active">
                AutoDQM
              </NavLink>
            </NavItem>
            <NavItem>
              <NavLink tag={RouterNavLink} to="/plots" activeClassName="active">
                Plots
              </NavLink>
            </NavItem>
          </Nav>
          <Switch>
            <Route exact path="/" component={InputPage} />
            <Route
              path="/plots/:subsystem/:refSeries/:refSample/:refRun/:dataSeries/:dataSample/:dataRun"
              component={PlotsPage}
            />
            <Route path="/plots" component={PlotsPage} />
          </Switch>
        </React.Fragment>
      </Router>
    );
  }
}

export default App;
